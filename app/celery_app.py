from celery import Celery
from app.telegram_bot import send_notification
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

celery = Celery(
    'app',
    broker='redis://redis_cache:6379/0',
    backend='redis://redis_cache:6379/0'
)

celery.conf.update(
    result_expires=3600,
)


@celery.task
def send_telegram_notification(user_id: int, message: str):
    import asyncio
    asyncio.run(send_notification(user_id, message))
