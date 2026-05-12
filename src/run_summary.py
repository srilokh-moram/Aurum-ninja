import time
from datetime import datetime

last_run_date = None

while True:
    now = datetime.now()

    # Check if it's around 4 PM (safe window)
    if now.hour == 16 and now.minute < 2:
    #if now.minute % 2 == 0:
        today = now.date()

        # Ensure it runs only once per day
        if last_run_date != today:
            print("Sending daily summary...")

            import subprocess
            subprocess.run(["venv\\Scripts\\python.exe", "src\\daily_summary.py"])

            last_run_date = today
            time.sleep(120)  # prevent duplicate runs

    time.sleep(30)