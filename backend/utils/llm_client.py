"""
Shared LLM client for calling OpenAI-compatible chat completion APIs (e.g., Groq).

This replaces direct calls to the local Ollama server so the rest of the
application can work with hosted models.
"""

import os
import logging
from typing import List, Dict, Optional, Any

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configuration via environment variables so you can swap providers without code changes.
LLM_API_KEY = os.getenv("LLM_API_KEY")  # e.g. Groq API key
LLM_BASE_URL = os.getenv(
    "LLM_BASE_URL", "https://api.groq.com/openai/v1/chat/completions"
)
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")


class LLMClientError(Exception):
    """Custom exception for LLM client errors."""


def _ensure_config():
    if not LLM_API_KEY:
        raise LLMClientError(
            "LLM_API_KEY is not set. Please create backend/.env with LLM_API_KEY=your_key"
        )


def call_llm(
    messages: List[Dict[str, str]],
    temperature: float = 0.2,
    max_tokens: int = 800,
    response_format: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Call the configured LLM provider and return the message content string.

    Args:
        messages: List of {"role": "system"|"user"|"assistant", "content": "..."}
        temperature: Sampling temperature
        max_tokens: Max new tokens to generate
        response_format: Optional response_format (e.g. {"type": "json_object"})

    Returns:
        The string content of the first choice's message.
    """
    _ensure_config()

    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }

    payload: Dict[str, Any] = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    if response_format is not None:
        payload["response_format"] = response_format

    logger.info(f"Calling LLM model '{LLM_MODEL}' via {LLM_BASE_URL}...")

    try:
        resp = requests.post(LLM_BASE_URL, json=payload, headers=headers, timeout=60)
        if resp.status_code != 200:
            raise LLMClientError(f"LLM API error {resp.status_code}: {resp.text[:300]}")

        data = resp.json()
        choices = data.get("choices")
        if not choices:
            raise LLMClientError("LLM response has no choices field")

        message = choices[0].get("message") or {}
        content = message.get("content")
        if not isinstance(content, str):
            raise LLMClientError("LLM response message content is not a string")

        return content

    except requests.RequestException as e:
        logger.error(f"Network error calling LLM API: {e}")
        raise LLMClientError(f"Network error calling LLM API: {e}") from e

    except ValueError as e:
        logger.error(f"Failed to parse LLM response JSON: {e}")
        raise LLMClientError(f"Failed to parse LLM response JSON: {e}") from e
