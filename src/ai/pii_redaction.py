import re
from decimal import Decimal


CUSTOMER_ID_PATTERN = re.compile(r"\bC\d{3,}\b", re.IGNORECASE)

# Replace amount-like numbers only in amount/money context
AMOUNT_CONTEXT_PATTERNS = [
    # amount / revenue / price / value / worth + number
    re.compile(
        r"\b(amount|revenue|price|value|worth)\s*(?:is\s*|=|>|<|>=|<=|above\s+|below\s+|greater\s+than\s+|less\s+than\s+)?(\d+(?:,\d{3})*(?:\.\d+)?)",
        re.IGNORECASE,
    ),
    # number + currency
    re.compile(r"\b(\d+(?:,\d{3})*(?:\.\d+)?)\s*(usd|eur|aed|sar)\b", re.IGNORECASE),
    # currency + number
    re.compile(r"\b(usd|eur|aed|sar)\s*(\d+(?:,\d{3})*(?:\.\d+)?)\b", re.IGNORECASE),
    # $123.45 style
    re.compile(r"(\$\s*\d+(?:,\d{3})*(?:\.\d+)?)", re.IGNORECASE),
]


def _normalize_amount_string(raw: str) -> str:
    raw = raw.strip()
    raw = raw.replace("$", "")
    raw = raw.replace(",", "")
    raw = re.sub(r"\b(usd|eur|aed|sar)\b", "", raw, flags=re.IGNORECASE).strip()
    return raw


def redact_sensitive_literals(question: str):
    """
    Returns:
        redacted_question, placeholder_map

    Example:
        Input:
            What is the total revenue from customer C001 above 5000 in the last 30 days?

        Output:
            (
                "What is the total revenue from customer CUSTOMER_REF_1 above AMOUNT_REF_1 in the last 30 days?",
                {
                    "CUSTOMER_REF_1": "C001",
                    "AMOUNT_REF_1": 5000.0
                }
            )
    """
    placeholder_map = {}
    customer_counter = 1
    amount_counter = 1

    # 1) Replace customer IDs
    def customer_replacer(match):
        nonlocal customer_counter
        real_value = match.group(0)
        placeholder = f"CUSTOMER_REF_{customer_counter}"
        placeholder_map[placeholder] = real_value
        customer_counter += 1
        return placeholder

    redacted = CUSTOMER_ID_PATTERN.sub(customer_replacer, question)

    # 2) Replace amount-like values only in amount context
    for pattern in AMOUNT_CONTEXT_PATTERNS:
        while True:
            match = pattern.search(redacted)
            if not match:
                break

            full_match = match.group(0)

            num_search = re.search(r"\d+(?:,\d{3})*(?:\.\d+)?", full_match)
            if not num_search:
                break

            raw_number = num_search.group(0)
            normalized = _normalize_amount_string(raw_number)

            try:
                amount_value = float(Decimal(normalized))
            except Exception:
                break

            placeholder = f"AMOUNT_REF_{amount_counter}"
            placeholder_map[placeholder] = amount_value
            amount_counter += 1

            replaced_phrase = full_match.replace(raw_number, placeholder, 1)
            redacted = redacted[:match.start()] + replaced_phrase + redacted[match.end():]

    return redacted, placeholder_map


def substitute_placeholders_with_params(sql: str, placeholder_map: dict[str, object]):
    """
    Convert placeholders in generated SQL into bound parameters.

    Example:
        WHERE customer_id = 'CUSTOMER_REF_1' AND amount_usd > AMOUNT_REF_1
    becomes:
        WHERE customer_id = ? AND amount_usd > ?
        params = ["C001", 5000.0]
    """
    rewritten_sql = sql
    params = []

    # Replace quoted placeholders first
    for placeholder, real_value in placeholder_map.items():
        quoted_token = f"'{placeholder}'"
        if quoted_token in rewritten_sql:
            rewritten_sql = rewritten_sql.replace(quoted_token, "?", 1)
            params.append(real_value)

    # Replace unquoted placeholders next
    for placeholder, real_value in placeholder_map.items():
        token_pattern = rf"\b{re.escape(placeholder)}\b"
        if re.search(token_pattern, rewritten_sql):
            rewritten_sql = re.sub(token_pattern, "?", rewritten_sql, count=1)
            params.append(real_value)

    return rewritten_sql, params



def restore_placeholders_for_display(sql: str, placeholder_map: dict[str, object]) -> str:
    """
    Restore placeholders back into user-readable SQL for API response display.

    Example:
        SELECT ... WHERE customer_id = 'CUSTOMER_REF_1' AND amount_usd > AMOUNT_REF_1
    becomes:
        SELECT ... WHERE customer_id = 'C001' AND amount_usd > 5000.0
    """
    restored_sql = sql

    for placeholder, real_value in placeholder_map.items():
        if isinstance(real_value, str):
            restored_sql = restored_sql.replace(f"'{placeholder}'", f"'{real_value}'")
            restored_sql = restored_sql.replace(placeholder, real_value)
        else:
            restored_sql = restored_sql.replace(placeholder, str(real_value))

    return restored_sql