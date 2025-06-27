from app.models.prediction import SalesPredictionRequest
from app.services.save_prediction_result import save_prediction_result
import joblib
import pandas as pd

def predict_by_factors(request: SalesPredictionRequest) -> float:
    model_path = "app/models/xgb_sales_predictor.pkl"
    model = joblib.load(model_path)

    # ✅ 예측을 위한 입력 데이터 구성
    X = pd.DataFrame([{
        "avg_temp": request.avg_temp,
        "precipitation": request.precipitation,
        "sentiment_index": request.sentiment_index
    }])

    # ✅ 예측 수행
    predicted_value = float(model.predict(X)[0])

    # ✅ 예측 결과 저장 (설명 자동 생성 포함)
    save_prediction_result(
        franchise_id=request.franchise_id,
        date=request.target_date,
        predicted_value=predicted_value,
        prediction_type="sales",
        period_type="weekly",
        model_used="XGBOOST"
    )

    return predicted_value
