from typing import Any, Dict
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
            try:
                return self._execute(request)
            except Exception as e:
                logger.error("Error executing use case", error=str(e), use_case=self.__class__.__name__)
                return self._error_response(str(e))

    def _get_context_vars(self, request: BaseRequest) -> Dict[str, Any]:
        """Generates context variables for logging."""
        return {"use_case": self.__class__.__name__}

    @abstractmethod
    def _execute(self, request: BaseRequest) -> BaseResponse:
        pass

    def _error_response(self, error_message: str) -> BaseResponse:
        """Logs an error and returns a response."""
        logger.error(error_message)
        return BaseResponse(error=error_message)


class UseCaseResponse(Model):
    """A basic class for all answers."""
    result: Any = None
    error: str = ''


class TransactionalUseCase(UseCase):
    """Abstract Use Case with transactional execution."""

    @transaction.atomic
    def execute(self, request: BaseRequest) -> UseCaseResponse:
        """
        Execute the Use Case within a database transaction.

        Overrides the base execute method to wrap the operation in an atomic block.
        """
        logger.info("Executing transactional use case", use_case=self.__class__.__name__)
        try:
            return super().execute(request)
        except Exception as e:
            logger.error("Error executing transactional use case", error=str(e), use_case=self.__class__.__name__)
            raise
