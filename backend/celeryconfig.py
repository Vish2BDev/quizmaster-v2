#!/usr/bin/env python3
"""
Celery Configuration for Quiz Master V2
"""
import os

# Broker settings
broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Task settings
task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
timezone = 'UTC'
enable_utc = True

# Task routing
task_routes = {
    'tasks.send_daily_reminder': {'queue': 'reminders'},
    'tasks.generate_monthly_report': {'queue': 'reports'},
    'tasks.export_quiz_data_csv': {'queue': 'exports'},
}

# Worker settings
worker_prefetch_multiplier = 1
task_acks_late = True

# Beat settings
beat_scheduler = 'celery.beat:PersistentScheduler' 