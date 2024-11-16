from typing import Any, Protocol, Dict
from abc import ABC, abstractmethod

import structlog
from django.db import transaction

from core.base_model import Model


logger = structlog.get_logger(__name__)


class BaseRequest(Model):
    """Base class for all Use Case requests."""
    pass


class BaseResponse(Model):
    """Base class for all Use Case responses."""
    result: Any = None
    error: str = ''


class UseCase(ABC):
    """Abstract class defining the interface for all Use Cases."""

    def execute(self, request: BaseRequest) -> BaseResponse:
        """Executes the Use Case."""
        with structlog.contextvars.bound_contextvars(**self._get_context_vars(request)):
            logger.info("Executing use case", use_case=self.__class__.__name__)
            return self._execute(request)

    def _get_context_vars(self, request: BaseRequest) -> Dict[str, Any]:
        """Generates context variables for logging."""
        return {"use_case": self.__class__.__name__}

    @abstractmethod
    def _execute(self, request: BaseRequest) -> BaseResponse:
        pass


class UseCase(ABC):
    """Abstract class defining the interface for all Use Cases."""

    def execute(self, request: BaseRequest) -> BaseResponse:
        """Executes the Use Case."""
        with structlog.contextvars.bound_contextvars(**self._get_context_vars(request)):
            logger.info("Executing use case", use_case=self.__class__.__name__)
            return self._execute(request)

    def _get_context_vars(self, request: BaseRequest) -> Dict[str, Any]:
        """Generates context variables for logging."""
        return {"use_case": self.__class__.__name__}

    @abstractmethod
    def _execute(self, request: BaseRequest) -> BaseResponse:
        pass


class TransactionalUseCase(UseCase):
    """Abstract Use Case with transactional execution."""

    @transaction.atomic
    def execute(self, request: BaseRequest) -> BaseResponse:
        """
        Execute the Use Case within a database transaction.

        Overrides the base execute method to wrap the operation in an atomic block.
        """
        logger.info("Executing transactional use case", use_case=self.__class__.__name__)
        return super().execute(request)
