import os


class Config:
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    CELERY_RESULT_BACKEND = os.getenv(
        "CELERY_RESULT_BACKEND",
        "redis://redis:6379/0",
    )
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://encar_user:encar_password@postgres:5432/encar_db",
    )
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))
    REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "0.03"))


config = Config()
