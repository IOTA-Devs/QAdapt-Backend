from typing import Annotated
from fastapi import APIRouter, Depends
from middlewares.deserializeUser import User, deserialize_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class NewPersonalAccessToken(BaseModel):
    expiration_delta: datetime | None = None
    token_name: str

class RemovePersonalAccessToken(BaseModel):
    token_id: int

@router.post("/generte_personal_access_token")
async def generate_personal_access_token(current_user: Annotated[User, Depends(deserialize_user)], new_token: NewPersonalAccessToken):
    pass

@router.delete("/delete_personal_access_token")
async def delete_personal_access_token(current_user: Annotated[User, Depends(deserialize_user)], token: RemovePersonalAccessToken):
    pass

@router.get("/get_personal_access_tokens")
async def get_personal_access_tokens(current_user: Annotated[User, Depends(deserialize_user)]):
    pass