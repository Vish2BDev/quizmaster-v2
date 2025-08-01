# Celery Background Jobs Setup Guide

This guide explains how to set up and use Celery background jobs for daily reminders and monthly reports in the Quiz Master application.

## Overview

The application uses Celery with Redis as the message broker to handle background tasks:

- **Daily Reminders**: Automatically send reminders to inactive users
- **Monthly Reports**: Generate and email monthly performance reports
- **CSV Exports**: Handle large data exports asynchronously

## Prerequisites

1. **Redis Server**: Required as the message broker
2. **Email Configuration**: For sending reminders and reports
3. **Google Chat Webhook** (Optional): For chat notifications

## Installation

### 1. Install Redis

**Windows:**
```bash
# Download and install Redis from: https://redis.io/download
# Or use Windows Subsystem for Linux (WSL)
```

**Linux/macOS:**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS with Homebrew
brew install redis
```

### 2. Install Python Dependencies

```bash
pip install celery redis
```

### 3. Environment Configuration

Create a `.env` file or set environment variables:

```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/1
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email Configuration
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Google Chat (Optional)
GCHAT_WEBHOOK=https://chat.googleapis.com/v1/spaces/YOUR_SPACE/messages?key=YOUR_KEY
```

## Running the Services

### 1. Start Redis Server

```bash
# Start Redis server
redis-server

# Verify Redis is running
redis-cli ping
# Should return: PONG
```

### 2. Start Flask Application

```bash
python app.py
```

### 3. Start Celery Worker

```bash
# In a new terminal
python run_celery.py
```

### 4. Start Celery Beat Scheduler

```bash
# In another new terminal
python run_celery_beat.py
```

## Testing the Setup

### 1. Run Celery Tests

```bash
python test_celery.py
```

This will test:
- Celery broker connection
- Task registration
- Async task execution

### 2. Manual Task Triggers

Use the admin API endpoints to manually trigger tasks:

```bash
# Trigger daily reminder
curl -X POST http://localhost:5000/api/admin/trigger-daily-reminder \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Trigger monthly report
curl -X POST http://localhost:5000/api/admin/trigger-monthly-report \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Check task status
curl http://localhost:5000/api/admin/task-status/TASK_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## API Endpoints

### Task Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/admin/trigger-daily-reminder` | POST | Manually trigger daily reminder |
| `/api/admin/trigger-monthly-report` | POST | Manually trigger monthly report |
| `/api/admin/task-status/<task_id>` | GET | Check task status |
| `/api/admin/test-daily-reminder` | POST | Test daily reminder (legacy) |
| `/api/admin/test-monthly-report` | POST | Test monthly report (legacy) |

### CSV Export

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/user/export-csv` | POST | Trigger user CSV export |
| `/api/admin/export-csv` | POST | Trigger admin CSV export |
| `/api/user/export-status/<task_id>` | GET | Check export status |

## Scheduled Tasks

### Daily Reminders
- **Schedule**: Every day at 6:00 PM UTC
- **Function**: Sends reminders to users who haven't taken a quiz in 24 hours
- **Delivery**: Email and Google Chat (if configured)

### Monthly Reports
- **Schedule**: 1st day of every month at midnight UTC
- **Function**: Generates performance reports for the previous month
- **Delivery**: Email to all admin users

## Task Configuration

Tasks are configured in `celeryconfig.py`:

```python
# Task routing
task_routes = {
    'tasks.send_daily_reminder': {'queue': 'reminders'},
    'tasks.generate_monthly_report': {'queue': 'reports'},
    'tasks.export_quiz_data_csv': {'queue': 'exports'},
}

# Beat schedule
beat_schedule = {
    'daily-reminder': {
        'task': 'tasks.send_daily_reminder',
        'schedule': crontab(hour=18, minute=0),
    },
    'monthly-report': {
        'task': 'tasks.generate_monthly_report',
        'schedule': crontab(0, 0, day_of_month=1),
    },
}
```

## Monitoring

### Celery Flower (Optional)

Install and run Flower for web-based monitoring:

```bash
pip install flower
celery -A tasks flower
```

Access the web interface at: http://localhost:5555

### Log Files

Check log files for debugging:
- Celery Worker: `logs/celery_worker.log`
- Celery Beat: `logs/celery_beat.log`
- Flask App: Application logs

## Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   - Ensure Redis server is running
   - Check Redis URL configuration
   - Verify firewall settings

2. **Tasks Not Executing**
   - Ensure Celery worker is running
   - Check task registration
   - Verify queue configuration

3. **Email Not Sending**
   - Check email credentials
   - Verify SMTP settings
   - Enable "Less secure app access" for Gmail

4. **Beat Schedule Not Working**
   - Ensure Celery Beat is running
   - Check timezone configuration
   - Verify crontab syntax

### Debug Commands

```bash
# Check Celery worker status
celery -A tasks inspect active

# List registered tasks
celery -A tasks inspect registered

# Check Redis connection
redis-cli ping

# Monitor Redis keys
redis-cli monitor
```

## Production Deployment

For production deployment, use process managers like Supervisor:

```ini
# /etc/supervisor/conf.d/quizmaster-celery.conf
[program:quizmaster-celery-worker]
command=/path/to/venv/bin/python /path/to/app/run_celery.py
directory=/path/to/app
user=www-data
autostart=true
autorestart=true
stdout_logfile=/var/log/celery/worker.log
stderr_logfile=/var/log/celery/worker.log

[program:quizmaster-celery-beat]
command=/path/to/venv/bin/python /path/to/app/run_celery_beat.py
directory=/path/to/app
user=www-data
autostart=true
autorestart=true
stdout_logfile=/var/log/celery/beat.log
stderr_logfile=/var/log/celery/beat.log
```

## Security Considerations

1. **Redis Security**
   - Use Redis AUTH if exposed to network
   - Configure firewall rules
   - Use SSL/TLS for production

2. **Email Security**
   - Use app-specific passwords
   - Store credentials securely
   - Enable 2FA on email accounts

3. **Task Security**
   - Validate task parameters
   - Implement rate limiting
   - Monitor task execution

## Performance Optimization

1. **Worker Scaling**
   ```bash
   # Run multiple workers
   celery -A tasks worker --concurrency=4
   ```

2. **Queue Separation**
   ```bash
   # Dedicated workers for different queues
   celery -A tasks worker -Q reminders
   celery -A tasks worker -Q reports
   celery -A tasks worker -Q exports
   ```

3. **Result Backend Optimization**
   - Set result expiration
   - Use appropriate serialization
   - Monitor memory usage

For more information, refer to the [Celery documentation](https://docs.celeryproject.org/).