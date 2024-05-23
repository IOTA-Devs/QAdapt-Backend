from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from ...internal import use_db
from ...classes import ErrorCodes, Error
from ...middlewares import User, deserialize_user

router = APIRouter()

@router.get('/me')
async def get_my_user_info(current_user: Annotated[User, Depends(deserialize_user)]):
    with use_db() as (cur, _):
        query = "SELECT userId as user_id, username, email, fullName as full_name, email, joinedAt as joined_at, avatarURL as avatar_url FROM Users WHERE userId = %s"
        cur.execute(query, (current_user.user_id,))
        user = cur.fetchone()

        if user == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Error("User not found", ErrorCodes.RESOURCE_NOT_FOUND).to_json())

        return user