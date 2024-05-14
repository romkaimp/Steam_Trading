# django_celery/celery_settings.py

import os
import celery

os.environ.setdefault("FASTAPI_SETTINGS_MODULE", "service/settings.env")
app = celery.Celery("fastapi_celery", broker="redis://localhost:6379")
app.config_from_object("settings.env", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "parsing_steam":
        {
            "task": "tasks.table_update",
            "schedule": 300,
        },
    "updating_ml":
        {
            "task": "tasks.update_weights",
            "schedule": 9000.0,
        }
}
