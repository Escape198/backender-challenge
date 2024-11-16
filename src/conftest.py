import os
import clickhouse_connect
import pytest
from clickhouse_connect.driver import Client


@pytest.fixture(scope='module')
def f_ch_client() -> Client:
    """Fixture for providing a ClickHouse client."""
    clickhouse_host = os.getenv('CLICKHOUSE_HOST', 'localhost')
    clickhouse_port = os.getenv('CLICKHOUSE_PORT', '9000')

    client = clickhouse_connect.get_client(host=clickhouse_host, port=int(clickhouse_port))
    yield client
    client.close()
