"""
SQLite storage for the arena: every battle run, every user vote, and the
running Elo rating per model — the same rating system chess (and LMSYS's
Chatbot Arena) uses to rank competitors from pairwise comparisons alone.
"""
import json
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

DEFAULT_ELO = 1200.0


class BattleRecord(Base):
    __tablename__ = "battles"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(Text, nullable=False)
    model_ids = Column(Text, nullable=False)    # JSON list, e.g. ["ollama:llama3.1", "openai:gpt-4o-mini"]
    results_json = Column(Text, nullable=False)  # JSON list of per-model results (text, latency, cost, tokens, judge_score)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "prompt": self.prompt,
            "model_ids": json.loads(self.model_ids),
            "results": json.loads(self.results_json),
            "created_at": self.created_at.isoformat(),
        }


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    battle_id = Column(Integer, nullable=False, index=True)
    winner_model_id = Column(String(100), nullable=True)  # null = tie/both-bad
    loser_model_ids = Column(Text, nullable=False)         # JSON list
    outcome = Column(String(20), default="win")            # win | tie | both_bad
    created_at = Column(DateTime, default=datetime.utcnow)


class ModelRating(Base):
    __tablename__ = "model_ratings"

    model_id = Column(String(100), primary_key=True)
    elo_rating = Column(Float, default=DEFAULT_ELO)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    ties = Column(Integer, default=0)

    def to_dict(self):
        total = self.wins + self.losses + self.ties
        win_rate = round(self.wins / total, 3) if total else 0.0
        return {
            "model_id": self.model_id,
            "elo_rating": round(self.elo_rating, 1),
            "wins": self.wins,
            "losses": self.losses,
            "ties": self.ties,
            "total_battles": total,
            "win_rate": win_rate,
        }


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
