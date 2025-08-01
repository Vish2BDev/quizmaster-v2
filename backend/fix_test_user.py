#!/usr/bin/env python3
"""
Script to fix the test user password.
"""

import sys
import os
from werkzeug.security import generate_password_hash

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User

def fix_test_user():
    """Fix the test user password."""
    with app.app_context():
        # Find the test user
        test_user = User.query.filter_by(email='test@example.com').first()
        
        if not test_user:
            print("Test user not found.")
            return
        
        # Update the password
        test_user.password_hash = generate_password_hash('password123')
        
        try:
            db.session.commit()
            print("Test user password updated successfully!")
            print("Email: test@example.com")
            print("Password: password123")
        except Exception as e:
            db.session.rollback()
            print(f"Error updating test user: {e}")
            sys.exit(1)

if __name__ == '__main__':
    fix_test_user()