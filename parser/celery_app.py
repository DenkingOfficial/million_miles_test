from celery import Celery
from celery.schedules import crontab
from config import config

celery_app = Celery(
    "encar_parser",
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND,
    include=["tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=7200,
    task_soft_time_limit=6600,
)

celery_app.conf.beat_schedule = {
    "parse-encar-daily": {
        "task": "tasks.parse_encar_data",
        "schedule": crontab(hour=21, minute=0),
    },
}
