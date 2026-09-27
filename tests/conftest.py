"""
tests/conftest.py
Test Fixtures, Canonical Model Imports, and Live FastAPI TestClient Configuration for
Krone Agriculture India Field Service & Telematics Dashboard (4-Tier E2E Test Suite).
All domain models, geospatial math algorithms, and engine services are imported directly from backend/app.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
import pytest
from fastapi.testclient import TestClient

# ============================================================================
# 1. SYS.PATH INJECTION: Point directly to backend package
# ============================================================================
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# ============================================================================
# 2. CANONICAL DOMAIN MODELS & SCHEMAS (backend/app/models)
# ============================================================================
from app.models.schemas import (
    GeoPoint,
    PulseKpis,
    PulseResponse,
    TechnicianLiveOnJob,
    TechnicianOnLeave,
    JobItem,
    MachineryUnderService,
    SyncRequest,
    SyncResponse,
    ProductivitySummary,
    TechnicianProductivityRecord,
    TrendDataPoint,
    ProductivityResponse,
    TechnicianDetail,
    JobDetail,
    JobStatus,
    JobType,
)
from app.models.telematics import (
    RawGpsPing,
    RawStop,
    Cluster5km,
    RouteAnomaly,
    JourneyLocation,
    JourneySummary,
    RouteResponse,
    RouteInspectorResponse,
)

# ============================================================================
# 3. CANONICAL SERVICE ENGINES & ALGORITHMS (backend/app/services)
# ============================================================================
from app.services.telematics_engine import (
    EARTH_RADIUS_KM,
    STATIONARY_SPEED_KMH,
    JITTER_DEADBAND_METERS,
    MIN_STOP_DURATION_SECONDS,
    UNAUTHORIZED_STOP_THRESHOLD_SECONDS,
    MAX_CLUSTER_RADIUS_KM,
    haversine_distance_km,
    haversine_distance,
    initial_bearing_radians,
    initial_bearing,
    cross_track_distance_km,
    cross_track_distance,
    weighted_cartesian_centroid,
    filter_stationary_jitter,
    apply_jitter_filter,
    extract_raw_stops,
    cluster_pings_5km,
    cluster_stops_5km,
    inspect_journey,
    compute_hours_balance,
    analyze_route_journey,
    inspect_route_telematics,
    calculate_hours,
)
from app.services.analytics_engine import AnalyticsEngine
from app.services.mock_generator import KroneMockGenerator
from app.services.sync_service import SyncService
from app.main import app as fastapi_app, create_app

# ============================================================================
# 4. BACKWARD COMPATIBILITY ALIASES FOR E2E TEST SUITE
# ============================================================================
LocationCoord = GeoPoint
PulseKPIs = PulseKpis
TechnicianOnJob = TechnicianLiveOnJob
TodayJob = JobItem
MachineUnderService = MachineryUnderService
ProductivityTrend = TrendDataPoint
OperationalCluster = Cluster5km
RouteInspectionResponse = RouteResponse


# ============================================================================
# 5. KRONE SYNTHETIC DATASET DELEGATION (Calling KroneMockGenerator)
# ============================================================================
def get_krone_synthetic_dataset() -> Dict[str, Any]:
    """Generates authentic Krone Agriculture India domain data via KroneMockGenerator."""
    generator = KroneMockGenerator()
    data = generator.generate_all()
    techs = []
    for t in data["technicians"]:
        t_copy = dict(t)
        raw_id = t.get("technician_id", t.get("id", ""))
        if raw_id.startswith("TECH-") and len(raw_id) == 7:
            padded_id = f"TECH-{int(raw_id.split('-')[1]):03d}"
        else:
            padded_id = raw_id
        t_copy["id"] = padded_id
        t_copy["technician_id"] = padded_id
        t_copy["job_id"] = t.get("active_job_id", t.get("job_id"))
        techs.append(t_copy)

    return {
        "technicians": techs,
        "jobs": data["jobs"],
        "machines": data["machinery"],
        "machinery": data["machinery"],
        "daily_shifts": data["daily_shifts"],
        "pulse_kpis": data["pulse_kpis"],
        "telematics_routes": data["telematics_routes"],
    }


# ============================================================================
# 6. PYTEST FIXTURES (Including Live FastAPI TestClient)
# ============================================================================
@pytest.fixture(scope="session")
def client() -> TestClient:
    """Live FastAPI TestClient for certifying live endpoints."""
    with TestClient(fastapi_app) as tc:
        yield tc


@pytest.fixture(scope="session")
def sync_service(client) -> SyncService:
    """Provides access to the application's live SyncService."""
    return client.app.state.sync_service


