"""Configuration loader for environment variables."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # GCP
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "code-reviewer-local")
    GCP_REGION = os.getenv("GCP_REGION", "asia-south1")

    # Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    # BigQuery
    BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET", "code_reviewer")
    BIGQUERY_TABLE = os.getenv("BIGQUERY_TABLE", "historical_reviews")

    # Pub/Sub
    PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC", "review-jobs")
    PUBSUB_SUBSCRIPTION = os.getenv("PUBSUB_SUBSCRIPTION", "review-worker")

    # Firestore
    FIRESTORE_COLLECTION = os.getenv("FIRESTORE_COLLECTION", "sessions")

    # Vertex AI
    VERTEX_INDEX_ID = os.getenv("VERTEX_INDEX_ID", "")
    VERTEX_ENDPOINT_ID = os.getenv("VERTEX_ENDPOINT_ID", "")

    # Local dev flag
    LOCAL_MODE = os.getenv("LOCAL_MODE", "true").lower() == "true"


config = Config()
