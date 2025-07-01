# 📁 app/services/accuracy_calculator.py

from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
from datetime import datetime, timedelta
from app.db.mariadb import get_connection
from math import sqrt
import pymysql.cursors

def calculate_accuracy_metrics(y_true, y_pred):
    try:
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

def get_week_range(target_date: datetime):
    monday = target_date - timedelta(days=target_date.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday

def fetch_actual_value(prediction_type, franchise_id, start_date, end_date):
    if prediction_type == 'sales':
        sql = """
            SELECT SUM(total_amount) AS total FROM sales
            WHERE franchise_id = %s AND sold_at BETWEEN %s AND %s
        """
    elif prediction_type == 'order_quantity':
        sql = """
            SELECT SUM(sod.quantity) AS total FROM store_order so
            JOIN store_order_detail sod ON so.store_order_id = sod.store_order_id
            WHERE so.franchise_id = %s AND so.delivery_due_date BETWEEN %s AND %s
        """
    elif prediction_type == 'purchase_quantity':
        sql = """
            SELECT SUM(pod.quantity) AS total FROM purchase_order po
            JOIN purchase_order_detail pod ON po.purchase_order_id = pod.purchase_order_id
            WHERE po.created_at BETWEEN %s AND %s
        """
    else:
        return 0

    conn = get_connection()
    with conn.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
        if prediction_type == 'purchase_quantity':
            cursor.execute(sql, (start_date, end_date))
        else:
            cursor.execute(sql, (franchise_id, start_date, end_date))
        row = cursor.fetchone()
    return row["total"] or 0

def calculate_and_save_accuracy_for_prediction(prediction_result):
    prediction_result_id = prediction_result['prediction_result_id']
    prediction_type = prediction_result['prediction_type']
    franchise_id = prediction_result['franchise_id']
    target_date = prediction_result['target_date']
    predicted_total = prediction_result['predicted_value']

    conn = get_connection()
    with conn.cursor(cursor=pymysql.cursors.DictCursor) as cursor:
        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM prediction_accuracy WHERE prediction_result_id = %s",
            (prediction_result_id,)
        )
        if cursor.fetchone()["cnt"] > 0:
            print(f"[SKIP] Already calculated: prediction_result_id={prediction_result_id}")
            return

    monday, sunday = get_week_range(target_date)
    actual_values = [
        fetch_actual_value(prediction_type, franchise_id, monday + timedelta(days=i), monday + timedelta(days=i))
        for i in range(7)
    ]
    actual_total = sum(actual_values)
    mae, rmse, mape = calculate_accuracy_metrics([actual_total], [predicted_total])

    print("========================")
    print(f"📊 prediction_result_id: {prediction_result_id}")
    print(f"📌 prediction_type: {prediction_type}")
    print(f"🏪 franchise_id: {franchise_id}")
    print(f"📆 target_date: {target_date}")
    print(f"✅ predicted_total: {predicted_total}")
    print(f"✅ actual_total: {actual_total}")
    print(f"📈 MAE: {mae}")
    print(f"📈 RMSE: {rmse}")
    print(f"📈 MAPE: {mape}")
    print("========================")

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
