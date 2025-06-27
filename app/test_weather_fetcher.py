from app.services.mid_weather_fetcher import get_weather_data
from datetime import datetime

# 오늘 날짜
date_str = datetime.today().strftime('%Y%m%d')

# 서울 강남구 격자 좌표 예시
nx, ny = 61, 126

avg_temp, total_rain = get_weather_data(date_str, nx, ny)
print(f"날짜: {date_str}")
print(f"평균 기온: {avg_temp}°C")
print(f"총 강수량: {total_rain}mm")
