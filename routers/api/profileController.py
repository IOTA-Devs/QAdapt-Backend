import psycopg2
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ...internal import get_conn, release_conn
from ...middlewares import User, deserialize_user
from ...classes import Error, ErrorCodes

router = APIRouter()

class NewUsernameBody(BaseModel):
    new_username: str

class NewNameBody(BaseModel):
    new_name: str

@router.post('/change_username')
async def change_username(current_user: Annotated[User, Depends(deserialize_user)], new_username_body: NewUsernameBody):
    db_conn = get_conn()
    db = db_conn.cursor()

    try:
        db.execute('UPDATE Users SET username = %s WHERE userId = %s', (new_username_body.new_username, current_user.user_id))
        db_conn.commit()
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=500, detail=Error(str(e), ErrorCodes.SERVICE_UNAVAILABLE).to_json())
    finally:
        release_conn(db_conn)

    return {"message": "Username changed successfully"}

@router.post('/change_name')
async def change_name(current_user: Annotated[User, Depends(deserialize_user)], new_name_body: NewNameBody):
    db_conn = get_conn()
    db = db_conn.cursor()

    try:
        db.execute('UPDATE Users SET full_name = %s WHERE userId = %s', (new_name_body.new_name, current_user.user_id))
        db_conn.commit()
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=500, detail=Error(str(e), ErrorCodes.SERVICE_UNAVAILABLE).to_json())
    finally:
        release_conn(db_conn)

    return {"message": "Name changed successfully"}

@router.post('/upload_avatar')
async def change_avatar(current_user: Annotated[User, Depends(deserialize_user)]):
    return {"message": "Avatar changed successfully"}

@router.post('/change_password')
async def change_password(current_user: Annotated[User, Depends(deserialize_user)]):
    return {"message": "Password changed successfully"}

@router.post('/delete_account')
async def delete_account(current_user: Annotated[User, Depends(deserialize_user)]):
    return {"message": "Account deleted successfully"}