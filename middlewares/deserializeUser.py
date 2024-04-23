from typing import Annotated
from fastapi import Depends, Header, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from pydantic import BaseModel
from util.jwt import verify_token

class User(BaseModel):
    username: str
    email: str
    session_id: str

async def deserialize_user(req: Request):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Unauthorized",
        headers={"WWW-Authenticate": "Bearer"}
    )

    token = req.headers.get("Authorization")

    if not token or not token.startswith("Bearer "):
        raise credentials_exception
    
    token.replace("Bearer ", "")

    if not token:
        raise credentials_exception
    
    payload = verify_token(token, "access")
    if payload["error"]:
        raise credentials_exception
    
    user = User(username=payload["payload"]["username"], email=payload["payload"]["email"], session_id=payload["payload"]["sessionId"])
    return user