"""
LLM Client Module.

This module provides a unified interface for interacting with different Large Language Model (LLM)
providers, specifically Anthropic and Ollama. It handles client initialization and text generation
requests, abstracting away the specific API details of each provider.
"""

#import os
from typing import Optional #, List, Dict, Any
import anthropic
import ollama
from .config import get_config

class LLMClient:
    """
    A client for interacting with various LLM providers.

    This class manages connections to Anthropic and Ollama services and provides
    a common method for generating text from prompts.
    """

    def __init__(self):
        """
        Initialize the LLMClient.

        Sets up the configuration and initializes clients for Anthropic (if API key is present)
        and Ollama (using the configured base URL).
        """

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

        Args:
            prompt (str): The user prompt to send to the model.
            model (str): The name of the model to use (e.g., "claude-3-opus", "qwen2.5-coder").
            system_prompt (Optional[str]): An optional system prompt to set the context or behavior.
            provider (str): The LLM provider to use ("anthropic" or "ollama"). Defaults to "ollama".

        Returns:
            str: The generated text response from the model.

        Raises:
            ValueError: If an unknown provider is specified.
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
        """
        Internal method to generate text using the Anthropic API.

        Args:
            prompt (str): The user prompt.
            model (str): The Anthropic model name.
            system_prompt (Optional[str]): Optional system prompt.

        Returns:
            str: The generated text.

        Raises:
            ValueError: If the Anthropic API key is not configured.
        """

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
        """
        Internal method to generate text using the Ollama API.

        Args:
            prompt (str): The user prompt.
            model (str): The Ollama model name.
            system_prompt (Optional[str]): Optional system prompt.

        Returns:
            str: The generated text.
        """

        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})
        response = self.ollama_client.chat(model=model, messages=messages)

        return response['message']['content']
