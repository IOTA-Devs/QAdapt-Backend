import threading
import time
import schedule

from .clearDeactivatedAccounts import clear_deactivated_accounts
from .clearUserSessions import clear_user_sessions

class ScheduledJob():
    def __init__(self, job, run_at_startup=False):
        self.job = job
        self.run_at_startup = run_at_startup

schedule.every().day.at("00:00").do(clear_deactivated_accounts)
schedule.every().saturday.at("00:00").do(clear_user_sessions)

# Add all jobs to a list as to run them all in a single thread
schedules = [
    ScheduledJob(clear_user_sessions, run_at_startup=True),
    ScheduledJob(clear_deactivated_accounts, run_at_startup=False)
]

def job():
    for scheduledJob in schedules:
        if scheduledJob.run_at_startup:
            scheduledJob.job()

    while True:
        schedule.run_pending()
        time.sleep(1)

def start_jobs():
    threading.Thread(target=job).start()