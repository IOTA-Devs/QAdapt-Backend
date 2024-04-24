from datetime import timedelta, datetime, timezone
import os
from jose import jwt
from os import getenv
from uuid import uuid4

def generate_access_token(data: dict, expiry_delta: timedelta | None = None):
    to_encode = data.copy()
    secret_key = os.getenv("ACCESS_TOKEN_SECRET_KEY")

    if expiry_delta:
        expire = datetime.now(timezone.utc) + expiry_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=1)

    to_encode.update({ "exp": expire })
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")

    return encoded_jwt, expire

def generate_refresh_token(expiry_delta: timedelta | None = None):
    if expiry_delta:
        expire = datetime.now(timezone.utc) + expiry_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=30)

    return str(uuid4()), expire

def verify_access_token(token: str):
    secret_key = getenv("ACCESS_TOKEN_SECRET_KEY")
    
    payload = jwt.decode(token, secret_key, algorithms=["HS256"])
    if payload["exp"] < datetime.now(timezone.utc).timestamp():
        return {"valid": False, "error": "Token has expired.", payload: None}
    if not payload:
        return {"valid": False, "error": "Invalid token provided.", payload: None}
    
    return {"valid": True, "error": None, "payload": payload}

def generate_new_access_token():
    pass