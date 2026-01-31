#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.leave import LeaveApplication, LeaveStatus
from app.models.employee import Employee

def fix_demo_data():
    db = SessionLocal()
    try:
        # Get the manager account (manager@izone.com should be John Manager ID: 2)
        manager = db.query(Employee).filter(Employee.email == 'manager@izone.com').first()
        if not manager:
            print("Manager account not found!")
            return
        
        print(f"Found manager: {manager.full_name} (ID: {manager.employee_id})")
        
        # Get some employees to assign to this manager
        employees = db.query(Employee).filter(
            Employee.role == 'employee',
            Employee.employee_id != manager.employee_id
        ).limit(3).all()
        
        print(f"Found {len(employees)} employees to assign to manager")
        
        # Assign employees to this manager
        for emp in employees:
            emp.manager_id = manager.employee_id
            print(f"  - Assigned {emp.full_name} to manager")
        
        # Create a pending leave application from one of the employees
        if employees:
            from datetime import date, timedelta
            from decimal import Decimal
            
            employee = employees[0]
            
            # Check if there's already a pending application from this employee
            existing = db.query(LeaveApplication).filter(
                LeaveApplication.employee_id == employee.employee_id,
                LeaveApplication.status == LeaveStatus.PENDING
            ).first()
            
            if not existing:
                # Create a new pending application
                new_app = LeaveApplication(
                    employee_id=employee.employee_id,
                    leave_type_id=1,  # Assuming leave type 1 exists
                    start_date=date.today() + timedelta(days=7),
                    end_date=date.today() + timedelta(days=9),
                    total_days=Decimal('3'),
                    reason="Need time off for personal matters",
                    status=LeaveStatus.PENDING
                )
                db.add(new_app)
                print(f"Created pending leave application for {employee.full_name}")
            else:
                print(f"Pending application already exists for {employee.full_name}")
        
        db.commit()
        print("Demo data fixed successfully!")
        
        # Verify the changes
        subordinates = db.query(Employee).filter(Employee.manager_id == manager.employee_id).all()
        print(f"Manager now has {len(subordinates)} subordinates:")
        for sub in subordinates:
            print(f"  - {sub.full_name}")
        
        # Check pending applications for this manager's team
        subordinate_ids = [sub.employee_id for sub in subordinates]
        pending_apps = db.query(LeaveApplication).filter(
            LeaveApplication.employee_id.in_(subordinate_ids),
            LeaveApplication.status == LeaveStatus.PENDING
        ).all()
        
        print(f"Pending applications for manager's team: {len(pending_apps)}")
        for app in pending_apps:
            emp = db.query(Employee).filter(Employee.employee_id == app.employee_id).first()
            print(f"  - {emp.full_name if emp else 'Unknown'}: {app.start_date} to {app.end_date}")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_demo_data()