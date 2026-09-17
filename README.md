# ⚔️ AI Model Testing Arena
Built AI mode evaluation platform that benchmarked multiple models across accurancy, structured-output reliability,
latency, cost, and adversarial test cases.



A blind, head-to-head comparison platform for LLMs: send one prompt to multiple models
simultaneously, compare their cost/latency/quality side by side, vote on which response is
better, and watch an Elo leaderboard emerge purely from those votes — the same methodology
LMSYS's Chatbot Arena uses to rank the world's LLMs.

---

## 🎯 The Problem I'm Solving

1. **"Which model should I actually use?" has no easy answer.** Benchmark leaderboards
   (MMLU, HumanEval, etc.) measure narrow academic tasks — they don't tell you which model
   is *actually* better for *your* prompts, in *your* domain, at *your* budget.
2. **Cost and quality are usually evaluated separately, if at all.** A team might know
   GPT-4o-mini costs less than GPT-4o, but rarely has a side-by-side view of "is the quality
   drop actually noticeable for our use case" — so they either overpay for a model they don't
   need or underpay for one that hurts output quality.
3. **Single-response evaluation is misleading.** Reading one model's answer in isolation
   makes everything look reasonable; the flaws in a response only become obvious when you
   see a *better* answer to the *same* prompt right next to it — which is exactly why blind
   pairwise comparison (not absolute scoring) is the standard for human LLM evaluation.

This project makes that comparison a repeatable, structured process instead of a one-off
gut check: same prompt, same moment, side-by-side, with objective metrics attached and a
running leaderboard that improves in accuracy with every vote.

---

## 🏗️ Architecture

```
React: pick 2-6 models + enter a prompt
    → POST /api/battle → asyncio.gather() calls every model CONCURRENTLY
        (Ollama models via HTTP, OpenAI models via async SDK)
    → each result timed (latency), token-counted, cost-estimated
    → optional LLM-as-judge pass: blind-labels responses A/B/C, asks a judge
      model to score each 1-10 (same technique as MT-Bench-style auto-eval)
    → battle persisted to SQLite, returned to frontend
React: renders responses blind (label only) → user votes for the better one
    → POST /api/vote → Elo rating update (elo.py) → GET /api/leaderboard
```

**Why async/`asyncio.gather` instead of calling models one at a time?** A 4-model battle
calling models sequentially takes the SUM of all four response times (potentially 30+
seconds). Calling them concurrently takes only as long as the SLOWEST model — the entire
point of using async here, not just a style preference.

**Why Elo instead of averaging judge scores?** LLM judge scores are noisy and can be biased
toward verbosity or a particular style. Elo built from *pairwise human preference* — "which
of these two was better" — is a weaker signal per vote but a much more robust one in
aggregate, and it's exactly why LMSYS built Chatbot Arena on the same mechanism rather than
a numeric scoring rubric.

## 📁 Project Structure

```
model-testing-arena/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI endpoints
│   │   ├── arena_engine.py    # Async parallel model caller (Ollama + OpenAI)
│   │   ├── evaluator.py       # Cost calculation + LLM-as-judge scoring
│   │   ├── elo.py             # Elo rating math (pure, unit-testable)
│   │   ├── rating_service.py  # Applies votes to the persisted leaderboard
│   │   └── database.py        # SQLite: battles, votes, model ratings
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/        # ModelSelector, ArenaBattleView, MetricComparison, PromptInput
    │   ├── pages/              # ArenaPage, LeaderboardPage, HistoryPage
    │   └── App.jsx
    └── package.json
```

---

## ✅ Features Built

- **Concurrent multi-model battles** — 2-6 models called in parallel via `asyncio.gather`,
  mixing free local Ollama models and paid OpenAI models in the same battle.
- **Blind comparison UI** — responses are labeled A/B/C (not model names) until the user
  votes or chooses to reveal, removing brand-name bias from the judgment.
- **Objective metrics per response** — latency (ms), token counts (native from Ollama/OpenAI,
  not estimated), and cost ($0 for local models, computed from a pricing table for paid ones).
- **LLM-as-judge auto-scoring** — an optional second LLM call rates every response 1-10 on a
  rubric, giving a quality signal even before any human votes.
- **Elo leaderboard built from real votes** — every vote updates two models' ratings using
  the standard chess Elo formula; verified with unit tests (equal ratings → symmetric ±16
  swing, underdog upset → large swing, tie → no change).
- **Full battle history** — every prompt + result set persisted and browsable later.
- **Graceful per-model failure handling** — if one model errors (unreachable Ollama, missing
  API key), the other models' results still render; the failed one shows the error inline
  instead of failing the whole battle.

