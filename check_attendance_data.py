#!/usr/bin/env python3
"""
Check attendance data in the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.attendance import Attendance
from app.models.employee import Employee

def main():
    db = SessionLocal()
    try:
        # Get all attendance records
        attendance_records = db.query(Attendance).order_by(Attendance.attendance_date.desc()).limit(20).all()
        print(f"Total attendance records in database: {db.query(Attendance).count()}")
        print("Recent attendance records:")
        print("=" * 80)
        
        for record in attendance_records:
            employee = db.query(Employee).filter(Employee.employee_id == record.employee_id).first()
            print(f"ID: {record.attendance_id}, Employee: {employee.full_name if employee else 'Unknown'} (ID: {record.employee_id})")
            print(f"  Date: {record.attendance_date}, Status: {record.status}")
            print(f"  Clock In: {record.clock_in_time}, Clock Out: {record.clock_out_time}")
            print()
            
        # Check unique employees with attendance
        unique_employees = db.query(Attendance.employee_id).distinct().all()
        print(f"Unique employees with attendance records: {len(unique_employees)}")
        for emp_id in unique_employees:
            employee = db.query(Employee).filter(Employee.employee_id == emp_id[0]).first()
            count = db.query(Attendance).filter(Attendance.employee_id == emp_id[0]).count()
            print(f"  Employee ID {emp_id[0]}: {employee.full_name if employee else 'Unknown'} ({count} records)")
            
    finally:
        db.close()

if __name__ == "__main__":
    main()