import psycopg2
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import RealDictCursor

from ...classes import ErrorCodes, Error
from ...internal import get_conn, release_conn
from ...middlewares import User, deserialize_user

router = APIRouter()

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
            query = "SELECT * FROM tests WHERE userid = %s"
            db.execute(query, (current_user.user_id,))
            collectionTests = db.fetchall()
            collection["tests"] = collectionTests
        return userCollections
        #return current_user
    except HTTPException:
        raise 
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=500, detail=Error(str(e), ErrorCodes.SERVICE_UNAVAILABLE).to_json())
    finally:
        release_conn(db_conn)

@router.post('/create_collection')
async def create_collection(current_user: Annotated[User, Depends(deserialize_user)]):
    return HTTPException(status_code=501, detail="Not implemented")

@router.post('/delete_collections')
async def delete_collections(current_user: Annotated[User, Depends(deserialize_user)]):
    return HTTPException(status_code=501, detail="Not implemented")

@router.put('/update_collection')
async def update_collection(current_user: Annotated[User, Depends(deserialize_user)]):
    return HTTPException(status_code=501, detail="Not implemented")