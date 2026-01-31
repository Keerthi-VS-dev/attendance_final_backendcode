#!/usr/bin/env python3
"""
Test team attendance endpoint without auth
"""
import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_no_auth():
    print("=== Testing Team Attendance Without Auth ===")
    
    url = f"{BASE_URL}/team-attendance/team-data"
    print(f"Testing: {url}")
    
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {data.get('count', 0)} records")
            if data.get('records'):
                print(f"Sample record: {data['records'][0]}")
        else:
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_no_auth()