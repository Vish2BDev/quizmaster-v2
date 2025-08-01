#!/usr/bin/env python3
"""
Setup script to create test users and sample data for Quiz Master V2
"""
from app import app, db, User, Subject, Chapter, Quiz, Question
from werkzeug.security import generate_password_hash
from datetime import datetime

def setup_test_data():
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Create admin user
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@quizmaster.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            print("✅ Admin user created: admin/admin123")
        
        # Create test users
        test_users = [
            {
                'username': 'john_doe',
                'email': 'john@example.com',
                'password': 'user123',
                'role': 'user'
            },
            {
                'username': 'jane_smith',
                'email': 'jane@example.com',
                'password': 'user123',
                'role': 'user'
            },
            {
                'username': 'bob_wilson',
                'email': 'bob@example.com',
                'password': 'user123',
                'role': 'user'
            }
        ]
        
        for user_data in test_users:
            user = User.query.filter_by(username=user_data['username']).first()
            if not user:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash=generate_password_hash(user_data['password']),
                    role=user_data['role']
                )
                db.session.add(user)
                print(f"✅ User created: {user_data['username']}/{user_data['password']}")
        
        # Create sample subjects
        subjects_data = [
            {
                'name': 'Mathematics',
                'description': 'Fundamental mathematics concepts and problem solving'
            },
            {
                'name': 'Science',
                'description': 'General science knowledge and scientific principles'
            },
            {
                'name': 'History',
                'description': 'World history and historical events'
            }
        ]
        
        for subject_data in subjects_data:
            subject = Subject.query.filter_by(name=subject_data['name']).first()
            if not subject:
                subject = Subject(**subject_data)
                db.session.add(subject)
                print(f"✅ Subject created: {subject_data['name']}")
        
        # Commit all changes
        db.session.commit()
        
        # Create sample chapters for Mathematics
        math_subject = Subject.query.filter_by(name='Mathematics').first()
        if math_subject:
            chapters_data = [
                {
                    'name': 'Algebra Basics',
                    'description': 'Introduction to algebraic concepts and equations',
                    'subject_id': math_subject.id
                },
                {
                    'name': 'Geometry Fundamentals',
                    'description': 'Basic geometric shapes and properties',
                    'subject_id': math_subject.id
                }
            ]
            
            for chapter_data in chapters_data:
                chapter = Chapter.query.filter_by(name=chapter_data['name']).first()
                if not chapter:
                    chapter = Chapter(**chapter_data)
                    db.session.add(chapter)
                    print(f"✅ Chapter created: {chapter_data['name']}")
        
        # Create sample quizzes for Algebra Basics
        algebra_chapter = Chapter.query.filter_by(name='Algebra Basics').first()
        if algebra_chapter:
            quizzes_data = [
                {
                    'title': 'Linear Equations',
                    'description': 'Solve basic linear equations',
                    'duration': 15,
                    'chapter_id': algebra_chapter.id,
                    'is_active': True
                },
                {
                    'title': 'Quadratic Equations',
                    'description': 'Solve quadratic equations using different methods',
                    'duration': 20,
                    'chapter_id': algebra_chapter.id,
                    'is_active': True
                }
            ]
            
            for quiz_data in quizzes_data:
                quiz = Quiz.query.filter_by(title=quiz_data['title']).first()
                if not quiz:
                    quiz = Quiz(**quiz_data)
                    db.session.add(quiz)
                    print(f"✅ Quiz created: {quiz_data['title']}")
        
        # Create sample questions for Linear Equations quiz
        linear_quiz = Quiz.query.filter_by(title='Linear Equations').first()
        if linear_quiz:
            questions_data = [
                {
                    'text': 'What is the solution to the equation 2x + 5 = 13?',
                    'option_a': 'x = 4',
                    'option_b': 'x = 6',
                    'option_c': 'x = 8',
                    'option_d': 'x = 9',
                    'correct_option': 'a',
                    'quiz_id': linear_quiz.id
                },
                {
                    'text': 'Solve for x: 3x - 7 = 8',
                    'option_a': 'x = 3',
                    'option_b': 'x = 5',
                    'option_c': 'x = 7',
                    'option_d': 'x = 9',
                    'correct_option': 'b',
                    'quiz_id': linear_quiz.id
                },
                {
                    'text': 'What is the value of x in the equation 4x + 2 = 18?',
                    'option_a': 'x = 2',
                    'option_b': 'x = 4',
                    'option_c': 'x = 6',
                    'option_d': 'x = 8',
                    'correct_option': 'b',
                    'quiz_id': linear_quiz.id
                }
            ]
            
            for question_data in questions_data:
                question = Question.query.filter_by(text=question_data['text']).first()
                if not question:
                    question = Question(**question_data)
                    db.session.add(question)
                    print(f"✅ Question created: {question_data['text'][:50]}...")
        
        # Final commit
        db.session.commit()
        print("\n🎉 Test data setup completed successfully!")
        print("\n📋 Available Credentials:")
        print("=" * 50)
        print("👑 ADMIN USER:")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Email: admin@quizmaster.com")
        print("\n👤 TEST USERS:")
        print("   Username: john_doe")
        print("   Password: user123")
        print("   Email: john@example.com")
        print("\n   Username: jane_smith")
        print("   Password: user123")
        print("   Email: jane@example.com")
        print("\n   Username: bob_wilson")
        print("   Password: user123")
        print("   Email: bob@example.com")
        print("\n📚 SAMPLE DATA CREATED:")
        print("   - 3 Subjects (Mathematics, Science, History)")
        print("   - 2 Chapters (Algebra Basics, Geometry Fundamentals)")
        print("   - 2 Quizzes (Linear Equations, Quadratic Equations)")
        print("   - 3 Questions in Linear Equations quiz")

if __name__ == '__main__':
    setup_test_data() 