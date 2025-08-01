#!/usr/bin/env python3
"""
Quiz Master V2 - Main Flask Application
"""
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from celery import Celery
import redis
import json
import time

# Import search blueprints
from routes.admin_search import admin_search_bp
from routes.user_search import user_search_bp
from routes.export import export_bp

# Initialize Flask app
app = Flask(__name__)

# Load configuration from config.py
from config import config as app_config
app.config.from_object(app_config['development'])

# Add JWT algorithm setting (not in config.py)
app.config['JWT_ALGORITHM'] = 'HS256'

# Initialize Redis connection
redis_client = redis.Redis.from_url(app.config['CACHE_REDIS_URL'])

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
cors = CORS(app)
cache = Cache(app)

# Initialize rate limiter with Redis storage
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=app.config['CACHE_REDIS_URL'],
    default_limits=["1000 per hour"]
)
limiter.init_app(app)

# Cache invalidation helper functions
def invalidate_quiz_caches():
    """Invalidate caches related to quiz data"""
    cache.delete_memoized(get_available_quizzes)
    cache.delete_memoized(get_leaderboard)
    cache.delete_memoized(admin_analytics_overview)
    cache.delete_memoized(get_community_stats)

def invalidate_subject_caches():
    """Invalidate caches related to subject data"""
    cache.delete_memoized(get_available_quizzes)

# Register search blueprints
app.register_blueprint(admin_search_bp)
app.register_blueprint(user_search_bp)

# Register export blueprint
app.register_blueprint(export_bp)

# Initialize Celery
celery = Celery(app.name)
celery.conf.update(app.config)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='user')  # 'admin' or 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade='all, delete-orphan')

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True, cascade='all, delete-orphan')

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    duration = db.Column(db.Integer, default=30)  # in minutes (legacy field)
    duration_minutes = db.Column(db.Integer, default=30)  # new field for scheduling
    start_time = db.Column(db.DateTime)  # when quiz becomes available
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete-orphan')
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True)
    
    def is_quiz_active(self):
        """Check if quiz is currently active based on schedule"""
        if not self.is_active or not self.start_time:
            return False
        
        now = datetime.utcnow()
        end_time = self.start_time + timedelta(minutes=self.duration_minutes)
        
        return self.start_time <= now <= end_time
    
    def get_quiz_status(self):
        """Get current status of the quiz"""
        if not self.is_active:
            return 'inactive'
        
        if not self.start_time:
            return 'active'  # No schedule set, always active
        
        now = datetime.utcnow()
        end_time = self.start_time + timedelta(minutes=self.duration_minutes)
        
        if now < self.start_time:
            return 'upcoming'
        elif now <= end_time:
            return 'active'
        else:
            return 'expired'
    
    def get_remaining_time(self):
        """Get remaining time in seconds for active quiz"""
        if not self.start_time:
            return None
        
        now = datetime.utcnow()
        end_time = self.start_time + timedelta(minutes=self.duration_minutes)
        
        if now > end_time:
            return 0
        
        return int((end_time - now).total_seconds())

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(500), nullable=False)
    option_b = db.Column(db.String(500), nullable=False)
    option_c = db.Column(db.String(500), nullable=False)
    option_d = db.Column(db.String(500), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)  # 'a', 'b', 'c', or 'd'
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    time_taken = db.Column(db.Integer)  # in seconds
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    answers = db.Column(db.JSON)  # Store user answers as JSON

# Authentication Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        role=data.get('role', 'user')
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    
    if user and check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'role': user.role}
        )
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    # With JWT, we can't invalidate tokens server-side easily
    # The client should remove the token from storage
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if user:
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        })
    return jsonify({'error': 'User not found'}), 404

# Admin Routes - Subject Management
@app.route('/api/admin/subjects', methods=['GET'])
@jwt_required()
def get_subjects():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    subjects = Subject.query.all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'description': s.description,
        'chapters_count': len(s.chapters),
        'created_at': s.created_at.isoformat()
    } for s in subjects])

@app.route('/api/admin/subjects', methods=['POST'])
@jwt_required()
def create_subject():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    subject = Subject(
        name=data['name'],
        description=data.get('description', '')
    )
    db.session.add(subject)
    db.session.commit()
    
    # Invalidate subject-related caches
    invalidate_subject_caches()
    
    return jsonify({'message': 'Subject created successfully', 'id': subject.id}), 201

# Chapter Management
@app.route('/api/admin/subjects/<int:subject_id>/chapters', methods=['GET'])
@jwt_required()
def get_chapters(subject_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'description': c.description,
        'quizzes_count': len(c.quizzes),
        'created_at': c.created_at.isoformat()
    } for c in chapters])

@app.route('/api/admin/subjects/<int:subject_id>/chapters', methods=['POST'])
@jwt_required()
def create_chapter(subject_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    chapter = Chapter(
        name=data['name'],
        description=data.get('description', ''),
        subject_id=subject_id
    )
    db.session.add(chapter)
    db.session.commit()
    return jsonify({'message': 'Chapter created successfully', 'id': chapter.id}), 201

# Get all chapters (for admin)
@app.route('/api/admin/chapters', methods=['GET'])
@jwt_required()
@cache.cached(timeout=600)  # Cache for 10 minutes
def get_all_chapters():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    chapters = Chapter.query.join(Subject).all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'description': c.description,
        'subject_id': c.subject_id,
        'subject_name': c.subject.name,
        'quizzes_count': len(c.quizzes),
        'created_at': c.created_at.isoformat()
    } for c in chapters])

