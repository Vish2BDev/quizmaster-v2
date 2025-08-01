#!/usr/bin/env python3
"""
Script to test the test user login credentials.
"""

import requests
import json

def test_user_login():
    """Test login with test user credentials."""
    url = 'http://localhost:5000/api/login'
    
    # Test user credentials
    credentials = {
        'username': 'testuser',
        'password': 'password123'
    }
    
    print(f"Testing login with credentials: {credentials['username']}")
    print(f"URL: {url}")
    
    try:
        response = requests.post(url, json=credentials)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Body: {json.dumps(data, indent=2)}")
            print("\n✅ Test user login successful!")
            print(f"Token: {data.get('access_token', 'N/A')[:50]}...")
            print(f"User: {data.get('user', 'N/A')}")
        else:
            print(f"❌ Login failed!")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is the backend server running?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_user_login()