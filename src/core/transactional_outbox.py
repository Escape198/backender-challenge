from contextlib import contextmanager
from django.db import transaction
from structlog import get_logger

from core.event_log_client import EventLogClient
from core.base_model import Model

logger = get_logger(__name__)


class transactional_outbox:
    """Context manager for transactional outbox logic."""
    def __init__(self, event_data=None):
        self.event_data = event_data or []

    def __enter__(self):
        logger.debug("Starting transactional outbox")
        transaction.set_autocommit(False)  # Explicitly disable autocommit
        return self.event_data

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logger.error(
                "Error in transactional outbox",
                error=str(exc_val),
                exc_type=exc_type.__name__,
            )
            transaction.rollback()  # Rollback on error
        else:
            logger.debug("Committing transactional outbox")
            transaction.commit()  # Commit on success
        transaction.set_autocommit(True)  # Restore autocommit
