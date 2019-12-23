import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghost_shopper.settings')

app = Celery('ghost_shopper', broker=settings.CELERY_BROKER_URL)
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    'delete_audio': {
        'task': 'ghost_shopper.check.tasks.delete_old_audio',
        'schedule': crontab(day_of_month=1, hour=2),
    },
    'make-docs': {
        'task': 'ghost_shopper.organisation_tree.tasks.create_documents',
        'schedule': crontab(day_of_month=1, hour=3),
    },
    'invoke_close_manager': {
        'task': 'ghost_shopper.check.tasks.invoke_check_close_manager',
        'schedule': crontab(hour=4),
    }

}