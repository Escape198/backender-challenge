import uuid
from collections.abc import Generator
from unittest.mock import ANY, patch

import pytest
from clickhouse_connect.driver import Client
from django.conf import settings

from users.use_cases import CreateUser, CreateUserRequest, UserCreated
from users.models import User

pytestmark = [pytest.mark.django_db]


@pytest.fixture()
def f_use_case() -> CreateUser:
    """
    Фикстура для создания экземпляра UseCase.
    """
    return CreateUser()


@pytest.fixture(autouse=True)
def f_clean_up_event_log(f_ch_client: Client) -> Generator:
    """
    Автоматическая очистка таблицы ClickHouse перед каждым тестом.
    """
    f_ch_client.query(f"TRUNCATE TABLE {settings.CLICKHOUSE_EVENT_LOG_TABLE_NAME}")
    yield


def test_user_created(f_use_case: CreateUser) -> None:
    """
    Проверка успешного создания пользователя.
    """
    request = CreateUserRequest(email="test@email.com", first_name="Test", last_name="Testovich",)

    response = f_use_case.execute(request)

    assert response.result.email == "test@email.com"
    assert response.error == ""


def test_emails_are_unique(f_use_case: CreateUser) -> None:
    """
    Проверка уникальности email.
    """
    request = CreateUserRequest(email="test@email.com", first_name="Test", last_name="Testovich",)

    f_use_case.execute(request)
    response = f_use_case.execute(request)

    assert response.result is None
    assert response.error == "User with this email already exists"


def test_event_log_entry_published(f_use_case: CreateUser, f_ch_client: Client) -> None:
    """
    Проверка публикации записи в ClickHouse при успешном создании пользователя.
    """
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