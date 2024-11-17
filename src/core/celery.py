from celery import Celery
from celery.signals import task_prerun, task_postrun
from django.conf import settings
import structlog
from structlog.contextvars import bind_contextvars

logger = structlog.get_logger(__name__)

app = Celery('core')
app.config_from_object(settings, namespace='CELERY')
app.autodiscover_tasks()


@task_prerun.connect
def setup_structlog(sender=None, task_id=None, **kwargs):
    """We log the start of the task and associate it with the context."""
    bind_contextvars(task_name=sender.name, task_id=task_id)
    logger.info("Celery task started", task_name=sender.name, task_id=task_id)


@task_postrun.connect
def teardown_structlog(sender=None, task_id=None, **kwargs):
    """Logging the completion of the task."""
    logger.info("Celery task completed", task_name=sender.name, task_id=task_id)


@task_postrun.connect
def log_task_failure(sender=None, task_id=None, exception=None, **kwargs):
    """Log errors if the task terminated with an error."""
    if exception:
        logger.error("Celery task failed", task_name=sender.name, task_id=task_id, exception=str(exception))
