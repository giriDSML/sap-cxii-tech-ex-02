import re


class RequestIntent:
    GREETING = "greeting"
    ORDERS_QUERY = "orders_query"


GREETING_PATTERNS = [
    r"^\s*hi\s*$",
    r"^\s*hello\s*$",
    r"^\s*hey\s*$",
    r"^\s*hi\s*,?\s*how are you\??\s*$",
    r"^\s*how are you\??\s*$",
    r"^\s*good morning\s*$",
    r"^\s*good evening\s*$",
    r"^\s*good afternoon\s*$",
    r"^\s*thanks\s*$",
    r"^\s*thank you\s*$",
]


def detect_request_intent(question: str) -> str:
    text = question.strip().lower()

    for pattern in GREETING_PATTERNS:
        if re.match(pattern, text):
            return RequestIntent.GREETING

    return RequestIntent.ORDERS_QUERY