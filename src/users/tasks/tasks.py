from celery import shared_task
from core.log_service import log_user_creation_event
from django.db import transaction
import structlog

logger = structlog.get_logger(__name__)


@shared_task(max_retries=3, default_retry_delay=10)
def log_user_creation(user_id, event_data):
    """
    Task to log user creation events in ClickHouse.

    Args:
        user_id: ID of the user being logged.
        event_data: Dictionary containing event information.
    """
    try:
        logger.info("Attempting to log user creation event", user_id=user_id)
        with transaction.atomic():
            log_user_creation_event(user_id=user_id, event_data=event_data)
        logger.info("User creation event logged successfully", user_id=user_id)

    except Exception as e:
        logger.error("Failed to log user creation event", user_id=user_id, error=str(e))
        raise log_user_creation.retry(exc=e)