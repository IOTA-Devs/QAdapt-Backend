from hashlib import sha256
from fastapi import APIRouter, HTTPException
import psycopg2
from config.db import get_conn, release_conn
from pydantic import BaseModel, EmailStr
from typing import Annotated
from util import sessionHandler
from util.password import get_password_hash, verify_password
from psycopg2.extras import RealDictCursor
from util.jwt import verify_token

router = APIRouter()

class NewUser(BaseModel):
    username: Annotated[str, { "min_length": 1, "max_length": 32 }]
    first_name: str
    last_name: str
    email: EmailStr
    password: Annotated[str, { "min_length": 8, "max_length": 50 }]

class UserLoginCredentials(BaseModel):
    email: EmailStr
    password: str

class TokenModel(BaseModel):
    refresh_token: str
    session_id: str

@router.post("/singup")
async def singup(new_user: NewUser):
    db_conn = get_conn()
    db = db_conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Check if the user already exists
        db.execute('SELECT * FROM Users WHERE email = %s', (new_user.email,))
        user = db.fetchone()
        if user:
            raise HTTPException(status_code=400, detail="Email already in use")

        # Hash the password for security and storage
        hashed_password = get_password_hash(new_user.password)

        db.execute('INSERT INTO Users (username, firstName, lastName, email, passwordHash) VALUES (%s, %s, %s, %s, %s) RETURNING userId', (new_user.username, new_user.first_name, new_user.last_name, new_user.email, hashed_password))
        db_conn.commit()
        user = db.fetchone()

        session = await sessionHandler.create_session(user["userid"])
        if not session:
            raise HTTPException(status_code=500, detail="Failed to create session")
    except HTTPException:
        raise
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=500, detail=str(e))

    release_conn(db_conn)
    return session

@router.post("/login")
async def login(user_credentials: UserLoginCredentials):
    db_conn = get_conn()
    db = db_conn.cursor(cursor_factory=RealDictCursor)

    try:
        db.execute('SELECT * FROM Users WHERE email = %s', (user_credentials.email,))
        user = db.fetchone()
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    if not verify_password(user_credentials.password, user["passwordHash"]):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    session = await sessionHandler.create_session(user["userId"])
    if not session:
        raise HTTPException(status_code=500, detail="Failed to create session")
    
    release_conn(db_conn)
    return session

@router.post("/token")
async def refresh_token(token_data: TokenModel):
    refresh_token = token_data.refresh_token
    session_id = token_data.session_id

    token_payload = verify_token(refresh_token, "refresh")
    if token_payload["error"]:
        raise HTTPException(status_code=400, detail=token_payload["error"])
    
    new_tokens = await sessionHandler.revalidate_session(refresh_token, session_id)
    if new_tokens["error"]:
        raise HTTPException(status_code=401, detail=new_tokens["error"])

    return new_tokens["tokens"]

@router.post("/logout")
async def logout(token_data: TokenModel):
    return { "message": "Logout" }