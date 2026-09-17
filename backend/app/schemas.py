from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class BattleRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4000)
    model_ids: List[str] = Field(..., min_length=2, max_length=6)
    use_judge: bool = True


class ModelResult(BaseModel):
    model_id: str
    status: str
    text: Optional[str] = None
    error: Optional[str] = None
    tokens_in: int
    tokens_out: int
    latency_ms: float
    estimated_cost_usd: float
    judge_score: Optional[float] = None


class BattleResponse(BaseModel):
    battle_id: int
    prompt: str
    results: List[ModelResult]


class VoteRequest(BaseModel):
    battle_id: int
    outcome: str = Field(..., pattern="^(win|tie|both_bad)$")
    winner_model_id: Optional[str] = None
    loser_model_ids: List[str] = Field(default_factory=list)


class LeaderboardEntry(BaseModel):
    model_id: str
    elo_rating: float
    wins: int
    losses: int
    ties: int
    total_battles: int
    win_rate: float


class AvailableModel(BaseModel):
    model_id: str
    provider: str
    display_name: str


class BattleHistoryItem(BaseModel):
    id: int
    prompt: str
    model_ids: List[str]
    created_at: datetime
