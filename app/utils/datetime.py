from datetime import datetime, timedelta, timezone

def get_ist_time():
    return datetime.now(timezone(timedelta(hours=5, minutes=30)))