from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from psycopg2.extras import RealDictCursor
from jose import jwt
from os import getenv

from ...internal import get_conn, release_conn
from ...middlewares import User, deserialize_user
from ...classes import Error, ErrorCodes

router = APIRouter()

class NewPersonalAccessTokenBody(BaseModel):
    expiration_delta: int | None = None # in seconds
    token_name: str

class RemovePersonalAccessTokenBody(BaseModel):
    token_id: int

@router.post("/generate_personal_access_token")
async def generate_personal_access_token(current_user: Annotated[User, Depends(deserialize_user)], new_token: NewPersonalAccessTokenBody):
    db_conn = get_conn()
    db = db_conn.cursor()

    # First check that the expiration delta is valid
    if new_token.expiration_delta is not None and new_token.expiration_delta < 0:
        raise HTTPException(status_code=400, detail=Error("Invalid expiration delta", ErrorCodes.BAD_REQUEST).to_json())
    
    # Check if the user has more than 5 tokens
    try:
        query = "SELECT COUNT(*) FROM PersonalAccessTokens WHERE userId = %s"
        db.execute(query, (current_user.user_id,))
        count = db.fetchone()[0]
    except Exception as e:
        print("Error fetching tokens: ", e)
        release_conn(db_conn)
        raise HTTPException(status_code=500, detail=Error("Error fetching tokens", ErrorCodes.INTERNAL_SERVER_ERROR).to_json())

    if count >= 5:
        release_conn(db_conn)
        raise HTTPException(status_code=400, detail=Error("User has reached the maximum number of tokens", ErrorCodes.INVALID_REQUEST).to_json())

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
    try:
        query = "INSERT INTO PersonalAccessTokens (userId, name, expiresAt, accessTokenHash) VALUES (%s, %s, %s, %s) RETURNING id"
        db.execute(query, (current_user.user_id, new_token.token_name, token_expires, token_hash.hexdigest()))
        token_id = db.fetchone()[0]
        db_conn.commit()
    except Exception as e:
        print("Error generating token: ", e)
        raise HTTPException(status_code=500, detail=Error("Error generating token", ErrorCodes.INTERNAL_SERVER_ERROR).to_json())
    finally:
        release_conn(db_conn)

    return { "token": token, "token_id": token_id }

@router.delete("/delete_personal_access_token")
async def delete_personal_access_token(current_user: Annotated[User, Depends(deserialize_user)], token: RemovePersonalAccessTokenBody):
    db_conn = get_conn()
    db = db_conn.cursor()

    try:
        query = "DELETE FROM PersonalAccessTokens WHERE userId = %s AND id = %s"
        db.execute(query, (current_user.user_id, token.token_id))
        db_conn.commit()
    except Exception as e:
        print("Error deleting token: ", e)
        raise HTTPException(status_code=500, detail=Error("Error deleting token", ErrorCodes.INTERNAL_SERVER_ERROR).to_json())
    finally:
        release_conn(db_conn)
    
    return { "message": "Token deleted" }

@router.get("/")
async def get_personal_access_tokens(current_user: Annotated[User, Depends(deserialize_user)]):
    db_conn = get_conn()
    db = db_conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        query = "SELECT userId as user_id, name, expiresAt as expires_at, createdAt as created_at FROM PersonalAccessTokens WHERE userId = %s"
        db.execute(query, (current_user.user_id,))
        tokens = db.fetchall()
    except Exception as e:
        print("Error fetching tokens: ", e)
        raise HTTPException(status_code=500, detail=Error("Error fetching tokens", ErrorCodes.INTERNAL_SERVER_ERROR).to_json())
    finally:
        release_conn(db_conn)

    if not tokens:
        return {
            "personal_tokens": []
        }
    
    return {
        "personal_tokens": tokens
    }