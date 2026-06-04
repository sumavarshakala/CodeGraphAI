"""
Ollama LLM client — qwen3:8b.

Changes vs original:
- Explicit num_ctx to prevent context-window surprises.
- Structured OllamaError exception so callers can decide how to surface it.
- Timeout raised to 360 s; connection/timeout errors caught separately.
- Thinking tokens disabled by default (think=False) to cut latency;
  re-enable by passing think=True to generate_answer().
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

import requests

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen3:8b"

# Keep context window deterministic.
# 8 192 is safe for qwen3:8b on 8 GB VRAM.
# Increase to 16_384 if you have >=16 GB VRAM.
DEFAULT_NUM_CTX = 8_192


@dataclass
class OllamaError(Exception):
    """Raised when Ollama returns an error or is unreachable."""

    message: str
    status_code: int | None = None

    def __str__(self) -> str:
        if self.status_code:
            return f"Ollama error {self.status_code}: {self.message}"
        return f"Ollama error: {self.message}"


def generate_answer(
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    num_ctx: int = DEFAULT_NUM_CTX,
    temperature: float = 0.1,
    think: bool = False,
    timeout: int = 360,
) -> str:
    """
    Send *prompt* to Ollama and return the response text.

    Raises:
        OllamaError: if Ollama is unreachable or returns a non-2xx status.
    """
    payload: dict = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_ctx": num_ctx,
            "temperature": temperature,
        },
    }
    # qwen3 supports a /no_think control token; honour caller preference.
    if not think:
        payload["think"] = False

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=timeout,
        )
    except requests.exceptions.ConnectionError as exc:
        raise OllamaError(
            message="Cannot connect to Ollama. Is it running on localhost:11434?"
        ) from exc
    except requests.exceptions.Timeout as exc:
        raise OllamaError(
            message=f"Ollama did not respond within {timeout} seconds."
        ) from exc

    if not response.ok:
        # Extract Ollama's own error message from the response body.
        try:
            detail = response.json().get("error", response.text[:300])
        except Exception:
            detail = response.text[:300]
        raise OllamaError(message=detail, status_code=response.status_code)

    data = response.json()
    return data.get("response", "")