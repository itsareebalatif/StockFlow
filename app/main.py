from fastapi import FastAPI

from fastapi import FastAPI
from app.core.config import settings
from app.routers import auth

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="StockFlow API - E-Commerce & Inventory Management Backend",
)

app.include_router(auth.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "app": settings.PROJECT_NAME}