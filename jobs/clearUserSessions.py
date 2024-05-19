import threading
import schedule
import time

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

schedule.every().saturday.at("00:00").do(clear_user_sessions)

def job():
    clear_user_sessions()
    while True:
        schedule.run_pending()
        time.sleep(1)

def start_job():
    threading.Thread(target=job).start()