"""Tests for the Gemini reviewer (mock mode)."""
import os
os.environ["LOCAL_MODE"] = "true"
os.environ["GEMINI_API_KEY"] = ""

from src.engine.gemini_reviewer import GeminiReviewer


def test_mock_review_returns_dict():
    reviewer = GeminiReviewer()
    result = reviewer.review(
        code="def f(): pass",
        ast_result={"facts": ["Missing docstring."]},
        rules=["Avoid single-character names"],
    )
    assert "summary" in result
    assert "issues" in result
    assert "quality_score" in result


def test_mock_review_score_is_bounded():
    reviewer = GeminiReviewer()
    result = reviewer.review(code="x", ast_result={"facts": []}, rules=[])
    assert 1 <= result["quality_score"] <= 10
