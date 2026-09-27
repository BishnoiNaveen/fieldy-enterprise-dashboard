# Remediation Design Report — E2E Test Suite Direct Integration (M1 Remediation Explorer 3)

**Work Product Target**: `tests/conftest.py`, `tests/test_tier1_features.py`, `tests/test_tier2_boundaries.py`, `tests/test_tier3_combinations.py`, `tests/test_tier4_scenarios.py`  
**Integration Target**: `backend/app/` (`models/schemas.py`, `models/telematics.py`, `services/telematics_engine.py`, `services/analytics_engine.py`, `services/mock_generator.py`, `services/sync_service.py`, `main.py`)  
**Investigator**: `m1_remed_explorer_3` (Explorer Archetype — Read-Only Remediation Design)  
**Date**: 2026-09-23  

---

## 1. Executive Summary & Root Cause Analysis

### 1.1 Forensic Diagnosis
As documented in the Forensic Auditor Evidence Report (`.agents/m1_auditor/report.md`), the 187 tests in `tests/` (`test_tier1_features.py`, `test_tier2_boundaries.py`, `test_tier3_combinations.py`, `test_tier4_scenarios.py`) suffered from **Prohibited Pattern #4: Self-Certifying Tests**. 

Specifically:
1. **Isolated Duplication in `tests/conftest.py`**:
   `tests/conftest.py` (727 lines total) re-implemented:
   - 15 duplicate Pydantic domain models (lines 17–166)
   - 7 duplicate spherical geodesy and clustering algorithms (`haversine_distance`, `initial_bearing`, `cross_track_distance`, `weighted_cartesian_centroid`, `apply_jitter_filter`, `cluster_stops_5km`, `inspect_route_telematics`, lines 171–431)
   - 1 hardcoded static mock dataset generator (lines 437–614)
   Over 444 lines (61% of `tests/conftest.py`) were verbatim or near-verbatim duplicate copies of backend logic.
2. **Disconnected Test Files**:
   All four tier test files contained AST imports exclusively from `conftest.py` (`from conftest import ...`). None of the 187 tests ever imported or tested any code in `backend/app`. Consequently, bugs, regressions, or facade behaviors in `backend/app` could never be detected by the E2E suite.
3. **Absence of Live Engine Certification**:
   The E2E test suite lacked a live `TestClient(app)` fixture, meaning the live FastAPI route stack (`/api/dashboard/pulse`, `/api/dashboard/sync`, `/api/analytics/productivity`, `/api/telematics/routes`, `/api/technicians`, `/api/jobs`), dependency injection graphs, and Pydantic request/response serialization pipelines were never certified by the 4-tier suite.

---

## 2. Architectural Remediation Blueprint

```
+--------------------------------------------------------------------------------------------------+
|                                    LIVE FASTAPI BACKEND (backend/app)                            |
|                                                                                                  |
|   +-----------------------+   +------------------------+   +---------------------------------+   |
|   | models/schemas.py     |   | models/telematics.py   |   | services/telematics_engine.py   |   |
|   | - PulseKpis           |   | - Cluster5km           |   | - haversine_distance_km         |   |
|   | - PulseResponse       |   | - RouteAnomaly         |   | - weighted_cartesian_centroid   |   |
|   | - JobItem             |   | - RouteResponse        |   | - filter_stationary_jitter      |   |
|   | - MachineryUnder...   |   | - JourneySummary       |   | - cluster_pings_5km             |   |
|   | - ProductivitySummary |   | - RawGpsPing           |   | - inspect_journey               |   |
|   +-----------+-----------+   +-----------+------------+   +----------------+----------------+   |
|               ^                           ^                                 ^                    |
|               |                           |                                 |                    |
|               +---------------------------+---------------------------------+                    |
|                                           |                                                      |
|                                (Direct Package Imports)                                          |
|                                           |                                                      |
|   +---------------------------------------+--------------------------------------------------+   |
|   |                                tests/conftest.py (Refactored)                            |   |
|   |                                                                                          |   |
|   |   1. sys.path.insert(0, backend_dir)                                                     |   |
|   |   2. Direct imports from backend/app/models and backend/app/services                     |   |
|   |   3. 100% Elimination of duplicated math functions                                       |   |
|   |   4. Backward-compatible aliases:                                                        |   |
|   |      - LocationCoord = GeoPoint, PulseKPIs = PulseKpis                                   |   |
|   |      - TodayJob = JobItem, MachineUnderService = MachineryUnderService                   |   |
|   |      - OperationalCluster = Cluster5km, RouteInspectionResponse = RouteResponse         |   |
|   |   5. Delegated adapter: inspect_route_telematics(...) -> telematics_engine               |   |
|   |   6. Live FastAPI TestClient Fixture: client = TestClient(app)                           |   |
|   +---------------------------------------+--------------------------------------------------+   |
|                                           |                                                      |
|               +---------------------------+---------------------------------+                    |
|               v                           v                                 v                    |
|   +-----------------------+   +------------------------+   +---------------------------------+   |
|   | test_tier1_features   |   | test_tier2_boundaries  |   | test_tier3_combinations        |   |
|   | - Direct imports      |   | - Direct imports       |   | - Direct imports                |   |
|   | - Certifies Live API  |   | - Boundary constraints |   | - Service interaction testing   |   |
|   +-----------------------+   +------------------------+   +----------------+----------------+   |
|                                                                             |                    |
|                                                                             v                    |
|                                                                +-----------------------------+   |
|                                                                | test_tier4_scenarios        |   |
|                                                                | - End-to-end real workflows |   |
|                                                                | - Live endpoint validation  |   |
|                                                                +-----------------------------+   |
+--------------------------------------------------------------------------------------------------+
```

