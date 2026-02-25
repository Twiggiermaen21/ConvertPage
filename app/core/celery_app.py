from celery import Celery
from app.core.config import settings

celery = Celery(
    "backend",
    broker=settings.REDIS_BROKER_URL,      
    backend=settings.REDIS_BACKEND_URL,     
)


celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Warsaw",
    enable_utc=True,
    task_track_started=True,                
    result_expires=3600,                    
)

# Celery będzie teraz szukać plików z zadaniami w tych lokalizacjach
celery.autodiscover_tasks([
    "app.services.audio_service",
    "app.services.yt_service",
    "app.services.pdf.merge",
    "app.services.pdf.split",
    "app.services.pdf.compress",
])