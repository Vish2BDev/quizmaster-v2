#!/usr/bin/env python3
"""
Export Routes for Quiz Master V2
Handles async CSV export functionality for both admins and users
"""

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from datetime import datetime

# Create blueprint
export_bp = Blueprint('export', __name__)

def auth_required(f):
    """Decorator for authentication"""
    from functools import wraps
    
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator for admin authentication"""
    from functools import wraps
    
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        from app import User
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
            
        return f(*args, **kwargs)
    return decorated_function

@export_bp.route('/api/export/admin-data', methods=['POST'])
@admin_required
def export_admin_data():
    """Trigger async CSV export for admin - user performance data"""
    try:
        from tasks import generate_admin_csv
        
        # Trigger async task
        task = generate_admin_csv.delay()
        
        return jsonify({
            'success': True,
            'task_id': task.id,
            'status': 'PENDING',
            'message': 'Admin data export started. Check status using task_id.'
        }), 202
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to start admin data export'
        }), 500

@export_bp.route('/api/export/user-history', methods=['POST'])
@auth_required
def export_user_history():
    """Trigger async CSV export for user - quiz history"""
    try:
        user_id = int(get_jwt_identity())
        from tasks import generate_user_csv
        
        # Trigger async task
        task = generate_user_csv.delay(user_id)
        
        return jsonify({
            'success': True,
            'task_id': task.id,
            'status': 'PENDING',
            'message': 'User quiz history export started. Check status using task_id.'
        }), 202
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to start user history export'
        }), 500

@export_bp.route('/api/export/status/<task_id>', methods=['GET'])
@auth_required
def get_export_status(task_id):
    """Check status of CSV export task"""
    try:
        from celery import Celery
        from celeryconfig import broker_url, result_backend
        
        # Get celery app instance
        celery_app = Celery('quiz_tasks')
        celery_app.config_from_object('celeryconfig')
        
        task = celery_app.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {
                'task_id': task_id,
                'state': task.state,
                'status': 'Task is waiting to be processed',
                'progress': 0
            }
        elif task.state == 'PROGRESS':
            response = {
                'task_id': task_id,
                'state': task.state,
                'status': task.info.get('status', 'Processing...'),
                'progress': task.info.get('progress', 50)
            }
        elif task.state == 'SUCCESS':
            result = task.result
            response = {
                'task_id': task_id,
                'state': task.state,
                'status': 'Export completed successfully',
                'progress': 100,
                'result': result,
                'download_url': f'/api/export/download/{result.get("filename")}' if result.get('filename') else None
            }
        else:  # FAILURE
            response = {
                'task_id': task_id,
                'state': task.state,
                'status': f'Export failed: {str(task.info)}',
                'progress': 0,
                'error': str(task.info)
            }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'task_id': task_id,
            'state': 'FAILURE',
            'status': f'Error checking task status: {str(e)}',
            'progress': 0,
            'error': str(e)
        }), 500

@export_bp.route('/api/export/download/<filename>', methods=['GET'])
@auth_required
def download_export_file(filename):
    """Download exported CSV file"""
    try:
        from app import User
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        # Security check: ensure user can only download their own files or admin files
        if user.role == 'user':
            # Users can only download files that start with their user_id
            if not filename.startswith(f'user_{user_id}_'):
                return jsonify({'error': 'Access denied to this file'}), 403
        elif user.role == 'admin':
            # Admins can download any file
            pass
        else:
            return jsonify({'error': 'Invalid user role'}), 403
        
        # Check if file exists
        filepath = os.path.join('exports', filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        # Check file size (max 5MB as per requirements)
        file_size = os.path.getsize(filepath)
        max_size = 5 * 1024 * 1024  # 5MB in bytes
        
        if file_size > max_size:
            return jsonify({
                'error': 'File too large',
                'message': 'Export file exceeds 5MB limit'
            }), 413
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to download export file'
        }), 500

@export_bp.route('/api/export/list', methods=['GET'])
@auth_required
def list_export_files():
    """List available export files for the current user"""
    try:
        from app import User
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        exports_dir = 'exports'
        if not os.path.exists(exports_dir):
            return jsonify({'files': []})
        
        files = []
        for filename in os.listdir(exports_dir):
            if filename.endswith('.csv'):
                filepath = os.path.join(exports_dir, filename)
                file_stat = os.stat(filepath)
                
                # Security check: filter files based on user role
                if user.role == 'user':
                    # Users can only see their own files
                    if not filename.startswith(f'user_{user_id}_'):
                        continue
                elif user.role == 'admin':
                    # Admins can see all files
                    pass
                else:
                    continue
                
                files.append({
                    'filename': filename,
                    'size': file_stat.st_size,
                    'created_at': datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                    'download_url': f'/api/export/download/{filename}'
                })
        
        # Sort by creation time (newest first)
        files.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({'files': files})
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to list export files'
        }), 500

@export_bp.route('/api/export/cleanup', methods=['POST'])
@admin_required
def cleanup_old_exports():
    """Admin endpoint to cleanup old export files (older than 30 days)"""
    try:
        from datetime import timedelta
        
        exports_dir = 'exports'
        if not os.path.exists(exports_dir):
            return jsonify({'message': 'No exports directory found', 'deleted_count': 0})
        
        cutoff_date = datetime.now() - timedelta(days=30)
        deleted_count = 0
        
        for filename in os.listdir(exports_dir):
            if filename.endswith('.csv'):
                filepath = os.path.join(exports_dir, filename)
                file_stat = os.stat(filepath)
                file_date = datetime.fromtimestamp(file_stat.st_ctime)
                
                if file_date < cutoff_date:
                    os.remove(filepath)
                    deleted_count += 1
        
        return jsonify({
            'message': f'Cleanup completed. Deleted {deleted_count} old export files.',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to cleanup old export files'
        }), 500