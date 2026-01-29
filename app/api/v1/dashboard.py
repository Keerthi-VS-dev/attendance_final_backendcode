from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from datetime import date, datetime, timedelta
from app.database import get_db
from app.models.employee import Employee
from app.models.attendance import Attendance, AttendanceStatus
from app.models.leave import LeaveApplication, LeaveStatus, LeaveBalance
from app.models.rave import Rave
from app.models.holiday import Holiday
from app.dependencies import get_current_user, get_current_manager_or_admin

router = APIRouter()


@router.get("/stats")
def get_dashboard_stats(
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics for current user"""
    today = date.today()
    current_year = today.year
    current_month = today.month
    
    # Today's attendance
    today_attendance = db.query(Attendance).filter(
        and_(
            Attendance.employee_id == current_user.employee_id,
            Attendance.attendance_date == today
        )
    ).first()
    
    # Monthly attendance statistics
    monthly_attendance = db.query(Attendance).filter(
        and_(
            Attendance.employee_id == current_user.employee_id,
            extract('year', Attendance.attendance_date) == current_year,
            extract('month', Attendance.attendance_date) == current_month
        )
    ).all()
    
    present_days = len([a for a in monthly_attendance if a.status == AttendanceStatus.PRESENT])
    late_days = len([a for a in monthly_attendance if a.status == AttendanceStatus.LATE])
    absent_days = len([a for a in monthly_attendance if a.status == AttendanceStatus.ABSENT])
    
    # Leave balance
    leave_balances = db.query(LeaveBalance).filter(
        and_(
            LeaveBalance.employee_id == current_user.employee_id,
            LeaveBalance.year == current_year
        )
    ).all()
    
    total_leave_balance = sum([float(b.remaining_days or 0) for b in leave_balances])
    
    # Pending leave applications
    pending_leaves = db.query(func.count(LeaveApplication.leave_application_id)).filter(
        and_(
            LeaveApplication.employee_id == current_user.employee_id,
            LeaveApplication.status == LeaveStatus.PENDING
        )
    ).scalar()
    
    # Raves received
    raves_received = db.query(func.count(Rave.rave_id)).filter(
        Rave.to_employee_id == current_user.employee_id
    ).scalar()
    
    # Upcoming holidays
    upcoming_holidays = db.query(Holiday).filter(
        Holiday.holiday_date >= today
    ).order_by(Holiday.holiday_date).limit(5).all()
    
    return {
        "today_attendance": {
            "clocked_in": today_attendance.clock_in_time is not None if today_attendance else False,
            "clocked_out": today_attendance.clock_out_time is not None if today_attendance else False,
            "clock_in_time": str(today_attendance.clock_in_time) if today_attendance and today_attendance.clock_in_time else None,
            "clock_out_time": str(today_attendance.clock_out_time) if today_attendance and today_attendance.clock_out_time else None,
            "status": today_attendance.status.value if today_attendance else None
        },
        "monthly_attendance": {
            "present_days": present_days,
            "late_days": late_days,
            "absent_days": absent_days,
            "total_days": len(monthly_attendance)
        },
        "leave_summary": {
            "total_balance": total_leave_balance,
            "pending_applications": pending_leaves or 0
        },
        "raves_received": raves_received or 0,
        "upcoming_holidays": [
            {
                "holiday_date": h.holiday_date,
                "holiday_name": h.holiday_name,
                "is_optional": h.is_optional
            }
            for h in upcoming_holidays
        ]
    }


@router.get("/manager/stats")
def get_manager_dashboard_stats(
    current_user: Employee = Depends(get_current_manager_or_admin),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics for managers (team overview)"""
    today = date.today()
    current_year = today.year
    current_month = today.month
    
    # Get subordinates
    subordinate_ids = [emp.employee_id for emp in current_user.subordinates]
    
    if not subordinate_ids:
        return {
            "team_size": 0,
            "today_attendance": {
                "present": 0,
                "late": 0,
                "absent": 0,
                "on_leave": 0
            },
            "pending_leave_approvals": 0,
            "monthly_attendance_rate": 0
        }
    
    # Today's team attendance
    today_attendance = db.query(Attendance).filter(
        and_(
            Attendance.employee_id.in_(subordinate_ids),
            Attendance.attendance_date == today
        )
    ).all()
    
    today_present = len([a for a in today_attendance if a.status == AttendanceStatus.PRESENT])
    today_late = len([a for a in today_attendance if a.status == AttendanceStatus.LATE])
    today_absent = len([a for a in today_attendance if a.status == AttendanceStatus.ABSENT])
    today_on_leave = len([a for a in today_attendance if a.status == AttendanceStatus.ON_LEAVE])
    
    # Pending leave approvals
    pending_leaves = db.query(func.count(LeaveApplication.leave_application_id)).filter(
        and_(
            LeaveApplication.employee_id.in_(subordinate_ids),
            LeaveApplication.status == LeaveStatus.PENDING
        )
    ).scalar()
    
    # Monthly attendance rate
    monthly_attendance = db.query(Attendance).filter(
        and_(
            Attendance.employee_id.in_(subordinate_ids),
            extract('year', Attendance.attendance_date) == current_year,
            extract('month', Attendance.attendance_date) == current_month
        )
    ).all()
    
    total_possible = len(subordinate_ids) * today.day
    total_present = len([a for a in monthly_attendance if a.status in [AttendanceStatus.PRESENT, AttendanceStatus.LATE]])
    attendance_rate = (total_present / total_possible * 100) if total_possible > 0 else 0
    
    return {
        "team_size": len(subordinate_ids),
        "today_attendance": {
            "present": today_present,
            "late": today_late,
            "absent": today_absent,
            "on_leave": today_on_leave
        },
        "pending_leave_approvals": pending_leaves or 0,
        "monthly_attendance_rate": round(attendance_rate, 2)
    }


@router.get("/admin/stats")
def get_admin_dashboard_stats(
    current_user: Employee = Depends(get_current_manager_or_admin),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics for admins (company-wide overview)"""
    today = date.today()
    current_year = today.year
    current_month = today.month
    
    # Total employees
    total_employees = db.query(func.count(Employee.employee_id)).filter(
        Employee.is_active == True
    ).scalar()
    
    # Today's attendance
    today_attendance = db.query(Attendance).filter(
        Attendance.attendance_date == today
    ).all()
    
    today_present = len([a for a in today_attendance if a.status == AttendanceStatus.PRESENT])
    today_late = len([a for a in today_attendance if a.status == AttendanceStatus.LATE])
    today_absent = total_employees - len(today_attendance)
    today_on_leave = len([a for a in today_attendance if a.status == AttendanceStatus.ON_LEAVE])
    
    # Pending leave applications
    pending_leaves = db.query(func.count(LeaveApplication.leave_application_id)).filter(
        LeaveApplication.status == LeaveStatus.PENDING
    ).scalar()
    
    # Monthly statistics
    monthly_attendance = db.query(Attendance).filter(
        and_(
            extract('year', Attendance.attendance_date) == current_year,
            extract('month', Attendance.attendance_date) == current_month
        )
    ).all()
    
    total_possible = total_employees * today.day
    total_present = len([a for a in monthly_attendance if a.status in [AttendanceStatus.PRESENT, AttendanceStatus.LATE]])
    attendance_rate = (total_present / total_possible * 100) if total_possible > 0 else 0
    
    # Total raves this month
    monthly_raves = db.query(func.count(Rave.rave_id)).filter(
        and_(
            extract('year', Rave.created_at) == current_year,
            extract('month', Rave.created_at) == current_month
        )
    ).scalar()
    
    return {
        "total_employees": total_employees or 0,
        "today_attendance": {
            "present": today_present,
            "late": today_late,
            "absent": today_absent,
            "on_leave": today_on_leave
        },
        "pending_leave_applications": pending_leaves or 0,
        "monthly_attendance_rate": round(attendance_rate, 2),
        "monthly_raves": monthly_raves or 0
    }


@router.get("/recent-activities")
def get_recent_activities(
    limit: int = Query(10, ge=1, le=50),
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent activities for current user"""
    activities = []
    
    # Recent attendance (last 7 days)
    seven_days_ago = date.today() - timedelta(days=7)
    recent_attendance = db.query(Attendance).filter(
        and_(
            Attendance.employee_id == current_user.employee_id,
            Attendance.attendance_date >= seven_days_ago
        )
    ).order_by(Attendance.attendance_date.desc()).limit(5).all()
    
    for att in recent_attendance:
        activities.append({
            "type": "attendance",
            "date": att.attendance_date,
            "description": f"Attendance marked as {att.status.value}",
            "timestamp": att.created_at
        })
    
    # Recent leave applications
    recent_leaves = db.query(LeaveApplication).filter(
        LeaveApplication.employee_id == current_user.employee_id
    ).order_by(LeaveApplication.applied_on.desc()).limit(5).all()
    
    for leave in recent_leaves:
        activities.append({
            "type": "leave",
            "date": leave.applied_on.date(),
            "description": f"Leave application {leave.status.value}: {leave.start_date} to {leave.end_date}",
            "timestamp": leave.applied_on
        })
    
    # Recent raves received
    recent_raves = db.query(Rave).filter(
        Rave.to_employee_id == current_user.employee_id
    ).order_by(Rave.created_at.desc()).limit(5).all()
    
    for rave in recent_raves:
        sender = db.query(Employee).filter(Employee.employee_id == rave.from_employee_id).first()
        sender_name = "Anonymous" if rave.is_anonymous else (sender.full_name if sender else "Unknown")
        
        activities.append({
            "type": "rave",
            "date": rave.created_at.date(),
            "description": f"Received rave from {sender_name}",
            "timestamp": rave.created_at
        })
    
    # Sort by timestamp and limit
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    return activities[:limit]
