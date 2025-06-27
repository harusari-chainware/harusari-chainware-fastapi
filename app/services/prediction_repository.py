from datetime import datetime
from app.models.prediction import PredictionInput
from app.db.mariadb import get_connection

# ✅ 가맹점 이름을 DB에서 조회하는 함수
def get_franchise_name(franchise_id: int) -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT franchise_name FROM franchise WHERE franchise_id = %s", (franchise_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else "알 수 없음"

def save_prediction_result(input: PredictionInput):
    conn = get_connection()
    cursor = conn.cursor()

    print(f"✅ INSERT 쿼리 실행: {input.franchise_id}, {input.start_date} ~ {input.end_date}")

    query = """
    INSERT INTO prediction_result (
        franchise_id, prediction_type, period_type,
        target_date, start_date, end_date,
        predicted_value, created_at,
        model_used, external_factors_used, explanation
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(query, (
        input.franchise_id,
        input.prediction_type,
        input.period_type,
        input.target_date,
        input.start_date,
        input.end_date,
        input.predicted_value,
        datetime.now(),
        input.model_used,
        input.external_factors_used,
        input.explanation  # 직접 None으로 전달해도 무방
    ))

    conn.commit()
    result_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return result_id
