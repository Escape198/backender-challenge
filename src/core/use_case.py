from typing import Any, Protocol, Dict
from abc import ABC, abstractmethod

import structlog
from django.db import transaction

from core.base_model import Model


logger = structlog.get_logger(__name__)


class UseCase(ABC):
    """Abstract class defining the interface for all Use Cases."""

    def execute(self, request: UseCaseRequest) -> UseCaseResponse:
        """Executes the Use Case."""
        with structlog.contextvars.bound_contextvars(**self._get_context_vars(request)):
            logger.info("Executing use case", use_case=self.__class__.__name__)
            return self._execute(request)

    def _get_context_vars(self, request: UseCaseRequest) -> Dict[str, Any]:
        """Generates context variables for logging."""
        return {"use_case": self.__class__.__name__}

    @abstractmethod
    def _execute(self, request: UseCaseRequest) -> UseCaseResponse:
        pass


class UseCaseResponse(Model):
    """A basic class for all answers."""
    result: Any = None
    error: str = ''


class UseCase(ABC):
    """Abstract class defining the interface for all Use Cases."""

    def execute(self, request: UseCaseRequest) -> UseCaseResponse:
        """Executes the Use Case."""
        with structlog.contextvars.bound_contextvars(**self._get_context_vars(request)):
            logger.info("Executing use case", use_case=self.__class__.__name__)
            return self._execute(request)

    def _get_context_vars(self, request: UseCaseRequest) -> Dict[str, Any]:
        """Generates context variables for logging."""
        return {"use_case": self.__class__.__name__}

    @abstractmethod
    def _execute(self, request: UseCaseRequest) -> UseCaseResponse:
        pass


class TransactionalUseCase(UseCase):
    """Abstract Use Case with transactional execution."""

    @transaction.atomic
    def execute(self, request: UseCaseRequest) -> UseCaseResponse:
        """
        Execute the Use Case within a database transaction.

        Overrides the base execute method to wrap the operation in an atomic block.
        """
        logger.info("Executing transactional use case", use_case=self.__class__.__name__)
        return super().execute(request)