---

## 🧠 Technical Skills This Project Demonstrates

| Area | Specific Skill |
|---|---|
| **Async Programming** | `asyncio.gather` for true concurrent I/O, per-task error isolation so one failure doesn't cancel the others, mixing async HTTP (`httpx`) and async SDK clients (OpenAI) |
| **API Integration** | Multi-provider abstraction (local Ollama HTTP API vs. cloud OpenAI SDK) behind one uniform interface |
| **Algorithm Implementation** | Elo rating system implemented from first principles and unit-tested in isolation, independent of the database/API layer |
| **ML Evaluation Methodology** | LLM-as-judge scoring, blind pairwise comparison design (bias mitigation via randomized/label-based presentation) |
| **Backend Engineering** | FastAPI REST design, SQLAlchemy persistence for battles/votes/ratings, Pydantic validation |
| **Frontend Engineering** | React state for async multi-step flows (select → battle → vote → reveal), Recharts metric visualization, controlled reveal/blind UI pattern |
| **Cost Engineering** | Token-based cost estimation from a configurable pricing table, distinguishing free (self-hosted) vs. metered (API) compute |

---

## 📄 How to Turn This Into a Strong Resume Bullet

**Weak:**
> Built a tool to compare different AI models using React and FastAPI.

**Strong (pick the framing that matches what you emphasize):**

> Built an LLM evaluation platform (React, FastAPI, asyncio) that runs blind, concurrent
> comparisons across multiple models and ranks them via an Elo rating system built from
> pairwise human votes — the same methodology behind LMSYS's Chatbot Arena.

> Implemented an async multi-provider model-calling engine that queries N LLMs concurrently
> (reducing a 4-model battle's latency from the sum of all calls to the slowest single call),
> with per-model error isolation so one failing provider never blocks the others.

> Designed and unit-tested an Elo rating system from first principles to rank AI models by
> quality using only pairwise preference votes — no labeled benchmark dataset required —
> and layered in an LLM-as-judge auto-scoring pass for immediate quality signal before votes
> accumulate.

**Formula:** `[Action verb] + [what you built] + [key technologies] + [the underlying
technique, named specifically] + [what it enables that a naive version couldn't]`. For this
kind of project, naming the *methodology* (Elo from pairwise votes, LLM-as-judge, async
concurrency) is what separates it from "I called some APIs" — it signals you understood a
real evaluation/systems problem, which is exactly what interviewers probe on for ML/AI
infrastructure roles.

---

## 🚀 Quick Start (Local Dev)

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

cp .env.example .env
# Default setup uses Ollama (free, local). Install it and pull a few models:
#   ollama pull llama3.1
#   ollama pull mistral
#   ollama pull phi3

uvicorn app.main:app --reload --port 8000
```

> To include OpenAI models in the arena, set `OPENAI_API_KEY` and `OPENAI_MODELS` in `.env`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`, select 2+ models, enter a prompt, and click **Start Battle**.

### 3. Docker (full stack)

```bash
cp backend/.env.example backend/.env
docker compose up --build
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/models` | Models available for battle (from `.env` config) |
| `POST` | `/api/battle` | Run a prompt across N models concurrently, with optional judge scoring |
| `POST` | `/api/vote` | Record a human preference; updates the Elo leaderboard |
| `GET` | `/api/leaderboard` | Elo ratings, sorted best-first |
| `GET` | `/api/battles` | Past battle history |
| `GET` | `/api/battles/{id}` | Full detail for one past battle |

## 🔐 Production Hardening Notes

- Add auth + rate limiting before exposing publicly — every battle call costs real
  inference time (and money, for paid models).
- Cache identical prompt+model-set battles briefly to avoid re-billing for repeated queries.
- Persist judge rationale (not just the score) if you want to audit why the judge scored a
  response a certain way — currently only the numeric score is kept.
- For statistically meaningful Elo ratings, consider Bradley-Terry model fitting on
  accumulated votes rather than pure sequential Elo updates, especially at scale.

## 🧭 Roadmap

- Multi-turn battles (conversation, not just single-prompt)
- Category-specific leaderboards (coding, creative writing, reasoning) rather than one
  global ranking
- Confidence intervals on Elo ratings (models with few battles shouldn't rank as confidently
  as models with hundreds)
- Export battle results as a shareable report

## Author
Muhiadin Said Hassan Software AI Engineer | Machine Learning Engineer | LLM Engineer

GitHub: @MUHIYADIN2025 Email: [muhidiin090448@gmail.com]

⭐ Support If you find this project useful, consider giving the repository a star ⭐ on GitHub.

Contributions, suggestions, and improvements are welcome.


