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


def test_user_creation_success(f_use_case: CreateUser) -> None:
    """
    Test the successful creation of a user.
    Ensures the response contains the correct data and no errors.
    """
    request = CreateUserRequest(
        email='test@email.com', first_name='Test', last_name='Testovich',
    )

    response = f_use_case.execute(request)

    # Verifying response details
    assert response.result.email == 'test@email.com'
    assert response.error == ''


def test_user_creation_duplicate_email(f_use_case: CreateUser) -> None:
    """
    Test that creating a user with a duplicate email raises an error.
    Ensures the use case handles unique constraints correctly.
    """
    request = CreateUserRequest(
        email='test@email.com', first_name='Test', last_name='Testovich',
    )

    f_use_case.execute(request)  # First attempt should succeed
    response = f_use_case.execute(request)  # Second attempt should fail

    # Verifying the error message
    assert response.result is None
    assert response.error == 'User with this email already exists'


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
