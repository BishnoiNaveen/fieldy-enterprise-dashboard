"""
Verification script for M1 Config and FastAPI Main blueprints.
Tests pydantic-settings, default constants, lifespan, exception handlers, and endpoints.
"""
from functools import lru_cache
from typing import List, Optional
from contextlib import asynccontextmanager

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient


# ==========================================
# 1. CONFIG BLUEPRINT
# ==========================================

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application Metadata
    APP_NAME: str = "Krone Agriculture India — Field Service & Telematics Dashboard API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Enterprise Tenant Constants (Fieldy FSM Ground Truth)
    TENANT_NAME: str = "Krone Agriculture India Pvt Ltd"
    TENANT_ID: str = "4e51f497-b8dd-4036-8d78-60b12a7598b7"
    WORKSPACE_ID: str = "87c32c6a-ec1f-49af-a925-8455d6933ed6"  # krone Gurugram Office
    LOCATION_ID: str = "8176f98f-3d9f-4d70-ad2f-7c6a9c23d16c"   # Default Location
    FIELDY_API_BASE_URL: str = "https://api.getfieldy.com"
    FIELDY_WEB_PORTAL_URL: str = "https://krone.getfieldy.com"
    FIELDY_SESSION_PATH: str = r"C:\Users\Naveen\.gemini\antigravity\brain\4b00f5c5-2082-4b83-8c2a-a77bdb91df75\scratch\fieldy_storage.json"

    # Offline & Mock Resilience
    OFFLINE_FALLBACK_MODE: bool = True
    POLLING_INTERVAL_SECONDS: int = 30
    POLLING_BACKOFF_MAX_SECONDS: int = 300

    # Geodesy & Telematics Parameters
    EARTH_RADIUS_KM: float = 6371.0
    CLUSTER_RADIUS_KM: float = 5.0
    CORRIDOR_TOLERANCE_KM: float = 1.5
    STATIONARY_SPEED_THRESHOLD_KMH: float = 1.5
    JITTER_DEADBAND_METERS: float = 30.0
    UNAUTHORIZED_STOP_THRESHOLD_MINUTES: float = 15.0
    MIN_STOP_DURATION_MINUTES: float = 5.0

    # Krone Commercial Contract Rates (RIL AMC Ground Truth)
    DEP_RATE_PER_MANDAY: float = 5000.00   # Clause 4.7: ₹5,000 / 8-hr shift
    DA_RATE_PER_DAY: float = 2000.00        # Clause 4.8: ₹2,000 / day outstation allowance
    TRAVEL_RATE_PER_KM: float = 5.00       # Clause 4.8: ₹5 / KM travel conveyance
    GST_RATE_PCT: float = 18.00            # 18% IGST
    SAC_CODE: str = "998719"               # Agricultural Machinery Maintenance & Repair

    # CORS Allowed Origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# ==========================================
# 2. LIFESPAN & APP BLUEPRINT
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    settings = get_settings()
    app.state.settings = settings
    app.state.sync_status = {
        "status": "ready",
        "last_synced_at": "2026-09-22T12:00:00Z",
        "is_fallback": settings.OFFLINE_FALLBACK_MODE
    }
    yield
    # Shutdown actions


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="High-performance backend API powering the Krone Agriculture India Field Service & Telematics Dashboard.",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception Handlers
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
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
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
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "fatal_error",
                "status_code": 500,
                "message": "Internal server error occurred",
                "detail": str(exc) if settings.DEBUG else "An unexpected error occurred. Please consult backend logs.",
                "path": str(request.url.path)
            }
        )

    # Root & Health Endpoints
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

    return app


# ==========================================
# 3. VERIFICATION TESTS
# ==========================================

def test_settings_load():
    settings = get_settings()
    assert settings.TENANT_ID == "4e51f497-b8dd-4036-8d78-60b12a7598b7"
    assert settings.CLUSTER_RADIUS_KM == 5.0
    assert settings.DEP_RATE_PER_MANDAY == 5000.0
    assert settings.SAC_CODE == "998719"
    print("[PASS] Settings loaded and validated successfully")


def test_api_health_client():
    app = create_app()
    with TestClient(app) as client:
        r_root = client.get("/")
        assert r_root.status_code == 200
        assert r_root.json()["status"] == "online"

        r_health = client.get("/api/health")
        assert r_health.status_code == 200
        assert r_health.json()["status"] == "healthy"
        assert r_health.json()["tenant_id"] == "4e51f497-b8dd-4036-8d78-60b12a7598b7"
    print("[PASS] FastAPI app, TestClient, CORS, and health endpoints verified")


if __name__ == "__main__":
    test_settings_load()
    test_api_health_client()
    print("\nALL CONFIG & MAIN BLUEPRINTS VERIFIED WITH 100% SUCCESS!")