---

## 3. Inventory of Duplicate Code Elimination in `tests/conftest.py`

| Code Component | Lines in Current `conftest.py` | Canonical Destination in `backend/app/` | Remediation Action |
|:---|:---:|:---|:---|
| `LocationCoord` | 17–23 | `app.models.schemas.GeoPoint` | **DELETE**. Alias to `GeoPoint`. |
| `PulseKPIs` | 25–32 | `app.models.schemas.PulseKpis` | **DELETE**. Alias to `PulseKpis`. |
| `TechnicianOnJob` | 34–42 | `app.models.schemas.TechnicianLiveOnJob` | **DELETE**. Alias to `TechnicianLiveOnJob`. |
| `TodayJob` | 44–54 | `app.models.schemas.JobItem` | **DELETE**. Alias to `JobItem`. |
| `MachineUnderService` | 56–64 | `app.models.schemas.MachineryUnderService` | **DELETE**. Alias to `MachineryUnderService`. |
| `PulseResponse` | 66–72 | `app.models.schemas.PulseResponse` | **DELETE**. Import directly. |
| `SyncRequest`, `SyncResponse` | 74–83 | `app.models.schemas.SyncRequest`, `SyncResponse` | **DELETE**. Import directly. |
| `ProductivitySummary` | 85–101 | `app.models.schemas.ProductivitySummary` | **DELETE**. Import directly. |
| `TechnicianProductivityRecord` | 103–112 | `app.models.schemas.TechnicianProductivityRecord` | **DELETE**. Import directly. |
| `ProductivityTrend` | 114–120 | `app.models.schemas.TrendDataPoint` | **DELETE**. Alias to `TrendDataPoint`. |
| `ProductivityResponse` | 122–126 | `app.models.schemas.ProductivityResponse` | **DELETE**. Import directly. |
| `JourneySummary` | 128–135 | `app.models.telematics.JourneySummary` | **DELETE**. Import directly. |
| `OperationalCluster` | 137–146 | `app.models.telematics.Cluster5km` | **DELETE**. Alias to `Cluster5km`. |
| `RouteAnomaly` | 148–154 | `app.models.telematics.RouteAnomaly` | **DELETE**. Import directly. |
| `RouteInspectionResponse` | 156–165 | `app.models.telematics.RouteResponse` | **DELETE**. Alias to `RouteResponse`. |
| `haversine_distance` | 171–184 | `app.services.telematics_engine.haversine_distance_km` | **DELETE**. Import directly. |
| `initial_bearing` | 186–193 | `app.services.telematics_engine.initial_bearing_radians` | **DELETE**. Import directly. |
| `cross_track_distance` | 195–206 | `app.services.telematics_engine.cross_track_distance_km` | **DELETE**. Import directly. |
| `weighted_cartesian_centroid` | 208–242 | `app.services.telematics_engine.weighted_cartesian_centroid` | **DELETE**. Import directly. |
| `apply_jitter_filter` | 244–285 | `app.services.telematics_engine.filter_stationary_jitter` | **DELETE**. Import directly. |
| `cluster_stops_5km` | 287–339 | `app.services.telematics_engine.cluster_pings_5km` | **DELETE**. Import directly. |
| `inspect_route_telematics` | 341–431 | Delegate to `telematics_engine` functions | **REFACTOR**. Thin bridge calling genuine backend algorithms. |
| `get_krone_synthetic_dataset` | 437–614 | `app.services.mock_generator.KroneMockGenerator` | **REFACTOR**. Thin bridge delegating to `KroneMockGenerator.generate_all()`. |

