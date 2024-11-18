from celery import Celery
from celery.signals import task_prerun, task_postrun
from django.conf import settings
import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars
import uuid

logger = structlog.get_logger(__name__)

app = Celery('core')
app.config_from_object(settings, namespace='CELERY')
app.autodiscover_tasks()


@task_prerun.connect
def setup_structlog(sender=None, task_id=None, **kwargs):
    """Log the start of a task and bind a trace ID for tracing."""
    trace_id = str(uuid.uuid4())
    bind_contextvars(task_name=sender.name, task_id=task_id, trace_id=trace_id)
    logger.info("Task started", task_name=sender.name, task_id=task_id, trace_id=trace_id)


@task_postrun.connect
def teardown_structlog(sender=None, task_id=None, state=None, exception=None, **kwargs):
    """Log the completion of a task, including errors if they occurred."""
    trace_id = structlog.contextvars.get_contextvars().get("trace_id", "unknown")

    if exception:
        logger.error(
            "Task failed", task_name=sender.name, task_id=task_id, trace_id=trace_id, error=str(exception), )
    else:
        logger.info(
            "Task completed successfully", task_name=sender.name, task_id=task_id, trace_id=trace_id, )

    clear_contextvars()
