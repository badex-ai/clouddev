import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

# Database configuration
class DatabaseConfig:
    # Database credentials - use environment variables for security
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'your_database_name')
    DB_USER = os.getenv('DB_USER', 'your_username')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'your_password')
    
    # Connection pool settings
    POOL_SIZE = 10
    MAX_OVERFLOW = 20
    POOL_RECYCLE = 3600
    POOL_PRE_PING = True
    
    @classmethod
    def get_database_url(cls):
        """
        Construct the database URL for PostgreSQL
        Format: postgresql://username:password@host:port/database
        
        """
        # URL encode the password to handle special characters
        encoded_password = quote_plus(cls.DB_PASSWORD)
        
        return f"postgresql://{cls.DB_USER}:{encoded_password}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"

# Create the SQLAlchemy engine
engine = create_engine(
    DatabaseConfig.get_database_url(),
    pool_size=DatabaseConfig.POOL_SIZE,
    max_overflow=DatabaseConfig.MAX_OVERFLOW,
    pool_recycle=DatabaseConfig.POOL_RECYCLE,
    pool_pre_ping=DatabaseConfig.POOL_PRE_PING,
    echo=False  # Set to True for SQL query logging
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for declarative models
Base = declarative_base()

def get_db():
    """
    Dependency function to get database session
    Use this in your application to get a database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """
    Test the database connection
    """
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            print("Database connection successful!")
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

# Alternative: Direct connection function
def get_db_session():
    """
    Get a new database session
    Remember to close the session after use
    """
    return SessionLocal()

# Example usage with context manager
class DatabaseManager:
    @staticmethod
    def get_session():
        """Context manager for database sessions"""
        session = SessionLocal()
        try:
            return session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

