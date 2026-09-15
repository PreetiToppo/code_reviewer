"""Unit tests for the quality scorer."""
from src.engine.quality_scorer import QualityScorer


scorer = QualityScorer()


def test_trusts_provided_score():
    review = {"quality_score": 8, "issues": []}
    assert scorer.score(review) == 8


def test_clamps_high_score():
    review = {"quality_score": 15}
    assert scorer.score(review) == 10


def test_clamps_low_score():
    review = {"quality_score": -3}
    assert scorer.score(review) == 1


def test_derives_score_from_critical_issues():
    review = {
        "issues": [
            {"severity": "critical"},
            {"severity": "critical"},
        ]
    }
    # 10 - (3 + 3) = 4
    assert scorer.score(review) == 4


def test_clean_review_scores_ten():
    review = {"issues": []}
    assert scorer.score(review) == 10


def test_handles_empty_review():
    # An empty review has no data — the scorer defaults to 1.
    assert scorer.score({}) == 1
