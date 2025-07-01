# 📁 app/services/accuracy_calculator.py

from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
from datetime import datetime, timedelta
from app.db.mariadb import get_connection
from math import sqrt
import pymysql.cursors

# 예측값과 실제값 리스트로 정확도 계산
def calculate_accuracy_metrics(y_true, y_pred):
    try:
        # 분모가 0인 경우 MAPE 계산 제외
        if any(y == 0 for y in y_true):
            mape = None
        else:
            mape = float(round(mean_absolute_percentage_error(y_true, y_pred) * 100, 2))

        mae = float(round(mean_absolute_error(y_true, y_pred), 2))
        rmse = float(round(sqrt(mean_squared_error(y_true, y_pred)), 2))
    except Exception as e:
        print("[ERROR] Accuracy calculation failed:", e)
        mae, rmse, mape = 0.0, 0.0, None
    return mae, rmse, mape

# 주차 기준 날짜 범위 계산 (월~일)
def get_week_range(target_date: datetime):
    monday = target_date - timedelta(days=target_date.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday

# 실제값을 예측 항목에 따라 조회
def fetch_actual_value(prediction_type, franchise_id, start_date, end_date):
    if prediction_type == 'sales':
        sql = (
            "SELECT SUM(total_amount) AS total FROM sales "
            "WHERE franchise_id = %s AND sold_at BETWEEN %s AND %s"
        )
    elif prediction_type == 'order_quantity':
        sql = (
            "SELECT SUM(sod.quantity) AS total FROM store_order so "
            "JOIN store_order_detail sod ON so.store_order_id = sod.store_order_id "
            "WHERE so.franchise_id = %s AND so.delivery_due_date BETWEEN %s AND %s"
        )
    elif prediction_type == 'purchase_quantity':
        sql = (
            "SELECT SUM(pod.quantity) AS total FROM purchase_order po "
            "JOIN purchase_order_detail pod ON po.purchase_order_id = pod.purchase_order_id "
            "WHERE po.created_at BETWEEN %s AND %s"
        )
    else:
        return 0

    conn = get_connection()
    with conn.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
        if prediction_type == 'purchase_quantity':
            cursor.execute(sql, (start_date, end_date))
        else:
            cursor.execute(sql, (franchise_id, start_date, end_date))
        row = cursor.fetchone()
        print(f"[DEBUG] {prediction_type} actual row: {row} for date range {start_date} ~ {end_date}")
    return row["total"] or 0

# 예측 결과 기반 정확도 계산 및 저장 (총합 기준)
def calculate_and_save_accuracy_for_prediction(prediction_result):
    prediction_result_id = prediction_result['prediction_result_id']
    prediction_type = prediction_result['prediction_type']
    franchise_id = prediction_result['franchise_id']
    target_date = prediction_result['target_date']
    predicted_total = prediction_result['predicted_value']

    monday, sunday = get_week_range(target_date)
    actual_values = []
    for i in range(7):
        date = monday + timedelta(days=i)
        actual = fetch_actual_value(prediction_type, franchise_id, date, date)
        actual_values.append(actual)

    actual_total = sum(actual_values)

    mae, rmse, mape = calculate_accuracy_metrics([actual_total], [predicted_total])

    # ✅ 디버깅 로그 출력
    print("========================")
    print(f"📊 prediction_result_id: {prediction_result_id}")
    print(f"📌 prediction_type: {prediction_type}")
    print(f"🏪 franchise_id: {franchise_id}")
    print(f"📆 target_date: {target_date}")
    print(f"✅ predicted_total: {predicted_total}")
    print(f"✅ actual_total: {actual_total}")
    print(f"📈 MAE: {mae} ({type(mae)})")
    print(f"📈 RMSE: {rmse} ({type(rmse)})")
    print(f"📈 MAPE: {mape} ({type(mape)})")
    print("========================")

    conn = get_connection()
    with conn.cursor() as cursor:
        if franchise_id is not None:
            cursor.execute(
                """
                INSERT INTO prediction_accuracy (
                    franchise_id, prediction_result_id, actual_value, mape, mae, rmse, calculated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (franchise_id, prediction_result_id, actual_total, mape, mae, rmse, datetime.now())
            )
        else:
            cursor.execute(
                """
                INSERT INTO prediction_accuracy (
                    prediction_result_id, actual_value, mape, mae, rmse, calculated_at
                ) VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (prediction_result_id, actual_total, mape, mae, rmse, datetime.now())
            )
    conn.commit()

# 여러 예측 결과에 대해 정확도 일괄 계산
def calculate_accuracy_for_all_predictions():
    conn = get_connection()
    with conn.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
        cursor.execute("""
            SELECT prediction_result_id, franchise_id, prediction_type, target_date, predicted_value
            FROM prediction_result
            WHERE period_type = 'WEEKLY'
        """)
        rows = cursor.fetchall()

    for row in rows:
        calculate_and_save_accuracy_for_prediction(row)

if __name__ == "__main__":
    calculate_accuracy_for_all_predictions()
