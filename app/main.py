from fastapi import FastAPI
from app.core.config import settings
from app.routers import (
    auth,
    users,
    categories,
    products,
    inventory,
    suppliers,
    orders,
    purchase_orders,
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="StockFlow API - E-Commerce & Inventory Management Backend",
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(inventory.router)
app.include_router(suppliers.router)
app.include_router(orders.router)
app.include_router(purchase_orders.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "app": settings.PROJECT_NAME}