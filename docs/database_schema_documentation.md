# Database Schema Documentation

## Overview
This document provides detailed information about the database schema for the iZone Workforce Management System.

## Database Tables

### 1. employees
Primary table for storing employee information.

**Columns:**
- `employee_id` (INTEGER, PRIMARY KEY) - Unique identifier for each employee
- `email` (VARCHAR(255), UNIQUE, NOT NULL) - Employee email address
- `password_hash` (VARCHAR(255), NOT NULL) - Hashed password
- `first_name` (VARCHAR(100), NOT NULL) - Employee first name
- `last_name` (VARCHAR(100), NOT NULL) - Employee last name
- `phone` (VARCHAR(20)) - Contact phone number
- `date_of_birth` (DATE) - Employee date of birth
- `joining_date` (DATE, NOT NULL) - Date employee joined the company
- `designation` (VARCHAR(100)) - Job title/position
- `department_id` (INTEGER, FOREIGN KEY) - References departments.department_id
- `manager_id` (INTEGER, FOREIGN KEY) - References employees.employee_id
- `role` (ENUM: 'ADMIN', 'MANAGER', 'EMPLOYEE') - User role in the system
- `profile_picture_url` (VARCHAR(500)) - URL to profile picture
- `is_active` (BOOLEAN, DEFAULT TRUE) - Whether the employee is active
- `created_at` (TIMESTAMP) - Record creation timestamp
- `updated_at` (TIMESTAMP) - Record last update timestamp

### 2. departments
Table for organizational departments.

**Columns:**
- `department_id` (INTEGER, PRIMARY KEY) - Unique identifier for each department
- `department_name` (VARCHAR(100), UNIQUE, NOT NULL) - Department name
- `description` (TEXT) - Department description
- `head_of_department` (INTEGER, FOREIGN KEY) - References employees.employee_id
- `created_at` (TIMESTAMP) - Record creation timestamp
- `updated_at` (TIMESTAMP) - Record last update timestamp

### 3. attendance
Daily attendance records for employees.

**Columns:**
- `attendance_id` (INTEGER, PRIMARY KEY) - Unique identifier for each attendance record
- `employee_id` (INTEGER, FOREIGN KEY, NOT NULL) - References employees.employee_id
- `attendance_date` (DATE, NOT NULL) - Date of attendance
- `clock_in_time` (TIME) - Time employee clocked in
- `clock_out_time` (TIME) - Time employee clocked out
- `hours_worked` (DECIMAL(4,2)) - Total hours worked
- `status` (ENUM: 'PRESENT', 'ABSENT', 'LATE', 'HALF_DAY', 'ON_LEAVE') - Attendance status
- `location` (VARCHAR(200)) - Work location
- `notes` (TEXT) - Additional notes
- `created_at` (TIMESTAMP) - Record creation timestamp
- `updated_at` (TIMESTAMP) - Record last update timestamp

**Constraints:**
- UNIQUE constraint on (employee_id, attendance_date)

### 4. leave_types
Types of leaves available in the system.

**Columns:**
- `leave_type_id` (INTEGER, PRIMARY KEY) - Unique identifier for each leave type
- `type_name` (VARCHAR(50), UNIQUE, NOT NULL) - Leave type name
- `description` (TEXT) - Leave type description
- `max_days_per_year` (INTEGER) - Maximum days allowed per year
- `requires_approval` (BOOLEAN, DEFAULT TRUE) - Whether approval is required
- `is_paid` (BOOLEAN, DEFAULT TRUE) - Whether the leave is paid
- `created_at` (TIMESTAMP) - Record creation timestamp
- `updated_at` (TIMESTAMP) - Record last update timestamp

### 5. leave_balance
Employee leave balances by type and year.

**Columns:**
- `balance_id` (INTEGER, PRIMARY KEY) - Unique identifier for each balance record
- `employee_id` (INTEGER, FOREIGN KEY, NOT NULL) - References employees.employee_id
- `leave_type_id` (INTEGER, FOREIGN KEY, NOT NULL) - References leave_types.leave_type_id
- `year` (INTEGER, NOT NULL) - Year for the balance
- `total_allocated` (DECIMAL(5,2), NOT NULL) - Total days allocated
- `used_days` (DECIMAL(5,2), DEFAULT 0) - Days already used
- `remaining_days` (DECIMAL(5,2)) - Remaining days available
- `created_at` (TIMESTAMP) - Record creation timestamp
- `updated_at` (TIMESTAMP) - Record last update timestamp

**Constraints:**
- UNIQUE constraint on (employee_id, leave_type_id, year)

### 6. leave_applications
Leave applications submitted by employees.

**Columns:**
- `leave_application_id` (INTEGER, PRIMARY KEY) - Unique identifier for each application
- `employee_id` (INTEGER, FOREIGN KEY, NOT NULL) - References employees.employee_id
- `leave_type_id` (INTEGER, FOREIGN KEY, NOT NULL) - References leave_types.leave_type_id
- `start_date` (DATE, NOT NULL) - Leave start date
- `end_date` (DATE, NOT NULL) - Leave end date
- `total_days` (DECIMAL(5,2), NOT NULL) - Total days requested
- `reason` (TEXT, NOT NULL) - Reason for leave
- `status` (ENUM: 'PENDING', 'APPROVED', 'REJECTED', 'CANCELLED') - Application status
- `approved_by` (INTEGER, FOREIGN KEY) - References employees.employee_id
- `applied_on` (TIMESTAMP) - Application submission timestamp
- `approved_rejected_on` (TIMESTAMP) - Approval/rejection timestamp
- `rejection_reason` (TEXT) - Reason for rejection
- `attachments` (TEXT) - File attachments (JSON array)
- `created_at` (TIMESTAMP) - Record creation timestamp
- `updated_at` (TIMESTAMP) - Record last update timestamp

