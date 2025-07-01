# 📁 app/services/prediction_result_service.py

from db.mariadb import get_connection

def get_prediction_values(prediction_result_id: int) -> list[float]:
    """
    prediction_result_id에 해당하는 7일치 예측값을 반환
    """
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT predicted_value
            FROM prediction_result_detail
            WHERE prediction_result_id = %s
            ORDER BY target_date ASC
        """, (prediction_result_id,))
        rows = cursor.fetchall()
    
    return [row[0] for row in rows]
