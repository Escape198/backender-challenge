import uuid
from collections.abc import Generator
from unittest.mock import ANY

import pytest
from clickhouse_connect.driver import Client
from django.conf import settings

from users.use_cases import CreateUser, CreateUserRequest, UserCreated

pytestmark = [pytest.mark.django_db]


@pytest.fixture()
def f_use_case() -> CreateUser:
    """A fixture for creating an instance of UseCase."""
    return CreateUser()


@pytest.fixture(autouse=True)
def f_clean_up_event_log(f_ch_client: Client) -> Generator:
    """Automatically clears the ClickHouse table before each test."""
    f_ch_client.query(f"TRUNCATE TABLE {settings.CLICKHOUSE_EVENT_LOG_TABLE_NAME}")
    yield


def test_user_created(f_use_case: CreateUser) -> None:
    """Verify that the user was successfully created."""
    request = CreateUserRequest(email="test@email.com", first_name="Test", last_name="Testovich",)

    response = f_use_case.execute(request)

    assert response.result.email == "test@email.com"
    assert response.error == ""


def test_emails_are_unique(f_use_case: CreateUser) -> None:
    """Email uniqueness check."""
    request = CreateUserRequest(email="test@email.com", first_name="Test", last_name="Testovich",)

    f_use_case.execute(request)
    response = f_use_case.execute(request)

    assert response.result is None
    assert response.error == "User with this email already exists"


def test_event_log_entry_published(f_use_case: CreateUser, f_ch_client: Client) -> None:
    """Verify that a record is published to ClickHouse when a user is successfully created."""
    email = f"test_{uuid.uuid4()}@email.com"
    request = CreateUserRequest(
        email=email, first_name="Test", last_name="Testovich",
    )

    f_use_case.execute(request)
    log = f_ch_client.query(
        f"SELECT * FROM {settings.CLICKHOUSE_EVENT_LOG_TABLE_NAME} WHERE event_type = 'user_created'"
    )

    assert log.result_rows == [
        (
            "user_created",
            ANY,
            "Local",
            UserCreated(email=email, first_name="Test", last_name="Testovich").model_dump_json(),
            1,
        ),
    ]


def test_empty_request_handling(f_use_case: CreateUser) -> None:
    """Verify that an empty or invalid request is properly handled."""
    request = CreateUserRequest(email="", first_name="", last_name="")

    response = f_use_case.execute(request)

    assert response.result is None
    assert response.error != ""
    assert "email" in response.error.lower()


def test_long_strings_handling(f_use_case: CreateUser) -> None:
    """Verify that overly long strings in the request are properly handled."""
    long_string = "a" * 256
    request = CreateUserRequest(email=f"{long_string}@email.com", first_name=long_string, last_name=long_string)

    response = f_use_case.execute(request)

    assert response.result is None
    assert response.error != ""
    assert "too long" in response.error.lower()


def test_invalid_email_format(f_use_case: CreateUser) -> None:
    """Verify that invalid email formats are properly handled."""
    invalid_email = "invalid_email_format"  # Некорректный формат email
    request = CreateUserRequest(email=invalid_email, first_name="Test", last_name="Testovich")

    response = f_use_case.execute(request)

    assert response.result is None
    assert response.error != ""
    assert "email" in response.error.lower()
