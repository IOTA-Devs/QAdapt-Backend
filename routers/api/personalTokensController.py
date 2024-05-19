from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from jose import jwt
from os import getenv

from ...internal import get_db_cursor
from ...middlewares import User, deserialize_user
from ...classes import Error, ErrorCodes

router = APIRouter()

class NewPersonalAccessTokenBody(BaseModel):
    expiration_delta: int | None = None # in seconds
    token_name: str

class RemovePersonalAccessTokenBody(BaseModel):
    token_ids: List[int]

@router.post("/generate_personal_access_token")
async def generate_personal_access_token(current_user: Annotated[User, Depends(deserialize_user)], new_token: NewPersonalAccessTokenBody):
    with get_db_cursor() as cur:
        # First check that the expiration delta is valid
        if new_token.expiration_delta is not None and new_token.expiration_delta < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Error("Invalid expiration delta", ErrorCodes.BAD_REQUEST).to_json())
        
        # Check if the user has more than 5 tokens
        query = "SELECT COUNT(*) FROM PersonalAccessTokens WHERE userId = %s"
        cur.execute(query, (current_user.user_id,))
        count = cur.fetchone()['count']

        if count >= 5:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Error("User has reached the maximum number of tokens", ErrorCodes.INVALID_REQUEST).to_json())

        # Generate the token
        secret_key = getenv("PERSONAL_TOKEN_SECRET_KEY")
        token = jwt.encode({
            "user_id": current_user.user_id,
            "token_name": new_token.token_name,
            "type": "personal_access_token"
        }, key=secret_key, algorithm="HS256")

        # Hash the token
        token_hash = sha256()
        token_hash.update(token.encode())

        token_expires = datetime.now(timezone.utc) + timedelta(seconds=new_token.expiration_delta) if new_token.expiration_delta is not None else None
        query = "INSERT INTO PersonalAccessTokens (userId, name, expiresAt, accessTokenHash) VALUES (%s, %s, %s, %s) RETURNING id"
        cur.execute(query, (current_user.user_id, new_token.token_name, token_expires, token_hash.hexdigest()))
        token_id = cur.fetchone()['id']

        return { "token": token, "token_id": token_id }

@router.delete("/delete_personal_access_tokens")
async def delete_personal_access_token(current_user: Annotated[User, Depends(deserialize_user)], tokens: RemovePersonalAccessTokenBody):
    if (len(tokens.token_ids) > 5):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Error("Cannot delete more than 5 tokens at once", ErrorCodes.INVALID_REQUEST).to_json())

    with get_db_cursor() as cur:
        query = "DELETE FROM PersonalAccessTokens WHERE userId = %s AND Id = ANY(%s)"
        cur.execute(query, (current_user.user_id, tokens.token_ids))
        return { "message": "Tokens deleted" }

@router.get("/")
async def get_personal_access_tokens(current_user: Annotated[User, Depends(deserialize_user)]):
    with get_db_cursor() as cur:
        query = "SELECT Id as token_id, userId as user_id, name, expiresAt as expires_at, createdAt as created_at FROM PersonalAccessTokens WHERE userId = %s"
        cur.execute(query, (current_user.user_id,))
        tokens = cur.fetchall()
        
        return {
            "personal_tokens": tokens
        }