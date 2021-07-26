from django.contrib.auth import get_user_model
from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.management import call_command
from config import celery_app

User = get_user_model()


@celery_app.task()
def get_users_count():
    """A pointless Celery task to demonstrate usage."""
    return User.objects.count()


# @celery_app.task()
# @shared_task
@celery_app.task()
def update_exchange_rate():
    call_command("update_rates", )
