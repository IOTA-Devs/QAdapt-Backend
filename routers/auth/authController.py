from fastapi import APIRouter
from config import db_conn

router = APIRouter()

@router.post("/singup")
async def singup():
    return { "message": "Singup" }

@router.post("/login")
async def login():
    return { "message": "Login" }

@router.post("/logout")
async def logout():
    return { "message": "Logout" }

@router.post("/token")
async def refresh_token():
    return { "message": "Refresh" }