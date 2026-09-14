"""POST /submit — submit code for review."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.api.auth import verify_user
from src.engine.ast_parser import ASTParser
from src.engine.gemini_reviewer import GeminiReviewer
from src.engine.rag_retriever import RAGRetriever
from src.engine.quality_scorer import QualityScorer
from src.data.firestore_client import FirestoreClient
from src.data.bigquery_client import BigQueryClient

router = APIRouter()

ast_parser = ASTParser()
reviewer = GeminiReviewer()
retriever = RAGRetriever()
scorer = QualityScorer()
firestore = FirestoreClient()
bigquery = BigQueryClient()


class SubmitRequest(BaseModel):
    code: str
    language: str = "python"


@router.post("/submit")
async def submit_code(req: SubmitRequest, user_id: str = Depends(verify_user)):
    ast_result = ast_parser.parse(req.code, req.language)
    rules = retriever.retrieve(req.code, top_k=3)
    review = reviewer.review(req.code, ast_result, rules)
    score = scorer.score(review)

    session = {
        "user_id": user_id,
        "language": req.language,
        "score": score,
        "review": review,
        "facts": ast_result.get("facts", []),
    }
    session_id = firestore.save_session(user_id, session)
    bigquery.log_review(user_id, score, len(review.get("issues", [])))

    return {
        "session_id": session_id,
        "quality_score": score,
        "review": review,
        "ast_facts": ast_result.get("facts", []),
        "matched_rules": rules,
    }
