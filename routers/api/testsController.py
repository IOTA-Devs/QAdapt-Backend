from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException

from ...middlewares import User, deserialize_user

router = APIRouter()

@router.get("/")
async def get_tests(current_user: Annotated[User, Depends(deserialize_user)]):
    return HTTPException(status_code=501, detail="Not implemented")

@router.delete("/delete_tests")
async def delete_tests(current_user: Annotated[User, Depends(deserialize_user)],):
    return HTTPException(status_code=501, detail="Not implemented")

@router.get("/report")
async def get_test_report_data(current_user: Annotated[User, Depends(deserialize_user)],):
    return HTTPException(status_code=501, detail="Not implemented")