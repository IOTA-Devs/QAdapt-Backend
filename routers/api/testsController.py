from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ...middlewares import User, deserialize_user
from ...internal import use_db
from ...classes import Error, ErrorCodes

router = APIRouter()

class RemoveTestsBody(BaseModel):
    test_ids: List[int]

@router.get("/")
async def get_tests(
    current_user: Annotated[User, Depends(deserialize_user)], 
    limit: Annotated[int, Field(gt=0, lt=501)] = 100, 
    cursor: int = None, 
    script_id: int = None, 
    recent: bool = True,
    filter: str = "all"
    ):
    with use_db() as (cur, _):
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
    
@router.get("/report/{test_id}")
async def get_test_report_data(
    current_user: Annotated[User, Depends(deserialize_user)],
    test_id: int
    ):
    with use_db() as (cur, _):
        # Query to get test details
        test_query = '''SELECT 
                        testId as test_id, 
                        scriptId AS script_id, 
                        name, 
                        startTimestamp AS start_timestamp, 
                        endTimestamp AS end_timestamp, 
                        status
                        FROM Tests 
                        WHERE userId = %s AND testId = %s'''
        cur.execute(test_query, [current_user.user_id, test_id])
        test = cur.fetchone()

        if not test:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Error(f"Test with id {test_id} not found for user {current_user.user_id}", ErrorCodes.RESOURCE_NOT_FOUND).to_json())
        
        # Query to get self-healing report details
        report_query = '''SELECT
                        seleniumSelectorName AS selenium_selector_name, 
                        healingDescription AS healing_description, 
                        status, 
                        screenshotPath AS screenshot_path 
                        FROM SelfHealingReports 
                        WHERE testId = %s'''
        cur.execute(report_query, (test_id,))
        reports = cur.fetchall()

        return {
            "test": test,
            "reports": reports
        }