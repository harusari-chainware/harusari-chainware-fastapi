from datetime import datetime
from app.models.prediction import PredictionInput
from app.utils.date_utils import get_next_week_range
from app.services.mid_weather_fetcher import get_weekly_weather_forecast
from app.services.region_resolver import resolve_midterm_region_code
from app.services.save_prediction_result import save_prediction_result
from app.services.franchise_service import get_all_franchise_addresses

def generate_weekly_predictions():
    dates = get_next_week_range()           
    start_date = dates[0]                   
    end_date = dates[-1]                    
    target_date = end_date

    franchises = get_all_franchise_addresses()
    for row in franchises:
        franchise_id = row["franchise_id"]
        address = row["franchise_address_road"]

        region_code, region_name = resolve_midterm_region_code(address)
        forecast = get_weekly_weather_forecast(region_code, start_date.isoformat())

        predicted_value = 1000000
        explanation = None

        prediction_input = PredictionInput(
            franchise_id=franchise_id,
            prediction_type="sales",
            period_type="WEEKLY",
            target_date=target_date,
            predicted_value=predicted_value,
            model_used="XGBOOST",
            external_factors_used=bool(forecast),
            explanation=explanation,
            start_date=start_date,
            end_date=end_date,
        )

        print(f"📌 예측 저장 테스트: {prediction_input.dict()}")
        save_prediction_result(prediction_input)
