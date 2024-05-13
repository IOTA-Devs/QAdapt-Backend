from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from .jobs import clear_user_sessions_job
from .routers import router

load_dotenv()
app = FastAPI()

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