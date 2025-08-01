#!/usr/bin/env python3
"""
Celery Background Tasks for Quiz Master V2
"""
from celery import Celery
from celery.schedules import crontab
import smtplib
import csv
import io
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
from datetime import datetime, timedelta
from jinja2 import Template
import os

# Initialize Celery
celery = Celery('quiz_tasks')
celery.config_from_object('celeryconfig')

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_USER = os.getenv('EMAIL_USER', 'your-email@gmail.com')
EMAIL_PASS = os.getenv('EMAIL_PASS', 'your-app-password')

# Google Chat webhook URL
GCHAT_WEBHOOK = os.getenv('GCHAT_WEBHOOK', 'https://chat.googleapis.com/v1/spaces/YOUR_SPACE/messages?key=YOUR_KEY')

@celery.task
def send_daily_reminder():
    """Send daily reminder to inactive users"""
    from app import app, db, User, QuizAttempt, Quiz
    
    with app.app_context():
        # Find users who haven't attempted any quiz in the last 24 hours
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        # Get users who haven't attempted any quiz recently
        recent_attempts = db.session.query(QuizAttempt.user_id).filter(
            QuizAttempt.started_at >= yesterday
        ).distinct().subquery()
        
        inactive_users = User.query.filter(
            User.role == 'user',
            User.is_active == True,
            ~User.id.in_(recent_attempts)
        ).all()
        
        # Get latest active quiz
        latest_quiz = Quiz.query.filter_by(is_active=True).order_by(Quiz.created_at.desc()).first()
        
        if not latest_quiz:
            return "No active quizzes available"
        
        # Send reminders via email and Google Chat
        for user in inactive_users:
            # Email reminder
            send_email_reminder.delay(user.email, user.username, latest_quiz.title, latest_quiz.id)
            
            # Google Chat reminder (if webhook configured)
            if GCHAT_WEBHOOK != 'https://chat.googleapis.com/v1/spaces/YOUR_SPACE/messages?key=YOUR_KEY':
                send_gchat_reminder.delay(user.username, latest_quiz.title)
        
        return f"Sent reminders to {len(inactive_users)} inactive users"

@celery.task
def send_email_reminder(email, username, quiz_title, quiz_id):
    """Send email reminder to user using HTML template"""
    try:
        from app import app
        
        with app.app_context():
            # Load HTML template
            template_path = os.path.join(os.path.dirname(__file__), 'templates', 'daily_reminder.html')
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            template = Template(template_content)
            
            # Get user stats for personalization
            from app import db, User, QuizAttempt
            user = User.query.filter_by(email=email).first()
            total_attempts = 0
            best_score = 0
            
            if user:
                attempts = QuizAttempt.query.filter_by(user_id=user.id).all()
                total_attempts = len(attempts)
                if attempts:
                    best_score = max((attempt.score / attempt.total_questions) * 100 for attempt in attempts)
            
            # Render template with data
            html_content = template.render(
                username=username,
                quiz_title=quiz_title,
                quiz_id=quiz_id,
                total_attempts=total_attempts,
                best_score=round(best_score, 1),
                quiz_url=f"http://localhost:3000/quiz/{quiz_id}"
            )
            
            msg = MIMEMultipart()
            msg['From'] = EMAIL_USER
            msg['To'] = email
            msg['Subject'] = "🎯 Daily Quiz Reminder - Quiz Master V2"
            
            msg.attach(MIMEText(html_content, 'html'))
            
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            text = msg.as_string()
            server.sendmail(EMAIL_USER, email, text)
            server.quit()
            
            return f"HTML email sent to {email}"
    except Exception as e:
        return f"Failed to send email to {email}: {str(e)}"

@celery.task
def send_gchat_reminder(username, quiz_title):
    """Send Google Chat reminder"""
    try:
        message = {
            "text": f"🎓 Reminder: {username}, you haven't attempted any quiz today. "
                   f"A new quiz '{quiz_title}' is now live. Attempt it now!"
        }
        
        response = requests.post(GCHAT_WEBHOOK, json=message)
        return f"Google Chat reminder sent for {username}"
    except Exception as e:
        return f"Failed to send Google Chat reminder: {str(e)}"

