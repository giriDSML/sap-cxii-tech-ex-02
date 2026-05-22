import re
import sqlite3

from src.config import FORCE_NL2SQL_RETRY
from src.ai.prompts import (
    build_system_prompt,
    build_retry_user_prompt,
    get_schema_context,
)


FORBIDDEN_SQL_KEYWORDS = {
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "pragma",
    "attach",
    "detach",
    "replace",
    "create",
    "truncate",
}


class NL2SQLValidationError(Exception):
    pass


class NL2SQLAnswerabilityError(Exception):
    pass


def _normalize_sql(sql: str) -> str:
    sql = sql.strip()

    if sql.startswith("```"):
        sql = sql.replace("```sql", "").replace("```", "").strip()

    if sql.endswith(";"):
        sql = sql[:-1].strip()

    return sql


def validate_sql(sql: str, conn: sqlite3.Connection) -> None:
    sql = _normalize_sql(sql)

    if not sql:
        raise NL2SQLValidationError("Generated SQL is empty")

    lowered = sql.lower()

    if ";" in sql:
        raise NL2SQLValidationError("Multiple SQL statements are not allowed")

    if not (lowered.startswith("select") or lowered.startswith("with")):
        raise NL2SQLValidationError("Only SELECT queries are allowed")

    for keyword in FORBIDDEN_SQL_KEYWORDS:
        if re.search(rf"\b{keyword}\b", lowered):
            raise NL2SQLValidationError(f"Forbidden SQL keyword detected: {keyword}")

    suspicious_patterns = [
        r"\bunion\b\s+\bselect\b",
        r"\bor\b\s+1\s*=\s*1\b",
        r"--",
        r"/\*",
        r"\*/",
    ]
    for pattern in suspicious_patterns:
        if re.search(pattern, lowered):
            raise NL2SQLValidationError(
                "Generated SQL contains suspicious injection-like pattern."
            )

    table_refs = re.findall(r"\b(?:from|join)\s+([a-zA-Z_][a-zA-Z0-9_]*)", lowered)
    if any(t != "orders" for t in table_refs):
        raise NL2SQLValidationError("SQL may only query the orders table")

    try:
        conn.execute(f"EXPLAIN QUERY PLAN {sql}")
    except sqlite3.Error as e:
        raise NL2SQLValidationError(f"SQL failed dry-run validation: {e}")


def generate_validated_sql(question: str, conn: sqlite3.Connection, llm_provider):
    schema_context = get_schema_context(conn)
    system_prompt = build_system_prompt(schema_context)

    total_tokens = 0
    retry_used = False
    initial_user_prompt = question
    retry_user_prompt = None

    initial_generated_sql = None
    forced_sql_after_hook = None
    retry_generated_sql = None

    # ---------------------------------------------------
    # First attempt
    # ---------------------------------------------------
    result, tokens = llm_provider.generate_json(system_prompt, initial_user_prompt)
    total_tokens += tokens

    can_answer = bool(result.get("can_answer", False))
    reason = str(result.get("reason", "")).strip()
    sql = str(result.get("sql", "")).strip()

    initial_generated_sql = _normalize_sql(sql)

    if not can_answer:
        raise NL2SQLAnswerabilityError(
            reason or "Question cannot be answered from the available schema"
        )

    # ---------------------------------------------------
    # Deterministic retry test hook
    # ---------------------------------------------------
    
    #if FORCE_NL2SQL_RETRY:
     #   sql = "SELECT SUM(non_existing_amount_column) FROM orders"
      #  forced_sql_after_hook = sql

    try:
        validate_sql(sql, conn)

        return {
            "sql_used": _normalize_sql(sql),
            "system_prompt": system_prompt,
            "initial_user_prompt": initial_user_prompt,
            "retry_user_prompt": retry_user_prompt,
            "initial_generated_sql": initial_generated_sql,
            "forced_sql_after_hook": forced_sql_after_hook,
            "retry_generated_sql": retry_generated_sql,
            "total_token_count": total_tokens,
            "retry_used": retry_used,
        }

    except Exception as first_error:
        retry_used = True

        retry_user_prompt = build_retry_user_prompt(
            question=question,
            previous_sql=sql,
            error_message=str(first_error),
            schema_context=schema_context,
        )

        retry_result, retry_tokens = llm_provider.generate_json(system_prompt, retry_user_prompt)
        total_tokens += retry_tokens

        can_answer_retry = bool(retry_result.get("can_answer", False))
        reason_retry = str(retry_result.get("reason", "")).strip()
        sql_retry = str(retry_result.get("sql", "")).strip()

        retry_generated_sql = _normalize_sql(sql_retry)

        if not can_answer_retry:
            raise NL2SQLAnswerabilityError(
                reason_retry or "Question cannot be answered from the available schema after retry"
            )

        validate_sql(sql_retry, conn)

        return {
            "sql_used": _normalize_sql(sql_retry),
            "system_prompt": system_prompt,
            "initial_user_prompt": initial_user_prompt,
            "retry_user_prompt": retry_user_prompt,
            "initial_generated_sql": initial_generated_sql,
            "forced_sql_after_hook": forced_sql_after_hook,
            "retry_generated_sql": retry_generated_sql,
            "total_token_count": total_tokens,
            "retry_used": retry_used,
        }