from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Query, status

from ...classes import ErrorCodes, Error
from ...internal import use_db, sanitize_search_query
from ...middlewares import User, deserialize_user

router = APIRouter()

class CollectionData(BaseModel):
    name: str = Field(max_length=32, min_length=1)
    description: str = Field(max_length=256, min_length=1)

@router.get('')
async def get_collections(
    current_user: Annotated[User, Depends(deserialize_user)],
    limit: Annotated[int, Field(gt=0, lt=101)] = 50, 
    cursor: int = None):

    with use_db() as (cur, _):
        params = [current_user.user_id]
        query = '''SELECT 
                    collectionId as collection_id,
                    name, 
                    lastModified as last_updated, 
                    description,
                    scripts,
                    tests
                    FROM collections WHERE userid = %s'''

        if cursor is not None:
            query += 'AND lastModified < %s'
            params.append(datetime.fromtimestamp(cursor / 1000.0))

        query += ' ORDER BY lastModified DESC LIMIT %s'
        params.append(limit)

        cur.execute(query, params)
        userCollections = cur.fetchall()

        return {
            "limit": limit,
            "collections": userCollections,
            "total_fetched": len(userCollections)
        }

@router.get('/count')
async def get_collections_count(current_user: Annotated[User, Depends(deserialize_user)]):
    with use_db() as (cur, _):
        query = "SELECT COUNT(*) FROM Collections WHERE userId = %s"
        cur.execute(query, (current_user.user_id,))
        count = cur.fetchone()["count"]

        return {"count": count}
    
@router.get('/search')
async def search_collections_by_name(current_user: Annotated[User, Depends(deserialize_user)], search_query: Annotated[str, Query(max_length=32, min_length=1)]):
    sanitized_query = sanitize_search_query(search_query)
    with use_db() as (cur, _):
        query = '''SELECT
                    collectionId as collection_id,
                    name, 
                    lastModified as last_updated, 
                    description,
                    scripts,
                    tests
                    FROM collections WHERE LOWER(name) LIKE LOWER(%s) AND userId = %s'''
        cur.execute(query, (f'%{sanitized_query}%', current_user.user_id))
        collections = cur.fetchall()

        return {
            "results": collections 
        }
    
@router.post('/create_collection')
async def create_collection(current_user: Annotated[User, Depends(deserialize_user)], collection_data: CollectionData):
    with use_db() as (cur, _):
        query = "INSERT INTO Collections (name, description, userId, lastModified) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)"
        cur.execute(query, (collection_data.name, collection_data.description, current_user.user_id))
    return {"message": "Collection created successfully"}

@router.delete('/delete_collection/{collection_id}')
async def delete_collection(current_user: Annotated[User, Depends(deserialize_user)], collection_id: int):
    with use_db() as (cur, _):
        # Check if the collection exists and belongs to the current user
        query = "SELECT COUNT(*) FROM Collections WHERE collectionId = %s AND userId = %s"
        cur.execute(query, (collection_id, current_user.user_id))
        collection_count = cur.fetchone()["count"]

        if collection_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Error(f"Collection with id {collection_id} not found for user {current_user.user_id}", ErrorCodes.RESOURCE_NOT_FOUND).to_json())

        # Delete the collection and associated scripts and tests
        query = "DELETE FROM Collections WHERE collectionId = %s AND userId = %s"
        cur.execute(query, (collection_id, current_user.user_id))
    return {"message": "Collection and associated data deleted successfully"}

@router.put('/update_collection/{collection_id}')
async def update_collection(current_user: Annotated[User, Depends(deserialize_user)], collection_id: int, collection_data: CollectionData):
    with use_db() as (cur, _):
        # Check if the collection exists and belongs to the current user
        query = "SELECT COUNT(*) FROM Collections WHERE collectionId = %s AND userId = %s"
        cur.execute(query, (collection_id, current_user.user_id))
        collection_count = cur.fetchone()["count"]

        if collection_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Error(f"Collection with id {collection_id} not found for user {current_user.user_id}", ErrorCodes.RESOURCE_NOT_FOUND).to_json())

        query = "UPDATE Collections SET name = %s, description = %s, lastModified = CURRENT_TIMESTAMP WHERE collectionId = %s AND userId = %s"
        cur.execute(query, (collection_data.name, collection_data.description, collection_id, current_user.user_id))
    return {"message": "Collection updated successfully"}