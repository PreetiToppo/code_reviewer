"""GET /history — fetch user's review history."""
from fastapi import APIRouter, Depends
from src.api.auth import verify_user
from src.data.firestore_client import FirestoreClient

router = APIRouter()
firestore = FirestoreClient()


@router.get("/history")
async def get_history(user_id: str = Depends(verify_user)):
    return {"user_id": user_id, "sessions": firestore.get_history(user_id)}
