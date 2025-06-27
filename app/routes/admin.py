# app/routes/admin.py
from fastapi import APIRouter
from app.services.external_factors_service import save_external_factors_for_next_week

router = APIRouter()

@router.post("/admin/update-external-factors")
def update_external_factors():
    save_external_factors_for_next_week()
    return {"message": "External factors updated"}