# Quiz Management
@app.route('/api/admin/chapters/<int:chapter_id>/quizzes', methods=['GET'])
@jwt_required()
def get_quizzes(chapter_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    return jsonify([{
        'id': q.id,
        'title': q.title,
        'description': q.description,
        'duration': q.duration,
        'duration_minutes': q.duration_minutes,
        'start_time': q.start_time.isoformat() if q.start_time else None,
        'questions_count': len(q.questions),
        'attempts_count': len(q.attempts),
        'is_active': q.is_active,
        'status': q.get_quiz_status(),
        'created_at': q.created_at.isoformat()
    } for q in quizzes])

@app.route('/api/admin/chapters/<int:chapter_id>/quizzes', methods=['POST'])
@jwt_required()
def create_quiz(chapter_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    # Parse start_time if provided
    start_time = None
    if data.get('start_time'):
        try:
            start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid start_time format. Use ISO format.'}), 400
    
    quiz = Quiz(
        title=data['title'],
        description=data.get('description', ''),
        duration=data.get('duration', 30),  # legacy field
        duration_minutes=data.get('duration_minutes', data.get('duration', 30)),
        start_time=start_time,
        chapter_id=chapter_id
    )
    db.session.add(quiz)
    db.session.commit()
    invalidate_quiz_caches()
    return jsonify({'message': 'Quiz created successfully', 'id': quiz.id}), 201

# Question Management
@app.route('/api/admin/quizzes/<int:quiz_id>/questions', methods=['GET'])
@jwt_required()
def get_questions(quiz_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return jsonify([{
        'id': q.id,
        'text': q.text,
        'option_a': q.option_a,
        'option_b': q.option_b,
        'option_c': q.option_c,
        'option_d': q.option_d,
        'correct_option': q.correct_option,
        'created_at': q.created_at.isoformat()
    } for q in questions])

@app.route('/api/admin/quizzes/<int:quiz_id>/questions', methods=['POST'])
@jwt_required()
def create_question(quiz_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    question = Question(
        text=data['text'],
        option_a=data['option_a'],
        option_b=data['option_b'],
        option_c=data['option_c'],
        option_d=data['option_d'],
        correct_option=data['correct_option'],
        quiz_id=quiz_id
    )
    db.session.add(question)
    db.session.commit()
    return jsonify({'message': 'Question created successfully', 'id': question.id}), 201

# User Routes - Quiz Taking
@app.route('/api/user/available-quizzes', methods=['GET'])
@app.route('/api/quizzes/available', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300)
def get_available_quizzes():
    quizzes = db.session.query(Quiz, Chapter, Subject).join(Chapter, Quiz.chapter_id == Chapter.id).join(Subject, Chapter.subject_id == Subject.id).filter(Quiz.is_active == True).all()
    # Filter out quizzes with no questions
    available_quizzes = [{
        'id': quiz.id,
        'title': quiz.title,
        'description': quiz.description,
        'duration': quiz.duration,
        'duration_minutes': quiz.duration_minutes,
        'start_time': quiz.start_time.isoformat() if quiz.start_time else None,
        'questions_count': len(quiz.questions),
        'chapter': chapter.name,
        'subject': subject.name,
        'status': quiz.get_quiz_status(),
        'is_quiz_active': quiz.is_quiz_active(),
        'remaining_time': quiz.get_remaining_time()
    } for quiz, chapter, subject in quizzes if len(quiz.questions) > 0]
    
    return jsonify(available_quizzes)

@app.route('/api/user/quiz/<int:quiz_id>/start', methods=['POST'])
@jwt_required()
def start_quiz(quiz_id):
    user_id = int(get_jwt_identity())
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check if quiz is active
    if not quiz.is_active:
        return jsonify({'error': 'Quiz is not active'}), 400
    
    # Check if quiz is within scheduled time
    if not quiz.is_quiz_active():
        status = quiz.get_quiz_status()
        if status == 'upcoming':
            return jsonify({
                'error': 'Quiz has not started yet',
                'status': status,
                'start_time': quiz.start_time.isoformat() if quiz.start_time else None
            }), 400
        elif status == 'expired':
            return jsonify({
                'error': 'Quiz has expired',
                'status': status
            }), 400
    
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    # Validate that quiz has questions
    if len(questions) == 0:
        return jsonify({'error': 'This quiz has no questions available. Please contact an administrator.'}), 400
    
    # Check if user has already attempted this quiz
    existing_attempt = QuizAttempt.query.filter_by(
        user_id=user_id, 
        quiz_id=quiz_id,
        completed_at=None
    ).first()
    
    if existing_attempt:
        return jsonify({'error': 'You have an incomplete attempt for this quiz'}), 400
    
    # Create quiz attempt record
    attempt = QuizAttempt(
        user_id=user_id,
        quiz_id=quiz_id,
        score=0,
        total_questions=len(questions),
        started_at=datetime.utcnow()
    )
    db.session.add(attempt)
    db.session.commit()
    
    # Return questions without correct answers
    return jsonify({
        'attempt_id': attempt.id,
        'quiz': {
            'id': quiz.id,
            'title': quiz.title,
            'duration': quiz.duration,
            'duration_minutes': quiz.duration_minutes,
            'start_time': quiz.start_time.isoformat() if quiz.start_time else None,
            'status': quiz.get_quiz_status(),
            'remaining_time': quiz.get_remaining_time()
        },
        'questions': [{
            'id': q.id,
            'text': q.text,
            'option_a': q.option_a,
            'option_b': q.option_b,
            'option_c': q.option_c,
            'option_d': q.option_d
        } for q in questions]
    })

# New endpoints for quiz scheduling
@app.route('/api/quiz/<int:quiz_id>/status', methods=['GET'])
@jwt_required()
def get_quiz_status(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    return jsonify({
        'id': quiz.id,
        'title': quiz.title,
        'status': quiz.get_quiz_status(),
        'is_active': quiz.is_quiz_active(),
        'start_time': quiz.start_time.isoformat() if quiz.start_time else None,
        'duration_minutes': quiz.duration_minutes,
        'remaining_time': quiz.get_remaining_time()
    })

@app.route('/api/quiz/<int:quiz_id>/is_active', methods=['GET'])
@jwt_required()
def check_quiz_active(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    return jsonify({
        'is_active': quiz.is_quiz_active(),
        'status': quiz.get_quiz_status()
    })

@app.route('/api/user/quiz/submit', methods=['POST'])
@jwt_required()
@limiter.limit("2 per minute")
def submit_quiz():
    data = request.get_json()
    attempt_id = data['attempt_id']
    answers = data['answers']  # {question_id: selected_option}
    
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    attempt.completed_at = datetime.utcnow()
    attempt.time_taken = (attempt.completed_at - attempt.started_at).total_seconds()
    attempt.answers = answers
    
    # Calculate score
    questions = Question.query.filter_by(quiz_id=attempt.quiz_id).all()
    score = 0
    for question in questions:
        if str(question.id) in answers and answers[str(question.id)] == question.correct_option:
            score += 1
    
    attempt.score = score
    db.session.commit()
    
    return jsonify({
        'score': score,
        'total_questions': attempt.total_questions,
        'percentage': round((score / attempt.total_questions) * 100, 2),
        'time_taken': attempt.time_taken
    })

# Analytics Routes
@app.route('/api/analytics/user-performance', methods=['GET'])
@app.route('/api/user/performance', methods=['GET'])
@jwt_required()
def get_user_performance():
    user_id = int(get_jwt_identity())
    attempts = QuizAttempt.query.filter_by(user_id=user_id).all()
    
    # Subject-wise performance
    subject_performance = {}
    for attempt in attempts:
        quiz = Quiz.query.get(attempt.quiz_id)
        chapter = Chapter.query.get(quiz.chapter_id)
        subject = Subject.query.get(chapter.subject_id)
        
        if subject.name not in subject_performance:
            subject_performance[subject.name] = {'total_score': 0, 'total_attempts': 0, 'total_questions': 0}
        
        subject_performance[subject.name]['total_score'] += attempt.score
        subject_performance[subject.name]['total_attempts'] += 1
        subject_performance[subject.name]['total_questions'] += attempt.total_questions
    
    return jsonify({
        'total_attempts': len(attempts),
        'subject_performance': subject_performance,
        'recent_attempts': [{
            'quiz_title': Quiz.query.get(a.quiz_id).title,
            'score': a.score,
            'total_questions': a.total_questions,
            'percentage': round((a.score / a.total_questions) * 100, 2),
            'completed_at': a.completed_at.isoformat() if a.completed_at else None
        } for a in attempts[-10:]]
    })

# Additional Admin Routes
@app.route('/api/admin/analytics/overview', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300)  # Cache for 5 minutes
def admin_analytics_overview():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    # Calculate date ranges
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    
    # 1. OVERALL METRICS (Summary Cards)
    total_users = User.query.filter_by(role='user').count()
    total_quizzes = Quiz.query.count()
    total_subjects = Subject.query.count()
    total_chapters = Chapter.query.count()
    total_questions = Question.query.count()
    total_attempts = QuizAttempt.query.count()
    
    # 2. USER ANALYTICS
    # Top 5 users by number of attempts
    top_users_by_attempts = db.session.query(
        User.username,
        db.func.count(QuizAttempt.id).label('attempt_count')
    ).join(QuizAttempt).group_by(User.id).order_by(db.desc('attempt_count')).limit(5).all()

    # Top 5 users by average score
    top_users_by_score = db.session.query(
        User.username,
        db.func.avg(QuizAttempt.score * 100.0 / QuizAttempt.total_questions).label('avg_score')
    ).join(QuizAttempt).group_by(User.id).order_by(db.desc('avg_score')).limit(5).all()
    
    # Active users this week
    active_users_week = db.session.query(User).join(QuizAttempt, User.id == QuizAttempt.user_id).filter(
        QuizAttempt.completed_at >= week_ago
    ).distinct().count()
    
    # Inactive users (0 attempts)
    inactive_users = User.query.filter_by(role='user').filter(
        ~User.id.in_(db.session.query(QuizAttempt.user_id).distinct())
    ).count()
    
    # 3. SUBJECT-WISE ANALYTICS
    subject_quiz_distribution = db.session.query(
        Subject.name,
        db.func.count(Quiz.id).label('quiz_count')
    ).join(Chapter, Subject.id == Chapter.subject_id).join(Quiz, Chapter.id == Quiz.chapter_id).group_by(Subject.id).all()

    # Average score per subject
    subject_avg_scores = db.session.query(
        Subject.name,
        db.func.avg(QuizAttempt.score * 100.0 / QuizAttempt.total_questions).label('avg_score')
    ).join(Chapter, Subject.id == Chapter.subject_id).join(Quiz, Chapter.id == Quiz.chapter_id).join(QuizAttempt, Quiz.id == QuizAttempt.quiz_id).group_by(Subject.id).all()

    # Most attempted subject
    most_attempted_subject = db.session.query(
        Subject.name,
        db.func.count(QuizAttempt.id).label('attempt_count')
    ).join(Chapter, Subject.id == Chapter.subject_id).join(Quiz, Chapter.id == Quiz.chapter_id).join(QuizAttempt, Quiz.id == QuizAttempt.quiz_id).group_by(Subject.id).order_by(db.desc('attempt_count')).first()
    
    # 4. QUIZ-WISE ANALYTICS
    quiz_attempt_counts = db.session.query(
        Quiz.title,
        db.func.count(QuizAttempt.id).label('attempt_count')
    ).join(QuizAttempt).group_by(Quiz.id).order_by(db.desc('attempt_count')).limit(10).all()

    quiz_avg_scores = db.session.query(
        Quiz.title,
        db.func.avg(QuizAttempt.score * 100.0 / QuizAttempt.total_questions).label('avg_score')
    ).join(QuizAttempt).group_by(Quiz.id).order_by(db.desc('avg_score')).limit(10).all()
    
    # 5. REAL-TIME/RECENT EVENTS
    recent_attempts = db.session.query(QuizAttempt).join(User, QuizAttempt.user_id == User.id).join(Quiz, QuizAttempt.quiz_id == Quiz.id).join(Chapter, Quiz.chapter_id == Chapter.id).join(Subject, Chapter.subject_id == Subject.id).filter(
        QuizAttempt.completed_at.isnot(None)
    ).order_by(QuizAttempt.completed_at.desc()).limit(10).all()
    
    recent_quizzes = Quiz.query.filter(Quiz.created_at >= week_ago).order_by(Quiz.created_at.desc()).limit(5).all()
    
    new_users_week = User.query.filter(
        User.created_at >= week_ago,
        User.role == 'user'
    ).order_by(User.created_at.desc()).limit(5).all()
    
    # 6. TIME-BASED ANALYTICS
    # Quiz attempts over time (last 30 days)
    thirty_days_ago = now - timedelta(days=30)
    daily_attempts = db.session.query(
        db.func.date(QuizAttempt.completed_at).label('date'),
        db.func.count(QuizAttempt.id).label('count')
    ).filter(
        QuizAttempt.completed_at >= thirty_days_ago,
        QuizAttempt.completed_at.isnot(None)
    ).group_by(db.func.date(QuizAttempt.completed_at)).order_by('date').all()
    
    return jsonify({
        'summary': {
            'total_users': total_users,
            'total_quizzes': total_quizzes,
            'total_subjects': total_subjects,
            'total_chapters': total_chapters,
            'total_questions': total_questions,
            'total_attempts': total_attempts
        },
        'user_stats': {
            'top_users_by_attempts': [{
                'username': u.username,
                'attempt_count': u.attempt_count
            } for u in top_users_by_attempts],
            'top_users_by_score': [{
                'username': u.username,
                'avg_score': round(float(u.avg_score), 2) if u.avg_score else 0
            } for u in top_users_by_score],
            'active_users_week': active_users_week,
            'inactive_users': inactive_users
        },
        'subject_stats': {
            'quiz_distribution': [{
                'subject': s.name,
                'quiz_count': s.quiz_count
            } for s in subject_quiz_distribution],
            'avg_scores': [{
                'subject': s.name,
                'avg_score': round(float(s.avg_score), 2) if s.avg_score else 0
            } for s in subject_avg_scores],
            'most_attempted': {
                'subject': most_attempted_subject.name if most_attempted_subject else 'N/A',
                'attempt_count': most_attempted_subject.attempt_count if most_attempted_subject else 0
            }
        },
        'quiz_stats': {
            'attempt_counts': [{
                'quiz': q.title,
                'attempt_count': q.attempt_count
            } for q in quiz_attempt_counts],
            'avg_scores': [{
                'quiz': q.title,
                'avg_score': round(float(q.avg_score), 2) if q.avg_score else 0
            } for q in quiz_avg_scores]
        },
        'recent_activity': {
            'recent_attempts': [{
                'user': a.user.username,
                'quiz': a.quiz.title,
                'subject': a.quiz.chapter.subject.name,
                'score': a.score,
                'total_questions': a.total_questions,
                'percentage': round((a.score / a.total_questions) * 100, 1) if a.total_questions > 0 else 0,
                'completed_at': a.completed_at.isoformat() if a.completed_at else None
            } for a in recent_attempts],
            'new_quizzes_week': [{
                'title': q.title,
                'subject': q.chapter.subject.name,
                'created_at': q.created_at.isoformat()
            } for q in recent_quizzes],
            'new_users_week': [{
                'username': u.username,
                'email': u.email,
                'created_at': u.created_at.isoformat()
            } for u in new_users_week]
        },
        'time_analytics': {
            'daily_attempts': [{
                'date': str(d.date),
                'count': d.count
            } for d in daily_attempts]
        }
    })

# CSV Generation Functions
def generate_csv_export(export_type='all_attempts'):
    """Generate CSV content for export"""
    import csv
    import io
    
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    
    if export_type == 'all_attempts':
        # Export all quiz attempts (admin only)
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
    return csv_content

def generate_user_csv_export(user_id):
    """Generate CSV content for user's quiz attempts"""
    import csv
    import io
    
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    
    # Export user's quiz attempts
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
    
    csv_content = csv_buffer.getvalue()
    csv_buffer.close()
    return csv_content

def generate_analytics_csv_export():
    """Generate CSV content for analytics data"""
    import csv
    import io
    
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    
    # Analytics summary data
    writer.writerow(['Metric', 'Value', 'Description'])
    
    # Overall statistics
    total_users = User.query.filter_by(role='user').count()
    total_quizzes = Quiz.query.count()
    total_subjects = Subject.query.count()
    total_chapters = Chapter.query.count()
    total_questions = Question.query.count()
    total_attempts = QuizAttempt.query.count()
    
    writer.writerow(['Total Users', total_users, 'Number of registered users'])
    writer.writerow(['Total Quizzes', total_quizzes, 'Number of available quizzes'])
    writer.writerow(['Total Subjects', total_subjects, 'Number of subjects'])
    writer.writerow(['Total Chapters', total_chapters, 'Number of chapters'])
    writer.writerow(['Total Questions', total_questions, 'Number of questions'])
    writer.writerow(['Total Attempts', total_attempts, 'Number of quiz attempts'])
    
    # Calculate average scores
    if total_attempts > 0:
        avg_score = db.session.query(db.func.avg(QuizAttempt.score * 100.0 / QuizAttempt.total_questions)).scalar()
        writer.writerow(['Average Score %', round(avg_score, 2), 'Average percentage score across all attempts'])
    
    # Add empty row for separation
    writer.writerow([])
    
    # Subject-wise performance
    writer.writerow(['Subject Performance Analysis'])
    writer.writerow(['Subject', 'Total Attempts', 'Average Score %', 'Total Questions'])
    
    subjects = Subject.query.all()
    for subject in subjects:
        subject_attempts = db.session.query(QuizAttempt).join(Quiz, QuizAttempt.quiz_id == Quiz.id).join(Chapter, Quiz.chapter_id == Chapter.id).filter(Chapter.subject_id == subject.id).all()
        
        if subject_attempts:
            total_subject_attempts = len(subject_attempts)
            avg_subject_score = sum((attempt.score / attempt.total_questions) * 100 for attempt in subject_attempts) / total_subject_attempts
            total_subject_questions = sum(attempt.total_questions for attempt in subject_attempts)
            
            writer.writerow([
                subject.name,
                total_subject_attempts,
                round(avg_subject_score, 2),
                total_subject_questions
            ])
    
    # Add empty row for separation
    writer.writerow([])
    
    # Top performing users
    writer.writerow(['Top Performing Users'])
    writer.writerow(['Username', 'Total Attempts', 'Average Score %', 'Best Score %'])
    
    top_users = db.session.query(
        User.username,
        db.func.count(QuizAttempt.id).label('attempt_count'),
        db.func.avg(QuizAttempt.score * 100.0 / QuizAttempt.total_questions).label('avg_score'),
        db.func.max(QuizAttempt.score * 100.0 / QuizAttempt.total_questions).label('best_score')
    ).join(QuizAttempt).group_by(User.id).order_by(db.desc('avg_score')).limit(10).all()
    
    for user_stat in top_users:
        writer.writerow([
            user_stat.username,
            user_stat.attempt_count,
            round(user_stat.avg_score, 2),
            round(user_stat.best_score, 2)
        ])
    
    csv_content = csv_buffer.getvalue()
    csv_buffer.close()
    return csv_content

# Export Routes
@app.route('/api/admin/export', methods=['GET'])
@jwt_required()
def export_data():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    export_type = request.args.get('type', 'all')
    
    try:
        csv_content = generate_csv_export(export_type)
        filename = f"quiz_export_{export_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        
        from flask import Response
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/user-attempts', methods=['POST'])
@jwt_required()
def export_user_attempts():
    user_id = int(get_jwt_identity())
    
    try:
        csv_content = generate_user_csv_export(user_id)
        filename = f"my_quiz_attempts_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        
        from flask import Response
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/export/all-attempts', methods=['POST'])
@jwt_required()
def export_all_attempts():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        csv_content = generate_csv_export('all_attempts')
        filename = f"all_quiz_attempts_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        
        from flask import Response
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# New Export Routes for Frontend
@app.route('/api/admin/export-all-data', methods=['GET'])
@jwt_required()
def export_all_data():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        csv_content = generate_csv_export('all_attempts')
        filename = f"quiz_master_all_data_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        
        from flask import Response
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/export-analytics', methods=['GET'])
@jwt_required()
def export_analytics():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        csv_content = generate_analytics_csv_export()
        filename = f"quiz_master_analytics_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        
        from flask import Response
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/export-user-data/<int:user_id>', methods=['GET'])
@jwt_required()
def export_user_data(user_id):
    admin_user_id = int(get_jwt_identity())
    admin_user = User.query.get(admin_user_id)
    
    if admin_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        csv_content = generate_user_csv_export(user_id)
        target_user = User.query.get(user_id)
        username = target_user.username if target_user else 'unknown'
        filename = f"quiz_master_user_{username}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        
        from flask import Response
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Async CSV Export Routes (Milestone 7)
@app.route('/api/user/export-csv', methods=['POST'])
@jwt_required()
def trigger_user_csv_export():
    """Trigger async CSV export for current user"""
    user_id = int(get_jwt_identity())
    
    try:
        # Import tasks here to avoid circular imports
        from tasks import export_quiz_data_csv
        
        # Trigger async task
        task = export_quiz_data_csv.delay(user_id, 'user_attempts')
        
        return jsonify({
            'success': True,
            'task_id': task.id,
            'message': 'CSV export started. You will receive an email when ready.',
            'status': 'pending'
        }), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/export-status/<task_id>', methods=['GET'])
@jwt_required()
def check_export_status(task_id):
    """Check status of CSV export task"""
    try:
        # Import celery here to avoid circular imports
        from celery import Celery
        from celeryconfig import broker_url, result_backend
        
        celery_app = Celery('quiz_master')
        celery_app.config_from_object('celeryconfig')
        
        task = celery_app.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'status': 'Task is waiting to be processed'
            }
        elif task.state == 'PROGRESS':
            response = {
                'state': task.state,
                'status': task.info.get('status', ''),
                'progress': task.info.get('progress', 0)
            }
        elif task.state == 'SUCCESS':
            response = {
                'state': task.state,
                'status': 'Export completed and emailed',
                'result': task.info
            }
        else:  # FAILURE
            response = {
                'state': task.state,
                'status': str(task.info),
            }
        
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/export-csv', methods=['POST'])
@jwt_required()
def trigger_admin_csv_export():
    """Trigger async CSV export for admin (all data)"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        # Import tasks here to avoid circular imports
        from tasks import export_quiz_data_csv
        
        # Trigger async task for all attempts
        task = export_quiz_data_csv.delay(user_id, 'all_attempts')
        
        return jsonify({
            'success': True,
            'task_id': task.id,
            'message': 'CSV export started. You will receive an email when ready.',
            'status': 'pending'
        }), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update/Delete Routes
@app.route('/api/admin/subjects/<int:subject_id>', methods=['PUT'])
@jwt_required()
def update_subject(subject_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    subject = Subject.query.get_or_404(subject_id)
    
    subject.name = data.get('name', subject.name)
    subject.description = data.get('description', subject.description)
    
    db.session.commit()
    invalidate_subject_caches()
    return jsonify({'message': 'Subject updated successfully'})

@app.route('/api/admin/subjects/<int:subject_id>', methods=['DELETE'])
@jwt_required()
def delete_subject(subject_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    invalidate_subject_caches()
    return jsonify({'message': 'Subject deleted successfully'})

@app.route('/api/admin/chapters/<int:chapter_id>', methods=['PUT'])
@jwt_required()
def update_chapter(chapter_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    chapter = Chapter.query.get_or_404(chapter_id)
    
    chapter.name = data.get('name', chapter.name)
    chapter.description = data.get('description', chapter.description)
    
    db.session.commit()
    return jsonify({'message': 'Chapter updated successfully'})

@app.route('/api/admin/chapters/<int:chapter_id>', methods=['DELETE'])
@jwt_required()
def delete_chapter(chapter_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    return jsonify({'message': 'Chapter deleted successfully'})

@app.route('/api/admin/quizzes/<int:quiz_id>', methods=['PUT'])
@jwt_required()
def update_quiz(quiz_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Parse start_time if provided
    if 'start_time' in data:
        if data['start_time']:
            try:
                quiz.start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid start_time format. Use ISO format.'}), 400
        else:
            quiz.start_time = None
    
    quiz.title = data.get('title', quiz.title)
    quiz.description = data.get('description', quiz.description)
    quiz.duration = data.get('duration', quiz.duration)  # legacy field
    quiz.duration_minutes = data.get('duration_minutes', quiz.duration_minutes)
    quiz.is_active = data.get('is_active', quiz.is_active)
    
    db.session.commit()
    invalidate_quiz_caches()
    return jsonify({'message': 'Quiz updated successfully'})

@app.route('/api/admin/quizzes/<int:quiz_id>', methods=['DELETE'])
@jwt_required()
def delete_quiz(quiz_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    invalidate_quiz_caches()
    return jsonify({'message': 'Quiz deleted successfully'})

@app.route('/api/admin/questions/<int:question_id>', methods=['PUT'])
@jwt_required()
def update_question(question_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    question = Question.query.get_or_404(question_id)
    
    question.text = data.get('text', question.text)
    question.option_a = data.get('option_a', question.option_a)
    question.option_b = data.get('option_b', question.option_b)
    question.option_c = data.get('option_c', question.option_c)
    question.option_d = data.get('option_d', question.option_d)
    question.correct_option = data.get('correct_option', question.correct_option)
    
    db.session.commit()
    return jsonify({'message': 'Question updated successfully'})

@app.route('/api/admin/questions/<int:question_id>', methods=['DELETE'])
@jwt_required()
def delete_question(question_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    return jsonify({'message': 'Question deleted successfully'})

# User Management Routes
@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
def get_all_users():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    users = User.query.all()
    return jsonify({
        'users': [{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat(),
            'quiz_attempts_count': len(user.quiz_attempts)
        } for user in users]
    })

@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    user = User.query.get_or_404(user_id)
    
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.role = data.get('role', user.role)
    user.is_active = data.get('is_active', user.is_active)
    
    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    user = User.query.get_or_404(user_id)
    # Don't allow deleting admin users
    if user.role == 'admin':
        return jsonify({'error': 'Cannot delete admin users'}), 400
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})

# Search functionality
# Legacy admin search endpoint - replaced by improved search blueprints
# The new search endpoints are available at:
# - /api/admin/search (improved version with pagination and caching)
# - /api/search (user search endpoint)
# - /api/admin/search/users, /api/admin/search/quizzes, etc. (dedicated endpoints)

# Test routes for Celery tasks (for demonstration)
@app.route('/api/admin/test-daily-reminder', methods=['POST'])
@jwt_required()
def test_daily_reminder():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        # Simulate daily reminder task
        from datetime import datetime, timedelta
        
        # Find users who haven't attempted any quiz in the last 24 hours
        yesterday = datetime.utcnow() - timedelta(days=1)
        
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
            return jsonify({'message': 'No active quizzes available for reminders'}), 200
        
        # Log reminders (simulate sending)
        reminder_logs = []
        for user in inactive_users:
            reminder_logs.append(f"Reminder sent to {user.username} ({user.email}) about quiz: {latest_quiz.title}")
        
        return jsonify({
            'message': f'Daily reminder task completed',
            'inactive_users_count': len(inactive_users),
            'latest_quiz': latest_quiz.title,
            'reminders': reminder_logs[:5]  # Show first 5 for brevity
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/events', methods=['GET'])
@jwt_required()
def get_admin_events():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        event_type = request.args.get('type')
        time_range = request.args.get('timeRange', '24h')
        
        # Calculate time filter based on range
        now = datetime.utcnow()
        if time_range == '1h':
            time_filter = now - timedelta(hours=1)
        elif time_range == '24h':
            time_filter = now - timedelta(hours=24)
        elif time_range == '7d':
            time_filter = now - timedelta(days=7)
        elif time_range == '30d':
            time_filter = now - timedelta(days=30)
        else:
            time_filter = now - timedelta(hours=24)
        
        # Generate events from recent quiz attempts and user registrations
        events = []
        
        # Recent quiz attempts
        recent_attempts = QuizAttempt.query.filter(
            QuizAttempt.completed_at >= time_filter
        ).order_by(QuizAttempt.completed_at.desc()).limit(50).all()
        
        for attempt in recent_attempts:
            if not event_type or event_type == 'quiz_attempt':
                events.append({
                    'id': f'attempt_{attempt.id}',
                    'type': 'quiz_attempt',
                    'title': f'Quiz Completed: {attempt.quiz.title}',
                    'description': f'{attempt.user.username} scored {attempt.score}/{attempt.total_questions}',
                    'timestamp': attempt.completed_at.isoformat(),
                    'user': {
                        'id': attempt.user.id,
                        'username': attempt.user.username
                    },
                    'metadata': {
                        'quiz_id': attempt.quiz.id,
                        'score': attempt.score,
                        'total_questions': attempt.total_questions,
                        'percentage': round((attempt.score / attempt.total_questions) * 100, 1)
                    }
                })
        
        # Recent user registrations
        recent_users = User.query.filter(
            User.created_at >= time_filter
        ).order_by(User.created_at.desc()).limit(20).all()
        
        for user in recent_users:
            if not event_type or event_type == 'user_registration':
                events.append({
                    'id': f'user_{user.id}',
                    'type': 'user_registration',
                    'title': 'New User Registration',
                    'description': f'{user.username} joined the platform',
                    'timestamp': user.created_at.isoformat(),
                    'user': {
                        'id': user.id,
                        'username': user.username
                    },
                    'metadata': {
                        'role': user.role
                    }
                })
        
        # Sort events by timestamp (newest first)
        events.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Apply pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_events = events[start_idx:end_idx]
        
        return jsonify({
            'events': paginated_events,
            'hasMore': len(events) > end_idx,
            'total': len(events),
            'page': page,
            'limit': limit
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/test-monthly-report', methods=['POST'])
@jwt_required()
def test_monthly_report():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        from datetime import datetime, timedelta
        
        # Calculate monthly stats
        current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month = (current_month - timedelta(days=1)).replace(day=1)
        
        # Get monthly attempts with a simple query
        monthly_attempts = QuizAttempt.query.filter(
            QuizAttempt.completed_at >= last_month,
            QuizAttempt.completed_at < current_month,
            QuizAttempt.completed_at.isnot(None)
        ).all()
        
        if not monthly_attempts:
            return jsonify({
                'message': 'No quiz attempts found for last month',
                'report_period': last_month.strftime("%B %Y"),
                'total_attempts': 0,
                'total_users': 0,
                'avg_percentage': 0,
                'subject_stats': {},
                'admin_recipients': []
            }), 200
        
        # Calculate statistics
        total_attempts = len(monthly_attempts)
        total_users = len(set(attempt.user_id for attempt in monthly_attempts))
        
        # Calculate averages safely
        if total_attempts > 0:
            avg_score = sum(attempt.score for attempt in monthly_attempts) / total_attempts
            avg_percentage = sum(
                (attempt.score / attempt.total_questions) * 100 
                for attempt in monthly_attempts 
                if attempt.total_questions > 0
            ) / total_attempts
        else:
            avg_score = 0
            avg_percentage = 0
        
        # Subject-wise performance using efficient queries
        subject_stats = {}
        
        # Get all related data in one go to avoid N+1 queries
        quiz_ids = [attempt.quiz_id for attempt in monthly_attempts]
        quizzes = {q.id: q for q in Quiz.query.filter(Quiz.id.in_(quiz_ids)).all()}
        
        chapter_ids = [q.chapter_id for q in quizzes.values()]
        chapters = {c.id: c for c in Chapter.query.filter(Chapter.id.in_(chapter_ids)).all()}
        
        subject_ids = [c.subject_id for c in chapters.values()]
        subjects = {s.id: s for s in Subject.query.filter(Subject.id.in_(subject_ids)).all()}
        
        # Now calculate subject stats efficiently
        for attempt in monthly_attempts:
            try:
                quiz = quizzes.get(attempt.quiz_id)
                if not quiz:
                    continue
                    
                chapter = chapters.get(quiz.chapter_id)
                if not chapter:
                    continue
                    
                subject = subjects.get(chapter.subject_id)
                if not subject:
                    continue
                
                subject_name = subject.name
                if subject_name not in subject_stats:
                    subject_stats[subject_name] = {
                        'attempts': 0, 
                        'total_score': 0, 
                        'total_questions': 0
                    }
                
                subject_stats[subject_name]['attempts'] += 1
                subject_stats[subject_name]['total_score'] += attempt.score
                subject_stats[subject_name]['total_questions'] += attempt.total_questions
            except Exception as e:
                print(f"Error processing attempt {attempt.id}: {e}")
                continue
        
        # Get admin emails for report distribution
        admins = User.query.filter_by(role='admin').all()
        admin_emails = [admin.email for admin in admins if admin.email]
        
        return jsonify({
            'message': 'Monthly report generated successfully',
            'report_period': last_month.strftime("%B %Y"),
            'total_attempts': total_attempts,
            'total_users': total_users,
            'avg_percentage': round(avg_percentage, 2),
            'subject_stats': subject_stats,
            'admin_recipients': admin_emails
        }), 200
        
    except Exception as e:
        print(f"Monthly report error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to generate monthly report: {str(e)}'}), 500

# Celery Task Management Endpoints
@app.route('/api/admin/trigger-daily-reminder', methods=['POST'])
@jwt_required()
def trigger_daily_reminder():
    """Manually trigger daily reminder task"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        from tasks import send_daily_reminder
        task = send_daily_reminder.delay()
        
        return jsonify({
            'message': 'Daily reminder task started',
            'task_id': task.id,
            'status': 'Task queued for processing'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/trigger-monthly-report', methods=['POST'])
@jwt_required()
def trigger_monthly_report():
    """Manually trigger monthly report generation"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        from tasks import generate_monthly_report
        task = generate_monthly_report.delay()
        
        return jsonify({
            'message': 'Monthly report generation started',
            'task_id': task.id,
            'status': 'Task queued for processing'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/task-status/<task_id>', methods=['GET'])
@jwt_required()
def check_task_status(task_id):
    """Check status of any Celery task"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        task = celery.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'status': 'Task is waiting to be processed'
            }
        elif task.state == 'PROGRESS':
            response = {
                'state': task.state,
                'status': task.info.get('status', ''),
                'progress': task.info.get('progress', 0)
            }
        elif task.state == 'SUCCESS':
            response = {
                'state': task.state,
                'status': 'Task completed successfully',
                'result': task.result
            }
        else:  # FAILURE
            response = {
                'state': task.state,
                'status': 'Task failed',
                'error': str(task.info)
            }
        
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Leaderboard and Achievements Endpoints
@app.route('/api/leaderboard', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_leaderboard():
    """Get leaderboard data based on user performance"""
    start_time = time.perf_counter()
    try:
        # Get time period from query params (default: week)
        period = request.args.get('period', 'week')
        limit = int(request.args.get('limit', 10))
        
        # Calculate date range based on period
        now = datetime.utcnow()
        if period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        elif period == 'all':
            start_date = datetime.min
        else:
            start_date = now - timedelta(days=7)  # Default to week
        
        # Query to get user rankings based on average score and total attempts
        leaderboard_query = db.session.query(
            User.id,
            User.username,
            db.func.count(QuizAttempt.id).label('total_attempts'),
            db.func.avg(QuizAttempt.score * 100.0 / QuizAttempt.total_questions).label('avg_percentage'),
            db.func.max(QuizAttempt.score * 100.0 / QuizAttempt.total_questions).label('best_score'),
            db.func.sum(QuizAttempt.score).label('total_score')
        ).join(
            QuizAttempt, User.id == QuizAttempt.user_id
        ).filter(
            QuizAttempt.completed_at >= start_date,
            QuizAttempt.completed_at.isnot(None),
            User.role == 'user'  # Only include regular users
        ).group_by(
            User.id, User.username
        ).having(
            db.func.count(QuizAttempt.id) > 0  # Must have at least one attempt
        ).order_by(
            db.func.avg(QuizAttempt.score * 100.0 / QuizAttempt.total_questions).desc(),
            db.func.count(QuizAttempt.id).desc()
        ).limit(limit)
        
        leaderboard_data = leaderboard_query.all()
        
        # Get current user's rank
        current_user_id = get_jwt_identity()
        user_rank = None
        user_stats = None
        
        # Find current user's position in the full ranking
        full_ranking_query = db.session.query(
            User.id,
            User.username,
            db.func.count(QuizAttempt.id).label('total_attempts'),
            db.func.avg(QuizAttempt.score * 100.0 / QuizAttempt.total_questions).label('avg_percentage')
        ).join(
            QuizAttempt, User.id == QuizAttempt.user_id
        ).filter(
            QuizAttempt.completed_at >= start_date,
            QuizAttempt.completed_at.isnot(None),
            User.role == 'user'
        ).group_by(
            User.id, User.username
        ).having(
            db.func.count(QuizAttempt.id) > 0
        ).order_by(
            db.func.avg(QuizAttempt.score * 100.0 / QuizAttempt.total_questions).desc(),
            db.func.count(QuizAttempt.id).desc()
        ).all()
        
        # Find current user's rank
        for idx, user_data in enumerate(full_ranking_query):
            if user_data.id == current_user_id:
                user_rank = idx + 1
                user_stats = {
                    'rank': user_rank,
                    'total_attempts': user_data.total_attempts,
                    'avg_percentage': round(float(user_data.avg_percentage or 0), 1)
                }
                break
        
        # Format leaderboard data
        leaderboard = []
        for idx, user_data in enumerate(leaderboard_data):
            leaderboard.append({
                'rank': idx + 1,
                'user_id': user_data.id,
                'username': user_data.username,
                'total_attempts': user_data.total_attempts,
                'avg_percentage': round(float(user_data.avg_percentage or 0), 1),
                'best_score': round(float(user_data.best_score or 0), 1),
                'total_score': int(user_data.total_score or 0)
            })
        
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        app.logger.info(f"Leaderboard API execution time: {execution_time:.2f}ms")
        
        response = jsonify({
            'leaderboard': leaderboard,
            'current_user': user_stats,
            'period': period,
            'total_users': len(full_ranking_query)
        })
        response.headers['X-Cache-Status'] = 'MISS' if not hasattr(request, 'cache_hit') else 'HIT'
        response.headers['X-Execution-Time'] = f"{execution_time:.2f}ms"
        return response
        
    except Exception as e:
        execution_time = (time.perf_counter() - start_time) * 1000
        print(f"Leaderboard error: {str(e)} (execution time: {execution_time:.2f}ms)")
        response = jsonify({'error': 'Failed to fetch leaderboard data'})
        response.headers['X-Cache-Status'] = 'error'
        response.headers['X-Execution-Time'] = f"{execution_time:.2f}ms"
        return response, 500

@app.route('/api/user/achievements', methods=['GET'])
@jwt_required()
def get_user_achievements():
    """Get user achievements based on quiz performance"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get user's quiz attempts
        attempts = QuizAttempt.query.filter_by(
            user_id=current_user_id
        ).filter(
            QuizAttempt.completed_at.isnot(None)
        ).all()
        
        if not attempts:
            return jsonify({
                'achievements': [],
                'locked_achievements': get_locked_achievements()
            })
        
        # Calculate achievement criteria
        total_attempts = len(attempts)
        total_score = sum(attempt.score for attempt in attempts)
        total_questions = sum(attempt.total_questions for attempt in attempts)
        avg_percentage = (total_score / total_questions * 100) if total_questions > 0 else 0
        best_score = max((attempt.score / attempt.total_questions * 100) for attempt in attempts)
        
        # Calculate streak (consecutive days with attempts)
        attempt_dates = sorted(set(attempt.completed_at.date() for attempt in attempts))
        current_streak = calculate_streak(attempt_dates)
        
        # Perfect scores count
        perfect_scores = sum(1 for attempt in attempts if attempt.score == attempt.total_questions)
        
        # Subject diversity
        unique_subjects = set()
        for attempt in attempts:
            quiz = Quiz.query.get(attempt.quiz_id)
            if quiz and quiz.chapter:
                unique_subjects.add(quiz.chapter.subject_id)
        
        achievements = []
        
        # Define achievements and check if unlocked
        achievement_definitions = [
            {
                'id': 'first_quiz',
                'title': 'Getting Started',
                'description': 'Complete your first quiz',
                'icon': 'fas fa-play-circle',
                'color': '#28a745',
                'condition': total_attempts >= 1
            },
            {
                'id': 'quiz_master',
                'title': 'Quiz Master',
                'description': 'Complete 10 quizzes',
                'icon': 'fas fa-graduation-cap',
                'color': '#007bff',
                'condition': total_attempts >= 10
            },
            {
                'id': 'perfectionist',
                'title': 'Perfectionist',
                'description': 'Score 100% on a quiz',
                'icon': 'fas fa-star',
                'color': '#ffc107',
                'condition': perfect_scores >= 1
            },
            {
                'id': 'high_achiever',
                'title': 'High Achiever',
                'description': 'Maintain 80% average score',
                'icon': 'fas fa-trophy',
                'color': '#fd7e14',
                'condition': avg_percentage >= 80 and total_attempts >= 5
            },
            {
                'id': 'dedicated_learner',
                'title': 'Dedicated Learner',
                'description': 'Complete quizzes for 7 consecutive days',
                'icon': 'fas fa-calendar-check',
                'color': '#6f42c1',
                'condition': current_streak >= 7
            },
            {
                'id': 'subject_explorer',
                'title': 'Subject Explorer',
                'description': 'Complete quizzes in 3 different subjects',
                'icon': 'fas fa-compass',
                'color': '#20c997',
                'condition': len(unique_subjects) >= 3
            },
            {
                'id': 'speed_demon',
                'title': 'Speed Demon',
                'description': 'Complete 25 quizzes',
                'icon': 'fas fa-bolt',
                'color': '#e83e8c',
                'condition': total_attempts >= 25
            },
            {
                'id': 'perfectionist_pro',
                'title': 'Perfectionist Pro',
                'description': 'Score 100% on 5 quizzes',
                'icon': 'fas fa-crown',
                'color': '#ffd700',
                'condition': perfect_scores >= 5
            }
        ]
        
        # Filter unlocked achievements
        for achievement in achievement_definitions:
            if achievement['condition']:
                achievements.append({
                    'id': achievement['id'],
                    'title': achievement['title'],
                    'description': achievement['description'],
                    'icon': achievement['icon'],
                    'color': achievement['color'],
                    'date': 'Recently Unlocked'  # Could be more specific with actual unlock date
                })
        
        # Get locked achievements
        locked_achievements = []
        for achievement in achievement_definitions:
            if not achievement['condition']:
                locked_achievements.append({
                    'id': achievement['id'],
                    'title': achievement['title'],
                    'description': achievement['description'],
                    'icon': achievement['icon'],
                    'progress': get_achievement_progress(achievement['id'], {
                        'total_attempts': total_attempts,
                        'perfect_scores': perfect_scores,
                        'avg_percentage': avg_percentage,
                        'current_streak': current_streak,
                        'unique_subjects': len(unique_subjects)
                    })
                })
        
        return jsonify({
            'achievements': achievements,
            'locked_achievements': locked_achievements,
            'stats': {
                'total_attempts': total_attempts,
                'avg_percentage': round(avg_percentage, 1),
                'best_score': round(best_score, 1),
                'current_streak': current_streak,
                'perfect_scores': perfect_scores,
                'subjects_explored': len(unique_subjects)
            }
        })
        
    except Exception as e:
        print(f"Achievements error: {str(e)}")
        return jsonify({'error': 'Failed to fetch achievements'}), 500

def calculate_streak(attempt_dates):
    """Calculate consecutive days streak"""
    if not attempt_dates:
        return 0
    
    # Sort dates in descending order
    sorted_dates = sorted(attempt_dates, reverse=True)
    
    # Check if there's an attempt today or yesterday
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)
    
    if sorted_dates[0] not in [today, yesterday]:
        return 0
    
    # Count consecutive days
    streak = 1
    current_date = sorted_dates[0]
    
    for i in range(1, len(sorted_dates)):
        expected_date = current_date - timedelta(days=1)
        if sorted_dates[i] == expected_date:
            streak += 1
            current_date = sorted_dates[i]
        else:
            break
    
    return streak

def get_achievement_progress(achievement_id, stats):
    """Get progress towards locked achievement"""
    progress_map = {
        'first_quiz': min(stats['total_attempts'], 1),
        'quiz_master': min(stats['total_attempts'] / 10 * 100, 100),
        'perfectionist': min(stats['perfect_scores'], 1) * 100,
        'high_achiever': min(stats['avg_percentage'], 80) / 80 * 100 if stats['total_attempts'] >= 5 else 0,
        'dedicated_learner': min(stats['current_streak'] / 7 * 100, 100),
        'subject_explorer': min(stats['unique_subjects'] / 3 * 100, 100),
        'speed_demon': min(stats['total_attempts'] / 25 * 100, 100),
        'perfectionist_pro': min(stats['perfect_scores'] / 5 * 100, 100)
    }
    
    return round(progress_map.get(achievement_id, 0), 1)

def get_locked_achievements():
    """Get default locked achievements for users with no attempts"""
    return [
        {
            'id': 'first_quiz',
            'title': 'Getting Started',
            'description': 'Complete your first quiz',
            'icon': 'fas fa-play-circle',
            'progress': 0
        },
        {
            'id': 'quiz_master',
            'title': 'Quiz Master',
            'description': 'Complete 10 quizzes',
            'icon': 'fas fa-graduation-cap',
            'progress': 0
        },
        {
            'id': 'perfectionist',
            'title': 'Perfectionist',
            'description': 'Score 100% on a quiz',
            'icon': 'fas fa-star',
            'progress': 0
        }
    ]

@app.route('/api/community/stats', methods=['GET'])
@jwt_required()
@cache.cached(timeout=600)  # Cache for 10 minutes
def get_community_stats():
    """Get community-wide statistics"""
    try:
        # Total users
        total_users = User.query.filter_by(role='user').count()
        
        # Active users (users with attempts in last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_users = db.session.query(User.id).join(
            QuizAttempt, User.id == QuizAttempt.user_id
        ).filter(
            QuizAttempt.completed_at >= thirty_days_ago,
            User.role == 'user'
        ).distinct().count()
        
        # Total quiz attempts
        total_attempts = QuizAttempt.query.filter(
            QuizAttempt.completed_at.isnot(None)
        ).count()
        
        # Average community score
        avg_score_result = db.session.query(
            db.func.avg(QuizAttempt.score * 100.0 / QuizAttempt.total_questions)
        ).filter(
            QuizAttempt.completed_at.isnot(None)
        ).scalar()
        
        avg_community_score = round(float(avg_score_result or 0), 1)
        
        # Most popular subject
        popular_subject = db.session.query(
            Subject.name,
            db.func.count(QuizAttempt.id).label('attempt_count')
        ).join(
            Chapter, Subject.id == Chapter.subject_id
        ).join(
            Quiz, Chapter.id == Quiz.chapter_id
        ).join(
            QuizAttempt, Quiz.id == QuizAttempt.quiz_id
        ).filter(
            QuizAttempt.completed_at.isnot(None)
        ).group_by(
            Subject.id, Subject.name
        ).order_by(
            db.func.count(QuizAttempt.id).desc()
        ).first()
        
        return jsonify({
            'total_users': total_users,
            'active_users': active_users,
            'total_attempts': total_attempts,
            'avg_community_score': avg_community_score,
            'most_popular_subject': popular_subject.name if popular_subject else 'N/A'
        })
        
    except Exception as e:
        print(f"Community stats error: {str(e)}")
        return jsonify({'error': 'Failed to fetch community stats'}), 500

# Database initialization
def init_db():
    with app.app_context():
        db.create_all()
        
        # Create default admin user
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created: admin/admin123")



# User Quiz Attempts API
@app.route('/api/user/quiz-attempts', methods=['GET'])
@jwt_required()
def get_user_quiz_attempts():
    try:
        user_id = get_jwt_identity()
        
        attempts = QuizAttempt.query.filter_by(
            user_id=user_id
        ).filter(
            QuizAttempt.completed_at.isnot(None)
        ).order_by(
            QuizAttempt.completed_at.desc()
        ).limit(10).all()
        
        attempt_list = []
        for attempt in attempts:
            attempt_list.append({
                'id': attempt.id,
                'quiz_title': attempt.quiz.title if attempt.quiz else 'Unknown Quiz',
                'score': attempt.score,
                'total_questions': attempt.total_questions,
                'percentage': round((attempt.score / attempt.total_questions * 100), 1) if attempt.total_questions > 0 else 0,
                'completed_at': attempt.completed_at.isoformat() if attempt.completed_at else None,
                'time_taken': attempt.time_taken
            })
        
        return jsonify(attempt_list)
        
    except Exception as e:
        print(f"User quiz attempts error: {str(e)}")
        return jsonify({'error': 'Failed to fetch user quiz attempts'}), 500

@app.route('/api/user/quiz-attempt/<int:attempt_id>', methods=['GET'])
@jwt_required()
def get_quiz_attempt_details(attempt_id):
    """Get detailed information about a specific quiz attempt"""
    try:
        user_id = get_jwt_identity()
        
        attempt = QuizAttempt.query.filter_by(
            id=attempt_id,
            user_id=user_id
        ).first()
        
        if not attempt:
            return jsonify({'error': 'Quiz attempt not found'}), 404
            
        quiz = Quiz.query.get(attempt.quiz_id)
        chapter = Chapter.query.get(quiz.chapter_id) if quiz else None
        subject = Subject.query.get(chapter.subject_id) if chapter else None
        
        # Get questions and user answers
        questions = Question.query.filter_by(quiz_id=attempt.quiz_id).all()
        user_answers = attempt.answers or {}
        
        question_details = []
        for question in questions:
            question_details.append({
                'id': question.id,
                'question_text': question.question_text,
                'options': {
                    'A': question.option_a,
                    'B': question.option_b,
                    'C': question.option_c,
                    'D': question.option_d
                },
                'correct_option': question.correct_option,
                'user_answer': user_answers.get(str(question.id)),
                'is_correct': user_answers.get(str(question.id)) == question.correct_option
            })
        
        return jsonify({
            'id': attempt.id,
            'quiz': {
                'id': quiz.id,
                'title': quiz.title,
                'description': quiz.description
            },
            'subject': {
                'id': subject.id if subject else None,
                'name': subject.name if subject else 'Unknown'
            },
            'chapter': {
                'id': chapter.id if chapter else None,
                'name': chapter.name if chapter else 'Unknown'
            },
            'score': attempt.score,
            'total_questions': attempt.total_questions,
            'percentage': round((attempt.score / attempt.total_questions) * 100, 2),
            'time_taken': attempt.time_taken,
            'started_at': attempt.started_at.isoformat() if attempt.started_at else None,
            'completed_at': attempt.completed_at.isoformat() if attempt.completed_at else None,
            'questions': question_details
        })
        
    except Exception as e:
        print(f"Quiz attempt details error: {str(e)}")
        return jsonify({'error': 'Failed to fetch quiz attempt details'}), 500

@app.route('/api/user/scores', methods=['GET'])
@jwt_required()
def get_user_scores():
    """Get comprehensive user score history with pagination and filtering"""
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        subject_filter = request.args.get('subject')
        sort_by = request.args.get('sort', 'date_desc')  # date_desc, date_asc, score_desc, score_asc
        
        # Base query
        query = QuizAttempt.query.filter_by(
            user_id=user_id
        ).filter(
            QuizAttempt.completed_at.isnot(None)
        )
        
        # Apply subject filter if provided
        if subject_filter:
            query = query.join(Quiz).join(Chapter).join(Subject).filter(
                Subject.name == subject_filter
            )
        
        # Apply sorting
        if sort_by == 'date_asc':
            query = query.order_by(QuizAttempt.completed_at.asc())
        elif sort_by == 'score_desc':
            query = query.order_by((QuizAttempt.score * 100.0 / QuizAttempt.total_questions).desc())
        elif sort_by == 'score_asc':
            query = query.order_by((QuizAttempt.score * 100.0 / QuizAttempt.total_questions).asc())
        else:  # date_desc (default)
            query = query.order_by(QuizAttempt.completed_at.desc())
        
        # Paginate
        paginated_attempts = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Format results
        attempts_list = []
        for attempt in paginated_attempts.items:
            quiz = Quiz.query.get(attempt.quiz_id)
            chapter = Chapter.query.get(quiz.chapter_id) if quiz else None
            subject = Subject.query.get(chapter.subject_id) if chapter else None
            
            attempts_list.append({
                'id': attempt.id,
                'quiz_id': attempt.quiz_id,
                'quiz_title': quiz.title if quiz else 'Unknown Quiz',
                'subject_name': subject.name if subject else 'Unknown Subject',
                'chapter_name': chapter.name if chapter else 'Unknown Chapter',
                'score': attempt.score,
                'total_questions': attempt.total_questions,
                'percentage': round((attempt.score / attempt.total_questions * 100), 1) if attempt.total_questions > 0 else 0,
                'time_taken': attempt.time_taken,
                'started_at': attempt.started_at.isoformat() if attempt.started_at else None,
                'completed_at': attempt.completed_at.isoformat() if attempt.completed_at else None
            })
        
        # Calculate statistics
        all_attempts = QuizAttempt.query.filter_by(
            user_id=user_id
        ).filter(
            QuizAttempt.completed_at.isnot(None)
        ).all()
        
        total_attempts = len(all_attempts)
        if total_attempts > 0:
            scores = [round((a.score / a.total_questions * 100), 1) for a in all_attempts if a.total_questions > 0]
            average_score = round(sum(scores) / len(scores), 1) if scores else 0
            best_score = max(scores) if scores else 0
            
            # Calculate improvement trend (last 5 vs previous 5)
            recent_scores = scores[:5] if len(scores) >= 5 else scores
            older_scores = scores[5:10] if len(scores) >= 10 else scores[len(recent_scores):]
            
            if len(older_scores) > 0:
                recent_avg = sum(recent_scores) / len(recent_scores)
                older_avg = sum(older_scores) / len(older_scores)
                trend = round(recent_avg - older_avg, 1)
            else:
                trend = 0
        else:
            average_score = 0
            best_score = 0
            trend = 0
        
        return jsonify({
            'attempts': attempts_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated_attempts.total,
                'pages': paginated_attempts.pages,
                'has_next': paginated_attempts.has_next,
                'has_prev': paginated_attempts.has_prev
            },
            'statistics': {
                'total_attempts': total_attempts,
                'average_score': average_score,
                'best_score': best_score,
                'improvement_trend': trend
            }
        })
        
    except Exception as e:
        print(f"User scores error: {str(e)}")
        return jsonify({'error': 'Failed to fetch user scores'}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)