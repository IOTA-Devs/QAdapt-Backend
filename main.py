from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .jobs import start_jobs
from .routers import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Check for required env variables
    required_env_vars = [
        "DB_NAME", 
        "DB_USER", 
        "DB_PASSWORD", 
        "ACCESS_TOKEN_SECRET_KEY", 
        "PERSONAL_TOKEN_SECRET_KEY",
        "STORAGE_ACCOUNT_NAME",
        "STORAGE_ACCOUNT_SAS_TOKEN",
        "STORAGE_CONTAINER_NAME"
    ]
    for var in required_env_vars:
        if var not in os.environ:
            raise Exception(f"Missing required environment variable: {var}")

    # Jobs
    start_jobs()

    yield

app = FastAPI(lifespan=lifespan)

# Allowed CORS origins
origins = [
    "http://localhost:1420",
    "https://black-ground-0bc6a5a1e.5.azurestaticapps.net/login"
]

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "PUT", "DELETE"],
    allow_headers=["*"]
)

# Load routes
app.include_router(router.router)