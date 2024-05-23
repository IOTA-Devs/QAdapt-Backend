from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .jobs import clear_user_sessions_job
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
    clear_user_sessions_job()

    yield

app = FastAPI(lifespan=lifespan, docs_url="/")

# Allowed CORS origins
origins = [
    "http://localhost:1420",
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