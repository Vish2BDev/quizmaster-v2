#!/usr/bin/env python3
"""
User Search Routes for Quiz Master V2
Provides search endpoints for regular users (limited to quizzes and subjects)
"""

from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import jwt
from models.search_utils import SearchService
import redis

# Create blueprint
user_search_bp = Blueprint('user_search', __name__)

# Initialize Redis client (optional)
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()  # Test connection
except:
    redis_client = None
    print("Redis not available, search caching disabled")


def auth_required(f):
    """Decorator to ensure only authenticated users can access the endpoint"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Decode JWT token
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            
            # Import User model here to avoid circular imports
            from app import User
            current_user = User.query.get(data['user_id'])
            
            if not current_user or not current_user.is_active:
                return jsonify({'error': 'User not found or inactive'}), 403
            
            # Add current_user to request context
            request.current_user = current_user
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'error': 'Authentication failed'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


@user_search_bp.route('/api/search', methods=['GET'])
@auth_required
def user_search():
    """
    User search endpoint (limited to quizzes and subjects)
    Query parameters:
    - query: search term (required)
    - type: subject|quiz|all (default: all)
    - page: page number (default: 1)
    - per_page: results per page (default: 10, max: 20)
    """
    try:
        # Get query parameters
        query = request.args.get('query', '').strip()
        search_type = request.args.get('type', 'all').lower()
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 20)  # Lower limit for users
        
        # Validate inputs
        if not query:
            return jsonify({
                'error': 'Query parameter is required',
                'message': 'Please provide a search query'
            }), 400
        
        if len(query) < 2:
            return jsonify({
                'error': 'Query too short',
                'message': 'Search query must be at least 2 characters long'
            }), 400
        
        valid_types = ['subject', 'quiz', 'all']
        if search_type not in valid_types:
            return jsonify({
                'error': 'Invalid search type',
                'message': f'Type must be one of: {", ".join(valid_types)}'
            }), 400
        
        if page < 1:
            return jsonify({
                'error': 'Invalid page number',
                'message': 'Page number must be 1 or greater'
            }), 400
        
        # Initialize search service
        from app import db
        search_service = SearchService(db, redis_client)
        
        # Perform search
        results = search_service.user_search(
            query=query,
            search_type=search_type,
            page=page,
            per_page=per_page
        )
        
        # Add request metadata
        results['request_info'] = {
            'query': query,
            'type': search_type,
            'page': page,
            'per_page': per_page,
            'user': request.current_user.username
        }
        
        return jsonify(results), 200
        
    except ValueError as e:
        return jsonify({
            'error': 'Invalid parameter format',
            'message': str(e)
        }), 400
    
    except Exception as e:
        current_app.logger.error(f"User search error: {str(e)}")
        return jsonify({
            'error': 'Search failed',
            'message': 'An error occurred while processing your search request'
        }), 500


@user_search_bp.route('/api/search/quizzes', methods=['GET'])
@auth_required
def search_quizzes_only():
    """
    Dedicated endpoint for searching quizzes only (user access)
    Query parameters:
    - q: search term (required)
    - page: page number (default: 1)
    - per_page: results per page (default: 10, max: 20)
    """
    try:
        query = request.args.get('q', '').strip()
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 20)
        
        if not query or len(query) < 2:
            return jsonify({
                'error': 'Invalid search query',
                'message': 'Search query must be at least 2 characters long'
            }), 400
        
        from app import db
        search_service = SearchService(db, redis_client)
        
        # Use 'user' role to filter only active quizzes
        results = search_service.search_quizzes(query, page, per_page, 'user')
        
        return jsonify({
            'quizzes': results,
            'request_info': {
                'query': query,
                'page': page,
                'per_page': per_page,
                'user': request.current_user.username
            }
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'Invalid parameter format', 'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"User quiz search error: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500


@user_search_bp.route('/api/search/subjects', methods=['GET'])
@auth_required
def search_subjects_only():
    """
    Dedicated endpoint for searching subjects only (user access)
    Query parameters:
    - q: search term (required)
    - page: page number (default: 1)
    - per_page: results per page (default: 10, max: 20)
    """
    try:
        query = request.args.get('q', '').strip()
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 20)
        
        if not query or len(query) < 2:
            return jsonify({
                'error': 'Invalid search query',
                'message': 'Search query must be at least 2 characters long'
            }), 400
        
        from app import db
        search_service = SearchService(db, redis_client)
        
        results = search_service.search_subjects(query, page, per_page)
        
        return jsonify({
            'subjects': results,
            'request_info': {
                'query': query,
                'page': page,
                'per_page': per_page,
                'user': request.current_user.username
            }
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'Invalid parameter format', 'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"User subject search error: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500


@user_search_bp.route('/api/search/suggestions', methods=['GET'])
@auth_required
def search_suggestions():
    """
    Get search suggestions based on partial query
    Query parameters:
    - q: partial search term (required, min 1 character)
    - type: subject|quiz|all (default: all)
    - limit: max suggestions (default: 5, max: 10)
    """
    try:
        query = request.args.get('q', '').strip()
        search_type = request.args.get('type', 'all').lower()
        limit = min(int(request.args.get('limit', 5)), 10)
        
        if not query:
            return jsonify({'suggestions': []}), 200
        
        if len(query) < 1:
            return jsonify({'suggestions': []}), 200
        
        valid_types = ['subject', 'quiz', 'all']
        if search_type not in valid_types:
            return jsonify({
                'error': 'Invalid search type',
                'message': f'Type must be one of: {", ".join(valid_types)}'
            }), 400
        
        from app import db, Quiz, Subject, Chapter
        suggestions = []
        
        # Get quiz suggestions
        if search_type in ['quiz', 'all']:
            quiz_suggestions = db.session.query(Quiz.title).filter(
                Quiz.title.ilike(f"%{query}%"),
                Quiz.is_active == True
            ).limit(limit // 2 if search_type == 'all' else limit).all()
            
            for title, in quiz_suggestions:
                suggestions.append({
                    'text': title,
                    'type': 'quiz'
                })
        
        # Get subject suggestions
        if search_type in ['subject', 'all']:
            subject_suggestions = db.session.query(Subject.name).filter(
                Subject.name.ilike(f"%{query}%")
            ).limit(limit // 2 if search_type == 'all' else limit).all()
            
            for name, in subject_suggestions:
                suggestions.append({
                    'text': name,
                    'type': 'subject'
                })
        
        # Limit total suggestions
        suggestions = suggestions[:limit]
        
        return jsonify({
            'suggestions': suggestions,
            'query': query,
            'type': search_type
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'Invalid parameter format', 'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Search suggestions error: {str(e)}")
        return jsonify({'error': 'Failed to get suggestions'}), 500


@user_search_bp.route('/api/search/recent', methods=['GET'])
@auth_required
def get_recent_searches():
    """
    Get user's recent search queries (if implemented with user activity tracking)
    For now, returns empty array as placeholder
    """
    try:
        # This would typically fetch from a user_search_history table
        # For now, return empty array as placeholder
        return jsonify({
            'recent_searches': [],
            'message': 'Recent search history not yet implemented'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Recent searches error: {str(e)}")
        return jsonify({'error': 'Failed to get recent searches'}), 500