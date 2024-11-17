import pytest
from clickhouse_driver import Client


@pytest.fixture(scope='module')
def f_ch_client() -> Client:
    client = Client(host='clickhouse')
    yield client
    client.disconnect()


@pytest.fixture
def f_clickhouse_event_table_name(settings):
    client = Client(host=settings.CLICKHOUSE_HOST, database=settings.CLICKHOUSE_DATABASE)
    table_name = settings.CLICKHOUSE_EVENT_LOG_TABLE_NAME

    # Проверка подключения и создание таблицы, если нужно
    client.execute(f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        id UUID,
        event_data String,
        created_at DateTime
    ) ENGINE = MergeTree()
    ORDER BY created_at
    ''')

    return table_name


def create_clickhouse_database():
    client = Client(host='clickhouse', port=9000)
    client.execute('CREATE DATABASE IF NOT EXISTS test_database')
    client.execute('''
        CREATE TABLE IF NOT EXISTS test_database.event_log (
            id UUID,
            event_data String,
            created_at DateTime
        ) ENGINE = MergeTree()
        ORDER BY created_at;
    ''')


@pytest.fixture(scope='session', autouse=True)
def setup_clickhouse():
    create_clickhouse_database()
