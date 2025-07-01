import os
from datetime import datetime, timedelta
from app.services.franchise_service import get_all_franchise_addresses
from app.services.mid_weather_fetcher import get_weekly_weather_forecast, get_weekly_rain_forecast
from app.services.region_resolver import resolve_midterm_region_code
from app.utils.date_utils import get_next_week_range
from app.db.mariadb import get_connection as get_db_connection
from app.services.sentiment_fetcher import get_sentiment_index
from app.services.holiday_fetcher import get_date_type  # ✅ 추가

print("🔥 [DEBUG] 실행 중인 external_factors_service.py 위치:", os.path.abspath(__file__))


def get_latest_sentiment_index(target_month: str):
    base = datetime.strptime(target_month, "%Y%m")
    for i in range(0, 3):
        ym = (base - timedelta(days=30 * i)).strftime("%Y%m")
        index = get_sentiment_index(ym)
        if index is not None:
            print(f"💡 사용된 소비자심리지수({ym}) → {index}")
            return index
    print("❗ 소비자심리지수 fallback 실패")
    return None


def save_external_factors_for_next_week():
    print("🚀 save_external_factors_for_next_week() 실행 시작")

    next_week_dates = get_next_week_range()
    conn = get_db_connection()
    cursor = conn.cursor()

    for franchise in get_all_franchise_addresses():
        try:
            address = franchise["franchise_address_road"]
            print(f"📥 원본 주소: {address}")
        except Exception as e:
            print(f"❌ address 추출 실패 → {e}")
            continue

        try:
            region_code, region_name = resolve_midterm_region_code(address)
        except Exception as e:
            print(f"❌ 지역 코드 해석 실패: {address} → {e}")
            continue

        if region_code == "UNKNOWN":
            print(f"⚠️ 지역 코드 매핑 실패: '{region_name}' → 예보 API 호출 스킵")
            continue

        weather_data = get_weekly_weather_forecast(region_code)
        rain_data = get_weekly_rain_forecast(region_code)


        for i, target_date in enumerate(next_week_dates):
            key = f"D{3 + i}"

            if weather_data is None or rain_data is None or key not in weather_data or key not in rain_data:
                print(f"❌ {region_name}의 {target_date} 예보 누락")
                continue

            try:
                ta_min = float(weather_data[key]["taMin"]) if weather_data[key]["taMin"] is not None else None
                ta_max = float(weather_data[key]["taMax"]) if weather_data[key]["taMax"] is not None else None
                rn_am = rain_data[key].get("rnProbAm")
                rn_pm = rain_data[key].get("rnProbPm")

                if None in [ta_min, ta_max, rn_am, rn_pm]:
                    raise ValueError("예보 값에 None 포함됨")

                avg_temp = (ta_min + ta_max) / 2
                precipitation = (float(rn_am) + float(rn_pm)) / 2
            except (TypeError, ValueError) as e:
                print(f"⚠️ {target_date} {region_name} 예보 변환 오류 → {e}")
                continue

            sentiment_month = target_date.strftime("%Y%m")
            sentiment = get_latest_sentiment_index(sentiment_month)
            date_type = get_date_type(target_date)

            print(f"💡 {target_date} {region_name} → {date_type}, 기온: {avg_temp}, 강수: {precipitation}, 심리지수: {sentiment}")

            try:
                cursor.execute("""
                    INSERT INTO external_factors (
                        date, region, date_type, avg_temp, precipitation, sentiment_index, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        avg_temp = VALUES(avg_temp),
                        precipitation = VALUES(precipitation),
                        sentiment_index = VALUES(sentiment_index),
                        date_type = VALUES(date_type)
                """, (
                    target_date,
                    region_name,
                    date_type,
                    avg_temp,
                    precipitation,
                    sentiment,
                    datetime.now()
                ))
                print(f"✅ {target_date} {region_name} 저장 완료")
            except Exception as e:
                print(f"❌ {target_date} DB 저장 실패 → {e}")
                continue

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ external_factors 테이블 저장 완료")
