from core.transactional_outbox import transactional_outbox
from users.models import User
import pytest


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
