from fastapi import FastAPI
from app.routes import predict
from app.routes import admin

app = FastAPI()
app.include_router(admin.router)
app.include_router(predict.router)