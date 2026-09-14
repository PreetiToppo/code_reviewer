"""
Gemini-powered code reviewer.

Combines symbolic AST facts + RAG-retrieved historical rules to ground
the LLM and reduce hallucination.
"""
from typing import Dict, List
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)

REVIEW_PROMPT = """You are an expert code reviewer.

You have been given:
1. Source code
2. Structural facts extracted by a symbolic AST parser
3. Historical review rules relevant to this code

Your job:
- Identify bugs, security issues, and architecture problems
- Suggest concrete fixes
- Assign a quality score from 1 to 10 (10 = production-ready)
- Ground every claim in the facts or rules provided — do not invent issues

Return your answer as JSON with keys:
{ "summary": str, "issues": [{"severity": str, "type": str, "line_hint": str, "fix": str}], "quality_score": int }

--- SOURCE CODE ---
{code}

--- AST FACTS ---
{facts}

--- HISTORICAL RULES ---
{rules}
"""


class GeminiReviewer:
    def __init__(self):
        self.enabled = bool(config.GEMINI_API_KEY)
        if self.enabled:
            import google.generativeai as genai
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel("gemini-2.5-flash")
        else:
            logger.warning("GEMINI_API_KEY not set — running in mock mode.")

    def review(self, code: str, ast_result: Dict, rules: List[str]) -> Dict:
        if not self.enabled:
            return self._mock_review(code, ast_result, rules)

        prompt = REVIEW_PROMPT.format(
            code=code,
            facts="\n".join(f"- {f}" for f in ast_result.get("facts", [])) or "None",
            rules="\n".join(f"- {r}" for r in rules) or "None",
        )

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            import json, re
            # Strip code fences if present
            text = re.sub(r"^```json|```$", "", text, flags=re.MULTILINE).strip()
            return json.loads(text)
        except Exception as e:
            logger.error(f"Gemini call failed: {e}")
            return self._mock_review(code, ast_result, rules)

    def _mock_review(self, code: str, ast_result: Dict, rules: List[str]) -> Dict:
        issues = []
        for fact in ast_result.get("facts", []):
            issues.append({
                "severity": "medium",
                "type": "ast_fact",
                "line_hint": "—",
                "fix": fact,
            })
        for rule in rules:
            issues.append({
                "severity": "info",
                "type": "historical_rule",
                "line_hint": "—",
                "fix": rule,
            })
        score = max(1, 10 - len(issues))
        return {
            "summary": f"Mock review: {len(issues)} issue(s) detected.",
            "issues": issues,
            "quality_score": score,
        }
