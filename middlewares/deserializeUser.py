from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from ..internal import verify_access_token

class User(BaseModel):
    user_id: int
    session_id: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def deserialize_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Unauthorized",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    payload = verify_access_token(token)
    if payload["error"]:
        raise credentials_exception
    
    user = User(session_id=payload["payload"]["sessionId"], user_id=payload["payload"]["userId"])
    return user