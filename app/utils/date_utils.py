from datetime import datetime, timedelta

def get_next_week_range():
    today = datetime.today()
    # 중기예보의 D3~D10에 맞추기 위해 today + 3일부터 시작
    base = today + timedelta(days=3)
    return [base.date() + timedelta(days=i) for i in range(7)]