@celery.task
def generate_monthly_report():
    """Generate and email monthly performance report"""
    from app import app, db, User, QuizAttempt, Quiz, Chapter, Subject
    
    with app.app_context():
        # Calculate monthly stats
        current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month = (current_month - timedelta(days=1)).replace(day=1)
        
        # Get monthly attempts
        monthly_attempts = QuizAttempt.query.filter(
            QuizAttempt.completed_at >= last_month,
            QuizAttempt.completed_at < current_month
        ).all()
        
        if not monthly_attempts:
            return "No attempts found for last month"
        
        # Calculate statistics
        total_attempts = len(monthly_attempts)
        total_users = len(set(attempt.user_id for attempt in monthly_attempts))
        avg_score = sum(attempt.score for attempt in monthly_attempts) / total_attempts
        avg_percentage = sum((attempt.score / attempt.total_questions) * 100 for attempt in monthly_attempts) / total_attempts
        
        # Subject-wise performance
        subject_stats = {}
        for attempt in monthly_attempts:
            quiz = Quiz.query.get(attempt.quiz_id)
            chapter = Chapter.query.get(quiz.chapter_id)
            subject = Subject.query.get(chapter.subject_id)
            
            if subject.name not in subject_stats:
                subject_stats[subject.name] = {'attempts': 0, 'total_score': 0, 'total_questions': 0}
            
            subject_stats[subject.name]['attempts'] += 1
            subject_stats[subject.name]['total_score'] += attempt.score
            subject_stats[subject.name]['total_questions'] += attempt.total_questions
        
        # Load and render HTML template
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'monthly_report_email.html')
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        html_template = Template(template_content)
        
        # Calculate additional metrics for the template
        avg_attempts_per_user = total_attempts / total_users if total_users > 0 else 0
        
        # Prepare subject performance data with progress bars
        subject_performance = []
        for subject_name, stats in subject_stats.items():
            avg_score_pct = (stats['total_score'] / stats['total_questions']) * 100
            subject_performance.append({
                'name': subject_name,
                'attempts': stats['attempts'],
                'avg_score': round(avg_score_pct, 1),
                'progress_width': min(avg_score_pct, 100)  # Cap at 100% for progress bar
            })
        
        # Sort by average score descending
        subject_performance.sort(key=lambda x: x['avg_score'], reverse=True)
        
        html_content = html_template.render(
            month_year=last_month.strftime("%B %Y"),
            total_attempts=total_attempts,
            total_users=total_users,
            avg_score=round(avg_percentage, 1),
            avg_attempts_per_user=round(avg_attempts_per_user, 1),
            subject_performance=subject_performance,
            generated_date=datetime.utcnow().strftime("%B %d, %Y")
        )
        
        # Email the report to all admins
        admins = User.query.filter_by(role='admin').all()
        for admin in admins:
            send_monthly_report_email.delay(admin.email, html_content, last_month.strftime("%B_%Y"))
        
        return f"Monthly report generated and sent to {len(admins)} admins"

