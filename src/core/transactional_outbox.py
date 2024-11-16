from contextlib import contextmanager
from django.db import transaction
from structlog import get_logger

from core.event_log_client import EventLogClient
from core.base_model import Model

logger = get_logger(__name__)


@contextmanager
def transactional_outbox(event_data: list[Model]):
    """
    A context manager for publishing events in transactional outbox style.

    This manager ensures that events are only published if the transaction was successful.
    """
    try:
        with transaction.atomic():
            yield
            logger.info("Publishing events via transactional outbox", event_count=len(event_data))
            with EventLogClient.init() as client:
                client.insert(event_data)
            logger.info("Events successfully published")
    except Exception as e:
        logger.error("Error in transactional outbox", error=str(e))
        raise
