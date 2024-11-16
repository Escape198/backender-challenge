from typing import Any, Protocol, Dict
from abc import ABC, abstractmethod

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


class UseCase(ABC):
    """Abstract class defining the interface for all Use Cases."""

    def execute(self, request: UseCaseRequest) -> UseCaseResponse:
        """
        The primary method of execution for the Use Case.

        Subclasses may override this method for custom behavior.
        """
        with structlog.contextvars.bound_contextvars(**self._get_context_vars(request)):
            logger.info("Executing use case", use_case=self.__class__.__name__)
            return self._execute(request)

    def _get_context_vars(self, request: UseCaseRequest) -> Dict[str, Any]:
        """
        Generates context variables for logging.

        WARNING:
        Do not query the database in this method.
        """
        return {"use_case": self.__class__.__name__}

    @abstractmethod
    def _execute(self, request: UseCaseRequest) -> UseCaseResponse:
        """An abstract method that must be implemented in subclasses."""
        pass


class TransactionalUseCase(UseCase):
    """Abstract Use Case with transactional execution."""

    @transaction.atomic
    def execute(self, request: UseCaseRequest) -> UseCaseResponse:
        """
        Execute the Use Case within a database transaction.

        Overrides the base execute method to wrap the operation in an atomic block.
        """
        with structlog.contextvars.bound_contextvars(**self._get_context_vars(request)):
            logger.info("Executing transactional use case", use_case=self.__class__.__name__)
            return self._execute(request)
