from datetime import date, datetime, timedelta, time as dtime

def get_week_range(dt):
    monday = dt - timedelta(days=dt.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday
