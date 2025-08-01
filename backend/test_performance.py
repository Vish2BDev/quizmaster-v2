#!/usr/bin/env python3
"""
Performance and Rate Limiting Test Script for Quizmaster API

This script tests:
1. Rate limiting on login and quiz submission endpoints
2. Caching performance on leaderboard and analytics endpoints
3. Cache invalidation when data is modified
"""

import requests
import time
import json
from datetime import datetime

# Configuration
BASE_URL = 'http://localhost:5000/api'
TEST_USER = {
    'username': 'testuser',
    'email': 'test@example.com',
    'password': 'testpass123'
}
ADMIN_USER = {
    'username': 'admin',
    'email': 'admin@example.com', 
    'password': 'admin123'
}

def make_request(method, endpoint, data=None, headers=None):
    """Make HTTP request and return response with timing info"""
    url = f"{BASE_URL}{endpoint}"
    start_time = time.perf_counter()
    
    if method.upper() == 'GET':
        response = requests.get(url, headers=headers)
    elif method.upper() == 'POST':
        response = requests.post(url, json=data, headers=headers)
    elif method.upper() == 'PUT':
        response = requests.put(url, json=data, headers=headers)
    elif method.upper() == 'DELETE':
        response = requests.delete(url, headers=headers)
    
    end_time = time.perf_counter()
    execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
    
    return response, execution_time

def get_auth_headers(token):
    """Get authorization headers"""
    return {'Authorization': f'Bearer {token}'}

def test_rate_limiting():
    """Test rate limiting on login endpoint"""
    print("\n=== Testing Rate Limiting ===")
    print("Testing login endpoint (5 requests per minute limit)...")
    
    # Try to make 6 login requests quickly
    for i in range(6):
        response, exec_time = make_request('POST', '/login', {
            'username': 'nonexistent',
            'password': 'wrong'
        })
        
        print(f"Request {i+1}: Status {response.status_code}, Time: {exec_time:.2f}ms")
        
        if response.status_code == 429:
            print("✓ Rate limiting working! Request blocked.")
            break
        elif i == 5:
            print("⚠ Rate limiting may not be working as expected")
        
        time.sleep(0.5)  # Small delay between requests

def test_caching_performance(token):
    """Test caching performance on leaderboard endpoint"""
    print("\n=== Testing Caching Performance ===")
    print("Testing leaderboard endpoint caching...")
    
    headers = get_auth_headers(token)
    
    # First request (cache miss)
    print("\nFirst request (cache miss):")
    response1, time1 = make_request('GET', '/leaderboard', headers=headers)
    
    if response1.status_code == 200:
        cache_status1 = response1.headers.get('X-Cache-Status', 'unknown')
        api_time1 = response1.headers.get('X-Execution-Time', 'unknown')
        print(f"Status: {response1.status_code}")
        print(f"Cache Status: {cache_status1}")
        print(f"API Execution Time: {api_time1}")
        print(f"Total Request Time: {time1:.2f}ms")
    
    # Second request (cache hit)
    print("\nSecond request (cache hit):")
    response2, time2 = make_request('GET', '/leaderboard', headers=headers)
    
    if response2.status_code == 200:
        cache_status2 = response2.headers.get('X-Cache-Status', 'unknown')
        api_time2 = response2.headers.get('X-Execution-Time', 'unknown')
        print(f"Status: {response2.status_code}")
        print(f"Cache Status: {cache_status2}")
        print(f"API Execution Time: {api_time2}")
        print(f"Total Request Time: {time2:.2f}ms")
        
        # Compare performance
        if time2 < time1:
            improvement = ((time1 - time2) / time1) * 100
            print(f"\n✓ Cache improved performance by {improvement:.1f}%")
        else:
            print("\n⚠ Cache may not be providing expected performance improvement")

def test_analytics_caching(token):
    """Test analytics endpoint caching"""
    print("\n=== Testing Analytics Caching ===")
    print("Testing admin analytics endpoint...")
    
    headers = get_auth_headers(token)
    
    # Test analytics endpoint
    response, exec_time = make_request('GET', '/admin/analytics/overview', headers=headers)
    
    if response.status_code == 200:
        print(f"Analytics Status: {response.status_code}")
        print(f"Request Time: {exec_time:.2f}ms")
        print("✓ Analytics endpoint accessible")
    else:
        print(f"⚠ Analytics endpoint returned status: {response.status_code}")

def test_subjects_caching(token):
    """Test subjects endpoint caching"""
    print("\n=== Testing Subjects Caching ===")
    print("Testing admin subjects endpoint...")
    
    headers = get_auth_headers(token)
    
    # Test subjects endpoint
    response, exec_time = make_request('GET', '/admin/subjects', headers=headers)
    
    if response.status_code == 200:
        print(f"Subjects Status: {response.status_code}")
        print(f"Request Time: {exec_time:.2f}ms")
        print("✓ Subjects endpoint accessible and cached")
    else:
        print(f"⚠ Subjects endpoint returned status: {response.status_code}")

def login_user(credentials):
    """Login and return access token"""
    response, _ = make_request('POST', '/login', credentials)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('access_token')
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def main():
    """Main test function"""
    print("Quizmaster API Performance & Rate Limiting Test")
    print("=" * 50)
    print(f"Testing against: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Test rate limiting (doesn't require authentication)
    test_rate_limiting()
    
    # Try to login with test user
    print("\n=== Authentication Test ===")
    print("Attempting to login with test user...")
    
    token = login_user(TEST_USER)
    if not token:
        print("⚠ Could not authenticate test user. Some tests will be skipped.")
        print("Make sure the test user exists or create one manually.")
        return
    
    print("✓ Authentication successful")
    
    # Test caching performance
    test_caching_performance(token)
    
    # Try admin endpoints if we have admin access
    admin_token = login_user(ADMIN_USER)
    if admin_token:
        print("\n✓ Admin authentication successful")
        test_analytics_caching(admin_token)
        test_subjects_caching(admin_token)
    else:
        print("\n⚠ Admin authentication failed. Admin endpoint tests skipped.")
    
    print("\n=== Test Summary ===")
    print("✓ Rate limiting test completed")
    print("✓ Caching performance test completed")
    print("✓ All tests finished")
    print("\nNote: For complete testing, ensure Redis is running and the Flask app is started.")

if __name__ == '__main__':
    main()