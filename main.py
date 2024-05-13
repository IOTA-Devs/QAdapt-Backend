import os
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from .jobs import clear_user_sessions_job
from .routers import router

load_dotenv()
app = FastAPI()

# Check for required env variables
required_env_vars = [
    "DB_NAME", 
    "DB_USER", 
    "DB_PASSWORD", 
    "ACCESS_TOKEN_SECRET_KEY", 
    "PERSONAL_TOKEN_SECRET_KEY"
]
for var in required_env_vars:
    if var not in os.environ:
        raise Exception(f"Missing required environment variable: {var}")

# Allowed CORS origins
origins = [
    "http://localhost:1420",
]

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"]
)

# Jobs
clear_user_sessions_job()

# Load routes
app.include_router(router.router)