**Total Duplicated Lines Removed**: 444 lines eliminated from `tests/conftest.py`.

---

## 4. Necessary Backend Domain Model Enhancements

To guarantee that importing domain models directly from `backend/app` preserves all business and boundary constraints, three minor enhancements to `backend/app/models/schemas.py` and `backend/app/models/telematics.py` are required:

### 4.1 Enforce Shift Hours Conservation in `backend/app/models/schemas.py`
In `ProductivitySummary`, the conservation check $H_{shift} \approx H_w + H_t + H_i$ (within 0.05 hr tolerance) must be validated via `@field_validator("total_shift_hours")`:
```python
    @field_validator("total_shift_hours")
    @classmethod
    def validate_conservation(cls, v: float, info: Any) -> float:
        values = info.data
        if "total_working_hours" in values and "total_travelling_hours" in values and "total_idle_hours" in values:
            expected_sum = values["total_working_hours"] + values["total_travelling_hours"] + values["total_idle_hours"]
            if abs(v - expected_sum) > 0.05:
                raise ValueError(f"Shift hours conservation violated: {v} != {expected_sum}")
        return v
```

### 4.2 Enforce Canonical Pattern & Enum Validation in `JobItem` (`schemas.py`)
In `JobItem`:
- Enforce canonical ticket format: `job_id: str = Field(..., pattern=r"^SR-26-\d{4}$")`
- Enforce valid job classification: `job_type: str = Field("Paid", pattern=r"^(Paid|AMC|Warranty|Internal|Training)$")`

### 4.3 Flex Location Types in `JourneySummary` (`telematics.py`)
In `backend/app/models/telematics.py`:
Support both `JourneyLocation` and `GeoPoint` in `JourneySummary`:
```python
class JourneySummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    start_location: Union[JourneyLocation, GeoPoint]
    destination: Union[JourneyLocation, GeoPoint]
    transit_duration_minutes: float
    unauthorized_stop_duration_minutes: float
    total_distance_km: float
    anomalies_detected: int
    ...
```

---

## 5. Surgical Refactoring Specifications

### 5.1 Proposed `tests/conftest.py` (Full Replacement)

