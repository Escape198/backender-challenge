from celery import shared_task
from core.log_service import log_user_creation_event
import structlog

logger = structlog.get_logger(__name__)


@shared_task(max_retries=3, default_retry_delay=10)
def log_user_creation(user_id, event_data):
    """Task to log user creation events in ClickHouse."""
    try:
        logger.info("Initiating log_user_creation_event service", user_id=user_id)
        log_user_creation_event(user_id, event_data)
        logger.info("User creation event processed successfully", user_id=user_id)
    except Exception as e:
        logger.error("Failed to process log_user_creation_event", user_id=user_id, error=str(e))
        raise log_user_creation.retry(exc=e)