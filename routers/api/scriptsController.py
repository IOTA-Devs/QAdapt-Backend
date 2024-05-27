from typing import Annotated
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status

from ...middlewares import User, deserialize_user
from ...internal import use_db
from ...classes import Error, ErrorCodes

router = APIRouter()

class ScriptData(BaseModel):
    name: str
    collection_id: int

@router.get('/')
async def get_scripts(current_user: Annotated[User, Depends(deserialize_user)]):
    with use_db() as (cur, _):
        query = "SELECT * FROM Scripts WHERE userId = %s"
        cur.execute(query, (current_user.user_id,))
        scripts = cur.fetchall()
        return scripts

@router.post('/create_script')
async def create_script(current_user: Annotated[User, Depends(deserialize_user)], script_data: ScriptData):
    with use_db() as (cur, _):
        query = "INSERT INTO Scripts (name, collectionId, userId) VALUES (%s, %s, %s)"
        cur.execute(query, (script_data.name, script_data.collection_id, current_user.user_id))
        return {"message": "Script created successfully"}

@router.put('/update_script/{script_id}')
async def update_script(current_user: Annotated[User, Depends(deserialize_user)], script_id: int, script_data: ScriptData):
    with use_db() as (cur, _):
        query = "UPDATE Scripts SET name = %s, collectionId = %s WHERE scriptId = %s AND userId = %s"
        cur.execute(query, (script_data.name, script_data.collection_id, script_id, current_user.user_id))
        return {"message": "Script updated successfully"}

@router.delete('/delete_script/{script_id}')
async def delete_script(current_user: Annotated[User, Depends(deserialize_user)], script_id: int):
    with use_db() as (cur, _):
        query = "DELETE FROM Scripts WHERE scriptId = %s AND userId = %s"
        cur.execute(query, (script_id, current_user.user_id))
        return {"message": "Script deleted successfully"}