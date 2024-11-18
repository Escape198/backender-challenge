import structlog
from celery import shared_task
from django.db import transaction

from core.event_log_client import EventLogClient
from core.log_service import log_user_creation_event
from outbox.models import OutboxEvent

logger = structlog.get_logger(__name__)


@shared_task(max_retries=3, default_retry_delay=10)
def log_user_creation(user_id, event_data):
    """Task to log user creation events in ClickHouse with transactional outbox."""
    try:
        with transaction.atomic():
            event, created = OutboxEvent.objects.get_or_create(
                user_id=user_id,
                defaults={"event_data": event_data, "status": "pending"},
            )

            if not created and event.status == "processed":
                logger.warning(
                    "Event already processed, skipping duplicate",
                    user_id=user_id, event_id=event.id,
                )
                return

            logger.info("Outbox event created or retrieved", event_id=event.id)

            # Логируем событие в ClickHouse
            with EventLogClient.init() as client:
                log_user_creation_event(user_id, event_data)

            event.status = "processed"
            event.save(update_fields=["status"])

            logger.info("User creation event logged successfully", user_id=user_id, event_id=event.id)

    except Exception as e:
        logger.error("Failed to log user creation event", user_id=user_id, error=str(e))
        raise log_user_creation.retry(exc=e)
