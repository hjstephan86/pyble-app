# database.py - Database Configuration

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Database engine - equivalent to DataSource in Spring Boot
engine = create_engine(
    settings.database_url, 
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# Session factory - equivalent to EntityManager
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models - equivalent to JPA @Entity base
Base = declarative_base()

# Dependency injection for database session (Spring Boot @Autowired equivalent)
def get_db():
    """
    Database dependency injection.
    This is equivalent to @Autowired EntityManager in Spring Boot.
    FastAPI will automatically inject this into route handlers.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database initialization function
def init_db():
    """
    Initialize database tables.
    Equivalent to @PostConstruct or Spring Boot's schema.sql
    """
    # Import all models here to ensure they are registered with Base
    from models import BibleVerse
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

# Database health check
def check_db_connection():
    """
    Check if database connection is working.
    Similar to Spring Boot Actuator health checks.
    """
    try:
        db = SessionLocal()
        # Execute a simple query
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

# Sample data insertion (for development)
def insert_sample_data():
    """
    Insert sample Bible verses for testing.
    Equivalent to data.sql in Spring Boot.
    """
    from models import BibleVerse
    
    db = SessionLocal()
    try:
        # Check if data already exists
        existing = db.query(BibleVerse).first()
        if existing:
            print("Sample data already exists.")
            return
        
        # Sample verses
        sample_verses = [
            BibleVerse(
                book="John",
                chapter=3,
                verse=16,
                text="For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life.",
                translation="NIV"
            ),
            BibleVerse(
                book="John",
                chapter=1,
                verse=1,
                text="In the beginning was the Word, and the Word was with God, and the Word was God.",
                translation="NIV"
            ),
            BibleVerse(
                book="Genesis",
                chapter=1,
                verse=1,
                text="In the beginning God created the heavens and the earth.",
                translation="NIV"
            ),
            BibleVerse(
                book="Psalm",
                chapter=23,
                verse=1,
                text="The Lord is my shepherd, I lack nothing.",
                translation="NIV"
            ),
            BibleVerse(
                book="Romans",
                chapter=8,
                verse=28,
                text="And we know that in all things God works for the good of those who love him, who have been called according to his purpose.",
                translation="NIV"
            )
        ]
        
        # Add sample data
        for verse in sample_verses:
            db.add(verse)
        
        db.commit()
        print(f"Inserted {len(sample_verses)} sample verses.")
        
    except Exception as e:
        print(f"Error inserting sample data: {e}")
        db.rollback()
    finally:
        db.close()

# Run this when the module is imported
if __name__ == "__main__":
    init_db()
    insert_sample_data()