@celery.task
def send_monthly_report_email(email, html_content, month_year):
    """Send monthly report via email"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = email
        msg['Subject'] = f"📊 Quiz Master V2 - Monthly Performance Report ({month_year.replace('_', ' ')})"
        
        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, email, text)
        server.quit()
        
        return f"Monthly report emailed to {email}"
    except Exception as e:
        return f"Failed to email report to {email}: {str(e)}"

@celery.task
def generate_admin_csv():
    """Generate CSV export for admin - user performance data"""
    from app import app, db, User, QuizAttempt, Quiz, Chapter, Subject
    
    with app.app_context():
        try:
            # Create CSV data
            csv_buffer = io.StringIO()
            writer = csv.DictWriter(csv_buffer, fieldnames=[
                'user_id', 'username', 'quizzes_taken', 'average_score', 
                'total_questions_answered', 'total_time_spent_minutes', 'last_activity'
            ])
            writer.writeheader()
            
            # Get all users with their performance data
            users = User.query.filter_by(role='user').all()
            
            for user in users:
                attempts = QuizAttempt.query.filter_by(user_id=user.id).all()
                
                if attempts:
                    total_score = sum(attempt.score for attempt in attempts)
                    total_questions = sum(attempt.total_questions for attempt in attempts)
                    total_time = sum(attempt.time_taken or 0 for attempt in attempts)
                    avg_score = round((total_score / total_questions) * 100, 2) if total_questions > 0 else 0
                    last_attempt = max(attempts, key=lambda x: x.completed_at or datetime.min)
                    
                    writer.writerow({
                        'user_id': user.id,
                        'username': user.username,
                        'quizzes_taken': len(attempts),
                        'average_score': avg_score,
                        'total_questions_answered': total_questions,
                        'total_time_spent_minutes': round(total_time / 60, 2) if total_time else 0,
                        'last_activity': last_attempt.completed_at.strftime('%Y-%m-%d %H:%M:%S') if last_attempt.completed_at else 'N/A'
                    })
                else:
                    writer.writerow({
                        'user_id': user.id,
                        'username': user.username,
                        'quizzes_taken': 0,
                        'average_score': 0,
                        'total_questions_answered': 0,
                        'total_time_spent_minutes': 0,
                        'last_activity': 'Never'
                    })
            
            csv_content = csv_buffer.getvalue()
            csv_buffer.close()
            
            # Save to exports folder
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"admin_user_performance_{timestamp}.csv"
            filepath = os.path.join('exports', filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                f.write(csv_content)
            
            return {
                'status': 'SUCCESS',
                'filename': filename,
                'filepath': filepath,
                'message': 'Admin CSV export completed successfully'
            }
            
        except Exception as e:
            return {
                'status': 'FAILURE',
                'error': str(e),
                'message': 'Failed to generate admin CSV export'
            }

@celery.task
def generate_user_csv(user_id):
    """Generate CSV export for user - quiz history"""
    from app import app, db, User, QuizAttempt, Quiz, Chapter, Subject
    
    with app.app_context():
        try:
            user = User.query.get(user_id)
            if not user:
                return {
                    'status': 'FAILURE',
                    'error': 'User not found',
                    'message': 'User not found'
                }
            
            # Create CSV data
            csv_buffer = io.StringIO()
            writer = csv.DictWriter(csv_buffer, fieldnames=[
                'quiz_id', 'quiz_title', 'subject', 'chapter', 'date_attempted', 
                'score', 'total_questions', 'percentage', 'time_taken_minutes', 'remarks'
            ])
            writer.writeheader()
            
            # Get user's quiz attempts
            attempts = QuizAttempt.query.filter_by(user_id=user_id).order_by(QuizAttempt.completed_at.desc()).all()
            
            for attempt in attempts:
                quiz = Quiz.query.get(attempt.quiz_id)
                chapter = Chapter.query.get(quiz.chapter_id)
                subject = Subject.query.get(chapter.subject_id)
                
                percentage = round((attempt.score / attempt.total_questions) * 100, 2) if attempt.total_questions > 0 else 0
                
                # Generate remarks based on performance
                if percentage >= 90:
                    remarks = "Excellent performance"
                elif percentage >= 80:
                    remarks = "Great performance"
                elif percentage >= 70:
                    remarks = "Good performance"
                elif percentage >= 60:
                    remarks = "Average performance"
                else:
                    remarks = "Needs improvement"
                
                writer.writerow({
                    'quiz_id': quiz.id,
                    'quiz_title': quiz.title,
                    'subject': subject.name,
                    'chapter': chapter.name,
                    'date_attempted': attempt.completed_at.strftime('%Y-%m-%d') if attempt.completed_at else 'In Progress',
                    'score': f"{attempt.score}/{attempt.total_questions}",
                    'total_questions': attempt.total_questions,
                    'percentage': f"{percentage}%",
                    'time_taken_minutes': round(attempt.time_taken / 60, 2) if attempt.time_taken else 0,
                    'remarks': remarks
                })
            
            csv_content = csv_buffer.getvalue()
            csv_buffer.close()
            
            # Save to exports folder
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"user_{user_id}_quiz_history_{timestamp}.csv"
            filepath = os.path.join('exports', filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                f.write(csv_content)
            
            return {
                'status': 'SUCCESS',
                'filename': filename,
                'filepath': filepath,
                'user_id': user_id,
                'username': user.username,
                'message': 'User CSV export completed successfully'
            }
            
        except Exception as e:
            return {
                'status': 'FAILURE',
                'error': str(e),
                'message': 'Failed to generate user CSV export'
            }

@celery.task
def export_quiz_data_csv(user_id, export_type='all'):
    """Legacy export quiz data to CSV (kept for backward compatibility)"""
    from app import app, db, User, QuizAttempt, Quiz, Chapter, Subject
    
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            return "User not found"
        
        # Create CSV data
        csv_buffer = io.StringIO()
        
        if export_type == 'user_attempts' and user.role == 'user':
            # Export user's quiz attempts
            writer = csv.writer(csv_buffer)
            writer.writerow(['Quiz Title', 'Subject', 'Chapter', 'Score', 'Total Questions', 'Percentage', 'Time Taken (min)', 'Attempted Date'])
            
            attempts = QuizAttempt.query.filter_by(user_id=user_id).order_by(QuizAttempt.completed_at.desc()).all()
            
            for attempt in attempts:
                quiz = Quiz.query.get(attempt.quiz_id)
                chapter = Chapter.query.get(quiz.chapter_id)
                subject = Subject.query.get(chapter.subject_id)
                
                writer.writerow([
                    quiz.title,
                    subject.name,
                    chapter.name,
                    attempt.score,
                    attempt.total_questions,
                    round((attempt.score / attempt.total_questions) * 100, 2),
                    round(attempt.time_taken / 60, 2) if attempt.time_taken else 0,
                    attempt.completed_at.strftime('%Y-%m-%d %H:%M:%S') if attempt.completed_at else 'In Progress'
                ])
                
        elif export_type == 'all_attempts' and user.role == 'admin':
            # Export all quiz attempts (admin only)
            writer = csv.writer(csv_buffer)
            writer.writerow(['User', 'Quiz Title', 'Subject', 'Chapter', 'Score', 'Total Questions', 'Percentage', 'Time Taken (min)', 'Attempted Date'])
            
            attempts = QuizAttempt.query.order_by(QuizAttempt.completed_at.desc()).all()
            
            for attempt in attempts:
                attempt_user = User.query.get(attempt.user_id)
                quiz = Quiz.query.get(attempt.quiz_id)
                chapter = Chapter.query.get(quiz.chapter_id)
                subject = Subject.query.get(chapter.subject_id)
                
                writer.writerow([
                    attempt_user.username,
                    quiz.title,
                    subject.name,
                    chapter.name,
                    attempt.score,
                    attempt.total_questions,
                    round((attempt.score / attempt.total_questions) * 100, 2),
                    round(attempt.time_taken / 60, 2) if attempt.time_taken else 0,
                    attempt.completed_at.strftime('%Y-%m-%d %H:%M:%S') if attempt.completed_at else 'In Progress'
                ])
        
        csv_content = csv_buffer.getvalue()
        csv_buffer.close()
        
        # Save CSV file temporarily and email it
        filename = f"quiz_export_{export_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Email the CSV file
        send_csv_export_email.delay(user.email, csv_content, filename, export_type)
        
        return f"CSV export completed and emailed to {user.email}"

@celery.task
def send_csv_export_email(email, csv_content, filename, export_type):
    """Send CSV export via email"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = email
        msg['Subject'] = f"Quiz Master V2 - Data Export ({export_type})"
        
        body = f"""
        Hi,
        
        Your requested data export is ready. Please find the CSV file attached.
        
        Export Type: {export_type}
        Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
        
        Best regards,
        Quiz Master V2 Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach CSV file
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(csv_content.encode())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= {filename}')
        msg.attach(part)
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, email, text)
        server.quit()
        
        return f"CSV export emailed to {email}"
    except Exception as e:
        return f"Failed to email CSV to {email}: {str(e)}"

# Celery Beat Schedule
celery.conf.beat_schedule = {
    'daily-reminder': {
        'task': 'tasks.send_daily_reminder',
        'schedule': crontab(hour=18, minute=0),  # 6 PM daily
    },
    'monthly-report': {
        'task': 'tasks.generate_monthly_report',
        'schedule': crontab(0, 0, day_of_month=1),  # 1st day of month at midnight
    },
}

celery.conf.timezone = 'UTC'