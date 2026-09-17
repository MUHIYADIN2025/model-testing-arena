"""Applies a user's vote to the persisted Elo leaderboard."""
from sqlalchemy.orm import Session

from app.database import ModelRating, DEFAULT_ELO
from app.elo import update_ratings, update_ratings_tie


def get_or_create_rating(db: Session, model_id: str) -> ModelRating:
    rating = db.query(ModelRating).filter(ModelRating.model_id == model_id).first()
    if not rating:
        rating = ModelRating(model_id=model_id, elo_rating=DEFAULT_ELO)
        db.add(rating)
        db.flush()
    return rating


def apply_vote(db: Session, winner_model_id: str, loser_model_ids: list, outcome: str) -> None:
    """
    Updates Elo ratings for one vote. A vote against multiple losers (a
    3+ model battle) applies a separate pairwise update against each loser
    — the standard way to extend Elo, designed for 1v1, to multi-way battles.
    """
    if outcome == "win":
        winner_rating = get_or_create_rating(db, winner_model_id)
        for loser_id in loser_model_ids:
            loser_rating = get_or_create_rating(db, loser_id)
            new_winner_elo, new_loser_elo = update_ratings(
                winner_rating.elo_rating, loser_rating.elo_rating
            )
            winner_rating.elo_rating = new_winner_elo
            loser_rating.elo_rating = new_loser_elo
            winner_rating.wins += 1
            loser_rating.losses += 1

    elif outcome == "tie":
        all_ids = ([winner_model_id] if winner_model_id else []) + loser_model_ids
        if len(all_ids) >= 2:
            rating_a = get_or_create_rating(db, all_ids[0])
            rating_b = get_or_create_rating(db, all_ids[1])
            new_a, new_b = update_ratings_tie(rating_a.elo_rating, rating_b.elo_rating)
            rating_a.elo_rating = new_a
            rating_b.elo_rating = new_b
            rating_a.ties += 1
            rating_b.ties += 1

    elif outcome == "both_bad":
        # No Elo change — a "both bad" vote signals prompt/response quality
        # issues, not a comparative preference, so ratings stay untouched.
        for model_id in loser_model_ids:
            get_or_create_rating(db, model_id)

    db.commit()
