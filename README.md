# 🏢 iZone Workforce Management API

A comprehensive workforce management REST API built with FastAPI, featuring attendance tracking, leave management, employee profiles, manager hierarchy, and peer appreciation system (Raves).

## ✨ Features

### 🔐 Authentication & Authorization
- JWT-based authentication
- Role-based access control (Admin, Manager, Employee)
- Secure password hashing with bcrypt
- Token refresh mechanism

### 👥 Employee Management
- Complete employee CRUD operations
- Department management
- Manager-subordinate hierarchy with assignment
- Employee directory with advanced search
- Profile management with pictures
- Manager assignment and tracking
- Soft delete (deactivation) support

### 🕐 Attendance Management
- Clock in/out functionality
- Real-time attendance tracking
- Automatic status calculation (Present/Late/Absent)
- Location tracking support
- Monthly attendance reports
- Attendance statistics and analytics

### 🌴 Leave Management
- Multiple leave types (Sick, Casual, Annual, etc.)
- Leave balance tracking
- Leave application workflow
- Manager approval/rejection system
- Leave history and reports
- Automatic balance updates

### ⭐ Rave/Appreciation System
- Peer-to-peer appreciation
- Category-based raves
- Anonymous rave support
- Rave leaderboard
- Activity feed

### 📊 Dashboard & Analytics
- Employee dashboard with key metrics
- Manager dashboard for team overview
- Admin dashboard for company-wide stats
- Recent activities feed
- Attendance trends

### 🔔 Notifications
- Real-time notifications
- Leave approval notifications
- Rave notifications
- System announcements

### 📅 Holiday Management
- Company holiday calendar
- Optional holidays support
- Upcoming holidays view

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- pip

### Installation in 3 Steps

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your database settings

# 3. Start the application
python start_server.py
```

The script automatically:
- ✅ Runs database migrations
- ✅ Seeds initial data (admin user, departments, leave types)
- ✅ Starts the server at http://localhost:8000

**Login with:**
- Email: `admin@example.com`
- Password: `admin123`

⚠️ Change password after first login!

---

### Detailed Setup Options

### Easy Installation & Startup

1. **Clone the repository**
```bash
git clone https://github.com/izone-repo/izone-workforce-api.git
cd izone-workforce-api
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your database configuration
```

4. **Start the application**
```bash
python start_server.py
```

The startup script will:
- ✅ Check all requirements
- ✅ Verify environment configuration  
- ✅ Test database connection
- ✅ Run database migrations
- ✅ Seed initial data (departments, leave types, admin user)
- ✅ Start the server

The API will be available at `http://localhost:8000`

**Default Admin Credentials:**
- Email: `admin@example.com`
- Password: `admin123`

⚠️ **Important:** Change the admin password after first login!

### Manual Setup (Alternative)

If you prefer manual setup:

1. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up database**
```bash
# Create PostgreSQL database
createdb izone_workforce
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run migrations**
```bash
alembic upgrade head
```

6. **Seed initial data (Optional but recommended)**
```bash
python seed_data.py
```

This will create:
- Default admin user (admin@example.com / admin123)
- Sample departments
- Leave types
- Rave categories
- Sample holidays

7. **Start server**
```bash
uvicorn app.main:app --reload
```

### Test the Installation

Run the test suite to verify everything is working:
```bash
python test_app.py
```

## 🌱 Seeding Initial Data

The `seed_data.py` script populates the database with initial data needed to run the application.

### What Gets Seeded:

1. **Admin User**
   - Email: admin@example.com
   - Password: admin123
   - Role: Admin

2. **Departments**
   - Engineering
   - Human Resources
   - Sales
   - Marketing
   - Finance

3. **Leave Types**
   - Annual Leave (20 days)
   - Sick Leave (12 days)
   - Casual Leave (10 days)
   - Maternity Leave (90 days)
   - Paternity Leave (7 days)

4. **Rave Categories**
   - Teamwork
   - Innovation
   - Leadership
   - Customer Service
   - Problem Solving

5. **Sample Holidays**
   - New Year's Day
   - Independence Day
   - Christmas
   - etc.

### Running Seed Script:

```bash
# After running migrations
python seed_data.py
```

### Important Notes:
- ⚠️ Run seed script only once (it checks for existing data)
- ⚠️ Change admin password after first login
- ✅ Safe to run multiple times (won't duplicate data)
- ✅ Creates leave balances for all employees automatically

### Using Docker

1. **Start services**
```bash
docker-compose up -d
```

2. **Run migrations**
```bash
docker-compose exec api alembic upgrade head
```

3. **Seed initial data (Optional)**
```bash
docker-compose exec api python seed_data.py
```

4. **Access the API**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Default Admin Login:**
- Email: admin@example.com
- Password: admin123

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints Overview

#### Authentication
- `POST /api/v1/auth/login` - Login with email and password
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user profile
- `POST /api/v1/auth/change-password` - Change password
- `POST /api/v1/auth/logout` - Logout

#### Employees
- `GET /api/v1/employees` - List employees (with filters: department, active status, search)
- `GET /api/v1/employees/{id}` - Get employee details
- `GET /api/v1/employees/{id}/subordinates` - Get employee's subordinates
- `POST /api/v1/employees` - Create employee (Admin only)
- `PUT /api/v1/employees/{id}` - Update employee
- `DELETE /api/v1/employees/{id}` - Soft delete employee (Admin only)

#### Departments
- `GET /api/v1/departments` - List departments
- `POST /api/v1/departments` - Create department (Admin)
- `PUT /api/v1/departments/{id}` - Update department (Admin)
- `DELETE /api/v1/departments/{id}` - Delete department (Admin)

#### Attendance
- `POST /api/v1/attendance/clock-in` - Clock in
- `POST /api/v1/attendance/clock-out` - Clock out
- `GET /api/v1/attendance/my-attendance` - Get my attendance
- `GET /api/v1/attendance/today` - Get today's attendance
- `GET /api/v1/attendance/statistics/monthly` - Monthly statistics

#### Leaves
- `GET /api/v1/leaves/types` - Get leave types
- `GET /api/v1/leaves/balance` - Get leave balance
- `GET /api/v1/leaves/applications` - Get leave applications
- `POST /api/v1/leaves/applications` - Apply for leave
- `PUT /api/v1/leaves/applications/{id}/approve` - Approve/Reject leave (Manager)
- `PUT /api/v1/leaves/applications/{id}/cancel` - Cancel leave

#### Raves
- `POST /api/v1/raves` - Send rave
- `GET /api/v1/raves` - Get raves feed
- `GET /api/v1/raves/received` - Get received raves
- `GET /api/v1/raves/sent` - Get sent raves
- `GET /api/v1/raves/employee/{id}` - Get employee raves
- `GET /api/v1/raves/statistics/leaderboard` - Get leaderboard

#### Dashboard
- `GET /api/v1/dashboard/stats` - Get dashboard stats
- `GET /api/v1/dashboard/manager/stats` - Get manager dashboard
- `GET /api/v1/dashboard/admin/stats` - Get admin dashboard

#### Notifications
- `GET /api/v1/notifications` - Get notifications
- `PUT /api/v1/notifications/{id}/read` - Mark as read
- `PUT /api/v1/notifications/mark-all-read` - Mark all as read

#### Holidays
- `GET /api/v1/holidays` - List holidays
- `GET /api/v1/holidays/upcoming` - Get upcoming holidays
- `POST /api/v1/holidays` - Create holiday (Admin)

## 🗄️ Database Schema

The application uses PostgreSQL with the following main tables:
- `employees` - Employee information with manager hierarchy
- `departments` - Department/division data
- `attendance` - Daily attendance records with clock in/out times
- `leave_types` - Types of leaves (Sick, Casual, Annual, etc.)
- `leave_balance` - Employee leave balances per year
- `leave_applications` - Leave requests with approval workflow
- `raves` - Appreciation records (peer-to-peer)
- `rave_categories` - Rave categories (Teamwork, Innovation, etc.)
- `holidays` - Company holidays calendar
- `notifications` - User notifications system

### Key Relationships
- Employees can have a manager (self-referential relationship)
- Employees belong to departments
- Attendance records linked to employees
- Leave applications require manager approval
- Raves sent between employees

## 🔧 Configuration

Key environment variables in `.env`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/izone_workforce

# Security
SECRET_KEY=your-secret-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=720  # 12 hours
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Server
HOST=0.0.0.0
PORT=8000

# Attendance
WORK_START_TIME=09:00
WORK_END_TIME=18:00
LATE_ARRIVAL_THRESHOLD_MINUTES=15

# Leave
ANNUAL_LEAVE_DAYS=20
SICK_LEAVE_DAYS=12
CASUAL_LEAVE_DAYS=10
```

## 🧪 Testing

Run tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app tests/
```

## 📁 Project Structure

```
izone-workforce-api/
├── app/                    # Application code
│   ├── api/               # API endpoints
│   │   └── v1/           # API version 1
│   ├── models/            # Database models (SQLAlchemy)
│   ├── schemas/           # Pydantic schemas (validation)
│   ├── services/          # Business logic
│   ├── utils/             # Utility functions
│   └── middleware/        # Custom middleware
├── alembic/               # Database migrations
│   └── versions/         # Migration files
├── tests/                 # Test suite
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker configuration
├── start_server.py        # Server startup script
├── seed_data.py          # Database seeding script ⭐
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
├── README.md             # This file
└── SETUP.md              # Detailed setup guide
```

## 🔒 Security Best Practices

1. **Never commit `.env` file** - Contains sensitive credentials
2. **Use strong SECRET_KEY** - Minimum 32 characters, randomly generated
3. **Enable HTTPS in production** - Use SSL/TLS certificates
4. **Keep dependencies updated** - Regularly update packages
5. **Use environment variables** - Never hardcode credentials
6. **Implement rate limiting** - Prevent abuse
7. **Validate all inputs** - Using Pydantic schemas
8. **Use prepared statements** - SQLAlchemy ORM prevents SQL injection
9. **Set appropriate token expiry** - Balance security and UX (currently 12 hours)
10. **Configure CORS properly** - Only allow trusted origins

## 🔗 Frontend Integration

This API is designed to work with the iZone Workforce Web frontend.

### Frontend Configuration

The frontend needs to set the API URL in its `.env` file:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

### CORS Configuration

Make sure to add your frontend URL to the CORS origins:

```env
# In backend .env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,https://yourfrontend.com
```

### Authentication Flow

1. Frontend sends login credentials to `/api/v1/auth/login`
2. Backend returns `access_token` and `refresh_token`
3. Frontend stores tokens in localStorage
4. Frontend adds `Authorization: Bearer <token>` header to all requests
5. When token expires (401), frontend calls `/api/v1/auth/refresh`
6. Backend returns new access token
7. Frontend retries original request

### Key Features for Frontend
- ✅ JWT token authentication
- ✅ Automatic token refresh
- ✅ 12-hour token expiry (configurable)
- ✅ Role-based access control
- ✅ Real-time notifications
- ✅ Comprehensive error responses

## 🚢 Deployment

### Production Environment Variables

```env
# Database (Use production database)
DATABASE_URL=postgresql://user:password@prod-db-host:5432/izone_workforce

# Security (Generate strong keys)
SECRET_KEY=your-very-long-random-secret-key-at-least-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=720
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (Add your frontend domain)
CORS_ORIGINS=https://yourfrontend.com,https://www.yourfrontend.com

# Server
HOST=0.0.0.0
PORT=8000
```

### Docker Deployment

1. Build image:
```bash
docker build -t izone-workforce-api .
```

2. Run container:
```bash
docker run -p 8000:8000 --env-file .env izone-workforce-api
```

### Production Considerations

- ✅ Use production WSGI server (uvicorn with workers)
- ✅ Set up reverse proxy (Nginx/Apache)
- ✅ Configure SSL/TLS certificates
- ✅ Set up database backups (automated)
- ✅ Implement logging and monitoring
- ✅ Use environment-specific configurations
- ✅ Set strong SECRET_KEY (minimum 32 characters)
- ✅ Enable HTTPS only
- ✅ Configure rate limiting
- ✅ Set up health checks
- ✅ Use connection pooling for database

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Write unit tests for new features
- Update documentation
- Use type hints
- Keep functions small and focused

## 📝 Version History

### v1.0.0 (Current)
- ✅ Complete employee management with manager hierarchy
- ✅ Attendance tracking with clock in/out
- ✅ Leave management with approval workflow
- ✅ Rave/appreciation system
- ✅ Role-based access control
- ✅ JWT authentication with refresh tokens
- ✅ Notification system
- ✅ Dashboard analytics
- ✅ 12-hour token expiry for better UX

## 👥 Team

Developed by iZone Development Team

## 📧 Support

For support:
- Email: support@izone.com
- GitHub Issues: [Open an issue](https://github.com/izone-repo/izone-workforce-api/issues)
- Documentation: See SETUP.md for detailed setup instructions

## 📄 License

This project is proprietary software owned by iZone.

---

**Built with ❤️ by iZone Team**

**Tech Stack:** FastAPI • PostgreSQL • SQLAlchemy • Pydantic • JWT • Alembic
