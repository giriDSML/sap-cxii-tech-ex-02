import sqlite3
import html
import json
from typing import Any

from src.config import (
    DB_PATH,
    NL2SQL_LOG_PATH,
    SENSITIVE_COLUMNS,
    ENABLE_LLM_ANSWER_SYNTHESIS,
    MAX_ROWS_FOR_LLM_SYNTHESIS,
)
from src.ai.nl2sql import (
    generate_validated_sql,
    NL2SQLAnswerabilityError,
    NL2SQLValidationError,
)
from src.ai.token_logging import log_nl2sql_event
from src.ai.prompts import build_answer_synthesis_prompt
from src.ai.responsible_ai_guardrails import (
    apply_responsible_ai_guardrails,
    ResponsibleAIGuardrailError,
)
from src.ai.request_intent import detect_request_intent, RequestIntent
from src.ai.pii_redaction import (
    redact_sensitive_literals,
    substitute_placeholders_with_params,
    restore_placeholders_for_display,
)
from src.db_layer.sqlite_client import get_connection
from src.ai.llm_router import get_llm_provider_for_tenant


def _rows_to_dicts(cursor: sqlite3.Cursor) -> list[dict[str, Any]]:
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _format_money(value: float | int | None) -> str:
    if value is None:
        return "$0.00"
    return f"${value:,.2f}"


def normalize_sql_for_display(sql: str) -> str:
    return html.unescape(sql)


def build_greeting_response() -> dict[str, Any]:
    return {
        "answer": (
            "Hello! I’m doing well. I can help you ask questions about the orders dataset, "
            "such as revenue, customer orders, counts, and date-based summaries."
        ),
        "sql_used": "",
        "rows": [],
    }


def contains_sensitive_columns(rows: list[dict[str, Any]]) -> bool:
    if not rows:
        return False

    first = rows[0]
    keys = set(first.keys())
    return any(col in keys for col in SENSITIVE_COLUMNS)


def build_deidentified_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Strict privacy-safe summary.
    This removes exact customer IDs and exact amounts.

    Note:
    Use this only when you do NOT want the LLM to mention exact values.
    For grounded answer generation, use build_llm_answer_payload().
    """
    if not rows:
        return {
            "row_count": 0,
            "has_results": False,
            "columns": [],
            "summary_type": "empty_result",
        }

    first = rows[0]
    columns = list(first.keys())

    summary = {
        "row_count": len(rows),
        "has_results": True,
        "columns": columns,
        "summary_type": "generic_result",
    }

    summary["sample_non_sensitive_keys"] = [
        c for c in columns if c not in SENSITIVE_COLUMNS
    ]

    date_values = []
    for row in rows[:MAX_ROWS_FOR_LLM_SYNTHESIS]:
        if "order_date" in row and row.get("order_date") is not None:
            date_values.append(str(row["order_date"]))

    if date_values:
        summary["date_range"] = {
            "min_order_date": min(date_values),
            "max_order_date": max(date_values),
        }

    return summary


def build_llm_answer_payload(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Grounded answer payload for LLM synthesis.

    This intentionally includes SQL result values so the LLM can generate a factual
    business answer.

    Use this when it is acceptable for the LLM provider to see these returned values.
    """
    return {
        "row_count": len(rows),
        "has_results": len(rows) > 0,
        "rows": rows[:MAX_ROWS_FOR_LLM_SYNTHESIS],
    }


def is_simple_result_shape(rows: list[dict[str, Any]]) -> bool:
    if not rows:
        return True

    first = rows[0]
    keys = set(first.keys())

    if keys == {"total_revenue", "order_count"}:
        return True

    if keys == {"total_revenue", "total_orders"}:
        return True

    if keys == {"avg_order_value"}:
        return True

    if len(rows) == 1 and keys == {"SUM(amount_usd)"}:
        return True

    if len(rows) == 1 and keys == {"COUNT(*)"}:
        return True

    if len(rows) == 1 and len(first) == 1:
        return True

    return False


