from app.db.mariadb import get_connection
from datetime import datetime
from app.models.prediction import PredictionInput

def save_prediction_result(prediction_input: PredictionInput) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    # 가맹점 주소 조회
    cursor.execute("""
        SELECT franchise_address FROM franchise
        WHERE franchise_id = %s
    """, (prediction_input.franchise_id,))
    row = cursor.fetchone()
    address = row["franchise_address"] if row else ""
    region = " ".join(address.split()[:2]) if address else "알 수 없음"

    # 외부 요인 조회
    cursor.execute("""
        SELECT avg_temp, precipitation, sentiment_index
        FROM external_factors
        WHERE region = %s AND date = %s
    """, (region, prediction_input.target_date))
    external = cursor.fetchone()

    external_used = external is not None

    # INSERT할 값 정의 (start_date, end_date 포함!)
    values = (
        prediction_input.franchise_id,
        prediction_input.prediction_type,
        prediction_input.period_type,
        prediction_input.target_date,
        prediction_input.start_date,
        prediction_input.end_date,
        prediction_input.predicted_value,
        datetime.now(),
        prediction_input.model_used,
        prediction_input.external_factors_used,
        prediction_input.explanation
    )

    cursor.execute("""
        INSERT INTO prediction_result (
            franchise_id, prediction_type, period_type,
            target_date, start_date, end_date,
            predicted_value, created_at,
            model_used, external_factors_used, explanation
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, values)

    conn.commit()
    result_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return result_id
