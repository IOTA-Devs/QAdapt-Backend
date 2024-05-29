from fastapi import APIRouter, Depends
from fastapi import HTTPException, status, UploadFile, Form, File
from pydantic import BaseModel

from typing import Annotated, Any
from ...middlewares.verifyPersonalAccessToken import TokenData, verify_personal_access_token
from ...internal import use_db
router = APIRouter()


@router.get("/alive")
async def api_is_alive():
    response = {
        "status": "alive"
    }
    
    return response


class startReportBody(BaseModel):
    reportId: int
@router.post("/start_report")
async def start_report(token: Annotated[TokenData, Depends(verify_personal_access_token)], reqBody: startReportBody):
    with use_db() as (cur, _):
        query =  "UPDATE selfhealingreports SET status='Failed', healingdescription='original locator failed, starting self-healing' WHERE reportid=%s RETURNING *"
        response = cur.execute(query, (reqBody.reportId,))
        return response


class createReportBody(BaseModel):
    selenium_selector: Annotated[str, Form()]
    testId: Annotated[str, Form()]
    img: Annotated[UploadFile, File()]
@router.post("/create_report_item", response_model=None)
async def create_report_item(
    token: Annotated[TokenData, Depends(verify_personal_access_token)],
    selenium_selector: Annotated[str, Form()],
    testId: Annotated[str, Form()],
    img: Annotated[UploadFile, File()]
):
    
    with use_db() as (cur, _):
        query = "INSERT INTO selfhealingreports (testid, seleniumselectorname, healingdescription, status, screenshotpath) VALUES (%s, %s, 'self-healing has not started', 'Pending', %s) RETURNING *"
        #verificar que testid sea del usuario actual en token
        #variable temporal, cuando consiga la path real usar eso
        img_path = ""
        cur.execute(query, (testId, selenium_selector, img_path))
        result = cur.fetchone()
        print("result es: ")
        print(result["reportid"])
        return result["reportid"]
    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")

class EndReportBody(BaseModel):
    status: str
    healingDescription: str
    reportId: str
@router.post("/end_report")
async def end_report(token: Annotated[TokenData, Depends(verify_personal_access_token)], reqBody: EndReportBody):
    with use_db() as (cur, _):
        query = "UPDATE selfhealingreports SET status=%s, healingdescription=%s WHERE reportid=%s RETURNING *"
        response = cur.execute(query, (reqBody.status, reqBody.healingDescription, reqBody.reportId))
        return response

class setupBody(BaseModel):
    test: str
    script: str
    collection: str
@router.post('/selfHealingSetup')
async def setup(token: Annotated[TokenData, Depends(verify_personal_access_token)], reqBody: setupBody):
    #checar si existe una coleccion con ese nombre, si no existe agregarla, checar si no existe un script con ese nombre si no existe crearlo y asignar a coleccion, checar si existe un test con ese nombre, si no existe agregarlo
    #si existe el test regresarlo y ya
    with use_db() as (cur, _):
        query = "SELECT * FROM tests WHERE userid=%s AND name=%s"
        response = cur.execute(query, (token.user_id, reqBody.test))
        if response:
            return response
        else:
            return {"nah man":"rip"}
    pass