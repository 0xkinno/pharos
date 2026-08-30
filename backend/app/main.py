"""
PHAROS FastAPI Application

Entry point for the PHAROS backend API.
Configures FastAPI app with CORS, lifespan events, and routes.
"""
from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.demo import router as demo_router
from app.api.judges import router as judges_router
from app.api.routes import router as main_router
from app.core.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()

# CORS origins — include all configured origins plus all localhost ports for dev.
# Next.js dev server uses 3000 by default but falls back to 3001, 3002, etc.
# if another process already owns 3000.
_cors_origins = settings.cors_origins_list + [
    "https://pharos-flame-nu.vercel.app",
    "https://pharos.vercel.app",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
]
# deduplicate while preserving order
_cors_origins = list(dict.fromkeys(_cors_origins))

# Allow all Vercel preview deployments (*.vercel.app) via regex
_cors_origin_regex = r"https://.*\.vercel\.app"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    logger.info("PHAROS API starting up...")
    start = time.time()

    # Diagnostic: log whether each watsonx env var is present (never log values)
    logger.info(
        "WATSONX_API_KEY present: %s",
        bool(settings.watsonx_api_key),
    )
    logger.info(
        "WATSONX_PROJECT_ID present: %s",
        bool(settings.watsonx_project_id),
    )
    logger.info(
        "WATSONX_URL: %s",
        settings.watsonx_url,
    )

    # Warm up the watsonx.ai client (non-blocking)
    from app.ai.watsonx_client import get_watsonx_client
    client = get_watsonx_client()
    if client.is_available():
        logger.info("watsonx.ai is configured and available.")
    else:
        logger.warning(
            "watsonx.ai not configured. AI features disabled. "
            "Compliance engine and demo data will work normally."
        )

    # Warm up the demo dataset
    try:
        from app.api.demo import get_demo_dataset
        get_demo_dataset()
        logger.info("Demo dataset ready.")
    except Exception as exc:
        logger.warning("Demo dataset warm-up failed: %s", exc)

    elapsed = time.time() - start
    logger.info("PHAROS API ready in %.2fs", elapsed)
    yield
    logger.info("PHAROS API shutting down.")


app = FastAPI(
    title="PHAROS API",
    description=(
        "Satellite orbital compliance checking against FCC, IADC, ISO, ESA, and COPUOS standards. "
        "Built for the IBM AI Builders Challenge August 2026."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS — allow frontend origin + always allow localhost for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_origin_regex=_cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(main_router)
app.include_router(judges_router)
app.include_router(demo_router)


@app.get("/")
async def root():
    """Root endpoint — redirects to docs."""
    return {
        "service": "PHAROS API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "judges": "/api/judges",
        "demo": "/api/demo",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """Global exception handler — never expose stack traces in production."""
    logger.error("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.environment == "development" else "An unexpected error occurred.",
        },
    )
