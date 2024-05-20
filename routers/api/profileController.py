from os import getenv
from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, status, UploadFile
from pydantic import BaseModel
from azure.storage.blob import ContentSettings
from datetime import datetime, timezone

from ...internal import verify_password, get_password_hash, get_db_cursor
from ...middlewares import User, deserialize_user
from ...classes import Error, ErrorCodes
from ...internal import sessionHandler, blob_service_client

router = APIRouter()

class NewProfileDataBody(BaseModel):
    new_username: str | None
    new_name: str | None

@router.put('/update')
async def update_profile_data(current_user: Annotated[User, Depends(deserialize_user)], new_profile_data_body: NewProfileDataBody):
    with get_db_cursor() as cur:
        if not new_profile_data_body.new_username and not new_profile_data_body.new_name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Error("No data provided", ErrorCodes.INVALID_REQUEST).to_json())
        
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
async def change_avatar(current_user: Annotated[User, Depends(deserialize_user)], avatar: UploadFile):
    if avatar.content_type != "image/jpg" and avatar.content_type != "image/jpeg": # Only allow JPG and JPEG images
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=Error("Image format not supported", ErrorCodes.INVALID_REQUEST).to_json())
    
    if avatar.size > 8 * 1000000: # Limit file uploads to 8MB
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=Error("Image is to large", ErrorCodes.INVALID_REQUEST).to_json())
    
    # Upload the image to blob storage
    container_name = getenv("STORAGE_CONTAINER_NAME")
    account_name = getenv("STORAGE_ACCOUNT_NAME")

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=f"{current_user.user_id}_avatar.{avatar.content_type.split('/')[1]}")
    blob_client.upload_blob(avatar.file.read(), overwrite=True, content_settings=ContentSettings(content_type='image/jpeg'))

    url = f"https://{account_name}.blob.core.windows.net/{container_name}/{current_user.user_id}_avatar.{avatar.content_type.split('/')[1]}?m={datetime.now(tz=timezone.utc).timestamp()}"

    # Set the url in the database for the user
    with get_db_cursor() as cur:
        query = "UPDATE Users SET avatarUrl = %s WHERE userId = %s"
        cur.execute(query, (url, current_user.user_id))

    return {"message": "Avatar changed successfully", "url": url}

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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Error("User not found", ErrorCodes.RESOURCE_NOT_FOUND).to_json())
        if not verify_password(old_password, user['passwordhash']):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Error("Invalid password", ErrorCodes.AUTHENTICATION_ERROR).to_json())

        # Hash the new password
        new_hashed_password = get_password_hash(new_password)

        query = "UPDATE Users SET passwordHash = %s WHERE userId = %s"
        cur.execute(query, (new_hashed_password, current_user.user_id))
        
        if sign_out_all:
            # Clear all user sessions
            sessionHandler.clear_all_user_sessions_except(current_user.user_id, current_user.session_id)

        return {"message": "Password changed successfully"}

@router.post('/delete_account')
async def delete_account(current_user: Annotated[User, Depends(deserialize_user)], password: Annotated[str, Form(min_length=8, max_length=50)]):
    with get_db_cursor() as cur:
        query = "SELECT passwordHash FROM Users WHERE userId = %s"
        cur.execute(query, (current_user.user_id,))
        user_password = cur.fetchone()
    
    if not verify_password(password, user_password["passwordhash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Error("Invalid password", ErrorCodes.AUTHENTICATION_ERROR).to_json())
    
    # Update account status for deletion
    deletionTimestamp = datetime.now(tz=timezone.utc).timestamp()
    query = "Update Users SET deletionTimestamp = %s"
    cur.execute(query, (deletionTimestamp,))

    return {"message": "Account has been queued for deletion", "deletion_timestamp": deletionTimestamp}