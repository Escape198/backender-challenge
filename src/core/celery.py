from celery import Celery
from celery.signals import task_prerun, task_postrun
from django.conf import settings

import structlog

logger = structlog.get_logger(__name__)

app = Celery('core')
app.config_from_object(settings, namespace='CELERY')
app.autodiscover_tasks()


@task_prerun.connect
def setup_structlog(sender=None, task_id=None, **kwargs):
    """Логируем старт задачи."""
    logger.info("Celery task started", task_name=sender.name, task_id=task_id)


@task_postrun.connect
def teardown_structlog(sender=None, task_id=None, **kwargs):
    """Логируем завершение задачи."""
    logger.info("Celery task completed", task_name=sender.name, task_id=task_id)
