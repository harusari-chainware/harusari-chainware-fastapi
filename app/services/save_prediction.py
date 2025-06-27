from datetime import datetime
from sqlalchemy import text
from app.db.mariadb import get_sqlalchemy_engine
from app.models.prediction import PredictionInput

def save_predictions_to_db(franchise_id: int, period: str, predictions: list, model_used: str, external_factors_used: bool, target_dates: list):
    engine = get_sqlalchemy_engine()
    print("[📅] 저장할 날짜 리스트:", target_dates)

    query = text("""
        INSERT INTO prediction_result (
            franchise_id,
            prediction_type,
            period_type,
            target_date,
            predicted_value,
            created_at,
            model_used,
            external_factors_used
        ) VALUES (
            :franchise_id,
            'sales',
            :period_type,
            :target_date,
            :predicted_value,
            :created_at,
            :model_used,
            :external_factors_used
        )
    """)

    with engine.connect() as conn:
        for i in range(len(predictions)):
            conn.execute(query, {
                "franchise_id": franchise_id,
                "period_type": period,
                "target_date": str(target_dates[i]),
                "predicted_value": round(predictions[i]),
                "created_at": datetime.now(),
                "model_used": model_used,
                "external_factors_used": external_factors_used
            })
        conn.commit()

def save_prediction_result(input: PredictionInput) -> int:
    engine = get_sqlalchemy_engine()

    query = text("""
        INSERT INTO prediction_result (
            franchise_id,
            prediction_type,
            period_type,
            target_date,
            predicted_value,
            start_date,
            end_date,
            created_at,
            model_used,
            external_factors_used,
            explanation
        ) VALUES (
            :franchise_id,
            :prediction_type,
            :period_type,
            :target_date,
            :predicted_value,
            :start_date,
            :end_date,
            :created_at,
            :model_used,
            :external_factors_used,
            :explanation
        )
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {
            "franchise_id": input.franchise_id,
            "prediction_type": input.prediction_type,
            "period_type": input.period_type,
            "target_date": input.target_date,
            "predicted_value": input.predicted_value,
            "start_date": input.start_date,
            "end_date": input.end_date,
            "created_at": datetime.now(),
            "model_used": input.model_used,
            "external_factors_used": input.external_factors_used,
            "explanation": input.explanation
        })
        conn.commit()
        return result.lastrowid