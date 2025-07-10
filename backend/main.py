from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from routes.user_route import router as user_router
from routes.task_routes import router as task_router
from routes.auth_routes import router as auth_router


app = FastAPI()




app.include_router(user_router, prefix="/users")