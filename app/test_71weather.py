from datetime import datetime
from app.services.mid_weather_fetcher import get_weekly_rain_forecast

# 테스트할 날짜: 2025년 7월 1일
target_date = datetime.strptime("2025-07-06", "%Y-%m-%d")

# 서울 강남구 예시 → 기상청 중기 예보용 지역 코드 (육상예보 기준)
region_code = "11B10101"

# 테스트 실행
rain_result = get_weekly_rain_forecast(region_code, target_date)

# 출력 결과 확인
print("📊 2025-07-01 기준 강수확률 예보 결과:")
for key, value in rain_result.items():
    print(f"{key} → 오전 확률: {value['rnProbAm']}%, 오후 확률: {value['rnProbPm']}%, 상태: {value['weatherAm']} / {value['weatherPm']}")
