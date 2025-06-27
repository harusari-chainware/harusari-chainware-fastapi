from sqlalchemy import create_engine
from app.db.mariadb import get_sqlalchemy_engine
import pandas as pd

def load_sales_data(franchise_id: int) -> pd.DataFrame:
    engine = get_sqlalchemy_engine()

    # ✅ f-string 방식으로 쿼리 문자열 수정
    query = f"""
    SELECT sold_at, total_amount
    FROM sales
    WHERE franchise_id = {franchise_id}
    ORDER BY sold_at
    """

    df = pd.read_sql(query, engine)

    print(f"[🔍] 불러온 행 수: {len(df)}")
    print(df.head())

    if df.empty:
        raise ValueError(f"[❌] franchise_id={franchise_id} 에 해당하는 유효한 데이터가 없습니다.")

    df['sold_at'] = pd.to_datetime(df['sold_at'])
    df['day_of_week'] = df['sold_at'].dt.dayofweek
    df['day'] = df['sold_at'].dt.day
    df['month'] = df['sold_at'].dt.month
    return df
