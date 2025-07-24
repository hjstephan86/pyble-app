#!/usr/bin/env python3
"""
Application Runner Script for Bible App

This script provides different ways to run the application:
- Development mode with auto-reload
- Production mode
- Database initialization
- Sample data loading

Usage:
    python run.py                    # Development mode
    python run.py --prod            # Production mode
    python run.py --init-db         # Initialize database only
    python run.py --load-samples    # Load sample data only
"""

import argparse
import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def run_development():
    """Run in development mode with auto-reload"""
    import uvicorn
    from config import settings
    
    print("🚀 Starting Bible App in DEVELOPMENT mode...")
    print(f"📱 Web Interface: http://{settings.host}:{settings.port}/")
    print(f"📋 API Documentation: http://{settings.host}:{settings.port}/swagger")
    print(f"💚 Health Check: http://{settings.host}:{settings.port}/health")
    print("🔄 Auto-reload enabled - Code changes will restart the server")
    print("-" * 60)
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level="info"
    )

def run_production():
    """Run in production mode"""
    import uvicorn
    from config import settings
    
    print("🏭 Starting Bible App in PRODUCTION mode...")
    print(f"📱 Web Interface: http://{settings.host}:{settings.port}/")
    print(f"📋 API Documentation: http://{settings.host}:{settings.port}/swagger")
    print(f"💚 Health Check: http://{settings.host}:{settings.port}/health")
    print("⚠️  Auto-reload disabled for production")
    print("-" * 60)
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        workers=4,  # Multiple workers for production
        log_level="warning"
    )

def init_database():
    """Initialize database tables"""
    print("🗃️  Initializing database...")
    
    try:
        from database import init_db, check_db_connection
        
        if not check_db_connection():
            print("❌ Database connection failed!")
            return False
        
        init_db()
        print("✅ Database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def load_sample_data():
    """Load sample Bible verses"""
    print("📚 Loading sample Bible verses...")
    
    try:
        from database import insert_sample_data
        
        insert_sample_data()
        print("✅ Sample data loaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Sample data loading failed: {e}")
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic',
        'jinja2'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def create_directories():
    """Create necessary directories"""
    directories = ['templates', 'logs']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("📁 Directories created/verified")

def setup_environment():
    """Setup environment file if it doesn't exist"""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists() and env_example.exists():
        print("📝 Creating .env file from .env.example...")
        env_file.write_text(env_example.read_text())
        print("✅ .env file created! Please review and modify as needed.")
    elif not env_file.exists():
        print("⚠️  No .env file found. Using default configuration.")

def display_info():
    """Display application information"""
    print("=" * 60)
    print("📖 PYTHON BIBLE APPLICATION")
    print("=" * 60)
    print("🏗️  Architecture: FastAPI (Spring Boot equivalent)")
    print("🗄️  Database: SQLite (configurable)")
    print("🌐 API: REST with automatic Swagger docs")
    print("📱 UI: Modern web interface")
    print("=" * 60)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Bible App Runner - Python equivalent of Spring Boot application"
    )
    
    parser.add_argument(
        '--prod', 
        action='store_true', 
        help='Run in production mode'
    )
    
    parser.add_argument(
        '--init-db', 
        action='store_true', 
        help='Initialize database only'
    )
    
    parser.add_argument(
        '--load-samples', 
        action='store_true', 
        help='Load sample data only'
    )
    
    parser.add_argument(
        '--check-deps', 
        action='store_true', 
        help='Check dependencies only'
    )
    
    parser.add_argument(
        '--setup', 
        action='store_true', 
        help='Setup environment and directories'
    )
    
    args = parser.parse_args()
    
    # Display app info
    display_info()
    
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    create_directories()
    
    # Handle specific commands
    if args.check_deps:
        print("✅ Dependency check completed!")
        return
    
    if args.setup:
        print("✅ Setup completed!")
        return
    
    if args.init_db:
        success = init_database()
        sys.exit(0 if success else 1)
    
    if args.load_samples:
        # Initialize DB first if needed
        init_database()
        success = load_sample_data()
        sys.exit(0 if success else 1)
    
    # Initialize database before starting server
    print("🔧 Setting up application...")
    if not init_database():
        print("❌ Failed to initialize database!")
        sys.exit(1)
    
    # Load sample data if database is empty
    try:
        from database import SessionLocal
        from models import BibleVerse
        
        db = SessionLocal()
        verse_count = db.query(BibleVerse).count()
        db.close()
        
        if verse_count == 0:
            print("📚 No data found, loading sample verses...")
            load_sample_data()
    except:
        pass  # Ignore errors, sample data is optional
    
    # Run the application
    if args.prod:
        run_production()
    else:
        run_development()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Bible App stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting Bible App: {e}")
        sys.exit(1)