from fastapi import APIRouter, Query
from pydantic import BaseModel
from datetime import date
from typing import List

from app.db.mariadb import get_connection
from app.models.prediction import PredictionInput, SalesPredictionRequest
from app.services.predictor import save_prediction_result
from app.services.predict_sales import predict_sales
from app.services.query_prediction import get_predictions
from app.services.predict_sales_by_factors import predict_by_factors
from app.services.schedule_predictor import predict_sales_for_next_week_all_franchises
from app.services.predict_order_quantity import predict_store_order_quantity
from app.services.predict_purchase_quantity import predict_purchase_order_quantity

router = APIRouter(prefix="/predict", tags=["Prediction"])

# ✅ 예측 저장
@router.post(
    "/",
    summary="예측 결과 저장",
    description="입력받은 예측 결과 데이터를 저장합니다."
)
def create_prediction(input: PredictionInput):
    result_id = save_prediction_result(input)
    return {"message": "Prediction saved", "prediction_result_id": result_id}


# ✅ 일반 예측 조회
@router.get(
    "/sales",
    summary="매출 예측 조회",
    description="특정 가맹점의 주간 또는 월간 매출을 예측합니다."
)
def get_sales_prediction(
    franchise_id: int = Query(..., description="가맹점 ID"),
    period: str = Query("weekly", description="예측 주기: weekly or monthly"),
    steps: int = Query(4, description="예측할 기간 수 (주 또는 월 기준)")
):
    predictions = predict_sales(franchise_id=franchise_id, period=period, steps=steps)
    return {"franchise_id": franchise_id, "period": period, "predictions": predictions}


# ✅ 저장된 예측 결과 조회
@router.get(
    "/predicted-results",
    summary="저장된 예측 결과 조회",
    description="DB에 저장된 예측 결과를 조회합니다."
)
def read_predictions(
    franchise_id: int = Query(..., description="가맹점 ID"),
    period: str = Query("weekly", description="예측 주기")
):
    print(f"[🔍] 예측 결과 조회: franchise_id={franchise_id}, period={period}")
    results = get_predictions(franchise_id, period)
    print(f"[📦] 결과 수: {len(results)}")
    return {"franchise_id": franchise_id, "period": period, "results": results}


# ✅ 외부 요인 기반 예측
@router.post(
    "/sales-by-factors",
    summary="외부 요인 기반 매출 예측",
    description="날씨, 휴일, 소비심리지수 등 외부 요인을 반영하여 매출을 예측합니다."
)
def predict_sales_by_factors(request: SalesPredictionRequest):
    predicted = predict_by_factors(request)
    return {
        "franchise_id": request.franchise_id,
        "target_date": request.target_date,
        "predicted_sales": predicted
    }


# ✅ 다음 주 예측 자동화
@router.post(
    "/schedule-sales-next-week",
    summary="다음 주 매출 예측 자동 실행",
    description="전체 가맹점에 대해 다음 주 매출 예측을 자동으로 수행하고 저장합니다."
)
def schedule_sales_prediction_for_all():
    result = predict_sales_for_next_week_all_franchises()
    return {"message": "Scheduled predictions completed", "count": result}


# ✅ 가맹점 주문량 예측 자동화
@router.post(
    "/schedule-order-prediction",
    summary="가맹점 주문량 예측 자동 실행",
    description="전체 가맹점에 대해 다음 주 주문 수량을 예측하고 저장합니다."
)
def schedule_order_quantity():
    count = predict_store_order_quantity()
    return {"message": "Order quantity prediction complete", "count": count}


# ✅ 본사 발주량 예측 자동화
@router.post(
    "/schedule-purchase-prediction",
    summary="본사 발주량 예측 자동 실행",
    description="전체 본사 발주 데이터를 기반으로 다음 주 발주 수량을 예측합니다."
)
def schedule_purchase_quantity():
    count = predict_purchase_order_quantity()
    return {"message": "Purchase quantity prediction complete", "count": count}


# ✅ 예측 결과 상세 조회
@router.get(
    "/results",
    summary="예측 결과 상세 조회",
    description="가맹점, 예측 유형, 기간을 기반으로 예측 결과를 조회합니다."
)
def get_prediction_results(
    franchise_id: int = Query(..., description="가맹점 ID"),
    prediction_type: str = Query(..., example="sales", description="예측 유형 (sales, order, purchase 등)"),
    start_date: date = Query(..., description="조회 시작일"),
    end_date: date = Query(..., description="조회 종료일")
):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT
        prediction_result_id,
        target_date,
        predicted_value,
        explanation,
        model_used,
        created_at
    FROM prediction_result
    WHERE franchise_id = %s
      AND prediction_type = %s
      AND target_date BETWEEN %s AND %s
    ORDER BY target_date ASC
    """

    cursor.execute(query, (franchise_id, prediction_type, start_date, end_date))
    rows = cursor.fetchall()
    results = list(rows)

    cursor.close()
    conn.close()

    return {"results": results}
