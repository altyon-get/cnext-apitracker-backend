from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cnext_apitracker_backend.settings')
app = Celery('cnext_apitracker_backend')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'hit-apis-every-hour': {
        'task': 'api.tasks.hit_apis_and_log',
        'schedule': crontab(minute='*/3')
    }
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
