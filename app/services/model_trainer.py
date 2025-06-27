import pandas as pd
import xgboost as xgb
import os
import joblib
from app.services.training_data_generator import generate_training_data

MODEL_PATH = "app/models/xgb_sales_predictor.pkl"
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

def train_and_save_model():
    df = generate_training_data()

    # 데이터 전처리
    df = df.dropna()
    X = df[["avg_temp", "precipitation", "sentiment_index"]]
    y = df["total_sales"]

    model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, max_depth=4)
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)
    print(f"✅ 모델 학습 및 저장 완료 → {MODEL_PATH}")
