"""Thin wrapper around the Anthropic Messages API that returns parsed JSON."""

from __future__ import annotations

import json
import re
from typing import Any


class LLMError(RuntimeError):
    """Raised when the model is unavailable or its reply cannot be used."""


def extract_json(text: str) -> Any:
    """Parse a JSON value from a model reply, tolerating code fences and stray prose."""
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.DOTALL)
    candidate = fenced.group(1) if fenced else text
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass
    start, end = candidate.find("{"), candidate.rfind("}")
    if start == -1 or end <= start:
        raise LLMError("The model reply contained no JSON object.")
    try:
        return json.loads(candidate[start : end + 1])
    except json.JSONDecodeError as exc:
        raise LLMError(f"The model reply was not valid JSON: {exc}") from exc


class LLMClient:
    """Facade so the rest of the app never talks to the SDK directly."""

    def __init__(self, api_key: str, model: str, max_tokens: int = 4096) -> None:
        try:
            import anthropic
        except ImportError as exc:
            raise LLMError("The anthropic package is missing. Run: pip install -r requirements.txt") from exc
        self._client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

    def complete_json(self, system: str, user: str) -> Any:
        message = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(block.text for block in message.content if block.type == "text")
        return extract_json(text)
