from fastapi import FastAPI, HTTPException,Request
from routes.user_route import router as user_router
from routes.task_routes import router as task_router
from routes.auth_routes import router as auth_router
from routes.family_routes import router as family_router
from config.db import test_connection
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()



app = FastAPI()

test_connection()  

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/api/v1/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}



app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])

app.include_router(user_router, prefix="/api/v1/users", tags=["users"])


app.include_router(task_router, prefix="/api/v1/tasks", tags=["tasks"])

app.include_router(family_router, prefix="/api/v1/family", tags=["families"])