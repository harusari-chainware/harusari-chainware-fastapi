from datetime import datetime
from app.db.mariadb import get_connection
from app.utils.date_utils import get_next_week_range
import pandas as pd

def create_weekly_prediction_input():
    next_week = get_next_week_range()
    conn = get_connection()
    cursor = conn.cursor()

    for date in next_week:
        query = """
        SELECT
            f.franchise_id,
            f.franchise_address,
            ef.date,
            ef.region,
            ef.avg_temp,
            ef.precipitation,
            ef.sentiment_index,
            COALESCE(SUM(s.total_amount), 0) AS past_sales_amount
        FROM franchise f
        LEFT JOIN external_factors ef
            ON ef.region = SUBSTRING_INDEX(f.franchise_address, ' ', 2) AND ef.date = %s
        LEFT JOIN sales s
            ON s.franchise_id = f.franchise_id AND s.sales_date BETWEEN DATE_SUB(%s, INTERVAL 28 DAY) AND %s
        GROUP BY f.franchise_id, ef.date;
        """

        cursor.execute(query, (date, date, date))
        rows = cursor.fetchall()
        print(f"📦 {date} 예측 입력 데이터 생성:")
        for row in rows:
            print(row)

    cursor.close()
    conn.close()


def prepare_training_data(table: str) -> pd.DataFrame:
    conn = get_connection()
    cursor = conn.cursor()

    if table == "store_order":
        query = """
        SELECT
            so.franchise_id,
            sod.product_id,
            so.delivery_due_date AS order_date,
            sod.quantity,
            ef.avg_temp,
            ef.precipitation,
            ef.sentiment_index
        FROM store_order so
        JOIN store_order_detail sod ON so.store_order_id = sod.store_order_id
        LEFT JOIN franchise f ON so.franchise_id = f.franchise_id
        LEFT JOIN external_factors ef ON ef.region = SUBSTRING_INDEX(f.franchise_address, ' ', 2)
                                     AND ef.date = so.delivery_due_date
        WHERE so.store_order_status = 'APPROVED'
          AND so.delivery_due_date < CURDATE()
        """
    elif table == "purchase_order":
        query = """
        SELECT
            pod.product_id,
            po.created_at AS order_date,
            pod.quantity,
            ef.avg_temp,
            ef.precipitation,
            ef.sentiment_index
        FROM purchase_order po
        JOIN purchase_order_detail pod ON po.purchase_order_id = pod.po_id  -- TODO: 추후 pod.purchase_order_id로 수정 필요
        LEFT JOIN external_factors ef ON ef.date = DATE(po.created_at)
                                     AND ef.region = '서울 강남구'  -- TODO: 본사 지역 설정 필요
        WHERE po.purchase_order_status IN ('APPROVED', 'WAREHOUSED')
          AND po.created_at < CURDATE()
        """
    else:
        raise ValueError("Only 'store_order' or 'purchase_order' is supported.")

    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    df = pd.DataFrame(rows)

    if df.empty:
        raise ValueError("No training data found.")

    df["order_date"] = pd.to_datetime(df["order_date"])
    df = df.sort_values("order_date")

    if table == "store_order":
        grouped = df.groupby([
            "franchise_id", "product_id", "order_date",
            "avg_temp", "precipitation", "sentiment_index"
        ]).agg({
            "quantity": "sum"
        }).reset_index()
    else:  # purchase_order
        grouped = df.groupby([
            "product_id", "order_date",
            "avg_temp", "precipitation", "sentiment_index"
        ]).agg({
            "quantity": "sum"
        }).reset_index()

    return grouped
