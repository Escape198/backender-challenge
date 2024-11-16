import re
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, List, Tuple, Sequence

import clickhouse_connect
import structlog
from clickhouse_connect.driver.exceptions import DatabaseError
from django.conf import settings
from django.utils import timezone

from core.base_model import Model

logger = structlog.get_logger(__name__)

EVENT_LOG_COLUMNS = [
    "event_type",
    "event_date_time",
    "environment",
    "event_context",
]


class EventLogClient:
    def __init__(
        self,
        client: clickhouse_connect.driver.Client,
        schema: str,
        table: str,
        environment: str,
    ) -> None:
        self._client = client
        self._schema = schema
        self._table = table
        self._environment = environment

    @classmethod
    @contextmanager
    def init(cls) -> Generator["EventLogClient", None, None]:
        """Client initialization for ClickHouse."""
        client = clickhouse_connect.get_client(
            host=settings.CLICKHOUSE_HOST, port=settings.CLICKHOUSE_PORT, user=settings.CLICKHOUSE_USER,
            password=settings.CLICKHOUSE_PASSWORD, query_retries=2, connect_timeout=30, send_receive_timeout=10, )
        try:
            yield cls(
                client=client, schema=settings.CLICKHOUSE_SCHEMA, table=settings.CLICKHOUSE_EVENT_LOG_TABLE_NAME,
                environment=settings.ENVIRONMENT, )
        except Exception as e:
            logger.error("Error while initializing ClickHouse client", error=str(e))
            raise
        finally:
            client.close()

    def insert(self, data: List[Model], batch_size: int = 100) -> None:
        """
        Inserts events into ClickHouse with batching support.

        :param data: List of events to insert.
        :param batch_size: Batch size for batch insertion (default is 100).
        """
        try:
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                self._client.insert(
                    data=self._convert_data(batch), column_names=EVENT_LOG_COLUMNS, database=self._schema,
                    table=self._table, )
                logger.info(
                    "Batch inserted into ClickHouse", batch_size=len(batch), total_records=len(data),
                    batch_number=(i // batch_size) + 1, )
        except DatabaseError as e:
            logger.error(
                "Unable to insert batch data into ClickHouse", error=str(e), table=self._table, schema=self._schema, )
            raise

    def query(self, query: str) -> List[tuple[Any]]:
        """Executing a request to ClickHouse."""
        logger.debug("Executing ClickHouse query", query=query)
        try:
            result: Sequence[Sequence] = self._client.query(query).result_rows

            converted_result: List[Tuple[Any, ...]] = [tuple(row) for row in result]
            logger.info("Query executed successfully", row_count=len(converted_result))
            return converted_result

        except DatabaseError as e:
            logger.error(
                "Failed to execute ClickHouse query", error=str(e), query=query, )
            raise

    def _convert_data(self, data: List[Model]) -> List[Tuple[str, Any, str, str]]:
        """Convert data for insertion into ClickHouse."""
        now = timezone.now()
        return [
            (
                self._to_snake_case(event.__class__.__name__),  # str
                now,  # Any (datetime)
                self._environment,  # str
                event.model_dump_json(),  # str
            ) for event in data]

    @staticmethod
    def _to_snake_case(event_name: str) -> str:
        """Convert the event name to snake_case."""
        result = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", event_name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", result).lower()
