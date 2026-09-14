"""
RAG retriever.

Loads historical review rules from CSV. In production this reads from
BigQuery + Vertex AI Vector Search. Locally, it reads the CSV directly
and does keyword matching.
"""
import csv
import os
from typing import List
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "historical_reviews.csv")


class RAGRetriever:
    def __init__(self):
        self.rules = self._load_csv()

    def _load_csv(self) -> List[dict]:
        if not os.path.exists(CSV_PATH):
            logger.warning(f"CSV not found at {CSV_PATH}")
            return []
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        """Very simple keyword overlap ranking. Replace with vector search later."""
        q = query.lower()
        scored = []
        for rule in self.rules:
            text = f"{rule.get('type','')} {rule.get('description','')}".lower()
            score = sum(1 for word in q.split() if word in text)
            scored.append((score, rule.get("description", "")))
        scored.sort(reverse=True)
        return [desc for score, desc in scored[:top_k] if score > 0] or [
            r.get("description", "") for r in self.rules[:top_k]
        ]
