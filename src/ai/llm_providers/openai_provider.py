import json
from openai import OpenAI

from src.ai.llm_providers.base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_name: str):
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def generate_json(self, system_prompt: str, user_prompt: str):
        response = self.client.chat.completions.create(
            model=self.model_name,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        content = response.choices[0].message.content
        parsed = json.loads(content)

        usage = response.usage
        token_count = 0
        if usage:
            token_count = (usage.prompt_tokens or 0) + (usage.completion_tokens or 0)

        return parsed, token_count

    def generate_text(self, system_prompt: str, user_prompt: str):
        response = self.client.chat.completions.create(
            model=self.model_name,
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        content = response.choices[0].message.content.strip()

        usage = response.usage
        token_count = 0
        if usage:
            token_count = (usage.prompt_tokens or 0) + (usage.completion_tokens or 0)

        return content, token_count