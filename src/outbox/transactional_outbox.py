from django.db import transaction
import structlog

logger = structlog.get_logger(__name__)


class transactional_outbox:
    """Context manager for transactional outbox logic."""
    def __init__(self, event_data=None, transaction_id=None):
        self.event_data = event_data or []
        self.transaction_id = transaction_id

    def __enter__(self):
        logger.debug("Starting transactional outbox", transaction_id=self.transaction_id)
        self.atomic_transaction = transaction.atomic()
        self.atomic_transaction.__enter__()
        return self

    def add_event(self, event_type: str, event_context: dict):
        """Adds an event to the outbox."""
        self.event_data.append({
            "event_type": event_type,
            "event_context": event_context,
            "transaction_id": self.transaction_id,
        })
        logger.info("Event added to outbox", event_type=event_type, transaction_id=self.transaction_id)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logger.error(
                "Error in transactional outbox",
                transaction_id=self.transaction_id,
                error=str(exc_val),
                exc_type=exc_type.__name__,
            )
        else:
            logger.debug("Committing transactional outbox", transaction_id=self.transaction_id)
        self.atomic_transaction.__exit__(exc_type, exc_val, exc_tb)
