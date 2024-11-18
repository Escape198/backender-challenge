from unittest.mock import patch

import pytest
from celery.exceptions import Retry

from outbox.models import OutboxEvent
from outbox.transactional_outbox import transactional_outbox
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
    event_data = {"email": "test@example.com", "first_name": "Test", "last_name": "User" }

    with patch("core.event_log_client.EventLogClient.insert") as mock_insert, patch(
        "users.tasks.tasks.log_user_creation.retry", side_effect=Retry("Task can be retried"),
    ) as mock_retry:
        mock_insert.side_effect = Exception("Simulated failure")

        try:
            log_user_creation(user_id=1, event_data=event_data)
        except Retry:
            ...

        mock_insert.assert_called_once_with([event_data])

        mock_retry.assert_called_once()


@pytest.mark.django_db
def test_log_user_creation_creates_event():
    """Test that the log_user_creation task creates an outbox event and logs it to ClickHouse."""
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    event_data = {"email": "test@example.com", "first_name": "Test", "last_name": "User"}

    with patch("core.event_log_client.EventLogClient.insert") as mock_insert:
        log_user_creation(user_id, event_data)

        event = OutboxEvent.objects.get(user_id=user_id)
        assert event.status == "processed"

        mock_insert.assert_called_once_with([event_data])


@pytest.mark.django_db
def test_log_user_creation_skips_processed_event():
    """Test that the task skips duplicate events with status 'processed'."""
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    event_data = {"email": "test@example.com", "first_name": "Test", "last_name": "User"}

    OutboxEvent.objects.create(user_id=user_id, event_data=event_data, status="processed")

    with patch("core.event_log_client.EventLogClient.insert") as mock_insert:
        log_user_creation(user_id, event_data)

        mock_insert.assert_not_called()


@pytest.mark.django_db
def test_log_user_creation_retries_on_failure():
    """Test that the task retries when an exception occurs."""
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    event_data = {"email": "test@example.com", "first_name": "Test", "last_name": "User"}

    OutboxEvent.objects.create(user_id=user_id, event_data=event_data, status="pending")

    with patch("core.event_log_client.EventLogClient.insert", side_effect=Exception("Connection error")) as mock_insert:
        with pytest.raises(Exception, match="Connection error"):
            log_user_creation(user_id, event_data)

        event = OutboxEvent.objects.get(user_id=user_id)
        assert event.status == "pending"
        mock_insert.assert_called_once()


@pytest.mark.django_db
def test_log_user_creation_resumes_failed_event():
    """Test that a previously failed event is retried and marked as processed upon success."""
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    event_data = {"email": "test@example.com", "first_name": "Test", "last_name": "User"}

    OutboxEvent.objects.create(user_id=user_id, event_data=event_data, status="pending")

    with patch("core.event_log_client.EventLogClient.insert") as mock_insert:
        log_user_creation(user_id, event_data)

        event = OutboxEvent.objects.get(user_id=user_id)
        assert event.status == "processed"

        mock_insert.assert_called_once_with([event_data])
