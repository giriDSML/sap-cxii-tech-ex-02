import json
from datetime import datetime, timezone
from pathlib import Path


def log_nl2sql_event(
    log_path: str,
    question: str,
    system_prompt: str,
    initial_user_prompt: str | None,
    retry_user_prompt: str | None,
    initial_generated_sql: str | None,
    forced_sql_after_hook: str | None,
    retry_generated_sql: str | None,
    answer_system_prompt: str | None,
    answer_user_prompt: str | None,
    generated_sql: str,
    token_count: int,
    retry_used: bool,
    status: str,
    error_message: str | None = None,
) -> None:
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question": question,
        "system_prompt": system_prompt,
        "initial_user_prompt": initial_user_prompt,
        "retry_user_prompt": retry_user_prompt,
        "initial_generated_sql": initial_generated_sql,
        "forced_sql_after_hook": forced_sql_after_hook,
        "retry_generated_sql": retry_generated_sql,
        "answer_system_prompt": answer_system_prompt,
        "answer_user_prompt": answer_user_prompt,
        "generated_sql": generated_sql,
        "token_count": token_count,
        "retry_used": retry_used,
        "status": status,
        "error_message": error_message,
    }

    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")