"""
Arena engine: sends the same prompt to N models concurrently and collects
each response with timing.

Model IDs use a "provider:model" convention (e.g. "ollama:llama3.1",
"openai:gpt-4o-mini") so the frontend can display provider badges and the
backend can route each call to the right client without ambiguity.

Concurrency: all models are called via asyncio.gather, so a 4-model battle
takes as long as the SLOWEST model, not the sum of all four — the core
reason this needs to be async rather than a simple loop.
"""
import asyncio
import logging
import time
from typing import Dict, List

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_openai_client = None


class ModelCallError(Exception):
    def __init__(self, model_id: str, message: str):
        self.model_id = model_id
        self.message = message
        super().__init__(f"{model_id}: {message}")


def parse_model_id(model_id: str) -> tuple:
    """'ollama:llama3.1' -> ('ollama', 'llama3.1')"""
    if ":" not in model_id:
        raise ValueError(f"Invalid model_id '{model_id}' — expected 'provider:model'")
    provider, model_name = model_id.split(":", 1)
    return provider, model_name


async def call_ollama(model_name: str, prompt: str) -> Dict:
    async with httpx.AsyncClient(timeout=settings.battle_timeout_seconds) as client:
        try:
            response = await client.post(
                f"{settings.ollama_base_url}/api/chat",
                json={
                    "model": model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                },
            )
            response.raise_for_status()
        except httpx.ConnectError as exc:
            raise ModelCallError(
                f"ollama:{model_name}",
                f"Could not reach Ollama at {settings.ollama_base_url}. Is it running?",
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise ModelCallError(
                f"ollama:{model_name}",
                f"Ollama returned {exc.response.status_code}. Is '{model_name}' pulled? "
                f"Run: ollama pull {model_name}",
            ) from exc

        data = response.json()
        return {
            "text": data["message"]["content"],
            # Ollama reports token counts natively — no need to estimate.
            "tokens_in": data.get("prompt_eval_count", 0),
            "tokens_out": data.get("eval_count", 0),
        }


def get_openai_client():
    global _openai_client
    if _openai_client is None:
        from openai import AsyncOpenAI
        _openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _openai_client


async def call_openai(model_name: str, prompt: str) -> Dict:
    if not settings.openai_api_key:
        raise ModelCallError(f"openai:{model_name}", "OPENAI_API_KEY is not configured.")

    client = get_openai_client()
    try:
        response = await client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
    except Exception as exc:
        raise ModelCallError(f"openai:{model_name}", str(exc)) from exc

    return {
        "text": response.choices[0].message.content,
        "tokens_in": response.usage.prompt_tokens,
        "tokens_out": response.usage.completion_tokens,
    }


async def call_model(model_id: str, prompt: str) -> Dict:
    """Dispatches to the right provider and wraps the result with timing + error handling."""
    provider, model_name = parse_model_id(model_id)
    start = time.perf_counter()

    try:
        if provider == "ollama":
            result = await call_ollama(model_name, prompt)
        elif provider == "openai":
            result = await call_openai(model_name, prompt)
        else:
            raise ValueError(f"Unknown provider '{provider}'")

        latency_ms = round((time.perf_counter() - start) * 1000, 1)
        return {
            "model_id": model_id,
            "status": "success",
            "text": result["text"],
            "tokens_in": result["tokens_in"],
            "tokens_out": result["tokens_out"],
            "latency_ms": latency_ms,
        }

    except ModelCallError as exc:
        latency_ms = round((time.perf_counter() - start) * 1000, 1)
        logger.warning("Model call failed for %s: %s", model_id, exc.message)
        return {
            "model_id": model_id,
            "status": "error",
            "text": None,
            "error": exc.message,
            "tokens_in": 0,
            "tokens_out": 0,
            "latency_ms": latency_ms,
        }


async def run_battle(model_ids: List[str], prompt: str) -> List[Dict]:
    """
    Calls every model concurrently and returns results in the SAME order
    as model_ids (not completion order), so the frontend can render a
    stable side-by-side layout regardless of which model responded first.
    """
    tasks = [call_model(model_id, prompt) for model_id in model_ids]
    results = await asyncio.gather(*tasks)
    return list(results)
