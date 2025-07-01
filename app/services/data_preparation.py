from datetime import datetime
from app.db.mariadb import get_connection
from app.utils.date_utils import get_next_week_range
import pandas as pd

def prepare_training_data(table: str) -> pd.DataFrame:
    conn = get_connection()
    cursor = conn.cursor()

    if table == "store_order":
        query = """
        SELECT
            so.franchise_id,
            sod.product_id,
            DATE(so.delivery_due_date) AS order_date,  -- ✅ 날짜 비교용으로 DATE 처리
            sod.quantity,
            ef.avg_temp,
            ef.precipitation,
            ef.sentiment_index
        FROM store_order so
        JOIN store_order_detail sod ON so.store_order_id = sod.store_order_id
        LEFT JOIN franchise f ON so.franchise_id = f.franchise_id
        LEFT JOIN external_factors ef 
            ON ef.region = REPLACE(SUBSTRING_INDEX(f.franchise_address_road, ' ', 2), '서울시', '서울')  -- ✅ 주소 변환
           AND ef.date = DATE(so.delivery_due_date)  -- ✅ 날짜 타입 맞춤
        WHERE so.store_order_status = 'APPROVED'
          AND so.delivery_due_date < CURDATE()
        """
    elif table == "purchase_order":
        query = """
        SELECT
            pod.product_id,
            DATE(po.created_at) AS order_date,
            pod.quantity,
            ef.avg_temp,
            ef.precipitation,
            ef.sentiment_index
        FROM purchase_order po
        JOIN purchase_order_detail pod ON po.purchase_order_id = pod.purchase_order_id
        LEFT JOIN external_factors ef 
            ON ef.date = DATE(po.created_at)
           AND ef.region = '서울 강남구'
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

    # ✅ 날짜 변환 및 정렬
    df["order_date"] = pd.to_datetime(df["order_date"]).dt.date
    df = df.sort_values("order_date")

    # ✅ 외부 요인 NULL 제거 (join 실패 row 제거)
    df = df.dropna(subset=["avg_temp", "precipitation", "sentiment_index"])

    # ✅ 디버깅 출력
    print("[DEBUG] ✅ 원시 로우 수:", len(df))
    print("[DEBUG] ✅ 일부 미리보기:")
    print(df.head())

    # ✅ 그룹핑
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

    print("[DEBUG] ✅ 그룹핑 결과 row 수:", len(grouped))
    print(grouped.head())

    return grouped
