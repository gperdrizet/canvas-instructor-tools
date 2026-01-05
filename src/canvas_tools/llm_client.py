#import os
from typing import Optional #, List, Dict, Any
import anthropic
import ollama
from .config import get_config

class LLMClient:

    def __init__(self):

        self.config = get_config()
        self.anthropic_client = None

        if self.config.anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=self.config.anthropic_api_key)

        # Ollama client is usually stateless/http based, but the python lib handles it.
        # We configure the host if needed.
        # The ollama library uses OLLAMA_HOST env var, but we can also pass it if needed.
        # For now, we assume the env var or default is sufficient for the library, 
        # or we set it explicitly if the library supports client instantiation.
        self.ollama_client = ollama.Client(base_url=self.config.ollama_base_url)

    def generate_text(
            self,
            prompt: str,
            model: str,
            system_prompt: Optional[str] = None,
            provider: str = "ollama"
    ) -> str:
        """
        Generate text using the specified provider and model.
        """

        if provider == "anthropic":
            return self._generate_anthropic(prompt, model, system_prompt)

        elif provider == "ollama":
            return self._generate_ollama(prompt, model, system_prompt)

        else:
            raise ValueError(f"Unknown provider: {provider}")

    def _generate_anthropic(
            self,
            prompt: str,
            model: str,
            system_prompt: Optional[str] = None
    ) -> str:

        if not self.anthropic_client:
            raise ValueError("Anthropic API key not configured.")

        messages = [{"role": "user", "content": prompt}]
        kwargs = {
            "model": model,
            "max_tokens": 4096,
            "messages": messages
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self.anthropic_client.messages.create(**kwargs)
        return response.content[0].text

    def _generate_ollama(
            self,
            prompt: str,
            model: str,
            system_prompt: Optional[str] = None
    ) -> str:

        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self.ollama_client.chat(model=model, messages=messages)

        return response['message']['content']
