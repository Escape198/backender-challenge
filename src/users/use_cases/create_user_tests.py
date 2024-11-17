import uuid
import logging
from collections.abc import Generator

import pytest
from clickhouse_driver import Client as ClickhouseClient
from django.conf import settings

from users.use_cases import CreateUser, CreateUserRequest
from core.event_log_client import EventLogClient

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.django_db]


@pytest.fixture()
def f_use_case() -> CreateUser:
    """
    Fixture for the CreateUser use case.
    """
    return CreateUser()


@pytest.fixture(autouse=True)
def f_clean_up_event_log(f_ch_client: ClickhouseClient) -> Generator:
    """
    Automatically cleans up the event log table in ClickHouse before and after each test.
    """
    f_ch_client.execute(f'TRUNCATE TABLE {settings.CLICKHOUSE_EVENT_LOG_TABLE_NAME}')
    yield
    f_ch_client.execute(f'TRUNCATE TABLE {settings.CLICKHOUSE_EVENT_LOG_TABLE_NAME}')


@pytest.mark.parametrize(
    "email, first_name, last_name, expected_error",
    [
        ("", "Test", "Testovich", "Email is required"),
        ("invalid_email", "Test", "Testovich", "Invalid email format"),
        ("a" * 256 + "@email.com", "Test", "Testovich", "Email is too long"),
        ("test@email.com", "a" * 256, "Testovich", "First name is too long"),
        ("test@email.com", "Test", "a" * 256, "Last name is too long"),
    ],
)
def test_invalid_user_creation(
    f_use_case: CreateUser,
    email: str,
    first_name: str,
    last_name: str,
    expected_error: str,
) -> None:
    """
    Test invalid user creation scenarios with various erroneous inputs.
    Ensures the correct error message is returned for each case.
    """
    request = CreateUserRequest(email=email, first_name=first_name, last_name=last_name)
    response = f_use_case.execute(request)

    # Verifying the response
    assert response.result is None
    assert response.error == expected_error


@pytest.fixture
def event_log_client() -> EventLogClient:
    """Fixture for initializing EventLogClient."""
    with EventLogClient.init() as client:
        yield client


@pytest.mark.skipif(
    not EventLogClient(
        client=ClickhouseClient(
            host=settings.CLICKHOUSE_HOST,
            port=settings.CLICKHOUSE_PORT,
            user=settings.CLICKHOUSE_USER,
            password=settings.CLICKHOUSE_PASSWORD,
        ),
        schema=settings.CLICKHOUSE_SCHEMA,
        table=settings.CLICKHOUSE_EVENT_LOG_TABLE_NAME,
        environment=settings.ENVIRONMENT,
    ).is_connected(),
    reason="ClickHouse is not available for testing",
)
def test_event_log_entry_created_in_clickhouse(
    f_use_case: CreateUser,
    f_ch_client: ClickhouseClient,
    f_clickhouse_event_table_name: str,
) -> None:
    """
    Test that a 'user_created' event is logged in the ClickHouse event log table.
    """
    import uuid
    from django.conf import settings
    import time

    # Подготовка данных
    email = f'test_{uuid.uuid4()}@email.com'
    first_name = "Test"
    last_name = "Testovich"
    request = CreateUserRequest(email=email, first_name=first_name, last_name=last_name)

    # Выполнение use case
    f_use_case.execute(request)

    # Запрос всех логов для отладки
    log_query = f"SELECT * FROM {settings.CLICKHOUSE_EVENT_LOG_TABLE_NAME}"
    logs = f_ch_client.query(log_query)
    logger.debug(f"All ClickHouse logs: {logs.result_rows}")

    # Проверка, что событие 'user_created' присутствует
    event_query = f"""
        SELECT event_type 
        FROM {settings.CLICKHOUSE_EVENT_LOG_TABLE_NAME} 
        WHERE event_type = 'user_created'
    """

    # Повторные попытки для ожидания записи
    for attempt in range(5):  # 5 попыток
        result = f_ch_client.query(event_query)
        logger.info(f"Query result attempt {attempt + 1}: {result.result_rows}")
        if result.result_rows:
            break
        time.sleep(1)  # ожидание 1 секунду

    assert result.result_rows == [('user_created',)]


def test_no_event_logged_on_failure(
    f_use_case: CreateUser,
    f_ch_client: ClickhouseClient,
    f_clickhouse_event_table_name: str,
) -> None:
    """
    Test that no event is logged in ClickHouse if user creation fails.
    """
    print(f"Using table: {f_clickhouse_event_table_name}")
    invalid_email = "invalid_email"
    request = CreateUserRequest(email=invalid_email, first_name="Test", last_name="Testovich")

    response = f_use_case.execute(request)

    # Ensuring the use case fails
    assert response.result is None
    assert response.error == "Invalid email format"

    # Ensuring no events are logged
    log_query = f"SELECT event_type FROM {settings.CLICKHOUSE_EVENT_LOG_TABLE_NAME} WHERE event_context LIKE '%invalid_email%'"

    # Correct method to execute the query
    result = f_ch_client.execute(log_query)

    # Check that the result is empty
    assert not result
