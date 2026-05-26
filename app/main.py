from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import ensure_data_dirs, get_cors_origins, settings
from app.database import init_db
from app.ml.classifier import DocumentClassifier
from app.models import HealthResponse
from app.routers import check, download, fix, history


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_data_dirs()
    await init_db()
    app.state.classifier = DocumentClassifier(settings.model_path)
    yield


app = FastAPI(
    title="GOST-Checker API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(check.router, prefix="/api", tags=["documents"])
app.include_router(fix.router, prefix="/api", tags=["documents"])
app.include_router(history.router, prefix="/api", tags=["history"])
app.include_router(download.router, prefix="/api", tags=["download"])


@app.get("/api/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        model_loaded=bool(getattr(app.state.classifier, "loaded", False)),
    )
