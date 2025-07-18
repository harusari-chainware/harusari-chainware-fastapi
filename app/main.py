from fastapi import FastAPI
from app.routes import predict
from app.routes import admin
from app.routes import health_check

app = FastAPI()
app.include_router(admin.router)
app.include_router(predict.router)

app.include_router(health_check.router)