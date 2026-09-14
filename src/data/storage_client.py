"""Cloud Storage for temporary code artifacts. No-op locally."""
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class StorageClient:
    def __init__(self):
        self.enabled = not config.LOCAL_MODE
        if self.enabled:
            try:
                from google.cloud import storage
                self.client = storage.Client(project=config.GCP_PROJECT_ID)
            except Exception as e:
                logger.warning(f"Storage init failed: {e}")
                self.enabled = False

    def upload_temp(self, name: str, content: str) -> str:
        if not self.enabled:
            return f"local://{name}"
        bucket = self.client.bucket(f"{config.GCP_PROJECT_ID}-code-artifacts")
        blob = bucket.blob(name)
        blob.upload_from_string(content)
        return f"gs://{bucket.name}/{name}"
