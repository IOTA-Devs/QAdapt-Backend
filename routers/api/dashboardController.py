from typing import Annotated
from fastapi import APIRouter, Depends, Query
from datetime import datetime, date, timezone
from pydantic import Field

from ...middlewares import User, deserialize_user
from ...internal import use_db, add_months, monthNamesAbbr

router = APIRouter()

@router.get("/general")
async def get_general(current_user: Annotated[User, Depends(deserialize_user)]):
    with use_db() as (cur, _):
        query = 'SELECT * FROM general_dashboard_data(%s)'
        
        cur.execute(query, [current_user.user_id])
        general_data = cur.fetchall()

        return {
            "dashboard_data": general_data[0]
        }

@router.get("/tests_table_data")
async def get_tests_table_data(
    current_user: Annotated[User, Depends(deserialize_user)], 
    start_date: date = Query(lt=datetime.now(tz=timezone.utc).date()),
    end_date: date = Query(lte=datetime.now(tz=timezone.utc).date())):

    with use_db() as (cur, _):
        query = '''SELECT date_part('month', startTimestamp) AS month, COUNT(userId) FROM Tests 
        WHERE userId = %s AND startTimestamp >= %s AND startTimestamp <= %s
        GROUP BY date_part('month', startTimestamp)'''

        cur.execute(query, [current_user.user_id, datetime.combine(start_date, datetime.min.time(), timezone.utc), datetime.combine(end_date, datetime.min.time(), timezone.utc)])
        tests_per_month = cur.fetchall()

        # populate the arrays
        curr_date = start_date
        graph_data = {}
        for _ in range((end_date.year - start_date.year) * 12 + end_date.month - start_date.month + 1):
            graph_data[monthNamesAbbr[curr_date.month] + "\n" + str(curr_date.year)] = 0
            curr_date = add_months(curr_date, 1)
        
        for month_tests in tests_per_month:
            graph_data[monthNamesAbbr[int(month_tests["month"])] + "\n" + str(datetime.now().year)] = month_tests["count"]
        
        labels = [] # labels is an array containing in this case the months of the year from the start_date to the end_date
        data = [] # labels contains the data for each month in the labels array

        labels, data = zip(*graph_data.items())

        return {
            "tests_graph_data": {
                "labels": labels,
                "data": data
            }
        }