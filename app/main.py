from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers

app = FastAPI(title=settings.app_name, debug=settings.debug)

register_exception_handlers(app)

app.include_router(auth_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
