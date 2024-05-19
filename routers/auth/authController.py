from fastapi import APIRouter, Depends, HTTPException, Form, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from typing import Annotated

from ...internal import get_password_hash, verify_password, get_db_cursor
from ...middlewares import User, deserialize_user
from ...classes import ErrorCodes, Error
from ...internal import sessionHandler

router = APIRouter()

@router.post("/signup")
async def singup(
    username: Annotated[str, Form(min_length=1, max_length=32)], 
    email: Annotated[EmailStr, Form()], 
    password: Annotated[str, Form(min_length=8, max_length=50)],
    full_name: Annotated[str, Form(min_length=1, max_length=150)] = None):

    with get_db_cursor() as cur:
        # Check if the user already existss
        cur.execute('SELECT * FROM Users WHERE email = %s', (email,))
        user = cur.fetchone()
        if user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Error("User already exists", ErrorCodes.RESOURCE_CONFLICT).to_json())

        # Hash the password for security and storage
        hashed_password = get_password_hash(password)

        cur.execute('INSERT INTO Users (username, email, passwordHash, fullName) VALUES (%s, %s, %s, %s) RETURNING userId, username', (username, email, hashed_password, full_name))
        user = cur.fetchone()

        # get session with access and refresh tokens
        session = await sessionHandler.create_session(user["userid"])
        if not session:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Error("Failed to create session", ErrorCodes.INTERNAL_SERVER_ERROR).to_json())
        
        session["user"] = {
            "username": user["username"],
            "user_id": user["userid"],
            "full_name": full_name,
            "email": email
        }
        return session

@router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    with get_db_cursor() as cur:
        # Verify if the user exists in hte database
        cur.execute('SELECT * FROM Users WHERE email = %s', (form_data.username,))
        user = cur.fetchone()
        
        # If the user does not exists or the password is invalid
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Error("Incorrect username or password", ErrorCodes.INCORRECT_CREDENTIALS).to_json())
        if not verify_password(form_data.password, user["passwordhash"]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Error("Incorrect username or password", ErrorCodes.INCORRECT_CREDENTIALS).to_json())
        
        # Create session with access and refresh tokens
        session = await sessionHandler.create_session(user["userid"])
        if not session:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Error("Failed to create session", ErrorCodes.INTERNAL_SERVER_ERROR).to_json())
        
        session["user"] = {
            "username": user["username"],
            "user_id": user["userid"],
            "full_name": user["fullname"],
            "email": user["email"]
        }
        return session

@router.post("/token")
async def refresh_token(refresh_token: Annotated[str, Form()], session_id: Annotated[str, Form()]):
    new_tokens = await sessionHandler.revalidate_session(refresh_token, session_id)
    if new_tokens["error"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Error("Invalid refresh token", ErrorCodes.AUTHENTICATION_ERROR).to_json())

    # Return new access and refresh tokens
    return new_tokens["tokens"]

@router.post("/logout")
async def logout(current_user: Annotated[User, Depends(deserialize_user)]):
    logged_out = await sessionHandler.delete_session(current_user.session_id)

    if (logged_out):
        return { "message": "Session closed" }
    
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Error("Failed to close session", ErrorCodes.INTERNAL_SERVER_ERROR).to_json())