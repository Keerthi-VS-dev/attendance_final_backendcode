#!/usr/bin/env python3
"""
Test admin access with debug output
"""
import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_admin_debug():
    print("=== Testing Admin with Debug Output ===")
    
    # Test with admin account
    print("1. Logging in as admin...")
    login_data = {"username": "admin@izone.com", "password": "admin123"}
    login_response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Admin login failed: {login_response.status_code}")
        return False
    
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Admin login successful")
    
    # Test team_data=true with admin
    print("2. Testing team_data=true with admin account...")
    url = f"{BASE_URL}/attendance/my-attendance?team_data=true&limit=5"
    
    try:
        response = requests.get(url, headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Records returned: {len(data)}")
            
            # Show all unique employees
            unique_employees = set()
            for record in data:
                unique_employees.add(record.get('employee_name', 'Unknown'))
            
            print(f"   Unique employees: {list(unique_employees)}")
            
            # Show sample records
            for i, record in enumerate(data[:3]):
                print(f"   Record {i+1}: {record.get('employee_name')} - {record.get('attendance_date')} - {record.get('status')}")
                
        else:
            print(f"   ❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_admin_debug()