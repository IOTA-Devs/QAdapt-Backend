from fastapi import APIRouter
from fastapi import HTTPException, status

router = APIRouter()

@router.get("/alive")
async def api_is_alive():
    response = {
        "status": "alive"
    }
    
    return response

@router.post("/start_report")
async def start_report():
    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")

@router.post("/create_report_item")
async def create_report_item():
    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")

@router.post("/end_report")
async def end_report():
    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")