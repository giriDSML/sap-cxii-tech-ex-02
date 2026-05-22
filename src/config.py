import os

# -------------------------------------------------------
# Database + logging
# -------------------------------------------------------
DB_PATH = os.getenv("DB_PATH", "db/orders.db")
NL2SQL_LOG_PATH = os.getenv("NL2SQL_LOG_PATH", "logs/nl2sql_requests.jsonl")

# -------------------------------------------------------
# Tenant routing
# -------------------------------------------------------
DEFAULT_TENANT_ID = os.getenv("DEFAULT_TENANT_ID", "tenant_US")

TENANT_LLM_MAP = {
    "tenant_KSA": "ollama",
    "tenant_US": "openai",
    "tenant_EU": "openai",
}

# -------------------------------------------------------
# Provider settings
# -------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

# Optional future Anthropic placeholders
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

# -------------------------------------------------------
# Responsible AI / guardrail settings
# -------------------------------------------------------
MAX_QUESTION_LENGTH = int(os.getenv("MAX_QUESTION_LENGTH", "1000"))
MIN_QUESTION_LENGTH = int(os.getenv("MIN_QUESTION_LENGTH", "3"))

ENABLE_ABUSE_GUARDRAILS = os.getenv("ENABLE_ABUSE_GUARDRAILS", "true").lower() == "true"
ENABLE_SQLI_GUARDRAILS = os.getenv("ENABLE_SQLI_GUARDRAILS", "true").lower() == "true"
ENABLE_UNSUPPORTED_DOMAIN_GUARDRAILS = os.getenv("ENABLE_UNSUPPORTED_DOMAIN_GUARDRAILS", "true").lower() == "true"
ENABLE_SECRET_SEEKING_GUARDRAILS = os.getenv("ENABLE_SECRET_SEEKING_GUARDRAILS", "true").lower() == "true"
ENABLE_PROMPT_INJECTION_GUARDRAILS = os.getenv("ENABLE_PROMPT_INJECTION_GUARDRAILS", "true").lower() == "true"
ENABLE_JAILBREAK_GUARDRAILS = os.getenv("ENABLE_JAILBREAK_GUARDRAILS", "true").lower() == "true"

# -------------------------------------------------------
# Sensitive data controls
# -------------------------------------------------------
SENSITIVE_COLUMNS = {
    "customer_id",
    "amount_usd",
    "original_amount",
}

ENABLE_LLM_ANSWER_SYNTHESIS = os.getenv("ENABLE_LLM_ANSWER_SYNTHESIS", "true").lower() == "true"
ENABLE_DEIDENTIFIED_SYNTHESIS = os.getenv("ENABLE_DEIDENTIFIED_SYNTHESIS", "true").lower() == "true"
MAX_ROWS_FOR_LLM_SYNTHESIS = int(os.getenv("MAX_ROWS_FOR_LLM_SYNTHESIS", "20"))


FORCE_NL2SQL_RETRY = False


# -------------------------------------------------------
# Semantic search / embedding index settings
# -------------------------------------------------------
SEMANTIC_INDEX_ROOT = os.getenv(
    "SEMANTIC_INDEX_ROOT",
    "artifacts/semantic_index"
)

SEMANTIC_ACTIVE_INDEX_FILE = os.getenv(
    "SEMANTIC_ACTIVE_INDEX_FILE",
    "artifacts/semantic_index/active_index.json"
)


#  Switch to open-source sentence transformer model
EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "sentence-transformers/all-MiniLM-L6-v2"
).strip()



DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "5"))
MAX_TOP_K = int(os.getenv("MAX_TOP_K", "20"))


# -------------------------------------------------------
# Semantic index reload endpoint
# -------------------------------------------------------
SEMANTIC_RELOAD_URL = os.getenv(
    "SEMANTIC_RELOAD_URL",
    "http://127.0.0.1:8000/orders/semantic_index/reload"
)