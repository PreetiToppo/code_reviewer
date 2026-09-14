"""
Pub/Sub worker skeleton.

In production, this subscribes to the review-jobs topic and processes
jobs asynchronously. Locally, it's a no-op stub.
"""
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)


def process_message(message: dict) -> None:
    logger.info(f"Processing review job: {message.get('session_id')}")
    # In production: fetch code, run ast_parser + reviewer, store result.


def start_worker() -> None:
    if config.LOCAL_MODE:
        logger.info("Local mode — Pub/Sub worker not started.")
        return

    from google.cloud import pubsub_v1
    subscriber = pubsub_v1.SubscriberClient()
    sub_path = subscriber.subscription_path(
        config.GCP_PROJECT_ID, config.PUBSUB_SUBSCRIPTION
    )

    def _callback(msg):
        try:
            import json
            process_message(json.loads(msg.data.decode("utf-8")))
            msg.ack()
        except Exception as e:
            logger.error(f"Worker error: {e}")
            msg.nack()

    logger.info(f"Listening on {sub_path}")
    subscriber.subscribe(sub_path, callback=_callback)


if __name__ == "__main__":
    start_worker()
