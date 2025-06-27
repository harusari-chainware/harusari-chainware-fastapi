from datetime import datetime, timedelta
import pandas as pd
import joblib
import os
from app.services.save_prediction import save_predictions_to_db

def predict_sales(franchise_id: int, period: str = "weekly", steps: int = 4):
    model_path = f"app/models/sales_models/{franchise_id}_{period}_xgb.pkl"

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"[❌] 모델 파일이 없습니다: {model_path}")

    model = joblib.load(model_path)
    last_index = model.n_features_in_
    X_future = pd.DataFrame({"time_index": range(last_index, last_index + steps)})

    predictions = model.predict(X_future).tolist()

    # ✅ target_date 계산
    today = datetime.today()
    if period == "weekly":
        target_dates = [(today + timedelta(weeks=i)).date() for i in range(1, steps + 1)]
    elif period == "monthly":
        target_dates = [(today.replace(day=1) + pd.DateOffset(months=i)).date() for i in range(1, steps + 1)]
    else:
        raise ValueError("period는 'weekly' 또는 'monthly' 이어야 합니다.")

    # ✅ 저장
    save_predictions_to_db(
        franchise_id=franchise_id,
        period=period,
        predictions=predictions,
        model_used="XGBOOST",
        external_factors_used=False,
        target_dates=target_dates  # ← 추가
    )

    return predictions
