from ..internal import get_conn, release_conn

def clear_user_sessions():
    db_conn = get_conn()
    db = db_conn.cursor()

    print("Clearing user sessions...")
    try:
        query = "DELETE FROM UserSessions WHERE expiresAt < NOW()"
        db.execute(query)
        db_conn.commit()
    except Exception as e:
        print("Error deleting sessions: ", e)
    finally:
        print("User Sessions Cleared Successfully")
        release_conn(db_conn)