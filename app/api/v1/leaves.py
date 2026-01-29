from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, extract, func
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from app.database import get_db
from app.models.employee import Employee, UserRole
from app.models.leave import LeaveType, LeaveBalance, LeaveApplication, LeaveStatus
from app.models.notification import Notification, NotificationType
from app.schemas.leave import (
    LeaveTypeCreate,
    LeaveTypeResponse,
    LeaveBalanceResponse,
    LeaveApplicationCreate,
    LeaveApplicationUpdate,
    LeaveApplicationResponse,
    LeaveApprovalRequest
)
from app.dependencies import get_current_user, get_current_admin, get_current_manager_or_admin

router = APIRouter()


def calculate_leave_days(start_date: date, end_date: date) -> Decimal:
    """Calculate number of leave days (including weekends for now)"""
    days = (end_date - start_date).days + 1
    return Decimal(str(days))


def create_notification(
    db: Session,
    employee_id: int,
    title: str,
    message: str,
    notification_type: NotificationType,
    link: Optional[str] = None
):
    """Helper function to create notifications"""
    notification = Notification(
        employee_id=employee_id,
        title=title,
        message=message,
        type=notification_type,
        link=link
    )
    db.add(notification)


# Leave Types Endpoints
@router.get("/types", response_model=List[LeaveTypeResponse])
def get_leave_types(
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all leave types"""
    leave_types = db.query(LeaveType).all()
    return leave_types


@router.post("/types", response_model=LeaveTypeResponse, status_code=status.HTTP_201_CREATED)
def create_leave_type(
    leave_type: LeaveTypeCreate,
    current_user: Employee = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new leave type (Admin only)"""
    # Check if leave type already exists
    existing = db.query(LeaveType).filter(LeaveType.type_name == leave_type.type_name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Leave type already exists"
        )
    
    db_leave_type = LeaveType(**leave_type.model_dump())
    db.add(db_leave_type)
    db.commit()
    db.refresh(db_leave_type)
    
    return db_leave_type


# Leave Balance Endpoints
@router.get("/balance", response_model=List[LeaveBalanceResponse])
def get_my_leave_balance(
    year: Optional[int] = Query(None),
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's leave balance"""
    if not year:
        year = datetime.now().year
    
    balances = db.query(LeaveBalance).filter(
        and_(
            LeaveBalance.employee_id == current_user.employee_id,
            LeaveBalance.year == year
        )
    ).all()
    
    # Enrich with leave type names
    results = []
    for balance in balances:
        leave_type = db.query(LeaveType).filter(
            LeaveType.leave_type_id == balance.leave_type_id
        ).first()
        
        balance_dict = {
            **balance.__dict__,
            "leave_type_name": leave_type.type_name if leave_type else None
        }
        results.append(balance_dict)
    
    return results


@router.get("/balance/employee/{employee_id}", response_model=List[LeaveBalanceResponse])
def get_employee_leave_balance(
    employee_id: int,
    year: Optional[int] = Query(None),
    current_user: Employee = Depends(get_current_manager_or_admin),
    db: Session = Depends(get_db)
):
    """Get leave balance for a specific employee (Manager/Admin only)"""
    if not year:
        year = datetime.now().year
    
    # Check if employee exists
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    balances = db.query(LeaveBalance).filter(
        and_(
            LeaveBalance.employee_id == employee_id,
            LeaveBalance.year == year
        )
    ).all()
    
    # Enrich with leave type names
    results = []
    for balance in balances:
        leave_type = db.query(LeaveType).filter(
            LeaveType.leave_type_id == balance.leave_type_id
        ).first()
        
        balance_dict = {
            **balance.__dict__,
            "leave_type_name": leave_type.type_name if leave_type else None
        }
        results.append(balance_dict)
    
    return results


# Leave Application Endpoints
@router.get("/applications", response_model=List[LeaveApplicationResponse])
def get_my_leave_applications(
    status_filter: Optional[LeaveStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's leave applications"""
    query = db.query(LeaveApplication).filter(LeaveApplication.employee_id == current_user.employee_id)
    
    if status_filter:
        query = query.filter(LeaveApplication.status == status_filter)
    
    applications = query.order_by(LeaveApplication.applied_on.desc()).offset(skip).limit(limit).all()
    
    # Enrich with names
    results = []
    for app in applications:
        leave_type = db.query(LeaveType).filter(LeaveType.leave_type_id == app.leave_type_id).first()
        approver = None
        if app.approved_by:
            approver = db.query(Employee).filter(Employee.employee_id == app.approved_by).first()
        
        app_dict = {
            **app.__dict__,
            "employee_name": current_user.full_name,
            "leave_type_name": leave_type.type_name if leave_type else None,
            "approver_name": approver.full_name if approver else None
        }
        results.append(app_dict)
    
    return results


@router.get("/applications/pending", response_model=List[LeaveApplicationResponse])
def get_pending_leave_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: Employee = Depends(get_current_manager_or_admin),
    db: Session = Depends(get_db)
):
    """Get pending leave applications for approval (Manager/Admin only)"""
    # Get subordinates if manager
    if current_user.role == UserRole.MANAGER:
        subordinate_ids = [emp.employee_id for emp in current_user.subordinates]
        query = db.query(LeaveApplication).filter(
            and_(
                LeaveApplication.employee_id.in_(subordinate_ids),
                LeaveApplication.status == LeaveStatus.PENDING
            )
        )
    else:
        # Admin can see all pending applications
        query = db.query(LeaveApplication).filter(LeaveApplication.status == LeaveStatus.PENDING)
    
    applications = query.order_by(LeaveApplication.applied_on.desc()).offset(skip).limit(limit).all()
    
    # Enrich with names
    results = []
    for app in applications:
        employee = db.query(Employee).filter(Employee.employee_id == app.employee_id).first()
        leave_type = db.query(LeaveType).filter(LeaveType.leave_type_id == app.leave_type_id).first()
        
        app_dict = {
            **app.__dict__,
            "employee_name": employee.full_name if employee else None,
            "leave_type_name": leave_type.type_name if leave_type else None,
            "approver_name": None
        }
        results.append(app_dict)
    
    return results


@router.post("/applications", response_model=LeaveApplicationResponse, status_code=status.HTTP_201_CREATED)
def apply_for_leave(
    leave_app: LeaveApplicationCreate,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Apply for leave"""
    # Validate leave type exists
    leave_type = db.query(LeaveType).filter(LeaveType.leave_type_id == leave_app.leave_type_id).first()
    if not leave_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave type not found"
        )
    
    # Calculate leave days
    total_days = calculate_leave_days(leave_app.start_date, leave_app.end_date)
    
    # Check leave balance
    year = leave_app.start_date.year
    balance = db.query(LeaveBalance).filter(
        and_(
            LeaveBalance.employee_id == current_user.employee_id,
            LeaveBalance.leave_type_id == leave_app.leave_type_id,
            LeaveBalance.year == year
        )
    ).first()
    
    if balance and balance.remaining_days < total_days:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient leave balance. Available: {balance.remaining_days} days"
        )
    
    # Create leave application
    db_application = LeaveApplication(
        employee_id=current_user.employee_id,
        leave_type_id=leave_app.leave_type_id,
        start_date=leave_app.start_date,
        end_date=leave_app.end_date,
        total_days=total_days,
        reason=leave_app.reason,
        attachments=leave_app.attachments,
        status=LeaveStatus.PENDING
    )
    
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    
    # Create notification for manager
    if current_user.manager_id:
        try:
            employee_full_name = getattr(current_user, 'full_name', f"{current_user.first_name} {current_user.last_name}")
            create_notification(
                db=db,
                employee_id=current_user.manager_id,
                title="New Leave Application",
                message=f"{employee_full_name} has applied for {leave_type.type_name} from {leave_app.start_date} to {leave_app.end_date}",
                notification_type=NotificationType.LEAVE,
                link=f"/leaves/applications/{db_application.leave_application_id}"
            )
        except Exception:
            # Don't fail the whole request if notification fails
            pass
    
    db.commit()
    
    # Prepare response
    employee_full_name = getattr(current_user, 'full_name', f"{current_user.first_name} {current_user.last_name}")
    
    return {
        "leave_application_id": db_application.leave_application_id,
        "employee_id": db_application.employee_id,
        "leave_type_id": db_application.leave_type_id,
        "start_date": db_application.start_date,
        "end_date": db_application.end_date,
        "total_days": db_application.total_days,
        "reason": db_application.reason,
        "status": db_application.status,
        "approved_by": db_application.approved_by,
        "applied_on": db_application.applied_on,
        "approved_rejected_on": db_application.approved_rejected_on,
        "rejection_reason": db_application.rejection_reason,
        "attachments": db_application.attachments,
        "created_at": db_application.created_at,
        "updated_at": db_application.updated_at,
        "employee_name": employee_full_name,
        "leave_type_name": leave_type.type_name,
        "approver_name": None
    }


@router.get("/applications/{application_id}", response_model=LeaveApplicationResponse)
def get_leave_application(
    application_id: int,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get leave application by ID"""
    application = db.query(LeaveApplication).filter(
        LeaveApplication.leave_application_id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave application not found"
        )
    
    # Check permissions
    is_own_application = application.employee_id == current_user.employee_id
    is_manager_of_applicant = current_user.employee_id in [emp.manager_id for emp in [db.query(Employee).filter(Employee.employee_id == application.employee_id).first()]]
    is_admin = current_user.role == UserRole.ADMIN
    
    if not (is_own_application or is_manager_of_applicant or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this application"
        )
    
    # Enrich with names
    employee = db.query(Employee).filter(Employee.employee_id == application.employee_id).first()
    leave_type = db.query(LeaveType).filter(LeaveType.leave_type_id == application.leave_type_id).first()
    approver = None
    if application.approved_by:
        approver = db.query(Employee).filter(Employee.employee_id == application.approved_by).first()
    
    app_dict = {
        **application.__dict__,
        "employee_name": employee.full_name if employee else None,
        "leave_type_name": leave_type.type_name if leave_type else None,
        "approver_name": approver.full_name if approver else None
    }
    
    return app_dict


@router.put("/applications/{application_id}/approve", response_model=LeaveApplicationResponse)
def approve_leave(
    application_id: int,
    approval_request: LeaveApprovalRequest,
    current_user: Employee = Depends(get_current_manager_or_admin),
    db: Session = Depends(get_db)
):
    """Approve or reject a leave application (Manager/Admin only)"""
    application = db.query(LeaveApplication).filter(
        LeaveApplication.leave_application_id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave application not found"
        )
    
    if application.status != LeaveStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot modify application with status: {application.status}"
        )
    
    # Update application
    application.status = approval_request.status
    application.approved_by = current_user.employee_id
    application.approved_rejected_on = datetime.now()
    
    if approval_request.status == LeaveStatus.REJECTED:
        application.rejection_reason = approval_request.rejection_reason
    
    # Update leave balance if approved
    if approval_request.status == LeaveStatus.APPROVED:
        year = application.start_date.year
        balance = db.query(LeaveBalance).filter(
            and_(
                LeaveBalance.employee_id == application.employee_id,
                LeaveBalance.leave_type_id == application.leave_type_id,
                LeaveBalance.year == year
            )
        ).first()
        
        if balance:
            balance.used_days += application.total_days
            balance.remaining_days = balance.total_allocated - balance.used_days
    
    # Create notification for employee
    employee = db.query(Employee).filter(Employee.employee_id == application.employee_id).first()
    leave_type = db.query(LeaveType).filter(LeaveType.leave_type_id == application.leave_type_id).first()
    
    status_text = "approved" if approval_request.status == LeaveStatus.APPROVED else "rejected"
    create_notification(
        db=db,
        employee_id=application.employee_id,
        title=f"Leave Application {status_text.capitalize()}",
        message=f"Your {leave_type.type_name} application from {application.start_date} to {application.end_date} has been {status_text} by {current_user.full_name}",
        notification_type=NotificationType.LEAVE,
        link=f"/leaves/applications/{application_id}"
    )
    
    db.commit()
    db.refresh(application)
    
    # Prepare response
    response_dict = {
        **application.__dict__,
        "employee_name": employee.full_name if employee else None,
        "leave_type_name": leave_type.type_name if leave_type else None,
        "approver_name": current_user.full_name
    }
    
    return response_dict


@router.put("/applications/{application_id}/cancel", response_model=LeaveApplicationResponse)
def cancel_leave(
    application_id: int,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a leave application"""
    application = db.query(LeaveApplication).filter(
        LeaveApplication.leave_application_id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave application not found"
        )
    
    # Check if user owns this application
    if application.employee_id != current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this application"
        )
    
    if application.status not in [LeaveStatus.PENDING, LeaveStatus.APPROVED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel application with status: {application.status}"
        )
    
    # If already approved, restore leave balance
    if application.status == LeaveStatus.APPROVED:
        year = application.start_date.year
        balance = db.query(LeaveBalance).filter(
            and_(
                LeaveBalance.employee_id == application.employee_id,
                LeaveBalance.leave_type_id == application.leave_type_id,
                LeaveBalance.year == year
            )
        ).first()
        
        if balance:
            balance.used_days -= application.total_days
            balance.remaining_days = balance.total_allocated - balance.used_days
    
    # Update status
    application.status = LeaveStatus.CANCELLED
    
    # Notify manager if it was pending
    if current_user.manager_id:
        leave_type = db.query(LeaveType).filter(LeaveType.leave_type_id == application.leave_type_id).first()
        create_notification(
            db=db,
            employee_id=current_user.manager_id,
            title="Leave Application Cancelled",
            message=f"{current_user.full_name} has cancelled their {leave_type.type_name} application from {application.start_date} to {application.end_date}",
            notification_type=NotificationType.LEAVE,
            link=f"/leaves/applications/{application_id}"
        )
    
    db.commit()
    db.refresh(application)
    
    # Prepare response
    leave_type = db.query(LeaveType).filter(LeaveType.leave_type_id == application.leave_type_id).first()
    approver = None
    if application.approved_by:
        approver = db.query(Employee).filter(Employee.employee_id == application.approved_by).first()
    
    response_dict = {
        **application.__dict__,
        "employee_name": current_user.full_name,
        "leave_type_name": leave_type.type_name if leave_type else None,
        "approver_name": approver.full_name if approver else None
    }
    
    return response_dict


@router.put("/applications/{application_id}", response_model=LeaveApplicationResponse)
def update_leave_application(
    application_id: int,
    leave_update: LeaveApplicationUpdate,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a pending leave application"""
    application = db.query(LeaveApplication).filter(
        LeaveApplication.leave_application_id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave application not found"
        )
    
    # Check if user owns this application
    if application.employee_id != current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this application"
        )
    
    if application.status != LeaveStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only update pending applications"
        )
    
    # Update fields
    update_data = leave_update.model_dump(exclude_unset=True)
    
    # Recalculate days if dates changed
    if 'start_date' in update_data or 'end_date' in update_data:
        start = update_data.get('start_date', application.start_date)
        end = update_data.get('end_date', application.end_date)
        update_data['total_days'] = calculate_leave_days(start, end)
    
    for field, value in update_data.items():
        setattr(application, field, value)
    
    db.commit()
    db.refresh(application)
    
    # Prepare response
    leave_type = db.query(LeaveType).filter(LeaveType.leave_type_id == application.leave_type_id).first()
    
    response_dict = {
        **application.__dict__,
        "employee_name": current_user.full_name,
        "leave_type_name": leave_type.type_name if leave_type else None,
        "approver_name": None
    }
    
    return response_dict