```python
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
# 5. DELEGATED ROUTE INSPECTOR ADAPTER (Calling Genuine Backend Engine)
# ============================================================================
def inspect_route_telematics(
    stops: List[Dict[str, Any]],
    base_loc: Dict[str, float],
    dest_loc: Dict[str, float],
    designated_distance_km: float = 80.0,
    actual_distance_km: float = 84.6,
    transit_moving_seconds: float = 5400.0,
    shift_start: Optional[datetime] = None,
    shift_end: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Adapter that delegates directly to genuine backend/app services:
    - cluster_pings_5km
    - inspect_journey
    - haversine_distance_km
    Eliminates duplicated math calculations.
    """
    clusters = cluster_pings_5km(stops, max_radius_km=5.0)
    classified_zones, summary = inspect_journey(clusters, base_loc, dest_loc)

    anomalies: List[Dict[str, Any]] = []
    for c in classified_zones:
        if c.get("is_anomaly", False):
            c_lat = float(c.get("centroid", {}).get("lat", c.get("centroid_lat", 0.0)))
            c_lng = float(c.get("centroid", {}).get("lng", c.get("centroid_lon", 0.0)))
            total_dur = float(c.get("total_duration_s", float(c.get("duration_minutes", 0.0)) * 60.0))
            anomalies.append({
                "type": "unauthorized_stop",
                "location": {"lat": c_lat, "lng": c_lng},
                "duration_minutes": round(total_dur / 60.0, 1),
                "started_at": str(c.get("start_time", "2026-09-22T08:45:00Z")),
                "description": c.get("anomaly_reason", "Vehicle stationary outside authorized corridor")
            })

    detour_ratio = actual_distance_km / max(1.0, designated_distance_km)
    excess_km = actual_distance_km - designated_distance_km
    if detour_ratio > 1.25 and excess_km > 10.0:
        anomalies.append({
            "type": "excessive_detour",
            "location": {"lat": float(base_loc["lat"]), "lng": float(base_loc.get("lon", base_loc.get("lng", 0.0)))},
            "duration_minutes": 0.0,
            "started_at": "2026-09-22T08:30:00Z",
            "description": f"Detour ratio {detour_ratio:.2f} exceeds 1.25 threshold (+{excess_km:.1f} km)"
        })

    working_s = summary["working_seconds"]
    unauth_s = summary["unauthorized_seconds"]
    base_dwell_s = summary["base_seconds"]

    H_w = working_s / 3600.0
    H_t = transit_moving_seconds / 3600.0
    H_i = (unauth_s + base_dwell_s) / 3600.0
    H_shift = H_w + H_t + H_i

    return {
        "clusters": classified_zones,
        "anomalies": anomalies,
        "H_w": round(H_w, 2),
        "H_t": round(H_t, 2),
        "H_i": round(H_i, 2),
        "H_shift": round(H_shift, 2),
        "working_seconds": working_s,
        "transit_moving_seconds": transit_moving_seconds,
        "unauth_stop_seconds": unauth_s,
        "total_distance_km": actual_distance_km,
        "detour_ratio": round(detour_ratio, 2)
    }


# ============================================================================
# 6. KRONE SYNTHETIC DATASET DELEGATION (Calling KroneMockGenerator)
# ============================================================================
def get_krone_synthetic_dataset() -> Dict[str, Any]:
    """Generates authentic Krone Agriculture India domain data via KroneMockGenerator."""
    generator = KroneMockGenerator()
    data = generator.generate_all()
    techs = []
    for t in data["technicians"]:
        t_copy = dict(t)
        t_copy["id"] = t.get("technician_id", t.get("id"))
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
# 7. PYTEST FIXTURES (Including Live FastAPI TestClient)
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
        TechnicianLiveOnJob(
            technician_id=t["id"],
            name=t["name"],
            status=t["status"],
            live_job_id=t.get("job_id"),
            customer_company="Reliance Industries Limited",
            machine_asset="Krone BigPack 1290 HDP",
            current_location=GeoPoint(lat=30.9010, lng=75.8573)
        )
        for t in krone_dataset["technicians"] if t["status"] == "On Paid Job"
    ]
    paid_count = len(techs_on_job)
    active_total = len([t for t in krone_dataset["technicians"] if t["status"] != "On Holiday/Leave"]) or 10
    leave_count = len([t for t in krone_dataset["technicians"] if t["status"] == "On Holiday/Leave"]) or 2
    util_pct = round((paid_count / active_total) * 100.0, 1)

    kpis = PulseKpis(
        technicians_on_paid_jobs=paid_count,
        technicians_active_total=active_total,
        technicians_on_leave=leave_count,
        total_jobs_today=len(krone_dataset["jobs"]),
        jobs_completed_today=len([j for j in krone_dataset["jobs"] if j.get("status") == "Completed"]),
        fleet_utilization_pct=util_pct
    )
    today_jobs = [JobItem(**j) for j in krone_dataset["jobs"]]
    machines = [MachineryUnderService(**m) for m in krone_dataset["machines"]]

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
```

---

### 5.2 Header Refactoring for `test_tier1_features.py` through `tier4_scenarios.py`

In `tests/test_tier1_features.py`, `tests/test_tier2_boundaries.py`, `tests/test_tier3_combinations.py`, and `tests/test_tier4_scenarios.py`, replace lines 10–38 with:

```python
import sys
from pathlib import Path

# Add backend directory to sys.path so genuine application packages are found
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# 1. Direct domain models & schemas from backend/app
from app.models.schemas import (
    GeoPoint,
    PulseKpis,
    PulseResponse,
    TechnicianLiveOnJob,
    JobItem,
    MachineryUnderService,
    SyncRequest,
    SyncResponse,
    ProductivitySummary,
    TechnicianProductivityRecord,
    TrendDataPoint,
    ProductivityResponse,
)
from app.models.telematics import (
    Cluster5km,
    RouteAnomaly,
    JourneySummary,
    RouteResponse,
)

# 2. Direct service algorithms from backend/app
from app.services.telematics_engine import (
    haversine_distance_km,
    haversine_distance,
    weighted_cartesian_centroid,
    filter_stationary_jitter,
    apply_jitter_filter,
    cluster_pings_5km,
    cluster_stops_5km,
    inspect_journey,
    compute_hours_balance,
    analyze_route_journey,
)
from app.services.analytics_engine import AnalyticsEngine
from app.services.mock_generator import KroneMockGenerator

# 3. Shared fixtures and test-facing aliases from conftest
from conftest import (
    LocationCoord,
    PulseKPIs,
    TechnicianOnJob,
    TodayJob,
    MachineUnderService,
    ProductivityTrend,
    OperationalCluster,
    RouteInspectionResponse,
    inspect_route_telematics,
    get_krone_synthetic_dataset,
)
```

