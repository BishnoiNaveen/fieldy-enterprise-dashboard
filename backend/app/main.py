"""
backend/app/main.py
FastAPI Application Entry Point, CORS, Lifespan, and Router Configuration
"""
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

import time
from typing import Dict, List
from app.config import get_settings
from app.services.sync_service import SyncService
from app.services.analytics_engine import AnalyticsEngine
from app.services.audit_engine import ForensicAuditEngine
from app.services.automation_service import AutomationService
from app.routers import dashboard, analytics, telematics, entities, amcs, audit, automation, security

logger = logging.getLogger("krone_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and graceful shutdown lifecycles.
    Initializes configuration, cache layers, and mock data stores.
    """
    settings = get_settings()
    logger.info("Starting up %s (v%s) in %s mode...", settings.APP_NAME, settings.APP_VERSION, settings.ENVIRONMENT)
    
    # Store settings, engines, and services in app state
    app.state.settings = settings
    app.state.analytics_engine = AnalyticsEngine()
    app.state.sync_service = SyncService()
    app.state.audit_engine = ForensicAuditEngine()
    app.state.automation_service = AutomationService()
    app.state.sync_status = {
        "status": "initialized",
        "last_synced_at": None,
        "is_fallback_mode": settings.OFFLINE_FALLBACK_MODE
    }

    # Start background synchronizer poller
    await app.state.sync_service.start_background_poller()

    yield

    # Clean shutdown
    logger.info("Shutting down %s gracefully...", settings.APP_NAME)
    await app.state.sync_service.stop_background_poller()


def create_app() -> FastAPI:
    """Application factory for FastAPI instance."""
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Enterprise Field Service & Telematics Dashboard API for Krone Agriculture India. "
            "Integrated with Fieldy FSM, 12-pillar forensic audit engine, and autonomous 5 km Haversine clustering."
        ),
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Initialize sync service and engines in app state immediately for test client availability
    app.state.settings = settings
    app.state.analytics_engine = AnalyticsEngine()
    app.state.sync_service = SyncService()
    app.state.audit_engine = ForensicAuditEngine()
    app.state.automation_service = AutomationService()

    # 1. CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. Rate-Limiting & Security Headers Middleware
    rate_limit_store: Dict[str, List[float]] = {}

    @app.middleware("http")
    async def security_and_rate_limit_middleware(request: Request, call_next):
        # Exempt health & docs endpoints
        if request.url.path in ["/health", "/api/health", "/docs", "/openapi.json", "/redoc"]:
            response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            return response

        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()
        window = 60.0
        max_requests = 300

        timestamps = rate_limit_store.get(client_ip, [])
        # Prune old timestamps
        timestamps = [t for t in timestamps if now - t < window]
        if len(timestamps) >= max_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "status": "rate_limit_exceeded",
                    "message": "Too many requests. Rate limit is 300 requests per minute."
                }
            )

        timestamps.append(now)
        rate_limit_store[client_ip] = timestamps

        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["X-Krone-Security"] = "Enterprise-Grade-Protected"
        return response

    # 2. Exception Handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "status_code": exc.status_code,
                "message": exc.detail,
                "path": str(request.url.path)
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "status": "validation_error",
                "status_code": 422,
                "message": "Request validation failed",
                "errors": exc.errors(),
                "path": str(request.url.path)
            }
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled server exception at %s: %s", request.url.path, exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "fatal_error",
                "status_code": 500,
                "message": "An internal server error occurred.",
                "detail": str(exc) if settings.DEBUG else "Please consult backend logs.",
                "path": str(request.url.path)
            }
        )

    # 3. System Health & Info Endpoints
    @app.get("/", tags=["System"])
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "tenant": settings.TENANT_NAME,
            "documentation": "/docs",
            "status": "online"
        }

    @app.get("/health", tags=["System"])
    @app.get("/api/health", tags=["System"])
    async def health_check():
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "tenant_id": settings.TENANT_ID,
            "workspace_id": settings.WORKSPACE_ID,
            "offline_mode": settings.OFFLINE_FALLBACK_MODE
        }

    # 4. Modular Router Registration
    app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
    app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
    app.include_router(telematics.router, prefix="/api/telematics", tags=["Telematics"])
    app.include_router(entities.router, prefix="/api", tags=["Entities"])
    app.include_router(amcs.router, prefix="/api/amcs", tags=["AMCs"])
    app.include_router(audit.router, prefix="/api/audit", tags=["Forensic Audit"])
    app.include_router(automation.router, prefix="/api/automations", tags=["Automations"])
    app.include_router(security.router, prefix="/api/security", tags=["Security"])

    return app


app = create_app()
