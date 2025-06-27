from sqlalchemy import text
from app.db.mariadb import get_sqlalchemy_engine

def get_predictions(franchise_id: int, period: str):
    print(f"[🔍] 예측 결과 조회: franchise_id={franchise_id}, period={period}")
    engine = get_sqlalchemy_engine()
    query = text("""
        SELECT target_date, predicted_value, model_used, external_factors_used
        FROM prediction_result
        WHERE franchise_id = :franchise_id
          AND prediction_type = 'sales'
          AND period_type = :period_type
        ORDER BY target_date
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {
            "franchise_id": franchise_id,
            "period_type": period
        })
        rows = result.mappings().all()  
        print(f"[📦] 결과 수: {len(rows)}")
        return rows
