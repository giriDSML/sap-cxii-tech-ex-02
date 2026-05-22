import json
import requests

from src.ai.llm_providers.base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: str, model_name: str):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name

    def generate_json(self, system_prompt: str, user_prompt: str):
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model_name,
            "prompt": f"{system_prompt}\n\nUser request:\n{user_prompt}",
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0
            }
        }

        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()

        body = response.json()
        content = body.get("response", "")
        parsed = json.loads(content)

        prompt_eval_count = body.get("prompt_eval_count", 0) or 0
        eval_count = body.get("eval_count", 0) or 0
        token_count = prompt_eval_count + eval_count

        return parsed, token_count

    def generate_text(self, system_prompt: str, user_prompt: str):
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model_name,
            "prompt": f"{system_prompt}\n\nUser request:\n{user_prompt}",
            "stream": False,
            "options": {
                "temperature": 0
            }
        }

        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()

        body = response.json()
        content = body.get("response", "").strip()

        prompt_eval_count = body.get("prompt_eval_count", 0) or 0
        eval_count = body.get("eval_count", 0) or 0
        token_count = prompt_eval_count + eval_count

        return content, token_count