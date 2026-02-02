# Backend Setup Guide

## 🚀 Quick Start

### 1. Environment Setup
Copy the example environment file and configure it:
```bash
cp .env.example .env
```

### 2. Configure Your .env File
Edit `.env` with your actual values:
```env
# Database Configuration
DATABASE_URL=postgresql://your_actual_user:your_actual_password@localhost:5432/your_actual_db_name
POSTGRES_DB=your_actual_db_name
POSTGRES_USER=your_actual_user
POSTGRES_PASSWORD=your_actual_password

# Security Configuration
SECRET_KEY=your-actual-secret-key-32-characters-minimum
```

### 3. Start the Application
```bash
# Development with Docker
docker-compose up -d

# Or for production
docker-compose -f docker-compose.prod.yml up -d
```

## 🔒 Security Notes

- **Never commit your `.env` file** - it contains sensitive credentials
- **Always use strong passwords** in production
- **Generate a secure SECRET_KEY** for JWT tokens
- **Update ALLOWED_ORIGINS** for your frontend domain

## 📝 Example Values

Replace these placeholders in your `.env` file:
- `your_database_name` → `workforce_db` or similar
- `your_db_user` → `admin` or your preferred username
- `your_actual_password` → A strong, unique password
- `your-actual-secret-key` → Generate with: `openssl rand -hex 32`