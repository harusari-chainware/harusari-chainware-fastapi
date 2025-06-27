from pydantic import BaseModel
from datetime import date
from typing import Optional

class PredictionInput(BaseModel):
    franchise_id: Optional[int]
    prediction_type: str
    period_type: str
    target_date: date
    predicted_value: float
    start_date: date
    end_date: date
    model_used: str = "PROPHET"
    external_factors_used: bool = False
    explanation: Optional[str] = None

class SalesPredictionRequest(BaseModel):
    franchise_id: int
    avg_temp: float
    precipitation: float
    sentiment_index: float
    target_date: date
