from typing import Annotated
from fastapi import APIRouter
from middlewares import deserialize_user, User

router = APIRouter()

@router.get("/test")
async def test(current_user: Annotated[User, deserialize_user]):
    return { "message": "Hello World" }