# app/services/xgboost_predictor.py
import xgboost as xgb
import pandas as pd

def train_and_predict(df: pd.DataFrame, target_col: str):
    print("[DEBUG] 🔍 train_and_predict 진입")
    print("[DEBUG] 👉 입력 데이터 row 수:", len(df))
    print(df.head())

    if df.empty:
        print("❗ [train_and_predict] 입력 데이터가 비어 있습니다. 예측을 건너뜁니다.")
        return []

    df = df.copy()
    df["time_index"] = range(len(df))

    for col in ["avg_temp", "precipitation", "sentiment_index"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    feature_cols = ["time_index"] + [col for col in ["avg_temp", "precipitation", "sentiment_index"] if col in df.columns]

    print("[DEBUG] 👉 feature_cols:", feature_cols)

    X = df[feature_cols]
    y = df[target_col]

    print("[DEBUG] 👉 학습용 X.shape:", X.shape)
    print("[DEBUG] 👉 타겟 y:", y.tolist())

    if X.empty or y.empty:
        print("⚠️ 학습 또는 예측 대상 데이터가 비어 있음")
        return []

    model = xgb.XGBRegressor(objective="reg:squarederror", n_estimators=100)
    model.fit(X, y)

    last_row = df.iloc[-1]
    input_row = [[
        len(df)
    ] + [last_row.get(col, 0.0) for col in feature_cols if col != "time_index"]]

    print("[DEBUG] 👉 예측 입력 input_row:", input_row)

    prediction = model.predict(input_row)[0]

    return [{
        "franchise_id": df["franchise_id"].iloc[0] if "franchise_id" in df.columns else None,
        "product_id": df["product_id"].iloc[0] if "product_id" in df.columns else None,
        "prediction": float(prediction),
        "avg_temp": last_row.get("avg_temp"),
        "precipitation": last_row.get("precipitation"),
        "sentiment_index": last_row.get("sentiment_index")
    }]
