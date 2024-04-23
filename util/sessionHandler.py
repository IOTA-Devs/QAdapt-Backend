from datetime import timedelta, datetime, timezone
from config.db import get_conn, release_conn
from util.jwt import generate_access_token, generate_refresh_token
from uuid import uuid4
from hashlib import sha256
from psycopg2.extras import RealDictCursor

async def create_session(user_id: int):
    db_conn = get_conn()
    db = db_conn.cursor(cursor_factory=RealDictCursor)

    try:
        db.execute('SELECT * FROM Users WHERE userId = %s', (user_id,))
        user = db.fetchone()
    except Exception as e:
        print("Error fetching user while creating session: ", e)
        return False

    session_id = str(uuid4())
    access_token_expiry = timedelta(hours=1)
    access_token, _ = generate_access_token({ "userId": user_id, "sessionId": session_id, "username": user["username"]}, access_token_expiry)
    refresh_token, refresh_token_expires_at = generate_refresh_token({ "userId": user_id, "sessionId": session_id, "username": user["username"]})

    refresh_token_hash = sha256()
    refresh_token_hash.update(refresh_token.encode())

    try:
        db.execute('INSERT INTO UserSessions (sessionId, userId, expiresAt, refreshTokenHash, lastAccessed) VALUES (%s, %s, %s, %s, %s)', (session_id, user_id, refresh_token_expires_at, refresh_token_hash.hexdigest(), datetime.now(timezone.utc)))
        db_conn.commit()
    except Exception as e:
        print("Error creating session: ", e)
        return False
    
    release_conn(db_conn)
    return { "access_token": access_token, "refresh_token": refresh_token, "expires_in": access_token_expiry, "session_id": session_id }

async def get_session(session_id: str):
    db_conn = get_conn()
    db = db_conn.cursor(cursor_factory=RealDictCursor)

    try:
        db.execute('SELECT * FROM UserSessions WHERE sessionId = %s', (session_id,))
        session = db.fetchone()
    except Exception as e:
        print("Error fetching session: ", e)
        return False

    release_conn(db_conn)
    return session

async def revalidate_session(old_refresh_token: str, session_id: str):
    db_conn = get_conn()
    db = db_conn.cursor(cursor_factory=RealDictCursor)

    try:
        db.execute('SELECT * FROM UserSessions WHERE sessionId = %s', (session_id,))
        session = db.fetchone()
    except Exception as e:
        print("Error fetching session: ", e)
        return { "tokens": None, "error": "Error fetching session."}
    
    if not session:
        return { "tokens": None, "error": "Session has expired or is invalid."}
    
    old_refresh_token_hash = sha256()
    old_refresh_token_hash.update(old_refresh_token.encode())
    if old_refresh_token_hash.hexdigest() != session["refreshTokenHash"]:
        # Clear all user sessions

        return { "tokens": None, "error": "Invalid refresh token." }
    
    access_token_expiry = timedelta(hours=1)
    new_refresh_token, refresh_token_expires_at = generate_refresh_token({ "userId": session["userid"], "sessionId": session_id, "username": session["username"]}, access_token_expiry)
    new_access_token, _ = generate_access_token({ "userId": session["userId"], "sessionId": session_id, "username": session["username"]})

    new_refresh_token_hash = sha256()
    new_refresh_token_hash.update(new_refresh_token.encode())

    try:
        db.execute('UPDATE UserSessions SET refreshTokenHash = %s, expiresAt = %s WHERE sessionId = %s', (new_refresh_token_hash.hexdigest(), refresh_token_expires_at, session_id))
        db_conn.commit()
    except Exception as e:
        print("Error updating session: ", e)
        return { "tokens": None, "error": "Error while updating session" }
    
    release_conn(db_conn)
    return { "tokens": { "access_token": new_access_token, "refresh_token": new_refresh_token, "expires_in": access_token_expiry }, "error": None }

async def delete_session(session_id: str):
    db_conn = get_conn()
    db = db_conn.cursor(cursor_factory=RealDictCursor)

    try: 
        db.execute('DELETE FROM UserSessions WHERE sessionId = %s', (session_id,))
        return True
    except Exception as e:
        print("Error deleting session", e)
        return False