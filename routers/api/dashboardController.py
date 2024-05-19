from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from ...middlewares import User, deserialize_user

router = APIRouter()

@router.get("/general")
async def get_general(current_user: Annotated[User, Depends(deserialize_user)]):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")

@router.get("/reports_timeline")
async def get_reports_timeline(current_user: Annotated[User, Depends(deserialize_user)]):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")

@router.get("/recent_reports")
async def get_recent_reports(current_user: Annotated[User, Depends(deserialize_user)]):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")

@router.get("/notifications")
async def get_notifications(current_user: Annotated[User, Depends(deserialize_user)]):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")