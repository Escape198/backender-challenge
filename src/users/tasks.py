from celery import shared_task
from core.event_log_client import EventLogClient
import structlog

logger = structlog.get_logger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def log_user_creation(self, user_id, event_data):
    """Task to log user creation events in ClickHouse."""
    try:
        logger.info("Attempting to log user creation event", user_id=user_id)
        with EventLogClient.init() as client:
            client.insert([event_data])
        logger.info("User creation event logged successfully", user_id=user_id)
    except Exception as e:
        logger.error("Failed to log user creation event", user_id=user_id, error=str(e))
        raise self.retry(exc=e)