import os
from celery import Celery

# Settings load .env themselves, so the worker sees the same config as the web app.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

app = Celery('main')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
