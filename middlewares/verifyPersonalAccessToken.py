from hashlib import sha256
from urllib.request import Request
from jose import jwt
from fastapi import HTTPException
from internal.db import get_conn, release_conn
from os import getenv
from datetime import datetime, timezone
from classes import Error, ErrorCodes
from psycopg2.extras import RealDictCursor

async def verify_personal_access_token(request: Request):
    token_exception = HTTPException(
        status_code=401,
        detail="Unauthorized"
    )

    # Get the token from the header
    token = request.headers.get("Authorization")

    if not token:
        raise token_exception
    
    secret = getenv("PERSONAL_TOKEN_SECRET_KEY")
    # Verify token expiration
    jwt_payload = jwt.decode(token, key=secret, algorithms=["HS256"])

    if not jwt_payload or jwt_payload["exp"] < datetime.now(timezone.utc).timestamp():
        raise token_exception
    
    # Verify token in the database
    db_conn = get_conn()
    db = db_conn.cursor(cursor_factory=RealDictCursor)

    try:
        hashed_token = sha256()
        hashed_token.update(token.encode())
        query = "SELECT * FROM PersonalAccessTokens WHERE accessTokenHash = %s"
        db.execute(query, (hashed_token.hexdigest(),))
        token_data = db.fetchone()
    except Exception as e:
        print("Error validating token: ", e)
        raise HTTPException(status_code=500, detail=Error("Error validating token", ErrorCodes.INTERNAL_SERVER_ERROR).to_json())
    finally:
        release_conn(db_conn)

    return token_data["userid"]