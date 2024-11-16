import uuid
from collections.abc import Generator

import pytest
from clickhouse_connect.driver import Client
from django.conf import settings

from users.use_cases import CreateUser, CreateUserRequest, UserCreated

pytestmark = [pytest.mark.django_db]


@pytest.fixture()
def f_use_case() -> CreateUser:
    """
    Fixture for the CreateUser use case.
    """
    return CreateUser()


@pytest.fixture(autouse=True)
def f_clean_up_event_log(f_ch_client: Client) -> Generator:
    """
    Automatically cleans up the event log table in ClickHouse before each test.
    Ensures the test environment is isolated and free of residue data.
    """
    f_ch_client.query(f'TRUNCATE TABLE {settings.CLICKHOUSE_EVENT_LOG_TABLE_NAME}')
    yield


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


def test_event_log_entry_created_in_clickhouse(
    f_use_case: CreateUser,
    f_ch_client: Client,
) -> None:
    """
    Test that a 'user_created' event is logged in the ClickHouse event log table.
    Ensures the log entry is correctly recorded after a successful user creation.
    """
    email = f'test_{uuid.uuid4()}@email.com'
    request = CreateUserRequest(
        email=email, first_name='Test', last_name='Testovich',
    )

    f_use_case.execute(request)

    # Fetching logs from ClickHouse for validation
    log_query = f"""
        SELECT event_type 
        FROM {settings.CLICKHOUSE_EVENT_LOG_TABLE_NAME} 
        WHERE event_type = 'user_created'
    """
    log = f_ch_client.query(log_query)

    # Verifying that the correct event was logged
    assert log.result_rows == [('user_created',), ]