---

### 5.3 Live FastAPI Endpoint Certification Tests to Add to Tier 1 & Tier 4

To ensure the test suite certifies the live running application, the following tests are added:

#### In `test_tier1_features.py`:
```python
    def test_f01_live_fastapi_pulse_endpoint(self, client):
        """Certifies GET /api/dashboard/pulse against live FastAPI application."""
        resp = client.get("/api/dashboard/pulse")
        assert resp.status_code == 200
        data = resp.json()
        model = PulseResponse(**data)
        assert model.kpis.technicians_on_paid_jobs >= 0
        assert len(model.today_jobs) > 0

    def test_f04_live_fastapi_sync_endpoint(self, client):
        """Certifies POST /api/dashboard/sync executes live synchronization cycle."""
        resp = client.post("/api/dashboard/sync", json={"force_refresh": True})
        assert resp.status_code == 200
        data = resp.json()
        model = SyncResponse(**data)
        assert model.status == "success"
        assert model.records_synced > 0

    def test_f11_live_fastapi_productivity_endpoint(self, client):
        """Certifies GET /api/analytics/productivity enforces hours conservation on live data."""
        resp = client.get("/api/analytics/productivity?timeframe=daily")
        assert resp.status_code == 200
        data = resp.json()
        model = ProductivityResponse(**data)
        s = model.summary
        assert abs(s.total_shift_hours - (s.total_working_hours + s.total_travelling_hours + s.total_idle_hours)) < 0.05

    def test_f16_live_fastapi_telematics_routes_endpoint(self, client):
        """Certifies GET /api/telematics/routes processes telemetry through telematics_engine."""
        resp = client.get("/api/telematics/routes?technician_id=TECH-01")
        assert resp.status_code == 200
        data = resp.json()
        model = RouteResponse(**data)
        assert len(model.route_polyline) > 0
        assert model.journey_summary.total_distance_km > 0
```

#### In `test_tier4_scenarios.py`:
In `test_scenario_1_ril_barwala_emergency_knotter_repair`:
```python
        # Certify scenario 1 against live FastAPI REST API
        resp = client.get("/api/telematics/routes?technician_id=TECH-01&date=2026-09-22")
        assert resp.status_code == 200
        route_data = resp.json()
        assert route_data["technician_id"] == "TECH-01"
        assert len(route_data["clusters_5km"]) >= 1
```

---

## 6. Verification and Regression Invalidation Plan

### 6.1 Independent Verification Commands
Once the implementer applies the refactoring:
1. **Verify No Duplicate Math in `tests/conftest.py`**:
   ```powershell
   & "C:\Users\Naveen\AppData\Local\Programs\Python\Python312\python.exe" -c "
   with open(r'tests\conftest.py') as f:
       code = f.read()
   assert 'def haversine_distance(' not in code, 'Duplicate haversine still present in conftest.py'
   assert 'def apply_jitter_filter(' not in code, 'Duplicate jitter filter still present in conftest.py'
   assert 'def cluster_stops_5km(' not in code, 'Duplicate cluster_stops still present in conftest.py'
   print('PASS: Zero duplicated math algorithms in tests/conftest.py')
   "
   ```

2. **Verify Direct Backend Package Imports**:
   ```powershell
   & "C:\Users\Naveen\AppData\Local\Programs\Python\Python312\python.exe" -c "
   import tests.test_tier1_features as t1
   assert hasattr(t1, 'haversine_distance_km')
   assert t1.haversine_distance_km.__module__ == 'app.services.telematics_engine'
   assert t1.PulseResponse.__module__ == 'app.models.schemas'
   print('PASS: test_tier1_features directly imports backend/app!')
   "
   ```

3. **Execute Full Test Suite (187 + 40 + live tests)**:
   ```powershell
   & "C:\Users\Naveen\AppData\Local\Programs\Python\Python312\python.exe" -m pytest tests/ backend/tests/ -v
   ```
   *Expected Outcome*: 100% PASS across all tests without a single warning or failure.

### 6.2 Invalidation Conditions
This remediation plan is invalidated if:
1. `tests/conftest.py` defines its own private implementation of `haversine_distance` or `cluster_stops_5km` instead of importing from `app.services.telematics_engine`.
2. Any test in `tests/test_tier1_features.py` through `tier4_scenarios.py` tests a mock object rather than the genuine backend schema or service.
3. Tests run without the FastAPI backend directory added to `sys.path`.
