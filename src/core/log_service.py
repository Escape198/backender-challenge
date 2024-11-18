import structlog

from core.event_log_client import EventLogClient

logger = structlog.get_logger(__name__)


def log_user_creation_event(user_id: int, event_data: dict) -> None:
    """Logs user creation event in ClickHouse."""
    try:
        logger.info("Attempting to log event in ClickHouse", user_id=user_id)
        with EventLogClient.init() as client:
            client.insert([event_data])
        logger.info("Event logged successfully", user_id=user_id)
    except Exception as e:
        logger.error("Error logging event in ClickHouse", user_id=user_id, error=str(e))
        raise
