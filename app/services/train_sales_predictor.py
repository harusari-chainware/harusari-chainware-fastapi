import pandas as pd
import xgboost as xgb
import os
import joblib
from app.services.data_loader import load_sales_data

MODEL_DIR = "app/models/sales_models"
os.makedirs(MODEL_DIR, exist_ok=True)

def train_sales_model(franchise_id: int, period: str = "weekly"):
    df = load_sales_data(franchise_id)
    print("[🔍] 불러온 데이터:", df.head())

    if period == "weekly":
        df = df.resample("W-MON", on="sold_at").sum().reset_index()
    elif period == "monthly":
        df = df.resample("M", on="sold_at").sum().reset_index()
    else:
        raise ValueError("Invalid period. Use 'weekly' or 'monthly'.")

    df["time_index"] = range(len(df))

    X = df[["time_index"]]
    y = df["total_amount"]

    model = xgb.XGBRegressor(objective="reg:squarederror", n_estimators=100)
    model.fit(X, y)

    model_path = os.path.join(MODEL_DIR, f"{franchise_id}_{period}_xgb.pkl")
    joblib.dump(model, model_path)

    print(f"[✅] 모델 저장 완료: {model_path}")

if __name__ == "__main__":
    train_sales_model(franchise_id=1, period="monthly")
