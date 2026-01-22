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
from utils.error_handler import AppError
from config.tracing import setup_tracing, get_tracer
from config.logging import setup_logging, get_logger
from middleware import RequestLoggingMiddleware

# Setup logging (must be first)
setup_logging(service_name="kaban-backend")
logger = get_logger("main")

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

setup_tracing(app=app, service_name="kaban-backend")

# Get tracer for manual spans
tracer = get_tracer(__name__)



# Register exception handlers - MUST be before middleware!


app.add_exception_handler(AppError, global_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

test_connection()

# CORS configuration - use environment variable for allowed origins
allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)

# Request logging middleware (after CORS)
app.add_middleware(RequestLoggingMiddleware)


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
