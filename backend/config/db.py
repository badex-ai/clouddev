import os
from sqlalchemy import create_engine,text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
from dotenv import load_dotenv


load_dotenv()

# Database configuration
class DatabaseConfig:
    # Database credentials - use environment variables for security
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    
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

print("Database URL:", DatabaseConfig.get_database_url())
# Create the SQLAlchemy engine
engine = create_engine(
    DatabaseConfig.get_database_url(),
    pool_size=DatabaseConfig.POOL_SIZE,
    max_overflow=DatabaseConfig.MAX_OVERFLOW,
    pool_recycle=DatabaseConfig.POOL_RECYCLE,
    pool_pre_ping=DatabaseConfig.POOL_PRE_PING,
    echo=False  # Set to True for SQL query logging
)

# Create a Base class for declarative models
Base = declarative_base()

Base.metadata.create_all(engine)
print ('Engine', engine)
# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
            # Use a simple query that doesn't depend on existing tables
            result = connection.execute(text("SELECT 1"))
            print("Database connection successful!")
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False



