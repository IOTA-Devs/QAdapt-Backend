import psycopg2
from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException
from pydantic import BaseModel
from psycopg2.extras import RealDictCursor

from ...internal import verify_password, get_password_hash, get_db_cursor
from ...middlewares import User, deserialize_user
from ...classes import Error, ErrorCodes
from ...internal import sessionHandler

router = APIRouter()

class NewProfileDataBody(BaseModel):
    new_username: str | None
    new_name: str | None

@router.put('/update')
async def update_profile_data(current_user: Annotated[User, Depends(deserialize_user)], new_profile_data_body: NewProfileDataBody):
    with get_db_cursor() as cur:
        if not new_profile_data_body.new_username and not new_profile_data_body.new_name:
            raise HTTPException(status_code=400, detail=Error("No data provided", ErrorCodes.BAD_REQUEST).to_json())
        
        query = 'UPDATE Users SET '
        params = []

        if new_profile_data_body.new_username:
            query += "username = %s"
            params.append(new_profile_data_body.new_username)
        
        if new_profile_data_body.new_name:
            if new_profile_data_body.new_username:
                query += ", "

            query += "fullName = %s"
            params.append(new_profile_data_body.new_name)

        params.append(current_user.user_id)
        query += "WHERE userId = %s"
        cur.execute(query, params)
                
        return {"message": "Profile data updated successfully"}

@router.post('/upload_avatar')
async def change_avatar(current_user: Annotated[User, Depends(deserialize_user)]):
    return {"message": "Avatar changed successfully"}

@router.post('/change_password')
async def change_password(   
    current_user: Annotated[User, Depends(deserialize_user)],
    old_password: Annotated[str, Form(min_length=8, max_length=50)],
    new_password: Annotated[str, Form(min_length=8, max_length=50)],
    sign_out_all: Annotated[bool, Form()] = False):

    with get_db_cursor() as cur:
        query = "SELECT passwordHash FROM Users WHERE userId = %s"
        cur.execute(query, (current_user.user_id,))
        user = cur.fetchone()

        if not user:
            raise HTTPException(status_code=404, detail=Error("User not found", ErrorCodes.RESOURCE_NOT_FOUND).to_json())
        if not verify_password(old_password, user['passwordhash']):
            raise HTTPException(status_code=400, detail=Error("Invalid password", ErrorCodes.AUTHENTICATION_ERROR).to_json())

        # Hash the new password
        new_hashed_password = get_password_hash(new_password)

        query = "UPDATE Users SET passwordHash = %s WHERE userId = %s"
        cur.execute(query, (new_hashed_password, current_user.user_id))
        
        if sign_out_all:
            # Clear all user sessions
            sessionHandler.clear_all_user_sessions(current_user.user_id)

        return {"message": "Password changed successfully"}

@router.post('/delete_account')
async def delete_account(current_user: Annotated[User, Depends(deserialize_user)]):
    return {"message": "Account deleted successfully"}