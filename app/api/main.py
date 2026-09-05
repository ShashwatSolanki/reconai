from fastapi import FastAPI

from app.api.routes.reconciliation import router as reconciliation_router

app = FastAPI(
    title="ReconAI",
    description="AI-powered financial reconciliation and exception management system",
    version="0.1.0",
)

app.include_router(reconciliation_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
