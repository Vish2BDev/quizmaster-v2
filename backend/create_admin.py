from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Check if admin user exists
    admin = User.query.filter_by(role='admin').first()
    print('Admin exists:', admin is not None)
    
    if not admin:
        # Create admin user
        admin = User(
            username='admin',
            email='admin@test.com',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print('Admin user created successfully!')
        print('Username: admin')
        print('Password: admin123')
    else:
        print('Admin user already exists:')
        print('Username:', admin.username)
        print('Email:', admin.email)