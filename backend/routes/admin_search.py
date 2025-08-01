#!/usr/bin/env python3
"""
Admin Search Routes for Quiz Master V2
Provides search endpoints for admin users with role-based access control
"""

from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import jwt
from models.search_utils import SearchService
import redis

# Create blueprint
admin_search_bp = Blueprint('admin_search', __name__)

# Initialize Redis client (optional)
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()  # Test connection
except:
    redis_client = None
    print("Redis not available, search caching disabled")


def admin_required(f):
    """Decorator to ensure only admin users can access the endpoint"""
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
            
            if not current_user or current_user.role != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
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


@admin_search_bp.route('/api/admin/search', methods=['GET'])
@admin_required
def admin_search():
    """
    Admin search endpoint
    Query parameters:
    - keyword: search term (required)
    - entity: user|subject|quiz|question|all (default: all)
    - page: page number (default: 1)
    - per_page: results per page (default: 10, max: 50)
    """
    try:
        # Get query parameters
        keyword = request.args.get('keyword', '').strip()
        entity = request.args.get('entity', 'all').lower()
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 50)  # Limit to 50
        
        # Validate inputs
        if not keyword:
            return jsonify({
                'error': 'Keyword parameter is required',
                'message': 'Please provide a search keyword'
            }), 400
        
        if len(keyword) < 2:
            return jsonify({
                'error': 'Keyword too short',
                'message': 'Search keyword must be at least 2 characters long'
            }), 400
        
        valid_entities = ['user', 'subject', 'quiz', 'question', 'all']
        if entity not in valid_entities:
            return jsonify({
                'error': 'Invalid entity type',
                'message': f'Entity must be one of: {", ".join(valid_entities)}'
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
        results = search_service.admin_search(
            query=keyword,
            entity=entity,
            page=page,
            per_page=per_page
        )
        
        # Add request metadata
        results['request_info'] = {
            'keyword': keyword,
            'entity': entity,
            'page': page,
            'per_page': per_page,
            'admin_user': request.current_user.username
        }
        
        return jsonify(results), 200
        
    except ValueError as e:
        return jsonify({
            'error': 'Invalid parameter format',
            'message': str(e)
        }), 400
    
    except Exception as e:
        current_app.logger.error(f"Admin search error: {str(e)}")
        return jsonify({
            'error': 'Search failed',
            'message': 'An error occurred while processing your search request'
        }), 500


@admin_search_bp.route('/api/admin/search/users', methods=['GET'])
@admin_required
def search_users_only():
    """
    Dedicated endpoint for searching users only
    Query parameters:
    - q: search term (required)
    - page: page number (default: 1)
    - per_page: results per page (default: 10, max: 50)
    """
    try:
        query = request.args.get('q', '').strip()
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 50)
        
        if not query or len(query) < 2:
            return jsonify({
                'error': 'Invalid search query',
                'message': 'Search query must be at least 2 characters long'
            }), 400
        
        from app import db
        search_service = SearchService(db, redis_client)
        
        results = search_service.search_users(query, page, per_page)
        
        return jsonify({
            'users': results,
            'request_info': {
                'query': query,
                'page': page,
                'per_page': per_page
            }
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'Invalid parameter format', 'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"User search error: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500


@admin_search_bp.route('/api/admin/search/quizzes', methods=['GET'])
@admin_required
def search_quizzes_only():
    """
    Dedicated endpoint for searching quizzes only
    Query parameters:
    - q: search term (required)
    - page: page number (default: 1)
    - per_page: results per page (default: 10, max: 50)
    """
    try:
        query = request.args.get('q', '').strip()
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 50)
        
        if not query or len(query) < 2:
            return jsonify({
                'error': 'Invalid search query',
                'message': 'Search query must be at least 2 characters long'
            }), 400
        
        from app import db
        search_service = SearchService(db, redis_client)
        
        results = search_service.search_quizzes(query, page, per_page, 'admin')
        
        return jsonify({
            'quizzes': results,
            'request_info': {
                'query': query,
                'page': page,
                'per_page': per_page
            }
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'Invalid parameter format', 'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Quiz search error: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500


@admin_search_bp.route('/api/admin/search/subjects', methods=['GET'])
@admin_required
def search_subjects_only():
    """
    Dedicated endpoint for searching subjects only
    """
    try:
        query = request.args.get('q', '').strip()
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 50)
        
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
                'per_page': per_page
            }
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'Invalid parameter format', 'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Subject search error: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500


@admin_search_bp.route('/api/admin/search/questions', methods=['GET'])
@admin_required
def search_questions_only():
    """
    Dedicated endpoint for searching questions only
    """
    try:
        query = request.args.get('q', '').strip()
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 50)
        
        if not query or len(query) < 2:
            return jsonify({
                'error': 'Invalid search query',
                'message': 'Search query must be at least 2 characters long'
            }), 400
        
        from app import db
        search_service = SearchService(db, redis_client)
        
        results = search_service.search_questions(query, page, per_page)
        
        return jsonify({
            'questions': results,
            'request_info': {
                'query': query,
                'page': page,
                'per_page': per_page
            }
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'Invalid parameter format', 'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Question search error: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500


@admin_search_bp.route('/api/admin/search/clear-cache', methods=['POST'])
@admin_required
def clear_search_cache():
    """
    Clear search cache (admin only)
    """
    try:
        if redis_client:
            # Clear all search-related cache keys
            keys = redis_client.keys('search:*')
            if keys:
                redis_client.delete(*keys)
                return jsonify({
                    'message': f'Cleared {len(keys)} cache entries',
                    'cleared_keys': len(keys)
                }), 200
            else:
                return jsonify({'message': 'No cache entries to clear'}), 200
        else:
            return jsonify({'message': 'Cache not available'}), 200
            
    except Exception as e:
        current_app.logger.error(f"Cache clear error: {str(e)}")
        return jsonify({'error': 'Failed to clear cache'}), 500