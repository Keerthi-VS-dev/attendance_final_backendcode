from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from typing import List, Optional
from app.database import get_db
from app.models.employee import Employee
from app.models.rave import Rave, RaveCategory
from app.models.notification import Notification, NotificationType
from app.schemas.rave import (
    RaveCategoryCreate,
    RaveCategoryResponse,
    RaveCreate,
    RaveResponse
)
from app.dependencies import get_current_user, get_current_admin

router = APIRouter()


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


# Rave Category Endpoints
@router.get("/categories", response_model=List[RaveCategoryResponse])
def get_rave_categories(
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all rave categories"""
    categories = db.query(RaveCategory).all()
    return categories


@router.post("/categories", response_model=RaveCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_rave_category(
    category: RaveCategoryCreate,
    current_user: Employee = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new rave category (Admin only)"""
    # Check if category already exists
    existing = db.query(RaveCategory).filter(
        RaveCategory.category_name == category.category_name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already exists"
        )
    
    db_category = RaveCategory(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return db_category


# Rave Endpoints
@router.post("/", response_model=RaveResponse, status_code=status.HTTP_201_CREATED)
def send_rave(
    rave: RaveCreate,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a rave/appreciation to another employee"""
    # Check if recipient exists
    recipient = db.query(Employee).filter(Employee.employee_id == rave.to_employee_id).first()
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient employee not found"
        )
    
    # Check if trying to rave yourself
    if rave.to_employee_id == current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot send rave to yourself"
        )
    
    # Verify category exists if provided
    if rave.category_id:
        category = db.query(RaveCategory).filter(
            RaveCategory.category_id == rave.category_id
        ).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rave category not found"
            )
    
    # Create rave
    db_rave = Rave(
        from_employee_id=current_user.employee_id,
        to_employee_id=rave.to_employee_id,
        category_id=rave.category_id,
        message=rave.message,
        is_anonymous=rave.is_anonymous
    )
    
    db.add(db_rave)
    db.commit()
    db.refresh(db_rave)
    
    # Create notification for recipient
    sender_name = "Anonymous" if rave.is_anonymous else current_user.full_name
    category = None
    category_text = ""
    if rave.category_id:
        category = db.query(RaveCategory).filter(RaveCategory.category_id == rave.category_id).first()
        category_text = f" for {category.category_name}" if category else ""
    
    create_notification(
        db=db,
        employee_id=rave.to_employee_id,
        title="New Rave Received!",
        message=f"{sender_name} sent you a rave{category_text}!",
        notification_type=NotificationType.RAVE,
        link=f"/raves/{db_rave.rave_id}"
    )
    
    db.commit()
    
    # Prepare response
    return {
        "rave_id": db_rave.rave_id,
        "from_employee_id": db_rave.from_employee_id,
        "to_employee_id": db_rave.to_employee_id,
        "category_id": db_rave.category_id,
        "message": db_rave.message,
        "is_anonymous": db_rave.is_anonymous,
        "created_at": db_rave.created_at,
        "sender_name": None if rave.is_anonymous else current_user.full_name,
        "recipient_name": recipient.full_name,
        "category_name": category.category_name if category else None
    }


@router.get("/", response_model=List[RaveResponse])
def get_raves(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    to_employee_id: Optional[int] = None,
    from_employee_id: Optional[int] = None,
    category_id: Optional[int] = None,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get raves with optional filters"""
    query = db.query(Rave)
    
    # Apply filters
    if to_employee_id:
        query = query.filter(Rave.to_employee_id == to_employee_id)
    
    if from_employee_id:
        query = query.filter(Rave.from_employee_id == from_employee_id)
    
    if category_id:
        query = query.filter(Rave.category_id == category_id)
    
    raves = query.order_by(desc(Rave.created_at)).offset(skip).limit(limit).all()
    
    # Enrich with names
    results = []
    for rave in raves:
        sender = db.query(Employee).filter(Employee.employee_id == rave.from_employee_id).first()
        recipient = db.query(Employee).filter(Employee.employee_id == rave.to_employee_id).first()
        category = None
        if rave.category_id:
            category = db.query(RaveCategory).filter(RaveCategory.category_id == rave.category_id).first()
        
        # Hide sender name if anonymous and not the sender
        sender_name = None
        if not rave.is_anonymous or rave.from_employee_id == current_user.employee_id:
            sender_name = sender.full_name if sender else None
        
        rave_dict = {
            "rave_id": rave.rave_id,
            "from_employee_id": rave.from_employee_id,
            "to_employee_id": rave.to_employee_id,
            "category_id": rave.category_id,
            "message": rave.message,
            "is_anonymous": rave.is_anonymous,
            "created_at": rave.created_at,
            "sender_name": sender_name,
            "recipient_name": recipient.full_name if recipient else None,
            "category_name": category.category_name if category else None
        }
        results.append(rave_dict)
    
    return results


@router.get("/received", response_model=List[RaveResponse])
def get_received_raves(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get raves received by current user"""
    raves = db.query(Rave).filter(
        Rave.to_employee_id == current_user.employee_id
    ).order_by(desc(Rave.created_at)).offset(skip).limit(limit).all()
    
    # Enrich with names
    results = []
    for rave in raves:
        sender = db.query(Employee).filter(Employee.employee_id == rave.from_employee_id).first()
        category = None
        if rave.category_id:
            category = db.query(RaveCategory).filter(RaveCategory.category_id == rave.category_id).first()
        
        sender_name = None if rave.is_anonymous else (sender.full_name if sender else None)
        
        rave_dict = {
            "rave_id": rave.rave_id,
            "from_employee_id": rave.from_employee_id,
            "to_employee_id": rave.to_employee_id,
            "category_id": rave.category_id,
            "message": rave.message,
            "is_anonymous": rave.is_anonymous,
            "created_at": rave.created_at,
            "sender_name": sender_name,
            "recipient_name": current_user.full_name,
            "category_name": category.category_name if category else None
        }
        results.append(rave_dict)
    
    return results


@router.get("/sent", response_model=List[RaveResponse])
def get_sent_raves(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get raves sent by current user"""
    raves = db.query(Rave).filter(
        Rave.from_employee_id == current_user.employee_id
    ).order_by(desc(Rave.created_at)).offset(skip).limit(limit).all()
    
    # Enrich with names
    results = []
    for rave in raves:
        recipient = db.query(Employee).filter(Employee.employee_id == rave.to_employee_id).first()
        category = None
        if rave.category_id:
            category = db.query(RaveCategory).filter(RaveCategory.category_id == rave.category_id).first()
        
        rave_dict = {
            "rave_id": rave.rave_id,
            "from_employee_id": rave.from_employee_id,
            "to_employee_id": rave.to_employee_id,
            "category_id": rave.category_id,
            "message": rave.message,
            "is_anonymous": rave.is_anonymous,
            "created_at": rave.created_at,
            "sender_name": current_user.full_name,
            "recipient_name": recipient.full_name if recipient else None,
            "category_name": category.category_name if category else None
        }
        results.append(rave_dict)
    
    return results


@router.get("/employee/{employee_id}", response_model=List[RaveResponse])
def get_employee_raves(
    employee_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get raves received by a specific employee"""
    # Check if employee exists
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    raves = db.query(Rave).filter(
        Rave.to_employee_id == employee_id
    ).order_by(desc(Rave.created_at)).offset(skip).limit(limit).all()
    
    # Enrich with names
    results = []
    for rave in raves:
        sender = db.query(Employee).filter(Employee.employee_id == rave.from_employee_id).first()
        category = None
        if rave.category_id:
            category = db.query(RaveCategory).filter(RaveCategory.category_id == rave.category_id).first()
        
        sender_name = None if rave.is_anonymous else (sender.full_name if sender else None)
        
        rave_dict = {
            "rave_id": rave.rave_id,
            "from_employee_id": rave.from_employee_id,
            "to_employee_id": rave.to_employee_id,
            "category_id": rave.category_id,
            "message": rave.message,
            "is_anonymous": rave.is_anonymous,
            "created_at": rave.created_at,
            "sender_name": sender_name,
            "recipient_name": employee.full_name,
            "category_name": category.category_name if category else None
        }
        results.append(rave_dict)
    
    return results


@router.get("/{rave_id}", response_model=RaveResponse)
def get_rave(
    rave_id: int,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific rave by ID"""
    rave = db.query(Rave).filter(Rave.rave_id == rave_id).first()
    
    if not rave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rave not found"
        )
    
    # Enrich with names
    sender = db.query(Employee).filter(Employee.employee_id == rave.from_employee_id).first()
    recipient = db.query(Employee).filter(Employee.employee_id == rave.to_employee_id).first()
    category = None
    if rave.category_id:
        category = db.query(RaveCategory).filter(RaveCategory.category_id == rave.category_id).first()
    
    # Show sender name if not anonymous or if current user is the sender
    sender_name = None
    if not rave.is_anonymous or rave.from_employee_id == current_user.employee_id:
        sender_name = sender.full_name if sender else None
    
    rave_dict = {
        "rave_id": rave.rave_id,
        "from_employee_id": rave.from_employee_id,
        "to_employee_id": rave.to_employee_id,
        "category_id": rave.category_id,
        "message": rave.message,
        "is_anonymous": rave.is_anonymous,
        "created_at": rave.created_at,
        "sender_name": sender_name,
        "recipient_name": recipient.full_name if recipient else None,
        "category_name": category.category_name if category else None
    }
    
    return rave_dict


@router.get("/statistics/leaderboard")
def get_rave_leaderboard(
    limit: int = Query(10, ge=1, le=50),
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get top employees by rave count"""
    # Query to get rave counts
    rave_counts = db.query(
        Rave.to_employee_id,
        func.count(Rave.rave_id).label('rave_count')
    ).group_by(Rave.to_employee_id).order_by(desc('rave_count')).limit(limit).all()
    
    # Get employee details
    results = []
    for to_employee_id, count in rave_counts:
        employee = db.query(Employee).filter(Employee.employee_id == to_employee_id).first()
        if employee:
            results.append({
                "employee_id": employee.employee_id,
                "employee_name": employee.full_name,
                "designation": employee.designation,
                "department_id": employee.department_id,
                "rave_count": count
            })
    
    return results
