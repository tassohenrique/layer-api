from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routers import auth, brands, health, notes, perfumes, reviews
from app.core.exceptions import AppError

app = FastAPI(
    title="Layer API",
    description="API REST de reviews de perfumes",
    version="0.1.0",
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    headers = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
        headers=headers,
    )


app.include_router(health.router)
app.include_router(brands.router)
app.include_router(notes.router)
app.include_router(perfumes.router)
app.include_router(auth.router)
app.include_router(reviews.router)
