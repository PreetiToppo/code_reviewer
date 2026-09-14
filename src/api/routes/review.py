"""GET /review/{session_id} — fetch a single review."""
from fastapi import APIRouter, Depends, HTTPException
from src.api.auth import verify_user
from src.data.firestore_client import FirestoreClient

router = APIRouter()
firestore = FirestoreClient()


@router.get("/review/{session_id}")
async def get_review(session_id: str, user_id: str = Depends(verify_user)):
    history = firestore.get_history(user_id)
    for s in history:
        if s.get("session_id") == session_id:
            return s
    raise HTTPException(status_code=404, detail="Session not found")
