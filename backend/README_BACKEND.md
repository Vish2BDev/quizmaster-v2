# Quiz Master V2 - Backend Setup

## Quick Start
1. Install Python 3.8+
2. Install Redis: `brew install redis` (Mac) or `sudo apt install redis` (Ubuntu)
3. Create virtual environment: `python -m venv venv`
4. Activate: `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows)
5. Install dependencies: `pip install -r requirements.txt`
6. Start Redis: `redis-server`
7. Run Flask: `python app.py`
8. Run Celery Worker (new terminal): `python run_celery.py`
9. Run Celery Beat (new terminal): `python run_celery_beat.py`

## Default Admin Account
- Username: admin
- Password: admin123

## API Endpoints
- Backend runs on: http://localhost:5000
- Admin Dashboard: http://localhost:5000/api/admin/analytics/overview
- User API: http://localhost:5000/api/user/available-quizzes 