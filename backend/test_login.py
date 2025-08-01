#!/usr/bin/env python3
"""
Test script to verify the login endpoint
"""
import requests
import json

def test_login():
    url = "http://localhost:5000/api/login"
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        print("🔍 Testing login endpoint...")
        print(f"URL: {url}")
        print(f"Data: {json.dumps(data, indent=2)}")
        print("-" * 50)
        
        response = requests.post(url, json=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            result = response.json()
            print(f"Token: {result.get('access_token', 'No token')[:50]}...")
            print(f"User: {result.get('user', 'No user data')}")
        else:
            print("❌ Login failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - Backend not running on port 5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_login() 