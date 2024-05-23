from hashlib import sha256
from urllib.request import Request
from jose import jwt
from fastapi import HTTPException, status
from internal.db import use_db
from os import getenv
from datetime import datetime, timezone

async def verify_personal_access_token(request: Request):
    token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
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
    with use_db() as (cur, _):
        hashed_token = sha256()
        hashed_token.update(token.encode())
        query = "SELECT * FROM PersonalAccessTokens WHERE accessTokenHash = %s"
        cur.execute(query, (hashed_token.hexdigest(),))
        token_data = cur.fetchone()

        if not token_data:
            raise token_exception

        return token_data["userid"]