def format_answer_deterministic(rows: list[dict[str, Any]]) -> str:
    """
    Optional deterministic formatter.
    This is kept as fallback only.
    Main answer path can use LLM if ENABLE_LLM_ANSWER_SYNTHESIS=True.
    """
    if not rows:
        return "No matching records found."

    first = rows[0]
    keys = set(first.keys())

    if keys in [
        {"total_revenue", "order_count"},
        {"total_revenue", "total_orders"},
    ]:
        total = first.get("total_revenue")
        count = first.get("order_count") or first.get("total_orders")
        return f"Total revenue: {_format_money(total)} ({count} orders)"

    if keys == {"avg_order_value"}:
        return f"Average order value: {_format_money(first['avg_order_value'])}"

    if len(rows) == 1 and "SUM(amount_usd)" in first:
        return f"Total revenue: {_format_money(first['SUM(amount_usd)'])}"

    if len(rows) == 1 and "COUNT(*)" in first:
        return f"Total orders: {first['COUNT(*)']}"

    if len(rows) == 1 and len(first) == 1:
        key = next(iter(first))
        return f"{key.replace('_', ' ').title()}: {first[key]}"

    return f"Returned {len(rows)} row(s)."


def build_safe_generic_answer(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "No matching records found."

    return f"Query executed successfully. Returned {len(rows)} row(s)."


def generate_answer_from_llm(
    question: str,
    sql_used: str,
    sanitized_payload: dict,
    llm_provider,
) -> tuple[str, int, str, str]:
    """
    LLM-based answer generation from grounded SQL result payload.

    Critical:
    - The payload must include row_count, has_results, and rows.
    - If rows contain values, the LLM must use them directly.
    """
    answer_system_prompt = """
You are a careful business data-answering assistant.

You answer strictly from the SQL result payload provided by the user.

Rules:
- Use only the provided payload.
- If row_count > 0, you MUST answer using the values in rows.
- Never say "No matching records found" when row_count > 0.
- Never say details are missing when rows contain fields.
- Do not invent values.
- Return plain text only.
""".strip()

    answer_user_prompt = build_answer_synthesis_prompt(
        question=question,
        sql_used=sql_used,
        sanitized_payload=sanitized_payload,
    )

    answer_text, token_count = llm_provider.generate_text(
        system_prompt=answer_system_prompt,
        user_prompt=answer_user_prompt,
    )

    return answer_text.strip(), token_count, answer_system_prompt, answer_user_prompt


def answer_question(question: str, tenant_id: str) -> dict[str, Any]:
    # ---------------------------------------------------
    # Step 1: Lightweight intent handling
    # ---------------------------------------------------
    intent = detect_request_intent(question)
    if intent == RequestIntent.GREETING:
        return build_greeting_response()

    conn = get_connection(DB_PATH)

    generated_sql = ""
    sql_for_display = ""
    system_prompt = ""
    initial_user_prompt = None
    retry_user_prompt = None
    initial_generated_sql = None
    forced_sql_after_hook = None
    retry_generated_sql = None
    answer_system_prompt = None
    answer_user_prompt = None
    token_count = 0
    retry_used = False

    try:
        # ---------------------------------------------------
        # Step 2: Responsible AI guardrails
        # ---------------------------------------------------
        question = apply_responsible_ai_guardrails(question)

        # ---------------------------------------------------
        # Step 3: Redact sensitive literals before SQL LLM call
        # ---------------------------------------------------
        redacted_question, placeholder_map = redact_sensitive_literals(question)

        # ---------------------------------------------------
        # Step 4: Resolve tenant-specific LLM provider
        # ---------------------------------------------------
        llm_provider = get_llm_provider_for_tenant(tenant_id)

        # ---------------------------------------------------
        # Step 5: Generate validated SQL
        # ---------------------------------------------------
        sql_result = generate_validated_sql(
            question=redacted_question,
            conn=conn,
            llm_provider=llm_provider,
        )

        generated_sql = sql_result["sql_used"]
        system_prompt = sql_result["system_prompt"]
        initial_user_prompt = sql_result["initial_user_prompt"]
        retry_user_prompt = sql_result["retry_user_prompt"]
        initial_generated_sql = sql_result["initial_generated_sql"]
        forced_sql_after_hook = sql_result["forced_sql_after_hook"]
        retry_generated_sql = sql_result["retry_generated_sql"]
        token_count = sql_result["total_token_count"]
        retry_used = sql_result["retry_used"]

        # ---------------------------------------------------
        # Step 6: Convert placeholders to execution params
        # and restore SQL for display
        # ---------------------------------------------------
        sql_for_exec, params = substitute_placeholders_with_params(
            generated_sql,
            placeholder_map,
        )

        sql_for_display = restore_placeholders_for_display(
            generated_sql,
            placeholder_map,
        )
        sql_for_display = normalize_sql_for_display(sql_for_display)

        # ---------------------------------------------------
        # Step 7: Execute SQL safely
        # ---------------------------------------------------
        cursor = conn.execute(sql_for_exec, params)
        rows = _rows_to_dicts(cursor)

        # ---------------------------------------------------
        # Step 8: Answer generation
        # ---------------------------------------------------
        if ENABLE_LLM_ANSWER_SYNTHESIS:
            # Grounded LLM payload with actual SQL result rows.
            # This fixes the issue where LLM said "No matching records found"
            # even when rows were present.
            sanitized_payload = build_llm_answer_payload(rows)

            # Temporary debug during testing.
            # You can remove this after validation.
            print("ANSWER SYNTHESIS PAYLOAD:")
            print(json.dumps(sanitized_payload, ensure_ascii=False, indent=2))

            (
                answer,
                answer_tokens,
                answer_system_prompt,
                answer_user_prompt,
            ) = generate_answer_from_llm(
                question=question,
                sql_used=sql_for_display,
                sanitized_payload=sanitized_payload,
                llm_provider=llm_provider,
            )
            token_count += answer_tokens

        elif is_simple_result_shape(rows):
            answer = format_answer_deterministic(rows)

        else:
            answer = build_safe_generic_answer(rows)

        # ---------------------------------------------------
        # Step 9: Logging
        # ---------------------------------------------------
        log_nl2sql_event(
            log_path=NL2SQL_LOG_PATH,
            question=question,
            system_prompt=system_prompt,
            initial_user_prompt=initial_user_prompt,
            retry_user_prompt=retry_user_prompt,
            initial_generated_sql=initial_generated_sql,
            forced_sql_after_hook=forced_sql_after_hook,
            retry_generated_sql=retry_generated_sql,
            answer_system_prompt=answer_system_prompt,
            answer_user_prompt=answer_user_prompt,
            generated_sql=sql_for_display,
            token_count=token_count,
            retry_used=retry_used,
            status="success",
        )

        return {
            "answer": answer,
            "sql_used": sql_for_display,
            "rows": rows,
        }

    except NL2SQLAnswerabilityError as e:
        log_nl2sql_event(
            log_path=NL2SQL_LOG_PATH,
            question=question,
            system_prompt=system_prompt,
            initial_user_prompt=initial_user_prompt,
            retry_user_prompt=retry_user_prompt,
            initial_generated_sql=initial_generated_sql,
            forced_sql_after_hook=forced_sql_after_hook,
            retry_generated_sql=retry_generated_sql,
            answer_system_prompt=answer_system_prompt,
            answer_user_prompt=answer_user_prompt,
            generated_sql=sql_for_display or generated_sql,
            token_count=token_count,
            retry_used=retry_used,
            status="cannot_answer",
            error_message=str(e),
        )
        raise

    except (
        ResponsibleAIGuardrailError,
        NL2SQLValidationError,
        sqlite3.Error,
        RuntimeError,
        ValueError,
    ) as e:
        log_nl2sql_event(
            log_path=NL2SQL_LOG_PATH,
            question=question,
            system_prompt=system_prompt,
            initial_user_prompt=initial_user_prompt,
            retry_user_prompt=retry_user_prompt,
            initial_generated_sql=initial_generated_sql,
            forced_sql_after_hook=forced_sql_after_hook,
            retry_generated_sql=retry_generated_sql,
            answer_system_prompt=answer_system_prompt,
            answer_user_prompt=answer_user_prompt,
            generated_sql=sql_for_display or generated_sql,
            token_count=token_count,
            retry_used=retry_used,
            status="error",
            error_message=str(e),
        )
        raise

    finally:
        conn.close()
