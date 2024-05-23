from ..internal import use_db

def clear_deactivated_accounts():
    with use_db as (cur, _):
        query = "DELETE FROM Users WHERE deletionTimestamp < NOW()"
        (cur, _).exeute(query)