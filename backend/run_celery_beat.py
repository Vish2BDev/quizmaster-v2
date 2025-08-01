#!/usr/bin/env python3
"""
Celery Beat Scheduler Startup Script
Run this in a separate terminal: python run_celery_beat.py
"""
import os
from celery import Celery
from app import app

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config.get('result_backend') or os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0',
        broker=app.config.get('broker_url') or os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
    )
    celery.conf.update(app.config)
    return celery

if __name__ == '__main__':
    celery_app = make_celery(app)
    celery_app.start(['celery', 'beat', '--loglevel=info'])