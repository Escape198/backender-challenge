from typing import Any, Protocol

import structlog
from django.db import transaction

from core.base_model import Model


logger = structlog.get_logger(__name__)


class UseCaseRequest(Model):
    """The base class for all queries."""
    pass


class UseCaseResponse(Model):
    """A basic class for all answers."""
    result: Any = None
    error: str = ''


class UseCase(Protocol):
    """A protocol that defines the interface for all Use Cases."""
    def execute(self, request: UseCaseRequest) -> UseCaseResponse:
        """The primary method of execution is Use Case."""
        with structlog.contextvars.bound_contextvars(**self._get_context_vars(request)):
            logger.info("Executing use case", use_case=self.__class__.__name__)
            return self._execute(request)

    def _get_context_vars(self, request: UseCaseRequest) -> dict[str, Any]:  # noqa: ARG002
        """
        Generates context variables for logging.
        !!! WARNING:
            Do not query the database in this method.
        """
        return {"use_case": self.__class__.__name__,}

    def _execute(self, request: UseCaseRequest) -> UseCaseResponse:
        """An abstract method that must be implemented in subclasses."""
        raise NotImplementedError("Subclasses must implement '_execute'")


class TransactionalUseCase(UseCase):
    """Abstract Use Case with transactional execution."""
    @transaction.atomic
    def execute(self, request: UseCaseRequest) -> UseCaseResponse:
        """Executing a Use Case in a Transaction."""
        with structlog.contextvars.bound_contextvars(**self._get_context_vars(request)):
            logger.info("Executing transactional use case", use_case=self.__class__.__name__)
            return self._execute(request)
