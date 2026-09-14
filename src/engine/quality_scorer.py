"""Normalises raw review output into a 1–10 quality score."""
from typing import Dict

SEVERITY_WEIGHT = {
    "critical": 3.0,
    "high": 2.0,
    "medium": 1.0,
    "low": 0.5,
    "info": 0.0,
}


class QualityScorer:
    """Turns a raw Gemini review into a clean 1–10 score.

    If the review already contains a `quality_score`, it trusts it (clamped).
    Otherwise, it derives the score from the severity of detected issues.
    """

    def score(self, review: Dict) -> int:
        if not review:
            return 1

        if "quality_score" in review:
            try:
                return max(1, min(10, int(review["quality_score"])))
            except (TypeError, ValueError):
                pass

        penalty = 0.0
        for issue in review.get("issues", []):
            severity = str(issue.get("severity", "low")).lower()
            penalty += SEVERITY_WEIGHT.get(severity, 0.5)

        return max(1, min(10, round(10 - penalty)))
