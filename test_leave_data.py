#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.leave import LeaveApplication
from app.models.employee import Employee

def test_leave_data():
    db = SessionLocal()
    try:
        # Check total leave applications
        total_applications = db.query(LeaveApplication).count()
        print(f"Total leave applications in database: {total_applications}")
        
        # Check applications by status
        pending_count = db.query(LeaveApplication).filter(LeaveApplication.status == 'pending').count()
        approved_count = db.query(LeaveApplication).filter(LeaveApplication.status == 'approved').count()
        rejected_count = db.query(LeaveApplication).filter(LeaveApplication.status == 'rejected').count()
        
        print(f"Pending applications: {pending_count}")
        print(f"Approved applications: {approved_count}")
        print(f"Rejected applications: {rejected_count}")
        
        # Check employees with manager role
        managers = db.query(Employee).filter(Employee.role == 'manager').all()
        print(f"Managers in database: {len(managers)}")
        for manager in managers:
            print(f"  - {manager.full_name} (ID: {manager.employee_id})")
            subordinates = db.query(Employee).filter(Employee.manager_id == manager.employee_id).all()
            print(f"    Subordinates: {len(subordinates)}")
            for sub in subordinates:
                print(f"      - {sub.full_name}")
        
        # Check admins
        admins = db.query(Employee).filter(Employee.role == 'admin').all()
        print(f"Admins in database: {len(admins)}")
        for admin in admins:
            print(f"  - {admin.full_name} (ID: {admin.employee_id})")
        
        # Show some sample applications
        sample_apps = db.query(LeaveApplication).limit(5).all()
        print(f"\nSample applications:")
        for app in sample_apps:
            employee = db.query(Employee).filter(Employee.employee_id == app.employee_id).first()
            print(f"  - {employee.full_name if employee else 'Unknown'}: {app.status} ({app.start_date} to {app.end_date})")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_leave_data()