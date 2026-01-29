from datetime import date
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.leave import LeaveBalance, LeaveApplication, LeaveStatus, LeaveType
from app.models.employee import Employee


class LeaveService:
    """Service class for leave-related business logic"""
    
    @staticmethod
    def calculate_leave_days(start_date: date, end_date: date) -> Decimal:
        """Calculate number of leave days (including weekends for now)"""
        days = (end_date - start_date).days + 1
        return Decimal(str(days))
    
    @staticmethod
    def get_leave_balance(db: Session, employee_id: int, leave_type_id: int, year: int) -> Optional[LeaveBalance]:
        """Get leave balance for an employee for a specific leave type and year"""
        return db.query(LeaveBalance).filter(
            and_(
                LeaveBalance.employee_id == employee_id,
                LeaveBalance.leave_type_id == leave_type_id,
                LeaveBalance.year == year
            )
        ).first()
    
    @staticmethod
    def has_sufficient_balance(db: Session, employee_id: int, leave_type_id: int, 
                             start_date: date, end_date: date) -> tuple[bool, str, Optional[Decimal]]:
        """Check if employee has sufficient leave balance"""
        year = start_date.year
        total_days = LeaveService.calculate_leave_days(start_date, end_date)
        
        balance = LeaveService.get_leave_balance(db, employee_id, leave_type_id, year)
        
        if not balance:
            return False, f"No leave balance found for year {year}", None
        
        if balance.remaining_days < total_days:
            return False, f"Insufficient leave balance. Available: {balance.remaining_days} days", balance.remaining_days
        
        return True, "Sufficient balance", balance.remaining_days
    
    @staticmethod
    def update_leave_balance(db: Session, employee_id: int, leave_type_id: int, 
                           year: int, days_to_deduct: Decimal) -> bool:
        """Update leave balance by deducting used days"""
        balance = LeaveService.get_leave_balance(db, employee_id, leave_type_id, year)
        
        if not balance:
            return False
        
        balance.used_days += days_to_deduct
        balance.remaining_days = balance.total_allocated - balance.used_days
        
        return True
    
    @staticmethod
    def restore_leave_balance(db: Session, employee_id: int, leave_type_id: int, 
                            year: int, days_to_restore: Decimal) -> bool:
        """Restore leave balance by adding back days"""
        balance = LeaveService.get_leave_balance(db, employee_id, leave_type_id, year)
        
        if not balance:
            return False
        
        balance.used_days -= days_to_restore
        balance.remaining_days = balance.total_allocated - balance.used_days
        
        return True
    
    @staticmethod
    def can_approve_leave(current_user: Employee, application: LeaveApplication) -> tuple[bool, str]:
        """Check if current user can approve the leave application"""
        from app.models.employee import UserRole
        
        # Admin can approve any leave
        if current_user.role == UserRole.ADMIN:
            return True, "Admin can approve"
        
        # Manager can approve subordinates' leaves
        if current_user.role == UserRole.MANAGER:
            # Check if the applicant is a subordinate
            subordinate_ids = [emp.employee_id for emp in current_user.subordinates]
            if application.employee_id in subordinate_ids:
                return True, "Manager can approve subordinate's leave"
            else:
                return False, "Can only approve subordinates' leaves"
        
        return False, "Insufficient privileges to approve leaves"
    
    @staticmethod
    def can_modify_application(current_user: Employee, application: LeaveApplication) -> tuple[bool, str]:
        """Check if current user can modify the leave application"""
        # Only the applicant can modify their own application
        if application.employee_id == current_user.employee_id:
            if application.status == LeaveStatus.PENDING:
                return True, "Can modify pending application"
            else:
                return False, f"Cannot modify application with status: {application.status}"
        
        return False, "Can only modify your own applications"