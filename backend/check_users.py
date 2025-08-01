#!/usr/bin/env python3
"""
Script to check users in the database and verify their credentials
"""
from app import app, db, User
from werkzeug.security import check_password_hash, generate_password_hash

def check_users():
    with app.app_context():
        print("🔍 Checking users in database...")
        print("=" * 50)
        
        # Get all users
        users = User.query.all()
        
        if not users:
            print("❌ No users found in database!")
            return
        
        print(f"✅ Found {len(users)} user(s) in database:")
        print()
        
        for user in users:
            print(f"👤 User ID: {user.id}")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Role: {user.role}")
            print(f"   Active: {user.is_active}")
            print(f"   Created: {user.created_at}")
            
            # Test password
            test_password = 'admin123' if user.username == 'admin' else 'user123'
            password_valid = check_password_hash(user.password_hash, test_password)
            print(f"   Password '{test_password}' valid: {'✅' if password_valid else '❌'}")
            print()
        
        # Test admin login specifically
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("🔐 Testing admin login...")
            admin_password_valid = check_password_hash(admin.password_hash, 'admin123')
            print(f"Admin password 'admin123' valid: {'✅' if admin_password_valid else '❌'}")
            
            if not admin_password_valid:
                print("❌ Admin password is incorrect!")
                print("Let's recreate the admin user...")
                
                # Recreate admin user
                admin.password_hash = generate_password_hash('admin123')
                db.session.commit()
                print("✅ Admin password updated to 'admin123'")
        else:
            print("❌ Admin user not found!")

if __name__ == '__main__':
    check_users() 