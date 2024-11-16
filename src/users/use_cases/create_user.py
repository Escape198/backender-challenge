from typing import Any

import structlog
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from core.base_model import Model
from core.transactional_outbox import transactional_outbox
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
        logger.info("creating a new user", email=request.email)

        if not request.email.strip():
            logger.error("invalid request: email is required")
            return CreateUserResponse(error="Email is required")

        try:
            validate_email(request.email)
        except ValidationError:
            logger.error("invalid request: invalid email format")
            return CreateUserResponse(error="Invalid email format")

        if len(request.email) > 255:
            logger.error("invalid request: email is too long")
            return CreateUserResponse(error="Email is too long")

        if len(request.first_name) > 255 or len(request.last_name) > 255:
            logger.error("invalid request: name fields are too long")
            return CreateUserResponse(error="Name fields are too long")

        try:
            event_data = []

            with transactional_outbox(event_data=event_data):
                user, created = User.objects.get_or_create(
                    email=request.email, defaults={"first_name": request.first_name, "last_name": request.last_name}, )

                if created:
                    logger.info("user has been created", user_id=user.id)

                    event_data.append(
                        UserCreated(email=user.email, first_name=user.first_name, last_name=user.last_name, )
                    )
                    return CreateUserResponse(result=user)

                logger.warning("user already exists", email=request.email)
                return CreateUserResponse(error="User with this email already exists")

        except Exception as e:
            logger.error("unexpected error during user creation", error=str(e))
            return CreateUserResponse(error="An unexpected error occurred")
