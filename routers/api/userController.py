from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
import psycopg2
from config.db import get_conn, release_conn
from psycopg2.extras import RealDictCursor
from models import ErrorCodes, Error

from middlewares.deserializeUser import User, deserialize_user

router = APIRouter()

@router.get('/me')
async def get_my_user_info(current_user: Annotated[User, Depends(deserialize_user)]):
    db_conn = get_conn()
    db = db_conn.cursor(cursor_factory=RealDictCursor)

    try:
        query = "SELECT userId as user_id, username, email, fullName as full_name, email, joinedAt as joined_at FROM Users WHERE userId = %s"
        db.execute(query, (current_user.user_id,))
        user = db.fetchone()

        if user == None:
            raise HTTPException(status_code=404, detail=Error("User not found", ErrorCodes.RESOURCE_NOT_FOUND).to_json())

        return user
    except HTTPException:
        raise
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=500, detail=Error(str(e), ErrorCodes.SERVICE_UNAVAILABLE).to_json())
    finally:
        release_conn(db_conn)