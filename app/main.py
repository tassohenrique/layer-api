from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routers import brands, health
from app.core.exceptions import AppError

app = FastAPI(
    title="Layer API",
    description="API REST de reviews de perfumes",
    version="0.1.0",
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


app.include_router(health.router)
app.include_router(brands.router)
