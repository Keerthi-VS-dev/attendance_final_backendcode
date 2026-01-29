from typing import Optional
from sqlalchemy.orm import Session
from app.models.notification import Notification, NotificationType


class NotificationService:
    """Service class for notification-related business logic"""
    
    @staticmethod
    def create_notification(
        db: Session,
        employee_id: int,
        title: str,
        message: str,
        notification_type: NotificationType,
        link: Optional[str] = None
    ) -> Notification:
        """Create a new notification"""
        notification = Notification(
            employee_id=employee_id,
            title=title,
            message=message,
            type=notification_type,
            link=link
        )
        db.add(notification)
        db.flush()  # Get the ID without committing
        return notification
    
    @staticmethod
    def mark_as_read(db: Session, notification_id: int, employee_id: int) -> bool:
        """Mark a notification as read"""
        notification = db.query(Notification).filter(
            Notification.notification_id == notification_id,
            Notification.employee_id == employee_id
        ).first()
        
        if notification:
            notification.is_read = True
            return True
        
        return False
    
    @staticmethod
    def mark_all_as_read(db: Session, employee_id: int) -> int:
        """Mark all notifications as read for an employee"""
        count = db.query(Notification).filter(
            Notification.employee_id == employee_id,
            Notification.is_read == False
        ).update({"is_read": True})
        
        return count
    
    @staticmethod
    def get_unread_count(db: Session, employee_id: int) -> int:
        """Get count of unread notifications for an employee"""
        return db.query(Notification).filter(
            Notification.employee_id == employee_id,
            Notification.is_read == False
        ).count()
    
    @staticmethod
    def create_leave_notification(
        db: Session,
        employee_id: int,
        applicant_name: str,
        leave_type: str,
        start_date: str,
        end_date: str,
        action: str = "applied",
        link: Optional[str] = None
    ) -> Notification:
        """Create a leave-related notification"""
        if action == "applied":
            title = "New Leave Application"
            message = f"{applicant_name} has applied for {leave_type} from {start_date} to {end_date}"
        elif action == "approved":
            title = "Leave Application Approved"
            message = f"Your {leave_type} application from {start_date} to {end_date} has been approved"
        elif action == "rejected":
            title = "Leave Application Rejected"
            message = f"Your {leave_type} application from {start_date} to {end_date} has been rejected"
        elif action == "cancelled":
            title = "Leave Application Cancelled"
            message = f"{applicant_name} has cancelled their {leave_type} application from {start_date} to {end_date}"
        else:
            title = "Leave Update"
            message = f"Leave application status updated: {action}"
        
        return NotificationService.create_notification(
            db=db,
            employee_id=employee_id,
            title=title,
            message=message,
            notification_type=NotificationType.LEAVE,
            link=link
        )
    
    @staticmethod
    def create_rave_notification(
        db: Session,
        employee_id: int,
        sender_name: str,
        category: str,
        is_anonymous: bool = False,
        link: Optional[str] = None
    ) -> Notification:
        """Create a rave-related notification"""
        if is_anonymous:
            title = "New Anonymous Rave"
            message = f"You received an anonymous {category} rave!"
        else:
            title = "New Rave"
            message = f"{sender_name} sent you a {category} rave!"
        
        return NotificationService.create_notification(
            db=db,
            employee_id=employee_id,
            title=title,
            message=message,
            notification_type=NotificationType.RAVE,
            link=link
        )