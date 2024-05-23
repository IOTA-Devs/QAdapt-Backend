from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import Field

from ...middlewares import User, deserialize_user
from ...internal import get_db_cursor

router = APIRouter()

@router.get("/")
async def get_tests(
    current_user: Annotated[User, Depends(deserialize_user)], 
    limit: Annotated[int, Field(gt=0, lt=501)] = 100, 
    cursor: int = None, 
    script_id: int = None, 
    recent: bool = True,
    filter: str = "all"
    ):
    with get_db_cursor() as cur:
        query = '''SELECT 
                    testId as test_id, 
                    scriptid AS script_id, 
                    name, 
                    startTimestamp AS start_timestamp, 
                    endTimestamp AS end_timestamp, 
                    status 
                    FROM Tests WHERE userId = %s '''
        params = [current_user.user_id]

        if script_id is not None:
            query += 'AND scriptId = %s'
            params.append(script_id)

        if cursor is not None:
            if recent:
                query += 'AND testId < %s'
            else:
                query += 'AND testId > %s'
            params.append(cursor)

        if filter != "all":
            query += 'AND status = %s'
            params.append(filter)

        query += f" ORDER BY testId {"DESC" if recent == True else "ASC"} LIMIT %s"
        params.append(limit)

        cur.execute(query, params)
        tests = cur.fetchall()

        return {
            "limit": limit,
            "tests": tests,
            "total_fetched": len(tests)
        }

@router.delete("/delete_tests")
async def delete_tests(current_user: Annotated[User, Depends(deserialize_user)],):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")

@router.get("/report")
async def get_test_report_data(current_user: Annotated[User, Depends(deserialize_user)],):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")