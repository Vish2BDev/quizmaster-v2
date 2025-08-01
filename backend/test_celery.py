#!/usr/bin/env python3
"""
Test script for Celery integration
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, celery
from tasks import send_daily_reminder, generate_monthly_report

def test_celery_connection():
    """Test if Celery can connect to Redis broker"""
    try:
        # Test broker connection
        inspect = celery.control.inspect()
        stats = inspect.stats()
        if stats:
            print("✅ Celery broker connection successful")
            return True
        else:
            print("❌ No Celery workers found")
            return False
    except Exception as e:
        print(f"❌ Celery broker connection failed: {e}")
        return False

def test_task_registration():
    """Test if tasks are properly registered"""
    try:
        registered_tasks = list(celery.tasks.keys())
        expected_tasks = [
            'tasks.send_daily_reminder',
            'tasks.generate_monthly_report',
            'tasks.export_quiz_data_csv'
        ]
        
        print(f"Registered tasks: {registered_tasks}")
        
        for task in expected_tasks:
            if task in registered_tasks:
                print(f"✅ Task {task} is registered")
            else:
                print(f"❌ Task {task} is NOT registered")
                return False
        return True
    except Exception as e:
        print(f"❌ Task registration check failed: {e}")
        return False

def test_async_task():
    """Test sending an async task"""
    try:
        # Test daily reminder task
        result = send_daily_reminder.delay()
        print(f"✅ Daily reminder task queued with ID: {result.id}")
        
        # Check task status
        print(f"Task state: {result.state}")
        return True
    except Exception as e:
        print(f"❌ Async task test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Celery Integration...\n")
    
    with app.app_context():
        tests = [
            ("Celery Connection", test_celery_connection),
            ("Task Registration", test_task_registration),
            ("Async Task", test_async_task)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n--- {test_name} ---")
            result = test_func()
            results.append(result)
        
        print("\n" + "="*50)
        print("TEST SUMMARY:")
        for i, (test_name, _) in enumerate(tests):
            status = "✅ PASS" if results[i] else "❌ FAIL"
            print(f"{test_name}: {status}")
        
        if all(results):
            print("\n🎉 All tests passed! Celery integration is working.")
        else:
            print("\n⚠️  Some tests failed. Check your Celery setup.")
            print("\nTroubleshooting:")
            print("1. Make sure Redis is running: redis-server")
            print("2. Start Celery worker: python run_celery.py")
            print("3. Check your configuration in config.py")

if __name__ == '__main__':
    main()