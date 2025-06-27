from app.models.prediction import PredictionInput
from app.db.mariadb import get_connection
from datetime import datetime
from app.services.prediction_repository import save_prediction_result