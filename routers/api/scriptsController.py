from typing import Annotated
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends

from ...middlewares import User, deserialize_user
from ...internal import use_db, sanitize_search_query

router = APIRouter()

class ScriptData(BaseModel):
    name: str = Field(max_length=32, min_length=1)
    collection_id: int

class UpdateScritData(BaseModel):
    name: str = Field(max_length=32, min_length=1)
    script_id: int

@router.get('/')
async def get_scripts(
    current_user: Annotated[User, Depends(deserialize_user)],
    collection_id: int,
    limit: Annotated[int, Field(gt=0, lt=501)] = 100,
    cursor: int = None):

    with use_db() as (cur, _):
        params = [current_user.user_id, collection_id]
        query = '''SELECT 
                    scriptId as script_id,
                    name,
                    tests
                    FROM Scripts WHERE userId = %s AND collectionId = %s'''

        if cursor is not None:
            query += 'AND scriptId < %s'
            params.append(cursor)
        
        query += ' ORDER BY scriptId DESC LIMIT %s'
        params.append(limit)
        cur.execute(query, params)
        scripts = cur.fetchall()
        
        return {
            "limit": limit,
            "scripts": scripts,
            "total_fetched": len(scripts)
        }
    
@router.get('/search')
async def search_scripts_by_name(current_user: Annotated[User, Depends(deserialize_user)], collection_id: int, search_query: str):
    sanitized_query = sanitize_search_query(search_query)
    with use_db() as (cur, _):
        query = '''SELECT 
                    scriptId as script_id,
                    name,
                    tests
                    FROM Scripts WHERE userId = %s AND collectionId = %s AND LOWER(name) LIKE LOWER(%s)'''
        cur.execute(query, (current_user.user_id, collection_id, f"%{sanitized_query}%"))
        scripts = cur.fetchall()

        print(sanitized_query)

        return {
            "results": scripts,
        }

@router.post('/create_script')
async def create_script(current_user: Annotated[User, Depends(deserialize_user)], script_data: ScriptData):
    with use_db() as (cur, _):
        query = "INSERT INTO Scripts (name, collectionId, userId) VALUES (%s, %s, %s)"
        cur.execute(query, (script_data.name, script_data.collection_id, current_user.user_id))
        return {"message": "Script created successfully"}

@router.put('/update_script')
async def update_script(current_user: Annotated[User, Depends(deserialize_user)], script_data: UpdateScritData):
    with use_db() as (cur, _):
        query = "UPDATE Scripts SET name = %s WHERE scriptId = %s AND userId = %s"
        cur.execute(query, (script_data.name, script_data.script_id, current_user.user_id))
        return {"message": "Script updated successfully"}

@router.delete('/delete_script/{script_id}')
async def delete_script(current_user: Annotated[User, Depends(deserialize_user)], script_id: int):
    with use_db() as (cur, _):
        query = "DELETE FROM Scripts WHERE scriptId = %s AND userId = %s"
        cur.execute(query, (script_id, current_user.user_id))
        return {"message": "Script deleted successfully"}