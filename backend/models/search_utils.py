#!/usr/bin/env python3
"""
Search Utilities Module for Quiz Master V2
Provides search functionality with caching and pagination
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, and_, func
import redis
import json
from datetime import datetime, timedelta


class SearchService:
    """Service class for handling search operations with caching"""
    
    def __init__(self, db, redis_client=None, cache_ttl=1800):
        self.db = db
        self.redis_client = redis_client
        self.cache_ttl = cache_ttl  # 30 minutes default
    
    def _get_cache_key(self, search_type, query, entity=None, page=1, per_page=10):
        """Generate cache key for search results"""
        key_parts = [search_type, query.lower(), str(page), str(per_page)]
        if entity:
            key_parts.append(entity)
        return f"search:{':'.join(key_parts)}"
    
    def _cache_results(self, cache_key, results):
        """Cache search results if Redis is available"""
        if self.redis_client:
            try:
                self.redis_client.setex(
                    cache_key, 
                    self.cache_ttl, 
                    json.dumps(results, default=str)
                )
            except Exception as e:
                print(f"Cache write error: {e}")
    
    def _get_cached_results(self, cache_key):
        """Retrieve cached search results"""
        if self.redis_client:
            try:
                cached = self.redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception as e:
                print(f"Cache read error: {e}")
        return None
    
    def search_users(self, query, page=1, per_page=10):
        """Search users by username or email"""
        from app import User
        
        # Build query with case-insensitive search
        search_query = User.query.filter(
            or_(
                User.username.ilike(f"%{query}%"),
                User.email.ilike(f"%{query}%")
            )
        ).filter(User.is_active == True)
        
        # Get paginated results
        pagination = search_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        users = [{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'created_at': user.created_at.isoformat(),
            'quiz_attempts_count': len(user.quiz_attempts)
        } for user in pagination.items]
        
        return {
            'results': users,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }
    
    def search_subjects(self, query, page=1, per_page=10):
        """Search subjects by name or description"""
        from app import Subject
        
        search_query = Subject.query.filter(
            or_(
                Subject.name.ilike(f"%{query}%"),
                Subject.description.ilike(f"%{query}%")
            )
        )
        
        pagination = search_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        subjects = [{
            'id': subject.id,
            'name': subject.name,
            'description': subject.description,
            'chapters_count': len(subject.chapters),
            'created_at': subject.created_at.isoformat()
        } for subject in pagination.items]
        
        return {
            'results': subjects,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }
    
    def search_quizzes(self, query, page=1, per_page=10, user_role='user'):
        """Search quizzes by title or description"""
        from app import Quiz, Chapter, Subject
        
        # Base query with joins for additional info
        base_query = self.db.session.query(Quiz, Chapter, Subject).join(
            Chapter, Quiz.chapter_id == Chapter.id
        ).join(
            Subject, Chapter.subject_id == Subject.id
        ).filter(
            or_(
                Quiz.title.ilike(f"%{query}%"),
                Quiz.description.ilike(f"%{query}%")
            )
        )
        
        # Filter by active quizzes for regular users
        if user_role != 'admin':
            base_query = base_query.filter(Quiz.is_active == True)
        
        # Get total count for pagination
        total = base_query.count()
        
        # Apply pagination
        results = base_query.offset((page - 1) * per_page).limit(per_page).all()
        
        quizzes = [{
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description,
            'duration_minutes': quiz.duration_minutes,
            'start_time': quiz.start_time.isoformat() if quiz.start_time else None,
            'is_active': quiz.is_active,
            'status': quiz.get_quiz_status(),
            'questions_count': len(quiz.questions),
            'attempts_count': len(quiz.attempts),
            'chapter': {
                'id': chapter.id,
                'name': chapter.name
            },
            'subject': {
                'id': subject.id,
                'name': subject.name
            },
            'created_at': quiz.created_at.isoformat()
        } for quiz, chapter, subject in results]
        
        pages = (total + per_page - 1) // per_page
        
        return {
            'results': quizzes,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': pages,
                'has_next': page < pages,
                'has_prev': page > 1
            }
        }
    
    def search_questions(self, query, page=1, per_page=10):
        """Search questions by text content"""
        from app import Question, Quiz, Chapter, Subject
        
        # Query with joins for context
        base_query = self.db.session.query(Question, Quiz, Chapter, Subject).join(
            Quiz, Question.quiz_id == Quiz.id
        ).join(
            Chapter, Quiz.chapter_id == Chapter.id
        ).join(
            Subject, Chapter.subject_id == Subject.id
        ).filter(
            Question.text.ilike(f"%{query}%")
        )
        
        total = base_query.count()
        results = base_query.offset((page - 1) * per_page).limit(per_page).all()
        
        questions = [{
            'id': question.id,
            'text': question.text[:200] + '...' if len(question.text) > 200 else question.text,
            'quiz': {
                'id': quiz.id,
                'title': quiz.title
            },
            'chapter': {
                'id': chapter.id,
                'name': chapter.name
            },
            'subject': {
                'id': subject.id,
                'name': subject.name
            },
            'created_at': question.created_at.isoformat()
        } for question, quiz, chapter, subject in results]
        
        pages = (total + per_page - 1) // per_page
        
        return {
            'results': questions,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': pages,
                'has_next': page < pages,
                'has_prev': page > 1
            }
        }
    
    def admin_search(self, query, entity='all', page=1, per_page=10):
        """Comprehensive admin search across all entities"""
        cache_key = self._get_cache_key('admin', query, entity, page, per_page)
        
        # Try to get cached results
        cached_results = self._get_cached_results(cache_key)
        if cached_results:
            return cached_results
        
        results = {}
        
        if entity in ['all', 'user']:
            results['users'] = self.search_users(query, page, per_page)
        
        if entity in ['all', 'subject']:
            results['subjects'] = self.search_subjects(query, page, per_page)
        
        if entity in ['all', 'quiz']:
            results['quizzes'] = self.search_quizzes(query, page, per_page, 'admin')
        
        if entity in ['all', 'question']:
            results['questions'] = self.search_questions(query, page, per_page)
        
        # Add metadata
        results['metadata'] = {
            'query': query,
            'entity': entity,
            'timestamp': datetime.utcnow().isoformat(),
            'total_results': sum(
                result.get('pagination', {}).get('total', 0) 
                for result in results.values() 
                if isinstance(result, dict) and 'pagination' in result
            )
        }
        
        # Cache results
        self._cache_results(cache_key, results)
        
        return results
    
    def user_search(self, query, search_type='all', page=1, per_page=10):
        """User search limited to quizzes and subjects"""
        cache_key = self._get_cache_key('user', query, search_type, page, per_page)
        
        # Try to get cached results
        cached_results = self._get_cached_results(cache_key)
        if cached_results:
            return cached_results
        
        results = {}
        
        if search_type in ['all', 'subject']:
            results['subjects'] = self.search_subjects(query, page, per_page)
        
        if search_type in ['all', 'quiz']:
            results['quizzes'] = self.search_quizzes(query, page, per_page, 'user')
        
        # Add metadata
        results['metadata'] = {
            'query': query,
            'type': search_type,
            'timestamp': datetime.utcnow().isoformat(),
            'total_results': sum(
                result.get('pagination', {}).get('total', 0) 
                for result in results.values() 
                if isinstance(result, dict) and 'pagination' in result
            )
        }
        
        # Cache results
        self._cache_results(cache_key, results)
        
        return results