from datetime import datetime
from app.models.prediction import PredictionInput
from app.utils.date_utils import get_next_week_range
from app.services.data_preparation import prepare_training_data
from app.services.xgboost_predictor import train_and_predict
from app.services.save_prediction_result import save_prediction_result
import pandas as pd

# 제품별 가맹점 주문량 예측 (product_id 기준)
def predict_store_order_quantity():
    dates = get_next_week_range()
    start_date = dates[0]
    end_date = dates[-1]
    target_date = end_date

    # 학습용 데이터 준비
    training_df = prepare_training_data(table="store_order")

    print("[DEBUG] 🔎 주문 데이터:")

    if not training_df.empty:
        # ✅ order_date를 datetime -> date로 변환
        training_df["order_date"] = pd.to_datetime(training_df["order_date"]).dt.date

        # 디버깅 출력
        print("[DEBUG] 🔍 order_date dtype:", training_df["order_date"].dtype)
        print(training_df[["franchise_id", "product_id", "order_date"]].drop_duplicates())
    else:
        print("❗ training_df가 비어 있습니다")

    # 예측 실행
    predictions = train_and_predict(training_df, target_col="quantity")

    # 예측 결과 저장
    for row in predictions:
        external_factors_used = all(
            k in row and row[k] is not None
            for k in ["avg_temp", "precipitation", "sentiment_index"]
        )

        prediction_input = PredictionInput(
            franchise_id=row["franchise_id"],
            prediction_type="order_quantity",
            period_type="WEEKLY",
            target_date=target_date,
            predicted_value=row["prediction"],
            model_used="XGBOOST",
            external_factors_used=external_factors_used,
            explanation=None,
            start_date=start_date,
            end_date=end_date
        )

        save_prediction_result(prediction_input)
