from src.config import (
    TENANT_LLM_MAP,
    DEFAULT_TENANT_ID,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
)
from src.ai.llm_providers.openai_provider import OpenAIProvider
from src.ai.llm_providers.ollama_provider import OllamaProvider

# Uncomment this only after you implement anthropic_provider.py
# from src.ai.llm_providers.anthropic_provider import AnthropicProvider


def get_provider_name_for_tenant(tenant_id: str) -> str:
    tenant_id = tenant_id or DEFAULT_TENANT_ID
    return TENANT_LLM_MAP.get(tenant_id, TENANT_LLM_MAP[DEFAULT_TENANT_ID])


def get_llm_provider_for_tenant(tenant_id: str):
    provider_name = get_provider_name_for_tenant(tenant_id)

    if provider_name == "openai":
        return OpenAIProvider(
            api_key=OPENAI_API_KEY,
            model_name=OPENAI_MODEL,
        )

    if provider_name == "ollama":
        return OllamaProvider(
            base_url=OLLAMA_BASE_URL,
            model_name=OLLAMA_MODEL,
        )

    # anthropic_provider.py
    # if provider_name == "anthropic":
    #     return AnthropicProvider(
    #         api_key=ANTHROPIC_API_KEY,
    #         model_name=ANTHROPIC_MODEL,
    #     )

    raise ValueError(f"Unsupported provider configured for tenant '{tenant_id}': {provider_name}")