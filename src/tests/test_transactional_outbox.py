import pytest
from unittest.mock import patch, call
from celery.exceptions import Retry
from core.transactional_outbox import transactional_outbox
from users.models import User
from users.tasks.tasks import log_user_creation


@pytest.mark.django_db
def test_transactional_outbox_success():
    """Ensure that transactional_outbox commits changes on success."""
    user_data = {"email": "test@example.com", "first_name": "Test", "last_name": "User"}
    event_data = []

    with transactional_outbox(event_data=event_data):
        user = User.objects.create(**user_data)
        event_data.append({"event_type": "user_created", "event_context": user_data})

    assert User.objects.filter(email=user_data["email"]).exists()
    assert len(event_data) == 1
    assert event_data[0]["event_type"] == "user_created"


@pytest.mark.django_db
def test_transactional_outbox_rollback():
    """Ensure that transactional_outbox rolls back changes on failure."""
    user_data = {"email": "test@example.com", "first_name": "Test", "last_name": "User"}
    event_data = []

    with pytest.raises(ValueError):
        with transactional_outbox(event_data=event_data):
            User.objects.create(**user_data)
            raise ValueError("Simulating failure")

    assert not User.objects.filter(email=user_data["email"]).exists()
    assert len(event_data) == 0


@pytest.mark.django_db
def test_log_user_creation_transactional():
    """
    Test that log_user_creation task respects transactional safety.
    Ensures no duplicate events are logged in ClickHouse in case of retries.
    """
    event_data = {"email": "test@example.com", "first_name": "Test", "last_name": "User", }

    with patch("core.event_log_client.EventLogClient.insert") as mock_insert, patch(
        "users.tasks.tasks.log_user_creation.retry", side_effect=Retry("Task can be retried")
    ) as mock_retry:
        mock_insert.side_effect = Exception("Simulated failure")

        try:
            log_user_creation(user_id=1, event_data=event_data)
        except Retry:
            ...

        mock_insert.assert_called_once_with([event_data])

        mock_retry.assert_called_once()
