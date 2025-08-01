#!/usr/bin/env python3
"""
Script to create a test user for Playwright testing.
"""

import sys
import os
from werkzeug.security import generate_password_hash
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User

def create_test_user():
    """Create a test user for automated testing."""
    with app.app_context():
        # Check if test user already exists
        existing_user = User.query.filter_by(email='test@example.com').first()
        
        if existing_user:
            print("Test user already exists.")
            return
        
        # Create test user
        test_user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('password123'),
            role='user',
            created_at=datetime.utcnow()
        )
        
        try:
            db.session.add(test_user)
            db.session.commit()
            print("Test user created successfully!")
            print("Email: test@example.com")
            print("Password: password123")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating test user: {e}")
            sys.exit(1)

if __name__ == '__main__':
    create_test_user()