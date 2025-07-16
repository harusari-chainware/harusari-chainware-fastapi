# app/routes/admin.py
from fastapi import APIRouter
from app.services.external_factors_service import save_external_factors_for_next_week

router = APIRouter()

@router.post(
    "/admin/update-external-factors",
    summary="외부 요인 데이터 업데이트",
    description="다음 주 예측을 위한 외부 요인 데이터를 저장합니다 (날씨, 휴일, 소비자심리지수 등).",
    tags=["Admin"]
)
def update_external_factors():
    """
    외부 요인 자동 수집 및 저장 API

    - 기상 예보
    - 휴일 정보
    - 소비자심리지수

    이 데이터를 기반으로 다음 주 예측이 수행됩니다.
    """
    save_external_factors_for_next_week()
    return {"message": "External factors updated"}
