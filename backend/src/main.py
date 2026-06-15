from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.core.config import settings
from src.core.exceptions import AppException
from src.api.routes import auth, collections, documents, chat, admin

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("novamind.startup", environment=settings.ENVIRONMENT)
    yield
    logger.info("novamind.shutdown")


app = FastAPI(
    title="NovaMind AI",
    description="Document Intelligence Platform — RAG-powered Q&A over your PDFs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    logger.warning(
        "app.exception",
        code=exc.code,
        message=str(exc),
        path=str(request.url),
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": str(exc), "details": exc.details}},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc: Exception):
    logger.error("app.unhandled_exception", error=str(exc), path=str(request.url))
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred", "details": {}}},
    )


app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(collections.router, prefix="/api/v1/collections", tags=["collections"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "environment": settings.ENVIRONMENT}
