import uuid
import pytest
from django.conf import settings

from users.use_cases import CreateUserRequest

'''
@pytest.mark.django_db
@pytest.mark.integration
def test_user_creation_with_event_logging(f_ch_client, f_use_case):
    """Test that user creation logs an event in ClickHouse."""
    email = f'test_{uuid.uuid4()}@example.com'
    first_name = "Test"
    last_name = "User"
    request = CreateUserRequest(email=email, first_name=first_name, last_name=last_name)

    response = f_use_case.execute(request)

    assert response.result is not None, f"Expected result, but got None. Error: {response.error}"
    assert response.error == "", f"Expected no error, but got: {response.error}"
    assert response.result.email == email, f"Expected email {email}, but got {response.result.email}"

    query = f"""
        SELECT event_context
        FROM {settings.CLICKHOUSE_EVENT_LOG_TABLE_NAME}
        WHERE event_type = 'user_created' AND event_context LIKE '%{email}%'
    """
    logs = f_ch_client.execute(query)

    assert len(logs) == 1, "Expected exactly one log entry."
    assert email in logs[0][0], f"Expected email to be in event log, but got {logs[0][0]}"
'''


@pytest.fixture
def f_use_case():
    """Fixture for CreateUser use case."""
    from users.use_cases import CreateUser
    return CreateUser()
