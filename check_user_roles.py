#!/usr/bin/env python3
"""
Check user roles in the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.employee import Employee

def main():
    db = SessionLocal()
    try:
        employees = db.query(Employee).all()
        print("Current users in database:")
        print("=" * 50)
        for emp in employees:
            print(f"ID: {emp.employee_id}, Email: {emp.email}, Role: {emp.role} (type: {type(emp.role)})")
            print(f"  Name: {emp.full_name}")
            print(f"  Role str: '{str(emp.role)}'")
            print(f"  Role repr: {repr(emp.role)}")
            print()
    finally:
        db.close()

if __name__ == "__main__":
    main()