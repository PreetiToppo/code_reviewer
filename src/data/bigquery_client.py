"""BigQuery client for historical rules. Falls back to no-op locally."""
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BigQueryClient:
    def __init__(self):
        self.enabled = not config.LOCAL_MODE
        if self.enabled:
            try:
                from google.cloud import bigquery
                self.client = bigquery.Client(project=config.GCP_PROJECT_ID)
            except Exception as e:
                logger.warning(f"BigQuery init failed: {e}")
                self.enabled = False

    def log_review(self, user_id: str, score: int, issue_count: int) -> None:
        if not self.enabled:
            logger.info(f"[LOCAL] review logged: user={user_id} score={score} issues={issue_count}")
            return
        table = f"{config.GCP_PROJECT_ID}.{config.BIGQUERY_DATASET}.reviews"
        rows = [{"user_id": user_id, "score": score, "issues": issue_count}]
        errors = self.client.insert_rows_json(table, rows)
        if errors:
            logger.error(f"BigQuery insert errors: {errors}")
