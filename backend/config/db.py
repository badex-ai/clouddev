import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
from dotenv import load_dotenv
from config.env import get_config
import redis.asyncio as redis
import structlog
import logging

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True
)

logger = structlog.get_logger()

load_dotenv()
config = get_config()

# Database configuration
class DatabaseConfig:
    DB_HOST = config["db_host"]
    DB_PORT = config["db_port"]
    DB_NAME = config["db_name"]
    DB_USER = config["db_user"]
    DB_PASSWORD = config["db_password"]
    
    POOL_SIZE = 10
    MAX_OVERFLOW = 20
    POOL_RECYCLE = 3600
    POOL_PRE_PING = True
    
    @classmethod
    def get_database_url(cls):
        encoded_password = quote_plus(cls.DB_PASSWORD)
        logger.info("password_encoded", encoded_password=encoded_password)
        
        return f"postgresql://{cls.DB_USER}:{encoded_password}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"

logger.info("database_url", url=DatabaseConfig.get_database_url())

engine = create_engine(
    DatabaseConfig.get_database_url(),
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={"connect_timeout": 5}
)

Base = declarative_base()
logger.info("engine_created", engine=str(engine))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info("database_connection_successful")
            return True
    except Exception as e:
        logger.error("database_connection_failed", error=str(e))
        return False

async def get_redis_pool():
    return await redis.from_url(
        os.getenv('REDIS_URL', 'redis://localhost:6379'),
        encoding="utf-8",
        decode_responses=True
    )

_redis_pool = None

async def get_redis():
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = await get_redis_pool()
    return _redis_pool
