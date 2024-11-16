from typing import Any

import structlog
from django.db import transaction

from core.base_model import Model
from core.event_log_client import EventLogClient
from core.use_case import UseCase, UseCaseRequest, UseCaseResponse
from users.models import User

logger = structlog.get_logger(__name__)


class UserCreated(Model):
    email: str
    first_name: str
    last_name: str


class CreateUserRequest(UseCaseRequest):
    email: str
    first_name: str = ''
    last_name: str = ''


class CreateUserResponse(UseCaseResponse):
    result: User | None = None
    error: str = ''


class CreateUser(UseCase):
    def _get_context_vars(self, request: UseCaseRequest) -> dict[str, Any]:
        """Forms context variables for user creation."""
        return {
            'email': request.email,
            'first_name': request.first_name,
            'last_name': request.last_name,
        }

    def _execute(self, request: CreateUserRequest) -> CreateUserResponse:
        """Basic method of creating a user with error handling and transactions."""
        logger.info('creating a new user', email=request.email)

        try:
            with transaction.atomic():
                user, created = User.objects.get_or_create(
                    email=request.email,
                    defaults={
                        'first_name': request.first_name,
                        'last_name': request.last_name,
                    },
                )

                if created:
                    logger.info('user has been created', user_id=user.id)
                    self._log_event(user)
                    return CreateUserResponse(result=user)

                logger.warning('user already exists', email=request.email)
                return CreateUserResponse(error='User with this email already exists')

        except Exception as e:
            logger.error('unexpected error during user creation', error=str(e))
            return CreateUserResponse(error='An unexpected error occurred')

    @staticmethod
    def _log_event(user: User) -> None:
        """Logging the user creation event."""
        try:
            with EventLogClient.init() as client:
                client.insert(
                    data=[
                        UserCreated(
                            email=user.email,
                            first_name=user.first_name,
                            last_name=user.last_name,
                        ),
                    ],
                )
                logger.info('event logged successfully', email=user.email)
        except Exception as e:
            logger.error('failed to log event', error=str(e))
            raise
