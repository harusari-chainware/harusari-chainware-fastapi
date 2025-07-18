from fastapi import APIRouter
from fastapi.responses import JSONResponse

import logging

logger = logging.getLogger("uvicorn.error")

router = APIRouter()


@router.get(
    "/api/v1/health/check",
    summary="Health Check API",
    description="애플리케이션이 정상적으로 실행 중인지 확인하는 API입니다.",
    tags=["Health"],
    response_description="정상 동작 여부 반환"
)
async def health_check():
    return JSONResponse(
        status_code=200,
        content={"status": "ok"}
    )
