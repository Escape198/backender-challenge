from uuid import uuid4
from typing import Any

import structlog
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import transaction

from core.base_model import Model
from core.transactional_outbox import transactional_outbox
from core.use_case import UseCase, BaseRequest, BaseResponse
from users.models import User

logger = structlog.get_logger(__name__)


class UserCreated(Model):
    email: str
    first_name: str
    last_name: str


class CreateUserRequest(BaseRequest):
    email: str
    first_name: str = ''
    last_name: str = ''


class CreateUserResponse(BaseResponse):
    result: User | None = None
    error: str = ''


class CreateUser(UseCase):
    def _get_context_vars(self, request: CreateUserRequest) -> dict[str, Any]:
        """Forms context variables for user creation."""
        return {
            'email': request.email,
            'first_name': request.first_name,
            'last_name': request.last_name,
        }

    @staticmethod
    def _error_response(error_message: str) -> CreateUserResponse:
        """Logs an error and returns a response."""
        logger.error(error_message)
        return CreateUserResponse(error=error_message)

    @staticmethod
    def _validate_field_length(field_value: str, field_name: str, max_length: int) -> bool:
        if len(field_value) > max_length:
            error_message = f"{field_name} is too long"
            logger.error(error_message)
            return False
        return True

    def _execute(self, request: CreateUserRequest) -> CreateUserResponse:
        transaction_id = str(uuid4())
        logger.info("starting user creation process", transaction_id=transaction_id, email=request.email)

        if not request.email.strip():
            return self._error_response("Email is required")

        try:
            validate_email(request.email)
        except ValidationError:
            return self._error_response("Invalid email format")

        if not self._validate_field_length(request.email, "Email", 255):
            return self._error_response("Email is too long")
        if not self._validate_field_length(request.first_name, "First name", 255):
            return self._error_response("First name is too long")
        if not self._validate_field_length(request.last_name, "Last name", 255):
            return self._error_response("Last name is too long")

        try:
            event_data = []

            with transaction.atomic():
                with transactional_outbox(event_data=event_data):
                    user, created = User.objects.get_or_create(
                        email=request.email,
                        defaults={"first_name": request.first_name, "last_name": request.last_name},
                    )

                    if created:
                        logger.info(
                            "user has been created",
                            transaction_id=transaction_id,
                            user_id=user.id,
                            email=user.email,
                        )

                        event_data.append(
                            UserCreated(
                                email=user.email,
                                first_name=user.first_name,
                                last_name=user.last_name,
                            )
                        )
                        return CreateUserResponse(result=user)

                    logger.warning(
                        "user already exists",
                        transaction_id=transaction_id,
                        email=request.email,
                    )
                    return self._error_response("User with this email already exists")

        except Exception as e:
            logger.error(
                "unexpected error during user creation",
                transaction_id=transaction_id,
                error=str(e),
            )
            return self._error_response("An unexpected error occurred")
