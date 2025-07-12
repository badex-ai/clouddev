from fastapi import FastAPI, HTTPException
from routes.user_route import router as user_router
from routes.task_routes import router as task_router
from routes.auth_routes import router as auth_router
from config.db import test_connection


app = FastAPI()

test_connection()  # Test the database connection at startup

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}

app.include_router(auth_router, prefix="/auth", tags=["authentication"])

app.include_router(user_router, prefix="/users")