"""
backend/app/config.py
Enterprise Configuration & Constants for Krone Agriculture India Dashboard
"""
from functools import lru_cache
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    LOCATION_ID: str = "8176f98f-3d9f-4d70-ad2f-7c6a9c23d16c"   # Gurugram Default Location
    FIELDY_API_BASE_URL: str = "https://api.getfieldy.com"
    FIELDY_WEB_PORTAL_URL: str = "https://krone.getfieldy.com"
    FIELDY_SESSION_PATH: str = r"C:\Users\Naveen\.gemini\antigravity\brain\4b00f5c5-2082-4b83-8c2a-a77bdb91df75\scratch\fieldy_storage.json"
    FIELDY_API_TOKEN: Optional[str] = None

    # Offline & Mock Resilience
    OFFLINE_FALLBACK_MODE: bool = True
    POLLING_INTERVAL_SECONDS: int = 30
    POLLING_BACKOFF_MAX_SECONDS: int = 300

    # Geodesy & Telematics Mathematical Constants
    EARTH_RADIUS_KM: float = 6371.0
    CLUSTER_RADIUS_KM: float = 5.0
    CORRIDOR_TOLERANCE_KM: float = 1.5
    STATIONARY_SPEED_THRESHOLD_KMH: float = 1.5
    JITTER_DEADBAND_METERS: float = 30.0
    UNAUTHORIZED_STOP_THRESHOLD_MINUTES: float = 15.0
    MIN_STOP_DURATION_MINUTES: float = 5.0

    # Krone Commercial Contract Rates (RIL Master AMC Ground Truth)
    DEP_RATE_PER_MANDAY: float = 5000.00   # Clause 4.7: ₹5,000 / 8-hr shift
    DA_RATE_PER_DAY: float = 2000.00        # Clause 4.8: ₹2,000 / day outstation allowance
    TRAVEL_RATE_PER_KM: float = 5.00       # Clause 4.8: ₹5 / KM travel conveyance
    GST_RATE_PCT: float = 18.00            # 18% IGST
    SAC_CODE: str = "998719"               # Agricultural Machinery Maintenance & Repair

    # CORS Allowed Origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",   # Vite dev server
        "http://127.0.0.1:5173",
        "http://localhost:4173",   # Vite preview server
        "http://127.0.0.1:4173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://bishnoinaveen.github.io"
    ]


@lru_cache()
def get_settings() -> Settings:
    """Returns a cached singleton of application settings."""
    return Settings()
