from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, List, Tuple

import structlog
from clickhouse_driver import Client
from clickhouse_driver.errors import Error
from django.conf import settings

from core.base_model import Model

logger = structlog.get_logger(__name__)

EVENT_LOG_COLUMNS = ["event_type", "event_date_time", "environment", "event_context", ]


class EventLogClient:
    def __init__(
            self, client: Client, schema: str, table: str, environment: str, ) -> None:
        self._client = client
        self._schema = schema
        self._table = table
        self._environment = environment

    @classmethod
    @contextmanager
    def init(cls) -> Generator["EventLogClient", None, None]:
        """Client initialization for ClickHouse."""
        logger.info("Connecting to ClickHouse", host=settings.CLICKHOUSE_HOST, port=settings.CLICKHOUSE_PORT)

        client = Client(
            host=settings.CLICKHOUSE_HOST, port=settings.CLICKHOUSE_PORT, user=settings.CLICKHOUSE_USER,
            password=settings.CLICKHOUSE_PASSWORD, database=settings.CLICKHOUSE_SCHEMA, connect_timeout=30,
            send_receive_timeout=10
        )
        try:
            yield cls(
                client=client, schema=settings.CLICKHOUSE_SCHEMA, table=settings.CLICKHOUSE_EVENT_LOG_TABLE_NAME,
                environment=settings.ENVIRONMENT, )
        except Exception as e:
            logger.error("Error while initializing ClickHouse client", error=str(e))
            raise
        finally:
            client.disconnect()

    def insert(self, data: List[Model], batch_size: int = 100) -> None:
        """
        Inserts events into ClickHouse with batching support.

        :param data: List of events to insert.
        :param batch_size: Batch size for batch insertion (default is 100).
        """
        if not self.is_connected():
            raise Error("ClickHouse is not available")

        logger.info("Inserting events into ClickHouse", data_count=len(data))
        try:
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                logger.info("Attempting batch insert", batch_size=len(batch), columns=EVENT_LOG_COLUMNS)

                # Prepare parameterized query for batch insert
                insert_query = f"""
                    INSERT INTO {self._schema}.{self._table} ({', '.join(EVENT_LOG_COLUMNS)})
                    VALUES
                """
                # Prepare the data to be inserted
                formatted_data = self._convert_data(batch)

                self._client.execute(insert_query, formatted_data)
                logger.info("Batch inserted successfully", batch_size=len(batch))

        except Error as e:
            logger.error("Failed to insert batch into ClickHouse", error=str(e))
            raise

    def execute_query(self, query: str) -> List[tuple[Any]]:
        """Execute a request to ClickHouse using execute."""
        logger.debug("Executing ClickHouse query", query=query)
        try:
            result = self._client.execute(query)

            converted_result: List[Tuple[Any, ...]] = [tuple(row) for row in result]
            logger.info("Query executed successfully", row_count=len(converted_result))
            return converted_result

        except Error as e:
            logger.error(
                "Failed to execute ClickHouse query", error=str(e), query=query, )
            raise

    def is_connected(self) -> bool:
        """Check if the client can connect to ClickHouse."""
        try:
            self._client.execute("SELECT 1")
            logger.debug("ClickHouse connection successful")
            return True
        except Error as e:
            logger.error("ClickHouse connection failed", error=str(e))
            return False

    def _convert_data(self, data: List[Model]) -> List[Tuple]:
        """
        Converts a list of Model instances into the format suitable for insertion into ClickHouse.
        """
        return [(event.event_type, event.event_date_time, self._environment, event.event_context) for event in data]
