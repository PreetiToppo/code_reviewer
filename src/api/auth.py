"""Firebase Auth middleware. Skips verification locally."""
from fastapi import Header, HTTPException
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def verify_user(authorization: str = Header(default="")) -> str:
    if config.LOCAL_MODE:
        return "local-user"

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = authorization.split(" ", 1)[1]
    try:
        from firebase_admin import auth, credentials
        import firebase_admin
        if not firebase_admin._apps:
            firebase_admin.initialize_app(credentials.ApplicationDefault())
        decoded = auth.verify_id_token(token)
        return decoded["uid"]
    except Exception as e:
        logger.error(f"Auth failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
