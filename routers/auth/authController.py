from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordRequestForm
import psycopg2
from config.db import get_conn, release_conn
from pydantic import EmailStr
from typing import Annotated
from middlewares.deserializeUser import User, deserialize_user
from util import sessionHandler
from util.password import get_password_hash, verify_password
from psycopg2.extras import RealDictCursor
from models import ErrorCodes, Error

router = APIRouter()

@router.post("/signup")
async def singup(
    username: Annotated[str, Form(min_length=1, max_length=32)], 
    email: Annotated[EmailStr, Form()], 
    password: Annotated[str, Form(min_length=8, max_length=50)]):
    db_conn = get_conn()
    db = db_conn.cursor(cursor_factory=RealDictCursor)
    try:
        # Check if the user already exists
        db.execute('SELECT * FROM Users WHERE email = %s', (email,))
        user = db.fetchone()
        if user:
            raise HTTPException(status_code=400, detail=Error("User already exists", ErrorCodes.RESOURCE_CONFLICT).to_json())

        # Hash the password for security and storage
        hashed_password = get_password_hash(password)

        db.execute('INSERT INTO Users (username, email, passwordHash) VALUES (%s, %s, %s) RETURNING userId, username', (username, email, hashed_password))
        db_conn.commit()
        user = db.fetchone()

        # get session with access and refresh tokens
        session = await sessionHandler.create_session(user["userid"])
        if not session:
            raise HTTPException(status_code=500, detail=Error("Failed to create session", ErrorCodes.INTERNAL_SERVER_ERROR).to_json())
    except HTTPException:
        raise
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=500, detail=Error(str(e), ErrorCodes.SERVICE_UNAVAILABLE).to_json())
    finally:
        release_conn(db_conn)
    
    session["user"] = {
        "username": user["username"],
        "user_id": user["userid"]
    }
    return session

@router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    db_conn = get_conn()
    db = db_conn.cursor(cursor_factory=RealDictCursor)

    # Verify if the user exists in hte database
    try:
        db.execute('SELECT * FROM Users WHERE email = %s', (form_data.username,))
        user = db.fetchone()
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=500, detail=Error(str(e), ErrorCodes.SERVICE_UNAVAILABLE).to_json())
    finally:
        release_conn(db_conn)
    
    # If the user does not exists or the password is invalid
    if not user:
        raise HTTPException(status_code=400, detail=Error("Incorrect username or password", ErrorCodes.INCORRECT_CREDENTIALS).to_json())
    if not verify_password(form_data.password, user["passwordhash"]):
        raise HTTPException(status_code=400, detail=Error("Incorrect username or password", ErrorCodes.INCORRECT_CREDENTIALS).to_json())
    
    # Create session with access and refresh tokens
    session = await sessionHandler.create_session(user["userid"])
    if not session:
        raise HTTPException(status_code=500, detail=Error("Failed to create session", ErrorCodes.INTERNAL_SERVER_ERROR).to_json())
    
    session["user"] = {
        "username": user["username"],
        "user_id": user["userid"]
    }
    return session

@router.post("/token")
async def refresh_token(refresh_token: Annotated[str, Form()], session_id: Annotated[str, Form()]):
    new_tokens = await sessionHandler.revalidate_session(refresh_token, session_id)
    if new_tokens["error"]:
        raise HTTPException(status_code=401, detail=Error("Invalid refresh token", ErrorCodes.AUTHENTICATION_ERROR).to_json())

    # Return new access and refresh tokens
    return new_tokens["tokens"]

@router.post("/logout")
async def logout(current_user: Annotated[User, Depends(deserialize_user)]):
    logged_out = await sessionHandler.delete_session(current_user.session_id)

    if (logged_out):
        return { "message": "Session closed" }
    
    raise HTTPException(status_code=500, detail=Error("Failed to close session", ErrorCodes.INTERNAL_SERVER_ERROR).to_json())