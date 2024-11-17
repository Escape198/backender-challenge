import pytest
from unittest.mock import patch
from users.tasks import log_user_creation
from users.models import User


@pytest.mark.django_db
def test_log_user_creation():
    """Test the log_user_creation Celery task."""
    with patch("core.event_log_client.EventLogClient.insert") as mock_insert:
        # Create a test user
        user = User.objects.create(email="test@example.com", first_name="Test", last_name="User")

        # Prepare event data
        event_data = {"email": user.email, "first_name": user.first_name, "last_name": user.last_name}

        # Call the Celery task
        log_user_creation(user.id, event_data)

        # Assert that insert was called once with the correct event data
        mock_insert.assert_called_once_with([event_data])

        # Optionally, you can test that the logger was also called, to verify logging functionality.  # If you are using structlog for logging, you can mock the logger or use a similar approach.