### 7. rave_categories
Categories for employee appreciation (RAVE) system.

**Columns:**
- `category_id` (INTEGER, PRIMARY KEY) - Unique identifier for each category
- `category_name` (VARCHAR(50), UNIQUE, NOT NULL) - Category name
- `description` (TEXT) - Category description
- `icon` (VARCHAR(100)) - Icon identifier
- `color` (VARCHAR(7)) - Color code (hex)
- `created_at` (TIMESTAMP) - Record creation timestamp
- `updated_at` (TIMESTAMP) - Record last update timestamp

### 8. raves
Employee appreciation messages.

**Columns:**
- `rave_id` (INTEGER, PRIMARY KEY) - Unique identifier for each rave
- `from_employee_id` (INTEGER, FOREIGN KEY, NOT NULL) - References employees.employee_id (sender)
- `to_employee_id` (INTEGER, FOREIGN KEY, NOT NULL) - References employees.employee_id (recipient)
- `category_id` (INTEGER, FOREIGN KEY, NOT NULL) - References rave_categories.category_id
- `message` (TEXT, NOT NULL) - Appreciation message
- `is_anonymous` (BOOLEAN, DEFAULT FALSE) - Whether the rave is anonymous
- `created_at` (TIMESTAMP) - Record creation timestamp
- `updated_at` (TIMESTAMP) - Record last update timestamp

### 9. holidays
Company holidays and special dates.

**Columns:**
- `holiday_id` (INTEGER, PRIMARY KEY) - Unique identifier for each holiday
- `holiday_name` (VARCHAR(100), NOT NULL) - Holiday name
- `holiday_date` (DATE, UNIQUE, NOT NULL) - Holiday date
- `description` (TEXT) - Holiday description
- `is_optional` (BOOLEAN, DEFAULT FALSE) - Whether the holiday is optional
- `created_at` (TIMESTAMP) - Record creation timestamp
- `updated_at` (TIMESTAMP) - Record last update timestamp

### 10. notifications
System notifications for users.

**Columns:**
- `notification_id` (INTEGER, PRIMARY KEY) - Unique identifier for each notification
- `employee_id` (INTEGER, FOREIGN KEY, NOT NULL) - References employees.employee_id
- `title` (VARCHAR(200), NOT NULL) - Notification title
- `message` (TEXT, NOT NULL) - Notification message
- `type` (ENUM: 'GENERAL', 'LEAVE', 'ATTENDANCE', 'RAVE', 'SYSTEM') - Notification type
- `is_read` (BOOLEAN, DEFAULT FALSE) - Whether the notification has been read
- `link` (VARCHAR(500)) - Optional link for the notification
- `created_at` (TIMESTAMP) - Record creation timestamp
- `updated_at` (TIMESTAMP) - Record last update timestamp

## Relationships

### Primary Relationships:
1. **employees** ↔ **departments**: Many-to-One (employees belong to departments)
2. **employees** ↔ **employees**: Self-referencing (manager relationship)
3. **employees** ↔ **attendance**: One-to-Many (employees have multiple attendance records)
4. **employees** ↔ **leave_applications**: One-to-Many (employees can have multiple leave applications)
5. **employees** ↔ **leave_balance**: One-to-Many (employees have balances for different leave types)
6. **employees** ↔ **raves**: One-to-Many (employees can send/receive multiple raves)
7. **employees** ↔ **notifications**: One-to-Many (employees can have multiple notifications)

### Secondary Relationships:
1. **leave_types** ↔ **leave_applications**: One-to-Many
2. **leave_types** ↔ **leave_balance**: One-to-Many
3. **rave_categories** ↔ **raves**: One-to-Many

## Indexes

### Performance Indexes:
- `ix_employees_email` - For login queries
- `ix_attendance_employee_id` - For attendance queries by employee
- `ix_attendance_attendance_date` - For date-based attendance queries
- `ix_leave_applications_employee_id` - For leave queries by employee
- `ix_leave_balance_employee_id` - For balance queries by employee
- `ix_notifications_employee_id` - For notification queries by employee
- `ix_raves_to_employee_id` - For received raves queries
- `ix_raves_from_employee_id` - For sent raves queries

## Data Integrity

### Constraints:
1. **Foreign Key Constraints**: Ensure referential integrity between related tables
2. **Unique Constraints**: Prevent duplicate records where necessary
3. **Check Constraints**: Ensure data validity (e.g., end_date >= start_date)
4. **Not Null Constraints**: Ensure required fields are populated

### Triggers:
1. **Updated At Triggers**: Automatically update `updated_at` timestamps
2. **Leave Balance Triggers**: Update remaining days when leave is approved
3. **Notification Triggers**: Create notifications for important events

## Migration Management

The database schema is managed using Alembic migrations:
- **Initial Migration**: `001_initial_migration.py` - Creates all tables and relationships
- **Version Control**: All schema changes are tracked through migration files
- **Rollback Support**: Migrations can be rolled back if needed

## Security Considerations

1. **Password Hashing**: Employee passwords are hashed using bcrypt
2. **Sensitive Data**: Personal information is protected with appropriate access controls
3. **Audit Trail**: Created/updated timestamps provide audit capabilities
4. **Data Validation**: Input validation prevents SQL injection and data corruption