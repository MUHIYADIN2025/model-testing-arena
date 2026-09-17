"""
Evaluator: turns raw arena_engine results into comparable metrics.

Two kinds of "quality" signal are produced:
1. Cost/latency/token metrics — objective, computed directly from the API response.
2. An optional LLM-as-judge score — a second LLM call that rates each response
   on a rubric (correctness, clarity, completeness). This is the same technique
   used by real model-eval pipelines (e.g. MT-Bench) when human raters aren't
   available for every single comparison; it's a heuristic, not ground truth,
   and the arena still lets a human vote as the final signal (see elo.py).
"""
import json
import logging
from typing import Dict, List

import httpx

from app.config import get_settings
from app.arena_engine import parse_model_id

logger = logging.getLogger(__name__)
settings = get_settings()


def estimate_cost(model_id: str, tokens_in: int, tokens_out: int) -> float:
    """Returns estimated USD cost for one response. Ollama models are always $0."""
    provider, model_name = parse_model_id(model_id)
    if provider == "ollama":
        return 0.0

    pricing = settings.pricing_table.get(model_name)
    if not pricing:
        return 0.0  # unknown model — don't guess a cost

    cost = (tokens_in / 1000) * pricing["input"] + (tokens_out / 1000) * pricing["output"]
    return round(cost, 6)


def enrich_with_cost(results: List[Dict]) -> List[Dict]:
    for result in results:
        if result["status"] == "success":
            result["estimated_cost_usd"] = estimate_cost(
                result["model_id"], result["tokens_in"], result["tokens_out"]
            )
        else:
            result["estimated_cost_usd"] = 0.0
    return results


JUDGE_SYSTEM_PROMPT = """You are an impartial judge evaluating AI model responses to the same \
prompt. Score EACH response from 1-10 on: correctness, clarity, and completeness — then give \
an overall score (1-10, can be a weighted blend, your judgment).

Respond with ONLY a JSON object mapping each response's label to its overall score, e.g.:
{"A": 8, "B": 6, "C": 9}

No explanation, no markdown, just the JSON object.
"""


async def _call_judge(system_prompt: str, user_prompt: str) -> str:
    if settings.judge_provider == "ollama":
        async with httpx.AsyncClient(timeout=settings.battle_timeout_seconds) as client:
            try:
                response = await client.post(
                    f"{settings.ollama_base_url}/api/chat",
                    json={
                        "model": settings.judge_model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "stream": False,
                        "format": "json",
                        "options": {"temperature": 0.1},
                    },
                )
                response.raise_for_status()
                return response.json()["message"]["content"]
            except httpx.ConnectError as exc:
                raise RuntimeError(
                    f"Could not reach Ollama judge at {settings.ollama_base_url}."
                ) from exc

    elif settings.judge_provider == "openai":
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.chat.completions.create(
            model=settings.judge_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content

    raise ValueError(f"Unknown judge_provider '{settings.judge_provider}'")


async def judge_battle(prompt: str, results: List[Dict]) -> List[Dict]:
    """
    Sends all successful responses to the judge model in one call (labeled
    A/B/C... so the judge can't be biased by seeing real model names) and
    attaches a judge_score to each result.
    """
    if settings.judge_provider == "none":
        return results

    successful = [r for r in results if r["status"] == "success"]
    if len(successful) < 2:
        return results  # judging a single response in isolation isn't meaningful

    labels = [chr(65 + i) for i in range(len(successful))]  # A, B, C...
    label_map = dict(zip(labels, [r["model_id"] for r in successful]))

    responses_block = "\n\n".join(
        f"Response {label}:\n{r['text']}" for label, r in zip(labels, successful)
    )
    user_prompt = f"Original prompt: {prompt}\n\n{responses_block}"

    try:
        raw = await _call_judge(JUDGE_SYSTEM_PROMPT, user_prompt)
        scores = json.loads(raw)
    except Exception:
        logger.exception("Judge scoring failed — continuing without judge scores")
        return results

    score_by_model_id = {
        label_map[label]: score for label, score in scores.items() if label in label_map
    }

    for result in results:
        result["judge_score"] = score_by_model_id.get(result["model_id"])

    return results
