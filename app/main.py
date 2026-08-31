from fastapi import FastAPI

app = FastAPI(
    title="StockFlow API",
    version="1.0.0",
)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "StockFlow API is running"}