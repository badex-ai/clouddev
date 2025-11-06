import os
from fastapi import FastAPI, HTTPException, Request
from routes.user_route import router as user_router
from routes.task_routes import router as task_router
from routes.auth_routes import router as auth_router
from routes.family_routes import router as family_router
from config.db import test_connection
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config.db import Base, engine
from utils.error_handler import global_exception_handler
import structlog

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.JSONRenderer()
    ],
)

logger = structlog.get_logger()

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    try:
        Base.metadata.create_all(engine)
        logger.info("database_startup", message="Database tables created successfully")
    except Exception as e:
        logger.error("database_startup_error", error=str(e))
    
    yield
    
    # Shutdown: cleanup if needed
    logger.info("shutdown", message="Application shutting down...")

app = FastAPI(lifespan=lifespan)

app.add_exception_handler(Exception, global_exception_handler)

test_connection()  

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/v1/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}

app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(user_router, prefix="/api/v1/users", tags=["users"])
app.include_router(task_router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(family_router, prefix="/api/v1/families", tags=["families"])