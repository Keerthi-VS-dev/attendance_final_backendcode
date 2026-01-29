"""
Script to seed the database with initial data
Run with: python seed_data.py
"""
import sys
from datetime import date, datetime
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine, Base
from app.models.employee import Employee, UserRole
from app.models.department import Department
from app.models.leave import LeaveType, LeaveBalance
from app.models.rave import RaveCategory
from app.models.holiday import Holiday
from app.utils.security import get_password_hash


def create_tables():
    """Create all tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")


def seed_departments(db: Session):
    """Seed departments"""
    print("\nSeeding departments...")
    
    departments = [
        Department(department_name="Engineering", description="Software Development and Engineering"),
        Department(department_name="Human Resources", description="HR and People Operations"),
        Department(department_name="Sales", description="Sales and Business Development"),
        Department(department_name="Marketing", description="Marketing and Communications"),
        Department(department_name="Finance", description="Finance and Accounting"),
        Department(department_name="Operations", description="Operations and Logistics"),
    ]
    
    for dept in departments:
        existing = db.query(Department).filter(Department.department_name == dept.department_name).first()
        if not existing:
            db.add(dept)
            print(f"  ✓ Added department: {dept.department_name}")
    
    db.commit()
    print("✓ Departments seeded successfully")


def seed_leave_types(db: Session):
    """Seed leave types"""
    print("\nSeeding leave types...")
    
    leave_types = [
        LeaveType(
            type_name="Annual Leave",
            description="Paid annual vacation leave",
            max_days_per_year=20,
            requires_approval=True,
            is_paid=True
        ),
        LeaveType(
            type_name="Sick Leave",
            description="Paid sick leave",
            max_days_per_year=12,
            requires_approval=True,
            is_paid=True
        ),
        LeaveType(
            type_name="Casual Leave",
            description="Casual leave for personal reasons",
            max_days_per_year=10,
            requires_approval=True,
            is_paid=True
        ),
        LeaveType(
            type_name="Work From Home",
            description="Work from home day",
            max_days_per_year=50,
            requires_approval=True,
            is_paid=True
        ),
        LeaveType(
            type_name="Unpaid Leave",
            description="Unpaid leave",
            max_days_per_year=30,
            requires_approval=True,
            is_paid=False
        ),
    ]
    
    for leave_type in leave_types:
        existing = db.query(LeaveType).filter(LeaveType.type_name == leave_type.type_name).first()
        if not existing:
            db.add(leave_type)
            print(f"  ✓ Added leave type: {leave_type.type_name}")
    
    db.commit()
    print("✓ Leave types seeded successfully")


def seed_rave_categories(db: Session):
    """Seed rave categories"""
    print("\nSeeding rave categories...")
    
    categories = [
        RaveCategory(category_name="Teamwork", description="Excellent teamwork and collaboration", icon="👥"),
        RaveCategory(category_name="Innovation", description="Innovative thinking and creativity", icon="💡"),
        RaveCategory(category_name="Leadership", description="Outstanding leadership qualities", icon="⭐"),
        RaveCategory(category_name="Excellence", description="Excellence in work quality", icon="🏆"),
        RaveCategory(category_name="Helpful", description="Being helpful to others", icon="🤝"),
        RaveCategory(category_name="Problem Solver", description="Great problem-solving skills", icon="🔧"),
    ]
    
    for category in categories:
        existing = db.query(RaveCategory).filter(RaveCategory.category_name == category.category_name).first()
        if not existing:
            db.add(category)
            print(f"  ✓ Added rave category: {category.category_name}")
    
    db.commit()
    print("✓ Rave categories seeded successfully")


def seed_admin_user(db: Session):
    """Seed admin user"""
    print("\nSeeding admin user...")
    
    # Check if admin exists
    admin = db.query(Employee).filter(Employee.email == "admin@izone.com").first()
    
    if not admin:
        # Get first department
        dept = db.query(Department).first()
        
        admin = Employee(
            email="admin@izone.com",
            password_hash=get_password_hash("admin123"),  # Change this password!
            first_name="Admin",
            last_name="User",
            phone="+1234567890",
            date_of_birth=date(1990, 1, 1),
            joining_date=date(2020, 1, 1),
            designation="System Administrator",
            department_id=dept.department_id if dept else None,
            role=UserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        print("  ✓ Admin user created")
        print(f"    Email: admin@izone.com")
        print(f"    Password: admin123")
        print("    ⚠️  IMPORTANT: Change this password immediately!")
    else:
        print("  ℹ️  Admin user already exists")
    
    print("✓ Admin user seeded successfully")


def seed_sample_employees(db: Session):
    """Seed sample employees"""
    print("\nSeeding sample employees...")
    
    # Get departments
    eng_dept = db.query(Department).filter(Department.department_name == "Engineering").first()
    hr_dept = db.query(Department).filter(Department.department_name == "Human Resources").first()
    
    sample_employees = [
        {
            "email": "manager@izone.com",
            "password": "manager123",
            "first_name": "John",
            "last_name": "Manager",
            "phone": "+1234567891",
            "date_of_birth": date(1985, 5, 15),
            "joining_date": date(2021, 3, 1),
            "designation": "Engineering Manager",
            "department_id": eng_dept.department_id if eng_dept else None,
            "role": UserRole.MANAGER,
        },
        {
            "email": "employee1@izone.com",
            "password": "employee123",
            "first_name": "Alice",
            "last_name": "Developer",
            "phone": "+1234567892",
            "date_of_birth": date(1992, 8, 20),
            "joining_date": date(2022, 1, 15),
            "designation": "Senior Developer",
            "department_id": eng_dept.department_id if eng_dept else None,
            "role": UserRole.EMPLOYEE,
        },
        {
            "email": "employee2@izone.com",
            "password": "employee123",
            "first_name": "Bob",
            "last_name": "Designer",
            "phone": "+1234567893",
            "date_of_birth": date(1993, 11, 10),
            "joining_date": date(2022, 6, 1),
            "designation": "UI/UX Designer",
            "department_id": eng_dept.department_id if eng_dept else None,
            "role": UserRole.EMPLOYEE,
        },
    ]
    
    manager = None
    for emp_data in sample_employees:
        existing = db.query(Employee).filter(Employee.email == emp_data["email"]).first()
        if not existing:
            password = emp_data.pop("password")
            employee = Employee(
                **emp_data,
                password_hash=get_password_hash(password),
                is_active=True
            )
            
            # Set manager for employees
            if employee.role == UserRole.EMPLOYEE and manager:
                employee.manager_id = manager.employee_id
            
            db.add(employee)
            db.commit()
            db.refresh(employee)
            
            if employee.role == UserRole.MANAGER:
                manager = employee
            
            print(f"  ✓ Added employee: {employee.email}")
            
            # Create leave balances for the employee
            leave_types = db.query(LeaveType).all()
            current_year = datetime.now().year
            
            for leave_type in leave_types:
                balance = LeaveBalance(
                    employee_id=employee.employee_id,
                    leave_type_id=leave_type.leave_type_id,
                    year=current_year,
                    total_allocated=leave_type.max_days_per_year,
                    used_days=0,
                    remaining_days=leave_type.max_days_per_year
                )
                db.add(balance)
            
            db.commit()
    
    print("✓ Sample employees seeded successfully")


def seed_holidays(db: Session):
    """Seed sample holidays"""
    print("\nSeeding holidays...")
    
    current_year = datetime.now().year
    holidays = [
        Holiday(
            holiday_date=date(current_year, 1, 1),
            holiday_name="New Year's Day",
            description="New Year celebration",
            is_optional=False
        ),
        Holiday(
            holiday_date=date(current_year, 7, 4),
            holiday_name="Independence Day",
            description="National Independence Day",
            is_optional=False
        ),
        Holiday(
            holiday_date=date(current_year, 12, 25),
            holiday_name="Christmas Day",
            description="Christmas celebration",
            is_optional=False
        ),
    ]
    
    for holiday in holidays:
        existing = db.query(Holiday).filter(Holiday.holiday_date == holiday.holiday_date).first()
        if not existing:
            db.add(holiday)
            print(f"  ✓ Added holiday: {holiday.holiday_name}")
    
    db.commit()
    print("✓ Holidays seeded successfully")


def main():
    """Main seeding function"""
    print("=" * 60)
    print("🌱 izone-workforce Database Seeding")
    print("=" * 60)
    
    # Create tables
    create_tables()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Seed data
        seed_departments(db)
        seed_leave_types(db)
        seed_rave_categories(db)
        seed_admin_user(db)
        seed_sample_employees(db)
        seed_holidays(db)
        
        print("\n" + "=" * 60)
        print("✅ Database seeding completed successfully!")
        print("=" * 60)
        print("\n📝 Default Credentials:")
        print("-" * 60)
        print("Admin:")
        print("  Email: admin@izone.com")
        print("  Password: admin123")
        print("\nManager:")
        print("  Email: manager@izone.com")
        print("  Password: manager123")
        print("\nEmployee:")
        print("  Email: employee1@izone.com")
        print("  Password: employee123")
        print("-" * 60)
        print("⚠️  IMPORTANT: Change these passwords after first login!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
