"""
AI Model Testing Arena — FastAPI entry point.

Run:
    uvicorn app.main:app --reload --port 8000

Endpoints:
    GET  /api/models        -> models available for battle (from .env config)
    POST /api/battle        -> run a prompt across N models concurrently
    POST /api/vote          -> record a human preference, updates Elo leaderboard
    GET  /api/leaderboard   -> Elo ratings, sorted best-first
    GET  /api/battles       -> past battle history
    GET  /api/battles/{id}  -> full detail for one past battle
"""
import json
import logging

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import arena_engine, evaluator, rating_service
from app.config import get_settings
from app.database import init_db, get_db, BattleRecord, ModelRating
from app.schemas import (
    BattleRequest, BattleResponse, VoteRequest,
    LeaderboardEntry, AvailableModel, BattleHistoryItem,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="AI Model Testing Arena API",
    description="Blind side-by-side LLM comparison with cost/latency metrics and an Elo leaderboard.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    logger.info("Database initialized. Environment: %s", settings.app_env)


@app.get("/")
def root():
    return {"status": "ok", "service": "AI Model Testing Arena API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/api/models", response_model=list[AvailableModel])
def list_models():
    models = []
    for name in settings.ollama_model_list:
        models.append({"model_id": f"ollama:{name}", "provider": "ollama", "display_name": name})
    for name in settings.openai_model_list:
        models.append({"model_id": f"openai:{name}", "provider": "openai", "display_name": name})
    return models


@app.post("/api/battle", response_model=BattleResponse)
async def run_battle(payload: BattleRequest, db: Session = Depends(get_db)):
    try:
        results = await arena_engine.run_battle(payload.model_ids, payload.prompt)
        results = evaluator.enrich_with_cost(results)

        if payload.use_judge:
            results = await evaluator.judge_battle(payload.prompt, results)
    except Exception as exc:
        logger.exception("Battle failed")
        raise HTTPException(status_code=500, detail=f"Battle failed: {exc}") from exc

    record = BattleRecord(
        prompt=payload.prompt,
        model_ids=json.dumps(payload.model_ids),
        results_json=json.dumps(results),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {"battle_id": record.id, "prompt": payload.prompt, "results": results}


@app.post("/api/vote")
def submit_vote(payload: VoteRequest, db: Session = Depends(get_db)):
    battle = db.query(BattleRecord).filter(BattleRecord.id == payload.battle_id).first()
    if not battle:
        raise HTTPException(status_code=404, detail="Battle not found.")

    try:
        rating_service.apply_vote(
            db, payload.winner_model_id, payload.loser_model_ids, payload.outcome
        )
    except Exception as exc:
        logger.exception("Vote application failed")
        raise HTTPException(status_code=500, detail="Failed to record vote.") from exc

    return {"status": "recorded"}


@app.get("/api/leaderboard", response_model=list[LeaderboardEntry])
def get_leaderboard(db: Session = Depends(get_db)):
    ratings = db.query(ModelRating).order_by(ModelRating.elo_rating.desc()).all()
    return [r.to_dict() for r in ratings]


@app.get("/api/battles", response_model=list[BattleHistoryItem])
def list_battles(limit: int = 50, db: Session = Depends(get_db)):
    records = (
        db.query(BattleRecord)
        .order_by(BattleRecord.created_at.desc())
        .limit(min(limit, 200))
        .all()
    )
    return [
        {
            "id": r.id,
            "prompt": r.prompt,
            "model_ids": json.loads(r.model_ids),
            "created_at": r.created_at,
        }
        for r in records
    ]


@app.get("/api/battles/{battle_id}")
def get_battle(battle_id: int, db: Session = Depends(get_db)):
    record = db.query(BattleRecord).filter(BattleRecord.id == battle_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Battle not found.")
    return record.to_dict()
