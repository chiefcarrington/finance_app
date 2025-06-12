"""Simple wrapper around the OpenAI API for structured responses."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

try:
    import openai
except ModuleNotFoundError as exc:  # pragma: no cover - optional dependency
    openai = None  # type: ignore


@dataclass
class GPTWrapper:
    """Wrapper for OpenAI's ChatCompletion API."""

    api_key: str
    model: str = "gpt-3.5-turbo"

    def _ensure_client(self) -> None:
        """Initialize the OpenAI client if available."""
        if openai is None:
            raise RuntimeError(
                "openai package not installed. Please install openai to use GPTWrapper."
            )
        openai.api_key = self.api_key

    def ask(self, prompt: str, *, system_message: Optional[str] = None) -> str:
        """Send a prompt and return the raw response text."""
        self._ensure_client()
        messages: List[Dict[str, str]] = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=0,
        )
        return response["choices"][0]["message"]["content"].strip()

    def ask_json(self, prompt: str, *, system_message: Optional[str] = None) -> Any:
        """Return the response parsed as JSON if possible."""
        content = self.ask(prompt, system_message=system_message)
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return content
