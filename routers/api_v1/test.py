from fastapi import APIRouter
from config import db_conn

router = APIRouter()

@router.get("/test")
async def test():
    return { "message": "Hello World" }