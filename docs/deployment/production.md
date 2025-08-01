# Production Deployment Guide

## Prerequisites

- Ubuntu 20.04+ or CentOS 8+
- Python 3.8+
- Node.js 16+
- Redis Server
- Nginx
- SSL Certificate (Let's Encrypt recommended)

## Server Setup

### 1. Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Dependencies
```bash
# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Redis
sudo apt install redis-server -y
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Install Nginx
sudo apt install nginx -y
sudo systemctl enable nginx
sudo systemctl start nginx
```

### 3. Create Application User
```bash
sudo adduser quizmaster
sudo usermod -aG sudo quizmaster
```

## Application Deployment

### 1. Clone Repository
```bash
cd /home/quizmaster
git clone <repository-url> quiz-master-v2
cd quiz-master-v2
```

### 2. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create production environment file
cp .env.example .env
# Edit .env with production values
nano .env
```

### 3. Frontend Build
```bash
cd ../frontend
npm install
npm run build
```

### 4. Database Setup
```bash
cd ../backend
source venv/bin/activate
python app.py
# This will create the database and tables
```

## Process Management

### 1. Install Supervisor
```bash
sudo apt install supervisor -y
```

### 2. Configure Flask Application
```bash
sudo nano /etc/supervisor/conf.d/quizmaster-flask.conf
```

Add the following configuration:
```ini
[program:quizmaster-flask]
command=/home/quizmaster/quiz-master-v2/backend/venv/bin/python app.py
directory=/home/quizmaster/quiz-master-v2/backend
user=quizmaster
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/quizmaster/flask.log
```

### 3. Configure Celery Worker
```bash
sudo nano /etc/supervisor/conf.d/quizmaster-celery.conf
```

Add the following configuration:
```ini
[program:quizmaster-celery]
command=/home/quizmaster/quiz-master-v2/backend/venv/bin/python run_celery.py
directory=/home/quizmaster/quiz-master-v2/backend
user=quizmaster
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/quizmaster/celery.log
```

### 4. Configure Celery Beat
```bash
sudo nano /etc/supervisor/conf.d/quizmaster-celerybeat.conf
```

Add the following configuration:
```ini
[program:quizmaster-celerybeat]
command=/home/quizmaster/quiz-master-v2/backend/venv/bin/python run_celery_beat.py
directory=/home/quizmaster/quiz-master-v2/backend
user=quizmaster
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/quizmaster/celerybeat.log
```

### 5. Create Log Directory
```bash
sudo mkdir -p /var/log/quizmaster
sudo chown quizmaster:quizmaster /var/log/quizmaster
```

### 6. Start Services
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

## Nginx Configuration

### 1. Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/quizmaster
```

Add the following configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend static files
    location / {
        root /home/quizmaster/quiz-master-v2/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:5000;
    }
}
```

### 2. Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/quizmaster /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## SSL Configuration

### 1. Install Certbot
```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Obtain SSL Certificate
```bash
sudo certbot --nginx -d your-domain.com
```

### 3. Auto-renewal
```bash
sudo crontab -e
# Add the following line:
0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring and Maintenance

### 1. Log Monitoring
```bash
# View application logs
sudo tail -f /var/log/quizmaster/flask.log
sudo tail -f /var/log/quizmaster/celery.log

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 2. Database Backups
```bash
# Create backup script
sudo nano /home/quizmaster/backup.sh
```

Add the following content:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/quizmaster/backups"
mkdir -p $BACKUP_DIR
cp /home/quizmaster/quiz-master-v2/backend/quiz_master.db $BACKUP_DIR/quiz_master_$DATE.db
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
```

### 3. Set up Cron Job for Backups
```bash
crontab -e
# Add the following line for daily backups at 2 AM:
0 2 * * * /home/quizmaster/backup.sh
```

## Security Considerations

### 1. Firewall Configuration
```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 2. Regular Updates
```bash
# Set up automatic security updates
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 3. Environment Variables
Ensure all sensitive information is stored in environment variables and not in the codebase.

## Troubleshooting

### Common Issues

1. **Celery not starting**: Check Redis connection and permissions
2. **Nginx 502 errors**: Verify Flask app is running on port 5000
3. **Database errors**: Check file permissions and disk space
4. **SSL issues**: Verify domain DNS and certificate renewal

### Useful Commands
```bash
# Check service status
sudo supervisorctl status

# Restart services
sudo supervisorctl restart quizmaster-flask
sudo supervisorctl restart quizmaster-celery

# Check Nginx configuration
sudo nginx -t

# View real-time logs
sudo journalctl -u nginx -f
``` 