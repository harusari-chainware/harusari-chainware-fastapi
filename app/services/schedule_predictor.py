from app.db.mariadb import get_connection
from app.services.predict_sales_by_factors import predict_by_factors
from app.models.prediction import SalesPredictionRequest
from app.utils.date_utils import get_next_week_range

def predict_sales_for_next_week_all_franchises() -> int:
    conn = get_connection()
    cursor = conn.cursor()  # 이미 DictCursor 이므로 그대로 사용

    # 📦 프랜차이즈 목록 조회
    cursor.execute("SELECT franchise_id, franchise_address FROM franchise")
    franchises = cursor.fetchall()

    # 디버그 출력
    print("📦 Raw Rows:", franchises)
    print("📦 Parsed franchises:", franchises)

    count = 0
    next_week_dates = get_next_week_range()
    print("[🧪] get_next_week_range 결과:", next_week_dates)

    for franchise in franchises:
        franchise_id = franchise["franchise_id"]
        address = franchise["franchise_address"]

        if not address:
            print(f"❌ 주소 없음 → franchise_id: {franchise_id}")
            continue

        region = " ".join(address.split()[:2])
        print(f"🗺️ franchise_id: {franchise_id}, region 추출 결과: {region}")

        for target_date in next_week_dates:
            cursor.execute("""
                SELECT avg_temp, precipitation, sentiment_index
                FROM external_factors
                WHERE region = %s AND date = %s
            """, (region, target_date))

            factor = cursor.fetchone()
            if not factor:
                print(f"❌ 외부요인 없음 → region: {region}, date: {target_date}")
                continue

            if None in factor.values():
                print(f"⚠️ 외부요인 일부 없음 → region: {region}, date: {target_date}, factor: {factor}")
                continue

            request = SalesPredictionRequest(
                franchise_id=franchise_id,
                avg_temp=float(factor["avg_temp"]),
                precipitation=float(factor["precipitation"]),
                sentiment_index=float(factor["sentiment_index"]),
                target_date=target_date
            )

            predict_by_factors(request)
            count += 1

    cursor.close()
    conn.close()
    return count
