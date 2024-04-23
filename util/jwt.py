from datetime import timedelta, datetime, timezone
from jose import jwt
from os import getenv

def generate_token(data: dict, secret_key: str, expiry_delta: timedelta | None = None):
    to_encode = data.copy()

    if expiry_delta:
        expire = datetime.now(timezone.utc) + expiry_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=1)

    to_encode.update({ "exp": expire })
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")

    return encoded_jwt, expire

def generate_access_token(data: dict, expiry_delta: timedelta | None = None):
    secret_key = getenv("ACCESS_TOKEN_SECRET_KEY")
    return generate_token(data, secret_key, expiry_delta)

def generate_refresh_token(data: dict, expiry_delta: timedelta | None = None):
    secret_key = getenv("REFRESH_TOKEN_SECRET_KEY")
    return generate_token(data, secret_key, expiry_delta)

def verify_token(token: str, token_type: str):
    if token_type == "access":
        secret_key = getenv("ACCESS_TOKEN_SECRET_KEY")
    elif token_type == "refresh":
        secret_key = getenv("REFRESH_TOKEN_SECRET_KEY")
    else:
        return {"valid": False, "error": "Invalid token type provided.", payload: None}
    
    payload = jwt.decode(token, secret_key, algorithms=["HS256"])
    if payload["exp"] < datetime.now(timezone.utc):
        return {"valid": False, "error": "Token has expired.", payload: None}
    if not payload:
        return {"valid": False, "error": "Invalid token provided.", payload: None}
    
    return {"valid": True, "error": None, "payload": payload}

def generate_new_access_token():
    pass