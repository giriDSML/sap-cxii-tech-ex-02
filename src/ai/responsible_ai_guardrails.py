# Please note these are the baseline (practical baseline) guardrails for responsible AI 
# in this project. In a production system, these would need to be much more robust and 
# comprehensive, potentially involving external content moderation services, 
# more advanced NLP techniques, and continuous monitoring and updating based on 
# real-world usage patterns.
import re

from src.config import (
    MAX_QUESTION_LENGTH,
    MIN_QUESTION_LENGTH,
    ENABLE_ABUSE_GUARDRAILS,
    ENABLE_SQLI_GUARDRAILS,
    ENABLE_UNSUPPORTED_DOMAIN_GUARDRAILS,
    ENABLE_SECRET_SEEKING_GUARDRAILS,
    ENABLE_PROMPT_INJECTION_GUARDRAILS,
    ENABLE_JAILBREAK_GUARDRAILS,
)


class ResponsibleAIGuardrailError(Exception):
    pass


# Unsupported business concepts for the current orders-only schema
UNSUPPORTED_DOMAIN_KEYWORDS = {
    "product",
    "products",
    "category",
    "categories",
    "supplier",
    "suppliers",
    "salesperson",
    "employee",
    "employees",
    "warehouse",
    "inventory",
    "shipment",
    "shipments",
    "store",
    "stores",
    "sku",
    "skus",
}


# Prompt injection / instruction hijacking patterns
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+previous\s+instructions",
    r"ignore\s+all\s+previous",
    r"ignore\s+the\s+rules",
    r"bypass\s+rules",
    r"forget\s+the\s+rules",
    r"show\s+system\s+prompt",
    r"reveal\s+system\s+prompt",
    r"show\s+developer\s+message",
    r"developer\s+message",
    r"hidden\s+instructions",
    r"internal\s+instructions",
    r"return\s+the\s+prompt",
]


# Jailbreak / safety-bypass / role-switch patterns
# These are my recommended baseline patterns for this exercise.
JAILBREAK_PATTERNS = [
    r"developer\s+mode",
    r"jailbreak",
    r"act\s+as\s+if\s+there\s+are\s+no\s+rules",
    r"pretend\s+you\s+have\s+no\s+restrictions",
    r"you\s+are\s+now\s+unrestricted",
    r"disable\s+safety",
    r"turn\s+off\s+guardrails",
    r"override\s+safety",
    r"break\s+the\s+rules",
    r"ignore\s+safety",
    r"do\s+not\s+follow\s+the\s+system\s+prompt",
    r"simulate\s+an\s+unfiltered\s+model",
]


# SQL injection / query manipulation patterns
SQLI_INPUT_PATTERNS = [
    r"\bor\b\s+1\s*=\s*1\b",
    r"\band\b\s+1\s*=\s*1\b",
    r"\bunion\b\s+\bselect\b",
    r"--",
    r"/\*",
    r"\*/",
    r";\s*select\b",
    r";\s*drop\b",
    r";\s*delete\b",
    r";\s*update\b",
    r";\s*insert\b",
    r";\s*alter\b",
    r";\s*pragma\b",
]


# Sensitive-data / secret-seeking patterns
SECRET_SEEKING_PATTERNS = [
    r"\bpassword\b",
    r"\bpasswords\b",
    r"\bsecret\b",
    r"\bsecrets\b",
    r"\bapi\s*key\b",
    r"\btoken\b",
    r"\baccess\s*token\b",
    r"\bcredential\b",
    r"\bcredentials\b",
    r"\bprivate\s*key\b",
    r"\bssh\s*key\b",
]


# Abusive / unsafe language (practical baseline)
ABUSIVE_OR_UNSAFE_PATTERNS = [
    r"\bidiot\b",
    r"\bstupid\b",
    r"\bdumb\b",
    r"\btrash\b",
    r"\bkill\b",
    r"\bhate\b",
    r"\battack\b",
    r"\bviolent\b",
    r"\bthreat\b",
]


def normalize_question(question: str) -> str:
    return question.strip()


def validate_question_basic(question: str) -> None:
    if not question:
        raise ResponsibleAIGuardrailError("Question cannot be empty.")

    if len(question.strip()) < MIN_QUESTION_LENGTH:
        raise ResponsibleAIGuardrailError("Question is too short to process.")

    if len(question) > MAX_QUESTION_LENGTH:
        raise ResponsibleAIGuardrailError(
            f"Question is too long. Please keep it under {MAX_QUESTION_LENGTH} characters."
        )

    # malformed / meaningless input checks
    if re.fullmatch(r"[\W_]+", question):
        raise ResponsibleAIGuardrailError("Question does not contain meaningful content.")

    if re.search(r"[!?.,]{6,}", question):
        raise ResponsibleAIGuardrailError("Question appears malformed or excessively noisy.")


def validate_prompt_injection(question: str) -> None:
    if not ENABLE_PROMPT_INJECTION_GUARDRAILS:
        return

    lowered = question.lower()

    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, lowered):
            raise ResponsibleAIGuardrailError(
                "Question contains unsafe instruction-like content and cannot be processed."
            )


def validate_jailbreak_input(question: str) -> None:
    if not ENABLE_JAILBREAK_GUARDRAILS:
        return

    lowered = question.lower()

    for pattern in JAILBREAK_PATTERNS:
        if re.search(pattern, lowered):
            raise ResponsibleAIGuardrailError(
                "Question contains jailbreak or safety-bypass style content and cannot be processed."
            )


def validate_sql_injection_input(question: str) -> None:
    if not ENABLE_SQLI_GUARDRAILS:
        return

    lowered = question.lower()

    for pattern in SQLI_INPUT_PATTERNS:
        if re.search(pattern, lowered):
            raise ResponsibleAIGuardrailError(
                "Question contains suspicious SQL-injection-like content and cannot be processed."
            )


def validate_supported_domain(question: str) -> None:
    if not ENABLE_UNSUPPORTED_DOMAIN_GUARDRAILS:
        return

    lowered = question.lower()

    for keyword in UNSUPPORTED_DOMAIN_KEYWORDS:
        if re.search(rf"\b{re.escape(keyword)}\b", lowered):
            raise ResponsibleAIGuardrailError(
                f"This question references unsupported schema concept: '{keyword}'."
            )


def validate_secret_seeking(question: str) -> None:
    if not ENABLE_SECRET_SEEKING_GUARDRAILS:
        return

    lowered = question.lower()

    for pattern in SECRET_SEEKING_PATTERNS:
        if re.search(pattern, lowered):
            raise ResponsibleAIGuardrailError(
                "Question requests sensitive credentials or secret-like information and cannot be processed."
            )


def validate_abusive_or_unsafe_input(question: str) -> None:
    if not ENABLE_ABUSE_GUARDRAILS:
        return

    lowered = question.lower()

    for pattern in ABUSIVE_OR_UNSAFE_PATTERNS:
        if re.search(pattern, lowered):
            raise ResponsibleAIGuardrailError(
                "Question contains abusive or unsafe language and cannot be processed."
            )


def apply_responsible_ai_guardrails(question: str) -> str:
    question = normalize_question(question)

    validate_question_basic(question)
    validate_prompt_injection(question)
    validate_jailbreak_input(question)
    validate_sql_injection_input(question)
    validate_supported_domain(question)
    validate_secret_seeking(question)
    validate_abusive_or_unsafe_input(question)

    return question