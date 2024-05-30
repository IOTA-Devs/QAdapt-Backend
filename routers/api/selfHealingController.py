from os import getenv
from fastapi import APIRouter, Depends
from fastapi import HTTPException, status, UploadFile, Form, File
from pydantic import BaseModel
from azure.storage.blob import ContentSettings
from datetime import datetime, timezone

from typing import Annotated, Any
from ...middlewares.verifyPersonalAccessToken import TokenData, verify_personal_access_token
from ...internal import use_db
from ...internal import blob_service_client
from ...classes import Error, ErrorCodes
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
        if img.size > 8 * 1000000:
            raise HTTPException(status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=Error("Image is too large", ErrorCodes.INVALID_REQUEST).to_json())

        container_name = getenv("STORAGE_CONTAINER_NAME")
        account_name = getenv("STORAGE_ACCOUNT_NAME")

        blob_client = blob_service_client.get_blob_client(container=container_name, blob=f"{token.user_id}_{result["reportid"]}_image.png")
        blob_client.upload_blob(img.file.read(), overwrite=True, content_settings=ContentSettings(content_type='image/jpeg'))
        
        url = f"https://{account_name}.blob.core.windows.net/{container_name}/{token.user_id}_{result["reportid"]}_image.png?m={datetime.now(tz=timezone.utc).timestamp()}"
        query = "UPDATE selfhealingreports SET screenshotpath = %s WHERE testid = %s RETURNING *"
        cur.execute(query, (url, result["testid"]))
        result = cur.fetchone()

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
        userId = str(token.user_id)
        cur.execute(query, (userId, reqBody.test))
        result = cur.fetchone()

        if result:
            return result
        else:
            # como no existe el test, revisar si existe el script especificado
            query = "SELECT * FROM scripts WHERE userid=%s AND name=%s"
            cur.execute(query, (userId, reqBody.script))
            result = cur.fetchone()
            if result:
                #crear y retornar el test que va a este script todo normal chill, obtener el id del script de result
                #no se bien como determinar el status de tests? buscar eso despues tambien lol, asumo que en creacion seria success ig
                query = "INSERT INTO tests (scriptid, userid, name, starttimestamp, endtimestamp, status) VALUES (%s, %s, %s, NOW(), NULL, 'Success') RETURNING *"
                cur.execute(query, (str(result["scriptid"]), userId, reqBody.test))
                result = cur.fetchone()
                return result
            else:
                #revisar si no existe la coleccion
                query = "SELECT * FROM collections WHERE userid=%s AND name=%s"
                cur.execute(query, (userId, reqBody.collection))
                result = cur.fetchone()
                if result:
                    #crear el script con el id de la collection obtener el id, crear el test con el id script retornoarlo
                    query = "INSERT INTO scripts (collectionid, userid, name) VALUES (%s, %s, %s) RETURNING *"
                    cur.execute(query, (str(result["collectionid"]), userId, reqBody.script))
                    result = cur.fetchone()
                    query = "INSERT INTO tests (scriptid, userid, name, starttimestamp, endtimestamp, status) VALUES (%s, %s, %s, NOW(), NULL, 'Success') RETURNING *"
                    cur.execute(query, (str(result["scriptid"]), userId, reqBody.test))
                    result = cur.fetchone()
                    return result
                else:
                    #crear la colelction, obtener el id, crear el script con id collection obtener id, crear test con id script retornarlo
                    #tal vez esta ruta deberia de dar un error porque no estoy seguro como incluir la descripcion de la coleccion si no existe 
                    query = "INSERT INTO collections (name, lastmodified, description, userid) VALUES (%s, NOW(), 'A collection of scripts', %s) RETURNING *"
                    cur.execute(query, (reqBody.collection, userId))
                    result = cur.fetchone()
                    query = "INSERT INTO scripts (collectionid, userid, name) VALUES (%s, %s, %s) RETURNING *"
                    cur.execute(query, (str(result["collectionid"]), userId, reqBody.script))
                    result = cur.fetchone()
                    query = "INSERT INTO tests (scriptid, userid, name, starttimestamp, endtimestamp, status) VALUES (%s, %s, %s, NOW(), NULL, 'Success') RETURNING *"
                    cur.execute(query, (str(result["scriptid"]), userId, reqBody.test))
                    result = cur.fetchone()
                    return result
        
    # pass