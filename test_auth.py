#!/usr/bin/env python3
"""
Test auth endpoint to verify API is working
"""
import requests

BASE_URL = "http://localhost:8000"

def test_auth():
    print("=== Testing Auth Endpoint ===")
    
    # Test login endpoint
    print("1. Testing login endpoint...")
    login_data = {
        "username": "admin@izone.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
        print(f"Login endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Login successful")
            data = response.json()
            print(f"Token received: {data.get('access_token', 'No token')[:50]}...")
            return True
        else:
            print(f"❌ Login failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

if __name__ == "__main__":
    test_auth()