from fastapi import FastAPI

from app.api.routers import health

app = FastAPI(
    title="Layer API",
    description="API REST de reviews de perfumes",
    version="0.1.0",
)

app.include_router(health.router)