@pytest.fixture(scope="session")
def analytics_engine() -> AnalyticsEngine:
    """Provides access to the application's live AnalyticsEngine."""
    return AnalyticsEngine()


@pytest.fixture(scope="session")
def krone_dataset() -> Dict[str, Any]:
    return get_krone_synthetic_dataset()


@pytest.fixture
def sample_pulse_response(krone_dataset) -> PulseResponse:
    techs_on_job = [
        TechnicianOnJob(
            technician_id=t["id"],
            name=t["name"],
            status=t["status"],
            live_job_id=t.get("job_id"),
            customer_company="Reliance Industries Limited",
            machine_asset="Krone BigPack 1290 HDP",
            current_location=LocationCoord(lat=30.9010, lng=75.8573)
        )
        for t in krone_dataset["technicians"] if t["status"] == "On Paid Job"
    ]
    paid_count = len(techs_on_job)
    active_total = len([t for t in krone_dataset["technicians"] if t["status"] != "On Holiday/Leave"]) or 10
    leave_count = len([t for t in krone_dataset["technicians"] if t["status"] == "On Holiday/Leave"]) or 2
    util_pct = round((paid_count / active_total) * 100.0, 1)

    kpis = PulseKPIs(
        technicians_on_paid_jobs=paid_count,
        technicians_active_total=active_total,
        technicians_on_leave=leave_count,
        total_jobs_today=len(krone_dataset["jobs"]),
        jobs_completed_today=len([j for j in krone_dataset["jobs"] if j.get("status") == "Completed"]),
        fleet_utilization_pct=util_pct
    )
    today_jobs = [TodayJob(**j) for j in krone_dataset["jobs"]]
    machines = [MachineUnderService(**m) for m in krone_dataset["machines"]]

    return PulseResponse(
        timestamp=datetime.now(timezone.utc).isoformat(),
        kpis=kpis,
        technicians_on_jobs=techs_on_job,
        today_jobs=today_jobs,
        machines_under_service=machines
    )


@pytest.fixture
def sample_journey_pings() -> List[Dict[str, Any]]:
    """Returns GPS trajectory from Ludhiana Depot (30.9010, 75.8573) to Barwala (30.3800, 76.8405)."""
    t0 = datetime(2026, 9, 22, 8, 0, 0, tzinfo=timezone.utc)
    pings = []

    # 1. Base Depot pings (stationary, speed 0 km/h)
    for m in range(20):
        pings.append({
            "lat": 30.9010 + (m * 0.00001),
            "lng": 75.8573 + (m * 0.00001),
            "speed_kmh": 0.0,
            "timestamp": (t0 + timedelta(minutes=m)).isoformat(),
            "timestamp_s": m * 60.0,
            "duration_s": 60
        })

    # 2. Highway transit (speed 65 km/h)
    for m in range(20, 60):
        frac = (m - 20) / 40.0
        lat = 30.9010 + frac * (30.6450 - 30.9010)
        lng = 75.8573 + frac * (76.3200 - 75.8573)
        pings.append({
            "lat": lat,
            "lng": lng,
            "speed_kmh": 65.0,
            "timestamp": (t0 + timedelta(minutes=m)).isoformat(),
            "timestamp_s": m * 60.0,
            "duration_s": 60
        })

    # 3. Dhaba Stop (stationary 25 min, speed 0 km/h)
    for m in range(60, 85):
        pings.append({
            "lat": 30.6450,
            "lng": 76.3200,
            "speed_kmh": 0.0,
            "timestamp": (t0 + timedelta(minutes=m)).isoformat(),
            "timestamp_s": m * 60.0,
            "duration_s": 60
        })

    # 4. Highway transit leg 2 (speed 60 km/h)
    for m in range(85, 125):
        frac = (m - 85) / 40.0
        lat = 30.6450 + frac * (30.3800 - 30.6450)
        lng = 76.3200 + frac * (76.8405 - 76.3200)
        pings.append({
            "lat": lat,
            "lng": lng,
            "speed_kmh": 60.0,
            "timestamp": (t0 + timedelta(minutes=m)).isoformat(),
            "timestamp_s": m * 60.0,
            "duration_s": 60
        })

    # 5. Customer Job Site (stationary 390 min, speed 0 km/h)
    for m in range(125, 185):
        pings.append({
            "lat": 30.3800 + ((m % 5) * 0.00005),
            "lng": 76.8405 + ((m % 5) * 0.00005),
            "speed_kmh": 0.0,
            "timestamp": (t0 + timedelta(minutes=m)).isoformat(),
            "timestamp_s": m * 60.0,
            "duration_s": 60
        })

    return pings
