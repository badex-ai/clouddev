from fastapi import FastAPI, HTTPException,Request
from routes.user_route import router as user_router
from routes.task_routes import router as task_router
from routes.auth_routes import router as auth_router
from routes.family_routes import router as family_router
from config.db import test_connection
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config.db import Base, engine

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    try:
        Base.metadata.create_all(engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {e}")
    
    yield
    
    # Shutdown: cleanup if needed
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)


app = FastAPI()

test_connection()  

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
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