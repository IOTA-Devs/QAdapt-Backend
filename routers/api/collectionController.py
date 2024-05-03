from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
import psycopg2
from config.db import get_conn, release_conn
from psycopg2.extras import RealDictCursor
from models import ErrorCodes, Error

from middlewares.deserializeUser import User, deserialize_user

router = APIRouter()

#buscar collections con el userId
#buscar pruebas con el collectionid
#innerjoin, procedure
@router.get('/')
async def get_collections(current_user: Annotated[User, Depends(deserialize_user)]):
    #idk si esto se tiene que hacer
    db_conn = get_conn()
    db = db_conn.cursor(cursor_factory=RealDictCursor)
    try:
        query = "SELECT collections.collectionid, collections.name, lastmodified, description FROM collections WHERE userid = 1"
        db.execute(query)
        userCollections = db.fetchall()
        return userCollections
        #return current_user
    except HTTPException:
        raise 
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=500, detail=Error(str(e), ErrorCodes.SERVICE_UNAVAILABLE).to_json())
    finally:
        release_conn(db_conn)
