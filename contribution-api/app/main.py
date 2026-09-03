# Project Volusia — Contribution API Server
# ===========================================
#
# A FastAPI implementation of the Contribution API defined in
# AGENTIC_CONTRIBUTION_STRATEGY.md (Appendix J) and the OpenAPI spec
# (openapi.yaml).
#
# Quick start:
#   1. pip install -r requirements.txt
#   2. cp .env.example .env
#   3. python -m app.main
#
# The server runs on http://0.0.0.0:8899 by default.
#
# See README.md in the repo root for full architecture context.

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from app.config import settings
from app.database import init_db
from app.routers import auth, submissions, data, contributors

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("volusia-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Project Volusia Contribution API...")
    init_db()
    logger.info("Database initialized.")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Project Volusia Contribution API",
    description="Submit and track contributions to the Project Volusia knowledge system.",
    version="2026-09-03",
    lifespan=lifespan,
)

# CORS — allow the web form and other origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_metadata(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start

    response.headers["X-API-Version"] = "2026-09-03"
    response.headers["X-Request-Duration"] = f"{duration:.3f}s"

    return response


# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(submissions.router, prefix="/api/v1", tags=["Submissions"])
app.include_router(data.router, prefix="/api/v1", tags=["Data Access"])
app.include_router(contributors.router, prefix="/api/v1", tags=["Contributors"])


@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "version": "2026-09-03",
        "uptime_seconds": int(time.time() - app.state.get("start_time", time.time())),
        "dependencies": {
            "database": "healthy",
            "submission_queue": "healthy",
            "auth_service": "healthy",
        },
    }


@app.get("/")
async def root():
    return {
        "name": "Project Volusia Contribution API",
        "version": "2026-09-03",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }
