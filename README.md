# 🏢 izone-workforce API

A comprehensive workforce management REST API built with FastAPI, featuring attendance tracking, leave management, employee profiles, and peer appreciation system.

## ✨ Features

### 🔐 Authentication & Authorization
- JWT-based authentication
- Role-based access control (Admin, Manager, Employee)
- Secure password hashing with bcrypt
- Token refresh mechanism

### 👥 Employee Management
- Complete employee CRUD operations
- Department management
- Manager-subordinate hierarchy
- Employee directory with search
- Profile management with pictures

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
- ✅ Start the server

The API will be available at `http://localhost:8000`

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

6. **Start server**
```bash
uvicorn app.main:app --reload
```

### Test the Installation

Run the test suite to verify everything is working:
```bash
python test_app.py
```

### Using Docker

1. **Start services**
```bash
docker-compose up -d
```

2. **Run migrations**
```bash
docker-compose exec api alembic upgrade head
```

3. **Access the API**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints Overview

#### Authentication
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/change-password` - Change password
- `POST /api/v1/auth/logout` - Logout

#### Employees
- `GET /api/v1/employees` - List employees
- `GET /api/v1/employees/{id}` - Get employee details
- `POST /api/v1/employees` - Create employee (Admin)
- `PUT /api/v1/employees/{id}` - Update employee
- `DELETE /api/v1/employees/{id}` - Delete employee (Admin)

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
- `employees` - Employee information
- `departments` - Department/division data
- `attendance` - Daily attendance records
- `leave_types` - Types of leaves
- `leave_balance` - Employee leave balances
- `leave_applications` - Leave requests
- `raves` - Appreciation records
- `rave_categories` - Rave categories
- `holidays` - Company holidays
- `notifications` - User notifications

## 🔧 Configuration

Key environment variables in `.env`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/izone_workforce

# Security
SECRET_KEY=your-secret-key-minimum-32-characters
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

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
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   ├── utils/             # Utility functions
│   └── middleware/        # Custom middleware
├── alembic/               # Database migrations
├── tests/                 # Test suite
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker configuration
├── start_server.py        # Server startup script
├── seed_data.py          # Database seeding
├── .env.example          # Environment template
└── README.md             # This file
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

## 🚢 Deployment

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

- Use production WSGI server (uvicorn with workers)
- Set up reverse proxy (Nginx)
- Configure SSL/TLS
- Set up database backups
- Implement logging and monitoring
- Use environment-specific configurations
- Set DEBUG=False

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 👥 Team

Developed by izone team

## 📧 Support

For support, email support@izone.com or open an issue in the repository.

---

Made with ❤️ by izone team
