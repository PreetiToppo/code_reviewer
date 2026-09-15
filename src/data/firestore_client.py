"""Firestore session history. Falls back to a local JSON file in local mode."""
import json
import os
from datetime import datetime
from typing import Dict, List

from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)

LOCAL_DB_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "local_sessions.json"
)


class FirestoreClient:
    def __init__(self):
        self.enabled = not config.LOCAL_MODE
        if self.enabled:
            try:
                from google.cloud import firestore
                self.db = firestore.Client(project=config.GCP_PROJECT_ID)
            except Exception as e:
                logger.warning(f"Firestore init failed, using local file: {e}")
                self.enabled = False
        if not self.enabled:
            self._ensure_local_file()

    # ---- Local file helpers ----
    def _ensure_local_file(self) -> None:
        os.makedirs(os.path.dirname(LOCAL_DB_PATH), exist_ok=True)
        if not os.path.exists(LOCAL_DB_PATH):
            with open(LOCAL_DB_PATH, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _read_local(self) -> Dict[str, List[dict]]:
        try:
            with open(LOCAL_DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _write_local(self, data: Dict[str, List[dict]]) -> None:
        with open(LOCAL_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    # ---- Public API ----
    def save_session(self, user_id: str, session: dict) -> str:
        session["timestamp"] = datetime.utcnow().isoformat()

        if self.enabled:
            doc = self.db.collection(config.FIRESTORE_COLLECTION).add(session)
            return doc[1].id

        data = self._read_local()
        data.setdefault(user_id, []).append(session)
        self._write_local(data)
        return f"local-{len(data[user_id])}"

    def get_history(self, user_id: str) -> List[dict]:
        if self.enabled:
            docs = (
                self.db.collection(config.FIRESTORE_COLLECTION)
                .where("user_id", "==", user_id)
                .stream()
            )
            return [d.to_dict() for d in docs]

        data = self._read_local()
        return data.get(user_id, [])
