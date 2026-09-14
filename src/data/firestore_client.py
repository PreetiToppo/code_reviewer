"""Firestore session history. Falls back to in-memory dict locally."""
from datetime import datetime
from typing import Dict, List
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FirestoreClient:
    def __init__(self):
        self._memory: Dict[str, List[dict]] = {}
        self.enabled = not config.LOCAL_MODE
        if self.enabled:
            try:
                from google.cloud import firestore
                self.db = firestore.Client(project=config.GCP_PROJECT_ID)
            except Exception as e:
                logger.warning(f"Firestore init failed, using memory: {e}")
                self.enabled = False

    def save_session(self, user_id: str, session: dict) -> str:
        session["timestamp"] = datetime.utcnow().isoformat()
        if self.enabled:
            doc = self.db.collection(config.FIRESTORE_COLLECTION).add(session)
            return doc[1].id
        self._memory.setdefault(user_id, []).append(session)
        return f"local-{len(self._memory[user_id])}"

    def get_history(self, user_id: str) -> List[dict]:
        if self.enabled:
            docs = (
                self.db.collection(config.FIRESTORE_COLLECTION)
                .where("user_id", "==", user_id)
                .stream()
            )
            return [d.to_dict() for d in docs]
        return self._memory.get(user_id, [])
