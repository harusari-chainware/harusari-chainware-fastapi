from datetime import datetime
from app.models.prediction import PredictionInput
from app.utils.date_utils import get_next_week_range
from app.services.data_preparation import prepare_training_data
from app.services.xgboost_predictor import train_and_predict
from app.services.save_prediction_result import save_prediction_result

# 제품별 가맹점 주문량 예측 (product_id 기준)
def predict_store_order_quantity():
    dates = get_next_week_range()
    start_date = dates[0]
    end_date = dates[-1]
    target_date = end_date

    training_df = prepare_training_data(table="store_order")
    predictions = train_and_predict(training_df, target_col="quantity")

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
