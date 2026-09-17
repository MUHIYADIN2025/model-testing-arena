"""
Elo rating updates from pairwise comparisons — the same algorithm chess
federations use, and the one LMSYS's Chatbot Arena popularized for ranking
LLMs purely from human "which response is better?" votes, with no need
for a labeled benchmark dataset.

Kept as its own module (no DB or FastAPI imports) so the math is trivially
unit-testable in isolation.
"""
from typing import Tuple

K_FACTOR = 32  # standard chess K-factor; higher = ratings move faster per battle


def expected_score(rating_a: float, rating_b: float) -> float:
    """Probability model A is judged better than model B, given current ratings."""
    return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400))


def update_ratings(rating_winner: float, rating_loser: float) -> Tuple[float, float]:
    """Standard win/loss update. Returns (new_winner_rating, new_loser_rating)."""
    expected_winner = expected_score(rating_winner, rating_loser)
    expected_loser = 1.0 - expected_winner

    new_winner = rating_winner + K_FACTOR * (1 - expected_winner)
    new_loser = rating_loser + K_FACTOR * (0 - expected_loser)
    return new_winner, new_loser


def update_ratings_tie(rating_a: float, rating_b: float) -> Tuple[float, float]:
    """Tie update — both models get a 0.5 'score' rather than 1/0."""
    expected_a = expected_score(rating_a, rating_b)
    expected_b = 1.0 - expected_a

    new_a = rating_a + K_FACTOR * (0.5 - expected_a)
    new_b = rating_b + K_FACTOR * (0.5 - expected_b)
    return new_a, new_b
