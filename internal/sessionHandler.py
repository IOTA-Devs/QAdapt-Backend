from datetime import timedelta, datetime, timezone
from uuid import uuid4
from hashlib import sha256

from .db import get_db_cursor
from .jwt import generate_access_token, generate_refresh_token

async def create_session(user_id: int):
    with get_db_cursor() as cur:
        # Create session id, access and refresh tokens
        session_id = str(uuid4())
        access_token_expiry = timedelta(hours=1)
        access_token, _ = generate_access_token({ "userId": user_id, "sessionId": session_id }, access_token_expiry)
        refresh_token, refresh_token_expires_at = generate_refresh_token()

        # Hash the current refresh token before storing it
        refresh_token_hash = sha256()
        refresh_token_hash.update(refresh_token.encode())

        # Inser the session in the database
        cur.execute('INSERT INTO UserSessions (sessionId, userId, expiresAt, refreshTokenHash, lastAccessed) VALUES (%s, %s, %s, %s, %s)', (session_id, user_id, refresh_token_expires_at, refresh_token_hash.hexdigest(), datetime.now(timezone.utc)))

        return { "access_token": access_token, "refresh_token": refresh_token, "expires_in": access_token_expiry.seconds, "session_id": session_id }

async def get_session(session_id: str):
    with get_db_cursor() as cur:
        cur.execute('SELECT * FROM UserSessions WHERE sessionId = %s', (session_id,))
        session = cur.fetchone()
    
    return session

async def revalidate_session(old_refresh_token: str, session_id: str):
    with get_db_cursor() as cur:
        # First validate that the session exists
        cur.execute('SELECT us.*, u.username FROM UserSessions us INNER JOIN Users u ON u.userId = us.userid WHERE sessionId = %s', (session_id,))
        session = cur.fetchone()
        
        if not session:
            return { "tokens": None, "error": "Session has expired or is invalid."}
        
        # Validate the provided refresh token with the one stored on the users session data
        old_refresh_token_hash = sha256()
        old_refresh_token_hash.update(old_refresh_token.encode())
        if old_refresh_token_hash.hexdigest() != session["refreshtokenhash"]:
            # Clear all user sessions
            clear_all_user_sessions(session["userid"])
            
            return { "tokens": None, "error": "Invalid refresh token." }
        
        # If the token is valid check if it is expired
        if session["expiresat"] < datetime.now(timezone.utc):
            return { "tokens": None, "error" : "Session has expired" }
        
        # Create new access and refresh tokens
        # Users sessions last up to 7 days before they have to log in again.
        # If the user enters the app and refreshes their session, the session expiration is displaced another 7 days from the moment it was refreshed,
        # effectively removing the need to log in unless they stop using the app for 7 days straight. 
        access_token_expiry = timedelta(hours=1)
        new_refresh_token, refresh_token_expires_at = generate_refresh_token()
        new_access_token, _ = generate_access_token({ "userId": session["userid"], "sessionId": session_id }, access_token_expiry)

        new_refresh_token_hash = sha256()
        new_refresh_token_hash.update(new_refresh_token.encode())

        # Update the users current session
        cur.execute('UPDATE UserSessions SET refreshTokenHash = %s, expiresAt = %s WHERE sessionId = %s', (new_refresh_token_hash.hexdigest(), refresh_token_expires_at, session_id))
        
        return { "tokens": { "access_token": new_access_token, "refresh_token": new_refresh_token, "expires_in": access_token_expiry.seconds }, "error": None }

async def delete_session(session_id: str):
    with get_db_cursor() as cur:
        cur.execute('DELETE FROM UserSessions WHERE sessionId = %s', (session_id,))
        return True

def clear_all_user_sessions(user_id: int):
    with get_db_cursor() as cur:
        cur.execute('DELETE FROM UserSessions WHERE userId = %s', (user_id,))