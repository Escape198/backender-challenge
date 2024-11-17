from django.db import transaction
from structlog import get_logger


logger = get_logger(__name__)


class transactional_outbox:
    """Context manager for transactional outbox logic."""
    def __init__(self, event_data=None, transaction_id=None):
        self.event_data = event_data or []
        self.transaction_id = transaction_id

    def __enter__(self):
        logger.debug("Starting transactional outbox", transaction_id=self.transaction_id)
        # Ensure the transaction is in atomic mode for safe commit/rollback handling
        self.atomic_transaction = transaction.atomic()
        self.atomic_transaction.__enter__()  # Start the atomic block
        return self.event_data

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logger.error(
                "Error in transactional outbox",
                transaction_id=self.transaction_id,
                error=str(exc_val),
                exc_type=exc_type.__name__,
            )
            self.atomic_transaction.__exit__(exc_type, exc_val, exc_tb)

            transaction.rollback()
        else:
            logger.debug(
                "Committing transactional outbox",
                transaction_id=self.transaction_id
            )
            self.atomic_transaction.__exit__(None, None, None)
        transaction.set_autocommit(True)
