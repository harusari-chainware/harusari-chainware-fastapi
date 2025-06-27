# app/utils/date_utils.py
from datetime import datetime, timedelta

def get_next_week_range():
    today = datetime.today()
    # 다음주 월요일 구하기
    next_monday = today + timedelta(days=(7 - today.weekday()))
    return [next_monday.date() + timedelta(days=i) for i in range(7)]
