#!/usr/bin/env python3
"""
Startup script for iZone Workforce API
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed"""
    print("Checking requirements...")
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import psycopg2
        import alembic
        import jose
        import passlib
        print("✓ All required packages are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists"""
    if Path(".env").exists():
        print("✓ .env file found")
        return True
    else:
        print("✗ .env file not found")
        print("Please copy .env.example to .env and configure your settings")
        return False

def test_database_connection():
    """Test database connection"""
    print("Testing database connection...")
    try:
        from app.config import settings
        from sqlalchemy import create_engine, text
        
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("Please check your DATABASE_URL in .env file")
        return False

def run_migrations():
    """Run database migrations"""
    print("Running database migrations...")
    try:
        # Check if migration exists
        versions_dir = Path("alembic/versions")
        if not versions_dir.exists() or not list(versions_dir.glob("*.py")):
            print("No migrations found, creating tables directly...")
            from app.database import Base, engine
            Base.metadata.create_all(bind=engine)
            print("✓ Database tables created")
        else:
            # Try to run alembic migrations, but don't fail if tables exist
            result = subprocess.run(["alembic", "upgrade", "head"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ Database migrations completed")
            elif "already exists" in result.stderr:
                print("✓ Database tables already exist")
            else:
                print(f"⚠ Migration warning: {result.stderr}")
                # Try to create tables directly as fallback
                print("Trying direct table creation...")
                from app.database import Base, engine
                Base.metadata.create_all(bind=engine)
                print("✓ Database tables created directly")
        return True
    except Exception as e:
        print(f"✗ Migration error: {e}")
        # Try to create tables directly as final fallback
        try:
            print("Trying direct table creation as fallback...")
            from app.database import Base, engine
            Base.metadata.create_all(bind=engine)
            print("✓ Database tables created directly")
            return True
        except Exception as e2:
            print(f"✗ Direct table creation also failed: {e2}")
            return False

def start_server():
    """Start the FastAPI server"""
    print("Starting iZone Workforce API server...")
    print("Server will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        from app.config import settings
        import uvicorn
        
        uvicorn.run(
            "app.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")

def main():
    """Main startup function"""
    print("=" * 50)
    print("iZone Workforce API - Startup")
    print("=" * 50)
    
    # Run all checks
    checks = [
        check_requirements,
        check_env_file,
        test_database_connection,
        run_migrations
    ]
    
    for check in checks:
        if not check():
            print("\n❌ Startup failed. Please fix the issues above.")
            return 1
        print()
    
    print("✅ All checks passed! Starting server...")
    print()
    
    # Start the server
    start_server()
    return 0

if __name__ == "__main__":
    sys.exit(main())