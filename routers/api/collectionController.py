import psycopg2
from typing import Annotated
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from psycopg2.extras import RealDictCursor

from ...classes import ErrorCodes, Error
from ...internal import get_conn, release_conn, use_db
from ...middlewares import User, deserialize_user

router = APIRouter()

class CollectionData(BaseModel):
    name: str
    description: str

#buscar collections con el userId
#buscar pruebas con el collectionid
#innerjoin, procedure
@router.get('/')
async def get_collections(current_user: Annotated[User, Depends(deserialize_user)]):
    # idk si esto se tiene que hacer
    db_conn = get_conn()
    db = db_conn.cursor(cursor_factory=RealDictCursor)
    try:
        query = "SELECT collections.collectionid, collections.name, lastmodified, description FROM collections WHERE userid = %s"
        db.execute(query, (current_user.user_id,))
        userCollections = db.fetchall()
        for collection in userCollections:
            query = "SELECT * FROM tests WHERE userid = %s AND collectionId = %s"
            db.execute(query, (current_user.user_id, collection['collectionid']))
            collectionTests = db.fetchall()
            collection["tests"] = collectionTests
        return userCollections
    except HTTPException:
        raise 
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Error(str(e), ErrorCodes.SERVICE_UNAVAILABLE).to_json())
    finally:
        release_conn(db_conn)

@router.post('/create_collection')
async def create_collection(current_user: Annotated[User, Depends(deserialize_user)], collection_data: CollectionData):
    with use_db() as (cur, _):
        query = "INSERT INTO Collections (name, description, userId, lastModified) VALUES (%s, %s, %s, CURRENT_DATE)"
        cur.execute(query, (collection_data.name, collection_data.description, current_user.user_id))
    return {"message": "Collection created successfully"}

@router.delete('/delete_collection/{collection_id}')
async def delete_collection(current_user: Annotated[User, Depends(deserialize_user)], collection_id: int):
    with use_db() as (cur, _):
        # Check if the collection exists and belongs to the current user
        query = "SELECT COUNT(*) FROM Collections WHERE collectionId = %s AND userId = %s"
        cur.execute(query, (collection_id, current_user.user_id))
        collection_count = cur.fetchone()[0]

        if collection_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found or does not belong to the current user")

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
        collection_count = cur.fetchone()[0]

        if collection_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found or does not belong to the current user")

        query = "UPDATE Collections SET name = %s, description = %s, lastModified = CURRENT_DATE WHERE collectionId = %s AND userId = %s"
        cur.execute(query, (collection_data.name, collection_data.description, collection_id, current_user.user_id))
    return {"message": "Collection updated successfully"}