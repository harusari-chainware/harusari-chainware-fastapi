import os
import requests
import urllib.parse
from typing import Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
from app.services.franchise_service import get_all_franchise_addresses
from app.services.region_resolver import resolve_midterm_region_code
from app.utils.date_utils import get_next_week_range
from app.db.mariadb import get_connection as get_db_connection
from app.services.sentiment_fetcher import get_sentiment_index
from app.services.holiday_fetcher import get_date_type

load_dotenv()

def get_latest_tmFc():
    now = datetime.now()
    if now.hour < 6:
        base_date = (now - timedelta(days=1)).strftime("%Y%m%d")
        base_time = "1800"
    elif now.hour < 18:
        base_date = now.strftime("%Y%m%d")
        base_time = "0600"
    else:
        base_date = now.strftime("%Y%m%d")
        base_time = "1800"
    return base_date + base_time


def get_weekly_weather_forecast(region_code: str, target_date) -> Optional[dict]:
    service_key = urllib.parse.unquote(os.getenv("WEATHER_API_KEY"))
    url = "http://apis.data.go.kr/1360000/MidFcstInfoService/getMidTa"
    params = {
        "serviceKey": service_key,
        "dataType": "JSON",
        "numOfRows": "10",
        "pageNo": "1",
        "regId": region_code,
        "tmFc": get_latest_tmFc()
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        print("🧾 기온 응답:", response.json())
        if response.status_code != 200:
            return None
        items = response.json()["response"]["body"]["items"]["item"][0]
        return {
            f"D{d}": {
                "taMin": items.get(f"taMin{d}"),
                "taMax": items.get(f"taMax{d}")
            } for d in range(3, 8)
        }
    except Exception as e:
        print("기온 예보 오류:", e)
        return None


def get_weekly_rain_forecast(region_code: str, target_date) -> Optional[dict]:
    service_key = urllib.parse.unquote(os.getenv("WEATHER_API_KEY"))
    url = "http://apis.data.go.kr/1360000/MidFcstInfoService/getMidLandFcst"
    params = {
        "serviceKey": service_key,
        "dataType": "JSON",
        "numOfRows": "10",
        "pageNo": "1",
        "regId": region_code,
        "tmFc": get_latest_tmFc()
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        print("🌧 강수확률 응답:", response.json())
        if response.status_code != 200:
            return None
        items = response.json()["response"]["body"]["items"]["item"][0]
        return {
            f"D{d}": {
                "rnProbAm": items.get(f"rnSt{d}Am"),
                "rnProbPm": items.get(f"rnSt{d}Pm"),
                "weatherAm": items.get(f"wf{d}Am"),
                "weatherPm": items.get(f"wf{d}Pm"),
            } for d in range(3, 8)
        }
    except Exception as e:
        print("강수확률 예보 오류:", e)
        return None


def get_latest_sentiment_index(target_month: str):
    base = datetime.strptime(target_month, "%Y%m")
    for i in range(3):
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
        address = franchise["franchise_address"]
        print(f"📥 원본 주소: {address}")

        try:
            region_code, region_name = resolve_midterm_region_code(address)
        except Exception as e:
            print(f"❌ 지역 코드 해석 실패: {address} → {e}")
            continue

        if region_code == "UNKNOWN":
            print(f"⚠️ 지역 코드 매핑 실패: '{region_name}' → 예보 API 호출 스킵")
            continue

        weather_data = get_weekly_weather_forecast(region_code, next_week_dates[0])
        rain_data = get_weekly_rain_forecast(region_code, next_week_dates[0])

        for i, target_date in enumerate(next_week_dates):
            key = f"D{3 + i}"

            if weather_data is None or rain_data is None or key not in weather_data or key not in rain_data:
                print(f"❌ {region_name}의 {target_date} 예보 누락")
                continue

            try:
                ta_min = float(weather_data[key]["taMin"]) if weather_data[key]["taMin"] is not None else None
                ta_max = float(weather_data[key]["taMax"]) if weather_data[key]["taMax"] is not None else None
                rn_prob_am = rain_data[key]["rnProbAm"]
                rn_prob_pm = rain_data[key]["rnProbPm"]

                if None in [ta_min, ta_max, rn_prob_am, rn_prob_pm]:
                    raise ValueError("예보 값에 None 포함됨")

                avg_temp = (ta_min + ta_max) / 2
                precipitation = (float(rn_prob_am) + float(rn_prob_pm)) / 2  # ✅ 평균으로 계산
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
                        date, region, is_holiday, avg_temp, precipitation, sentiment_index, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        avg_temp = VALUES(avg_temp),
                        precipitation = VALUES(precipitation),
                        sentiment_index = VALUES(sentiment_index),
                        is_holiday = VALUES(is_holiday)
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
