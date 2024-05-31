from os import getenv
from fastapi import APIRouter, Depends
from fastapi import HTTPException, status, UploadFile, Form, File
from pydantic import BaseModel
from azure.storage.blob import ContentSettings
from datetime import datetime, timezone

from typing import Annotated
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

# borrar este: https://qadapt.blob.core.windows.net/qadapt-container/20_1183_image.png?m=1717081950.944575
@router.post("/start_report")
async def start_report(
    token: Annotated[TokenData, Depends(verify_personal_access_token)], 
    reportId: Annotated[str, Form()],
    img: Annotated[UploadFile, File()]
):
    print("se hizo start_report o nah?")
    with use_db() as (cur, _):
        if img.size > 8 * 1000000:
            raise HTTPException(status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=Error("Image is too large", ErrorCodes.INVALID_REQUEST).to_json())

        container_name = getenv("STORAGE_CONTAINER_NAME")
        account_name = getenv("STORAGE_ACCOUNT_NAME")

        blob_client = blob_service_client.get_blob_client(container=container_name, blob=f"{token.user_id}_{reportId}_image.png")
        blob_client.upload_blob(img.file.read(), overwrite=True, content_settings=ContentSettings(content_type='image/jpeg'))
        
        url = f"https://{account_name}.blob.core.windows.net/{container_name}/{token.user_id}_{reportId}_image.png?m={datetime.now(tz=timezone.utc).timestamp()}"
        query =  "UPDATE selfhealingreports SET status='Failed', healingdescription='original locator failed, starting self-healing', screenshoturl=%s WHERE reportid=%s RETURNING *"
        cur.execute(query, (url, reportId))
        response = cur.fetchone()
        return response

@router.delete("/deleteReports")
async def delete_reports(
        token: Annotated[TokenData, Depends(verify_personal_access_token)],
        testid: int
):
    deletedReports = []
    # return testid
    with use_db() as (cur, _):

        container_name = getenv("STORAGE_CONTAINER_NAME")

        query = "SELECT * FROM selfhealingreports WHERE testid=%s;"
        cur.execute(query, (testid,))
        reports = cur.fetchall()
        for report in reports:
            print(report["reportid"])
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=f"{token.user_id}_{report["reportid"]}_image.png")
            if blob_client.exists():
                blob_client.delete_blob(delete_snapshots="include")

            query = "DELETE FROM selfhealingreports WHERE reportid=%s RETURNING *"
            cur.execute(query, (report["reportid"],))
            deletedReport = cur.fetchone()
            deletedReports.append(deletedReport)

        return deletedReports

class createReport(BaseModel):
    selenium_selector: str
    testId: str
@router.post("/create_report_item", response_model=None)
async def create_report_item(
    token: Annotated[TokenData, Depends(verify_personal_access_token)],
    reqBody: createReport
):
    with use_db() as (cur, _):
        query = "INSERT INTO selfhealingreports (testid, seleniumselectorname, healingdescription, status, screenshoturl) VALUES (%s, %s, 'self-healing has not started', 'Pending', %s) RETURNING *"
        img_path = ""
        cur.execute(query, (reqBody.testId, reqBody.selenium_selector, img_path))
        result = cur.fetchone()

        return result["reportid"]

#cambiar todo el maldito request a usar form-data
@router.post("/end_report")
async def end_report(
    token: Annotated[TokenData, Depends(verify_personal_access_token)],
    status: Annotated[str, Form()],
    healingDescription: Annotated[str, Form()],
    reportId: Annotated[str, Form()],
    img: Annotated[UploadFile, File()]
):
    with use_db() as (cur, _):
        #checar si screenshoturl tiene algo, si smn borrar el blob y hacerle update en bd, si no crear el blob y update en bd
        container_name = getenv("STORAGE_CONTAINER_NAME")
        account_name = getenv("STORAGE_ACCOUNT_NAME")
        if img.size > 8 * 1000000:
            raise HTTPException(status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=Error("Image is too large", ErrorCodes.INVALID_REQUEST).to_json())

        #como tengo overwrite=True no se deberian de crear nuevos blobs por la forma que son su nombre, si se han estado creando nuevos cambiarlo
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=f"{token.user_id}_{reportId}_image.png")
        blob_client.upload_blob(img.file.read(), overwrite=True, content_settings=ContentSettings(content_type='image/jpeg'))

        url = f"https://{account_name}.blob.core.windows.net/{container_name}/{token.user_id}_{reportId}_image.png?m={datetime.now(tz=timezone.utc).timestamp()}"
        query = "UPDATE selfhealingreports SET status=%s, healingDescription=%s, screenshoturl=%s WHERE reportid=%s RETURNING *"
        cur.execute(query, (status, healingDescription, url, reportId))
        response = cur.fetchone()
        return response

class setupBody(BaseModel):
    test: str
    script: str
    collection: str
@router.post('/selfHealingSetup')
async def setup(token: Annotated[TokenData, Depends(verify_personal_access_token)], reqBody: setupBody):
    print("comienzo de setup")
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
                print("final de setup")
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
                    print("final de setup")
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
                    print("final de setup")
                    return result
        