from abc import ABC, abstractmethod
from typing import Any


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_json(self, system_prompt: str, user_prompt: str) -> tuple[dict[str, Any], int]:
        """
        Generate a structured JSON response from the provider.

        Returns:
            parsed_json_response, token_count
        """
        raise NotImplementedError

    @abstractmethod
    def generate_text(self, system_prompt: str, user_prompt: str) -> tuple[str, int]:
        """
        Generate a plain-text response from the provider.

        Returns:
            plain_text_response, token_count
        """
        raise NotImplementedError