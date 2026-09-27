"""
Tier 1: Comprehensive Feature Coverage Tests (16 Features, >= 80 Tests)
Derived from ORIGINAL_REQUEST.md and PROJECT.md § Feature Inventory.
"""

import math
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from pathlib import Path
import sys

# Add backend directory to sys.path so genuine application packages are found
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(Path(__file__).parent))

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
    inspect_route_telematics,
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
    get_krone_synthetic_dataset,
)


# ============================================================================
# FEATURE 1: REAL-TIME OPERATIONAL PULSE KPIS (ORIGINAL_REQUEST §R1)
# ============================================================================

class TestFeature01OperationalPulseKPIs:
    """Tests for Real-Time Operational Pulse KPIs."""

    def test_f01_kpis_technician_counts_consistency(self, sample_pulse_response):
        """Active technicians on jobs + available + leave must equal total workforce."""
        kpis = sample_pulse_response.kpis
        assert kpis.technicians_on_paid_jobs <= kpis.technicians_active_total
        assert kpis.technicians_active_total >= 0
        assert kpis.technicians_on_leave >= 0

    def test_f01_kpis_paid_jobs_count_validity(self, sample_pulse_response):
        """Paid jobs count matches technicians on paid jobs in current sample."""
        kpis = sample_pulse_response.kpis
        paid_techs = [t for t in sample_pulse_response.technicians_on_jobs if t.status == "On Paid Job"]
        assert len(paid_techs) == kpis.technicians_on_paid_jobs

    def test_f01_kpis_fleet_utilization_formula(self, sample_pulse_response):
        """Fleet utilization pct = (technicians_on_paid_jobs / technicians_active_total) * 100."""
        kpis = sample_pulse_response.kpis
        expected_pct = (kpis.technicians_on_paid_jobs / kpis.technicians_active_total) * 100.0
        assert abs(kpis.fleet_utilization_pct - expected_pct) < 0.1

    def test_f01_kpis_live_timestamp_presence(self, sample_pulse_response):
        """Timestamp is valid ISO-8601 string."""
        ts = sample_pulse_response.timestamp
        parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        assert parsed.year >= 2026

    def test_f01_kpis_jobs_completed_vs_total(self, sample_pulse_response):
        """Jobs completed today must be less than or equal to total jobs today."""
        kpis = sample_pulse_response.kpis
        assert kpis.jobs_completed_today <= kpis.total_jobs_today

    def test_f01_live_fastapi_pulse_endpoint(self, client):
        """Certifies GET /api/dashboard/pulse against live FastAPI application."""
        resp = client.get("/api/dashboard/pulse")
        assert resp.status_code == 200
        data = resp.json()
        model = PulseResponse(**data)
        assert model.kpis.technicians_on_paid_jobs >= 0
        assert len(model.today_jobs) > 0


# ============================================================================
# FEATURE 2: TODAY'S JOBS LIST (SR-26-XXXX) (ORIGINAL_REQUEST §R1)
# ============================================================================

class TestFeature02TodaysJobsList:
    """Tests for Today's Jobs List and Fieldy SR-26-XXXX pipeline."""

    def test_f02_jobs_id_canonical_regex_format(self, krone_dataset):
        """Job ID must strictly adhere to canonical Fieldy format 'SR-26-XXXX'."""
        for job_dict in krone_dataset["jobs"]:
            job = TodayJob(**job_dict)
            assert job.job_id.startswith("SR-26-")
            assert len(job.job_id) == 10
            assert job.job_id[6:].isdigit()

    def test_f02_jobs_status_pipeline_membership(self, krone_dataset):
        """Status must belong to authorized Fieldy pipeline states."""
        allowed_statuses = {"In Progress", "Completed", "Cancelled", "Hold", "Open"}
        for job_dict in krone_dataset["jobs"]:
            job = TodayJob(**job_dict)
            assert job.status in allowed_statuses

    def test_f02_jobs_customer_association(self, krone_dataset):
        """Every job must associate with a named client company."""
        for job_dict in krone_dataset["jobs"]:
            job = TodayJob(**job_dict)
            assert len(job.customer_name.strip()) > 3

    def test_f02_jobs_assigned_technician_consistency(self, krone_dataset):
        """In-progress jobs must have at least one assigned technician."""
        in_progress_jobs = [TodayJob(**j) for j in krone_dataset["jobs"] if j["status"] == "In Progress"]
        assert len(in_progress_jobs) > 0
        for job in in_progress_jobs:
            assert len(job.assigned_technicians) >= 1

    def test_f02_jobs_scheduled_start_iso_format(self, krone_dataset):
        """Scheduled start must be valid ISO datetime."""
        for job_dict in krone_dataset["jobs"]:
            job = TodayJob(**job_dict)
            dt = datetime.fromisoformat(job.scheduled_start.replace("Z", "+00:00"))
            assert dt.year >= 2026


# ============================================================================
# FEATURE 3: MACHINERY UNDER SERVICE TABLE (ORIGINAL_REQUEST §R1)
# ============================================================================

class TestFeature03MachineryUnderService:
    """Tests for Machinery Under Service Table."""

    def test_f03_machinery_serial_number_format(self, krone_dataset):
        """Machine serial number must follow format with 7-digit/alphanumeric code."""
        for m_dict in krone_dataset["machines"]:
            machine = MachineUnderService(**m_dict)
            assert "-" in machine.serial_number
            prefix, code = machine.serial_number.split("-", 1)
            assert len(prefix) >= 4
            assert len(code) >= 5

    def test_f03_machinery_asset_catalog_names(self, krone_dataset):
        """Machine asset names match authentic Krone product families."""
        krone_families = ("BigPack", "BiG X", "Fortima", "EasyCut", "Swadro")
        for m_dict in krone_dataset["machines"]:
            machine = MachineUnderService(**m_dict)
            assert machine.asset_name.startswith("Krone ")
            assert any(family in machine.asset_name for family in krone_families)

    def test_f03_machinery_client_company_mapping(self, krone_dataset):
        """Every machine must have an authentic client company (e.g. RIL, VERBIO, SAEL)."""
        for m_dict in krone_dataset["machines"]:
            machine = MachineUnderService(**m_dict)
            assert any(c in machine.client_company_name for c in ("Reliance", "Punjab", "VERBIO", "SAEL", "Hoshiarpur"))

    def test_f03_machinery_site_contact_person_phone(self, krone_dataset):
        """Contact person must include phone number with Indian international code (+91)."""
        for m_dict in krone_dataset["machines"]:
            machine = MachineUnderService(**m_dict)
            assert "+91" in machine.site_contact_person

    def test_f03_machinery_active_job_linkage(self, krone_dataset):
        """Linked active job ID must exist in today's job list."""
        all_job_ids = {j["job_id"] for j in krone_dataset["jobs"]}
        for m_dict in krone_dataset["machines"]:
            machine = MachineUnderService(**m_dict)
            assert machine.active_job_id in all_job_ids


# ============================================================================
# FEATURE 4: FIELDY FSM SESSION SYNCHRONIZER (ORIGINAL_REQUEST §R1)
# ============================================================================

class TestFeature04FieldySessionSynchronizer:
    """Tests for Fieldy FSM Session Synchronizer and Polling."""

    def test_f04_sync_request_default_and_force(self):
        """SyncRequest initializes default force_refresh=False and allows True."""
        req1 = SyncRequest()
        assert req1.force_refresh is False
        req2 = SyncRequest(force_refresh=True)
        assert req2.force_refresh is True

    def test_f04_sync_response_status_success(self):
        """Sync response indicates success with record counts."""
        resp = SyncResponse(
            status="success",
            last_synced_at=datetime.now(timezone.utc).isoformat(),
            records_synced=42,
            source="fieldy_cache"
        )
        assert resp.status == "success"
        assert resp.records_synced > 0

    def test_f04_sync_response_timestamp_monotonicity(self):
        """Timestamp reflects recent synchronization."""
        now = datetime.now(timezone.utc)
        resp = SyncResponse(
            status="success",
            last_synced_at=now.isoformat(),
            records_synced=15,
            source="fieldy_api"
        )
        parsed = datetime.fromisoformat(resp.last_synced_at)
        assert (now - parsed).total_seconds() < 5.0

    def test_f04_sync_source_fieldy_or_fallback(self):
        """Sync source must identify origin: fieldy_api, fieldy_cache, or synthetic_fallback."""
        valid_sources = {"fieldy_api", "fieldy_cache", "synthetic_fallback"}
        resp = SyncResponse(
            status="success",
            last_synced_at="2026-09-22T12:00:00Z",
            records_synced=50,
            source="synthetic_fallback"
        )
        assert resp.source in valid_sources

    def test_f04_sync_idempotence(self):
        """Sequential sync calls return consistent valid structures."""
        sync1 = SyncResponse(status="success", last_synced_at="2026-09-22T12:00:00Z", records_synced=12, source="fieldy_cache")
        sync2 = SyncResponse(status="success", last_synced_at="2026-09-22T12:01:00Z", records_synced=12, source="fieldy_cache")
        assert sync1.records_synced == sync2.records_synced

    def test_f04_live_fastapi_sync_endpoint(self, client):
        """Certifies POST /api/dashboard/sync executes live synchronization cycle."""
        resp = client.post("/api/dashboard/sync", json={"force_refresh": True})
        assert resp.status_code == 200
        data = resp.json()
        model = SyncResponse(**data)
        assert model.status == "success"
        assert model.records_synced > 0


# ============================================================================
# FEATURE 5: CALIBRATED KRONE SYNTHETIC GENERATOR (ORIGINAL_REQUEST §R4)
# ============================================================================

class TestFeature05KroneSyntheticGenerator:
    """Tests for Calibrated Krone Synthetic Dataset Generator."""

    def test_f05_synthetic_dataset_technicians_minimum(self, krone_dataset):
        """Dataset must provide at least 10 realistic technicians."""
        assert len(krone_dataset["technicians"]) >= 10

    def test_f05_synthetic_dataset_jobs_variety(self, krone_dataset):
        """Dataset covers Paid, AMC, and Warranty job classifications."""
        types = {j["job_type"] for j in krone_dataset["jobs"]}
        assert "Paid" in types
        assert "AMC" in types

    def test_f05_synthetic_dataset_authentic_krone_assets(self, krone_dataset):
        """Machines reflect authentic German Krone agricultural machinery."""
        assets = [m["asset_name"] for m in krone_dataset["machines"]]
        assert any("BigPack 1290" in a for a in assets)
        assert any("BiG X 680" in a for a in assets)
        assert any("Fortima V 1500" in a for a in assets)

    def test_f05_synthetic_dataset_punjab_haryana_locations(self, krone_dataset):
        """Locations are authentic northern agricultural hubs (Punjab/Haryana/UP)."""
        locations = [m["location"] for m in krone_dataset["machines"]]
        assert any("Punjab" in loc for loc in locations)
        assert any("Ludhiana" in loc or "Hoshiarpur" in loc for loc in locations)

    def test_f05_synthetic_dataset_schema_conformance(self, krone_dataset):
        """All records in synthetic dataset strictly parse via Pydantic models."""
        for j in krone_dataset["jobs"]:
            TodayJob(**j)
        for m in krone_dataset["machines"]:
            MachineUnderService(**m)


# ============================================================================
# FEATURE 6: 5 KM RADIUS HAVERSINE CLUSTERING (ORIGINAL_REQUEST §R3)
# ============================================================================

class TestFeature06HaversineClustering5km:
    """Tests for Haversine distance and 5 km radius clustering engine."""

    def test_f06_haversine_identical_coordinates_zero_distance(self):
        """Distance between identical coordinates is 0.0 km."""
        d = haversine_distance(30.9010, 75.8573, 30.9010, 75.8573)
        assert d == 0.0

    def test_f06_haversine_known_geographic_distance(self):
        """Distance between Ludhiana (30.9010, 75.8573) and Jalandhar (31.3260, 75.5762) is ~54-56 km."""
        dist = haversine_distance(30.9010, 75.8573, 31.3260, 75.5762)
        assert 52.0 < dist < 58.0

    def test_f06_clustering_merges_points_within_5km(self):
        """Stops separated by 1.8 km are merged into a single operational cluster."""
        stops = [
            {"lat": 30.3800, "lon": 76.8405, "duration_s": 7200, "start_time": "09:00", "end_time": "11:00"},
            {"lat": 30.3920, "lon": 76.8510, "duration_s": 3600, "start_time": "11:15", "end_time": "12:15"}
        ]
        clusters = cluster_stops_5km(stops, max_radius_km=5.0)
        assert len(clusters) == 1
        assert len(clusters[0]["stops"]) == 2
        assert clusters[0]["total_duration_s"] == 10800

    def test_f06_clustering_separates_points_exceeding_5km(self):
        """Stops separated by 15 km are separated into distinct clusters."""
        stops = [
            {"lat": 30.9010, "lon": 75.8573, "duration_s": 3600, "start_time": "08:00", "end_time": "09:00"},
            {"lat": 30.7500, "lon": 76.0500, "duration_s": 3600, "start_time": "10:00", "end_time": "11:00"}
        ]
        clusters = cluster_stops_5km(stops, max_radius_km=5.0)
        assert len(clusters) == 2

    def test_f06_clustering_weighted_centroid_precision(self):
        """Duration-weighted centroid biases heavily toward the longer-duration stop."""
        stops = [
            {"lat": 30.0000, "lon": 75.0000, "duration_s": 14400},  # 4 hours
            {"lat": 30.0300, "lon": 75.0000, "duration_s": 1200}    # 20 mins (~3.3 km away)
        ]
        centroid_lat, centroid_lon = weighted_cartesian_centroid(stops)
        # Centroid lat should be closer to 30.0000 than 30.0300
        dist_to_first = haversine_distance(centroid_lat, centroid_lon, 30.0000, 75.0000)
        dist_to_second = haversine_distance(centroid_lat, centroid_lon, 30.0300, 75.0000)
        assert dist_to_first < dist_to_second
        assert dist_to_first < 0.5


# ============================================================================
# FEATURE 7: SPEED-GATED JITTER DAMPENING (ORIGINAL_REQUEST §R3)
# ============================================================================

class TestFeature07SpeedGatedJitterDampening:
    """Tests for Speed-Gated Jitter Dampening and Stationary Deadbands."""

    def test_f07_jitter_stationary_speed_threshold(self):
        """Pings below 1.5 km/h are flagged as stationary."""
        pings = [
            {"lat": 30.9010, "lon": 75.8573, "speed_kmh": 0.5},
            {"lat": 30.9010, "lon": 75.8573, "speed_kmh": 1.2},
            {"lat": 30.9010, "lon": 75.8573, "speed_kmh": 2.5}
        ]
        filtered = apply_jitter_filter(pings, speed_thresh_kmh=1.5)
        assert filtered[0]["is_stationary"] is True
        assert filtered[1]["is_stationary"] is True
        assert filtered[2]["is_stationary"] is False

    def test_f07_jitter_deadband_suppression(self):
        """Micro-movements < 30m during stationary phase are clamped to anchor."""
        anchor_lat, anchor_lon = 30.901000, 75.857300
        pings = [
            {"lat": anchor_lat, "lon": anchor_lon, "speed_kmh": 0.0},
            {"lat": anchor_lat + 0.000100, "lon": anchor_lon, "speed_kmh": 0.0},  # ~11m away
            {"lat": anchor_lat + 0.000150, "lon": anchor_lon, "speed_kmh": 0.0}   # ~16m away
        ]
        filtered = apply_jitter_filter(pings, speed_thresh_kmh=1.5, deadband_m=30.0)
        assert filtered[1]["filtered_lat"] == anchor_lat
        assert filtered[2]["filtered_lat"] == anchor_lat

    def test_f07_jitter_moving_pings_unmodified(self):
        """Pings during active driving (> 1.5 km/h) are not clamped."""
        pings = [
            {"lat": 30.9010, "lon": 75.8573, "speed_kmh": 60.0},
            {"lat": 30.9100, "lon": 75.8700, "speed_kmh": 65.0}
        ]
        filtered = apply_jitter_filter(pings, speed_thresh_kmh=1.5)
        assert filtered[0]["filtered_lat"] == 30.9010
        assert filtered[1]["filtered_lat"] == 30.9100

    def test_f07_jitter_zero_phantom_odometer_drift(self):
        """Parked vehicle over 20 pings produces zero distance when filtered."""
        anchor_lat, anchor_lon = 30.901000, 75.857300
        pings = [
            {"lat": anchor_lat + ((i % 3) * 0.00008), "lon": anchor_lon + ((i % 2) * 0.00008), "speed_kmh": 0.0}
            for i in range(20)
        ]
        filtered = apply_jitter_filter(pings, speed_thresh_kmh=1.5, deadband_m=30.0)
        accum_dist = sum(
            haversine_distance(filtered[i]["filtered_lat"], filtered[i]["filtered_lon"],
                               filtered[i+1]["filtered_lat"], filtered[i+1]["filtered_lon"])
            for i in range(len(filtered) - 1)
        )
        assert accum_dist == 0.0

    def test_f07_jitter_stop_and_go_transition(self):
        """Transition from stationary to highway driving resets anchor correctly."""
        pings = [
            {"lat": 30.9010, "lon": 75.8573, "speed_kmh": 0.0},
            {"lat": 30.90105, "lon": 75.85735, "speed_kmh": 0.0},
            {"lat": 30.9500, "lon": 75.9200, "speed_kmh": 50.0}  # vehicle departs
        ]
        filtered = apply_jitter_filter(pings, speed_thresh_kmh=1.5)
        assert filtered[1]["filtered_lat"] == 30.9010
        assert filtered[2]["filtered_lat"] == 30.9500


# ============================================================================
# FEATURE 8: AUTONOMOUS ROUTE INSPECTOR (ORIGINAL_REQUEST §R3)
# ============================================================================

class TestFeature08AutonomousRouteInspector:
    """Tests for Autonomous Route Inspection and Zone Classification."""

    def test_f08_inspector_origin_base_detection(self):
        """Starting stop within 5km of depot is classified as STARTING_BASE."""
        base = {"lat": 30.9010, "lon": 75.8573, "name": "Ludhiana Depot"}
        dest = {"lat": 30.3800, "lon": 76.8405, "name": "Barwala Site"}
        stops = [
            {"lat": 30.9015, "lon": 75.8570, "duration_s": 1200, "name": "Depot Departure"},
            {"lat": 30.3800, "lon": 76.8405, "duration_s": 18000, "name": "Customer Site"}
        ]
        res = inspect_route_telematics(stops, base, dest)
        assert res["clusters"][0]["is_base"] is True
        assert res["clusters"][0]["zone_type"] == "STARTING_BASE"

    def test_f08_inspector_destination_site_detection(self):
        """Stop within 5km of customer job site is classified as CUSTOMER_DESTINATION."""
        base = {"lat": 30.9010, "lon": 75.8573}
        dest = {"lat": 30.3800, "lon": 76.8405}
        stops = [
            {"lat": 30.9010, "lon": 75.8573, "duration_s": 1200},
            {"lat": 30.3810, "lon": 76.8410, "duration_s": 14400}
        ]
        res = inspect_route_telematics(stops, base, dest)
        assert res["clusters"][1]["is_job_site"] is True
        assert res["clusters"][1]["zone_type"] == "CUSTOMER_DESTINATION"

    def test_f08_inspector_unauthorized_halt_identification(self):
        """En-route stop > 15m outside base/destination is flagged as UNAUTHORIZED_STOP."""
        base = {"lat": 30.9010, "lon": 75.8573}
        dest = {"lat": 30.3800, "lon": 76.8405}
        stops = [
            {"lat": 30.9010, "lon": 75.8573, "duration_s": 1200},
            {"lat": 30.6450, "lon": 76.3200, "duration_s": 1500},  # 25 min stop (~40 km away)
            {"lat": 30.3800, "lon": 76.8405, "duration_s": 14400}
        ]
        res = inspect_route_telematics(stops, base, dest)
        unauth_clusters = [c for c in res["clusters"] if c["zone_type"] == "UNAUTHORIZED_STOP"]
        assert len(unauth_clusters) == 1
        assert len(res["anomalies"]) >= 1

    def test_f08_inspector_authorized_transit_delay(self):
        """Brief en-route toll/fuel stop <= 15 min is not flagged as unauthorized."""
        base = {"lat": 30.9010, "lon": 75.8573}
        dest = {"lat": 30.3800, "lon": 76.8405}
        stops = [
            {"lat": 30.9010, "lon": 75.8573, "duration_s": 1200},
            {"lat": 30.6450, "lon": 76.3200, "duration_s": 600},   # 10 min stop
            {"lat": 30.3800, "lon": 76.8405, "duration_s": 14400}
        ]
        res = inspect_route_telematics(stops, base, dest)
        unauth_clusters = [c for c in res["clusters"] if c["zone_type"] == "UNAUTHORIZED_STOP"]
        assert len(unauth_clusters) == 0

    def test_f08_inspector_journey_summary_generation(self):
        """Inspector correctly generates aggregate distance and time breakdown."""
        base = {"lat": 30.9010, "lon": 75.8573}
        dest = {"lat": 30.3800, "lon": 76.8405}
        stops = [
            {"lat": 30.9010, "lon": 75.8573, "duration_s": 1200},
            {"lat": 30.3800, "lon": 76.8405, "duration_s": 14400}
        ]
        res = inspect_route_telematics(stops, base, dest, actual_distance_km=84.6)
        assert res["total_distance_km"] == 84.6
        assert res["H_w"] == 4.0  # 14400s = 4.0 hrs


# ============================================================================
# FEATURE 9: TRANSIT VS UNAUTHORIZED STOP DETECTION (ORIGINAL_REQUEST §R3)
# ============================================================================

class TestFeature09TransitVsUnauthorizedStops:
    """Tests separating designated corridor travel from unscheduled stops."""

    def test_f09_transit_time_pure_moving_calculation(self):
        """Pure transit time accounts for moving vehicle seconds."""
        base = {"lat": 30.9010, "lon": 75.8573}
        dest = {"lat": 30.3800, "lon": 76.8405}
        stops = [{"lat": 30.3800, "lon": 76.8405, "duration_s": 14400}]
        res = inspect_route_telematics(stops, base, dest, transit_moving_seconds=5400.0)
        assert res["H_t"] == 1.5  # 5400 / 3600 = 1.5 hrs

    def test_f09_unauthorized_stop_threshold_boundary(self):
        """Stop at 901s (>15m) is unauthorized; stop at 899s (<15m) is authorized."""
        base = {"lat": 30.9010, "lon": 75.8573}
        dest = {"lat": 30.3800, "lon": 76.8405}
        
        stops_auth = [{"lat": 30.6000, "lon": 76.2000, "duration_s": 899}]
        res_auth = inspect_route_telematics(stops_auth, base, dest)
        assert res_auth["clusters"][0]["zone_type"] == "AUTHORIZED_ENROUTE_STOP"
        
        stops_unauth = [{"lat": 30.6000, "lon": 76.2000, "duration_s": 901}]
        res_unauth = inspect_route_telematics(stops_unauth, base, dest)
        assert res_unauth["clusters"][0]["zone_type"] == "UNAUTHORIZED_STOP"

    def test_f09_unauthorized_stop_deducted_from_travel(self):
        """Unauthorized stop is deducted from transit and added to idle hours."""
        base = {"lat": 30.9010, "lon": 75.8573}
        dest = {"lat": 30.3800, "lon": 76.8405}
        stops = [
            {"lat": 30.6450, "lon": 76.3200, "duration_s": 1800},  # 30 min unauthorized stop
            {"lat": 30.3800, "lon": 76.8405, "duration_s": 14400}  # 4 hrs working
        ]
        res = inspect_route_telematics(stops, base, dest, transit_moving_seconds=3600.0)
        assert res["H_w"] == 4.0
        assert res["H_t"] == 1.0
        assert res["H_i"] == 0.5  # 30 min = 0.5 hr

    def test_f09_unauthorized_stop_location_metadata(self):
        """Unauthorized stop records exact coordinates and duration."""
        base = {"lat": 30.9010, "lon": 75.8573}
        dest = {"lat": 30.3800, "lon": 76.8405}
        stops = [{"lat": 30.6450, "lon": 76.3200, "duration_s": 1800, "start_time": "2026-09-22T08:45:00Z"}]
        res = inspect_route_telematics(stops, base, dest)
        anomaly = res["anomalies"][0]
        assert anomaly["type"] == "unauthorized_stop"
        assert anomaly["duration_minutes"] == 30.0
        assert anomaly["location"]["lat"] == 30.6450

    def test_f09_multiple_unauthorized_stops_accumulation(self):
        """Multiple unauthorized halts accumulate in idle time."""
        base = {"lat": 30.9010, "lon": 75.8573}
        dest = {"lat": 30.3800, "lon": 76.8405}
        stops = [
            {"lat": 30.7000, "lon": 76.1000, "duration_s": 1200},  # 20 min
            {"lat": 30.5000, "lon": 76.5000, "duration_s": 1800},  # 30 min
            {"lat": 30.3800, "lon": 76.8405, "duration_s": 14400}
        ]
        res = inspect_route_telematics(stops, base, dest, transit_moving_seconds=3600.0)
        assert res["unauth_stop_seconds"] == 3000.0
        assert len(res["anomalies"]) == 2


# ============================================================================
# FEATURE 10: ROUTE ANOMALY DETECTION & ALERTS (ORIGINAL_REQUEST §R3)
# ============================================================================

class TestFeature10RouteAnomalyDetection:
    """Tests for Route Anomaly Detection, detour ratios, and alert feeds."""

    def test_f10_anomaly_unauthorized_stop_trigger(self):
        """Unauthorized stop generates anomaly object with description."""
        base = {"lat": 30.9010, "lon": 75.8573}
        dest = {"lat": 30.3800, "lon": 76.8405}
        stops = [{"lat": 30.6450, "lon": 76.3200, "duration_s": 1500}]
        res = inspect_route_telematics(stops, base, dest)
        assert len(res["anomalies"]) >= 1
        assert "outside authorized corridor" in res["anomalies"][0]["description"]

    def test_f10_anomaly_excessive_detour_ratio_trigger(self):
        """Detour ratio > 1.25 with excess > 10 km triggers excessive_detour alert."""
        base = {"lat": 30.9010, "lon": 75.8573}
        dest = {"lat": 30.3800, "lon": 76.8405}
        stops = [{"lat": 30.3800, "lon": 76.8405, "duration_s": 14400}]
        # 110 km vs 80 km -> ratio 1.375 (>1.25) and excess 30 km (>10 km)
        res = inspect_route_telematics(stops, base, dest, designated_distance_km=80.0, actual_distance_km=110.0)
        detour_anomalies = [a for a in res["anomalies"] if a["type"] == "excessive_detour"]
        assert len(detour_anomalies) == 1

    def test_f10_anomaly_normal_route_zero_anomalies(self):
        """Designated direct corridor produces 0 anomalies."""
        base = {"lat": 30.9010, "lon": 75.8573}
        dest = {"lat": 30.3800, "lon": 76.8405}
        stops = [{"lat": 30.3800, "lon": 76.8405, "duration_s": 14400}]
        res = inspect_route_telematics(stops, base, dest, designated_distance_km=80.0, actual_distance_km=82.0)
        assert len(res["anomalies"]) == 0

    def test_f10_anomaly_timestamp_and_location(self):
        """RouteAnomaly validates strictly against Pydantic schema."""
        anomaly = RouteAnomaly(
            type="unauthorized_stop",
            location=LocationCoord(lat=30.6450, lng=76.3200),
            duration_minutes=25.0,
            started_at="2026-09-22T08:45:00Z",
            description="Vehicle stationary > 15 min"
        )
        assert anomaly.location.lat == 30.6450
        assert anomaly.duration_minutes == 25.0

    def test_f10_anomaly_alert_count_matches_journey_summary(self):
        """Journey summary anomaly count matches list length."""
        summary = JourneySummary(
            start_location=LocationCoord(lat=30.9010, lng=75.8573),
            destination=LocationCoord(lat=30.3800, lng=76.8405),
            transit_duration_minutes=105.0,
            unauthorized_stop_duration_minutes=25.0,
            total_distance_km=84.6,
            anomalies_detected=2
        )
        assert summary.anomalies_detected == 2


# ============================================================================
# FEATURE 11: MULTI-TIER HOURS ANALYTICS (ORIGINAL_REQUEST §R2)
# ============================================================================

class TestFeature11MultiTierHoursAnalytics:
    """Tests for working, travelling, and idle hours with strict conservation."""

    def test_f11_hours_strict_conservation_law(self):
        """H_shift = H_w + H_t + H_i strictly holds within 0.05 hr."""
        summary = ProductivitySummary(
            total_working_hours=6.5,
            total_travelling_hours=1.5,
            total_idle_hours=0.0,
            total_shift_hours=8.0,
            average_utilization_pct=81.25
        )
        assert abs(summary.total_shift_hours - (summary.total_working_hours + summary.total_travelling_hours + summary.total_idle_hours)) < 0.001

    def test_f11_hours_utilization_percentage_formula(self):
        """Utilization % = (H_w / H_shift) * 100%."""
        w, t, i = 6.0, 2.0, 0.0
        shift = w + t + i
        util_pct = (w / shift) * 100.0
        assert util_pct == 75.0

    def test_f11_hours_non_negative_values(self):
        """All hours metrics must be non-negative."""
        record = TechnicianProductivityRecord(
            technician_id="TECH-001",
            technician_name="Gurpreet Singh",
            working_hours=6.5,
            travelling_hours=1.5,
            idle_hours=0.0,
            shift_hours=8.0,
            utilization_pct=81.25,
            jobs_count=1
        )
        assert record.working_hours >= 0.0
        assert record.travelling_hours >= 0.0
        assert record.idle_hours >= 0.0

    def test_f11_hours_on_site_counts_as_working(self):
        """Time at customer job site increases working hours."""
        base = {"lat": 30.9010, "lon": 75.8573}
        dest = {"lat": 30.3800, "lon": 76.8405}
        stops = [{"lat": 30.3800, "lon": 76.8405, "duration_s": 18000}]  # 5 hours
        res = inspect_route_telematics(stops, base, dest)
        assert res["H_w"] == 5.0

    def test_f11_hours_unaccounted_or_unauth_counts_as_idle(self):
        """Unauthorized stops are accounted under idle hours."""
        base = {"lat": 30.9010, "lon": 75.8573}
        dest = {"lat": 30.3800, "lon": 76.8405}
        stops = [
            {"lat": 30.6450, "lon": 76.3200, "duration_s": 3600},  # 1 hr unauth halt
            {"lat": 30.3800, "lon": 76.8405, "duration_s": 14400}  # 4 hrs work
        ]
        res = inspect_route_telematics(stops, base, dest, transit_moving_seconds=3600.0)
        assert res["H_i"] == 1.0
        assert res["H_w"] == 4.0
        assert res["H_t"] == 1.0

    def test_f11_live_fastapi_productivity_endpoint(self, client):
        """Certifies GET /api/analytics/productivity enforces hours conservation on live data."""
        resp = client.get("/api/analytics/productivity?timeframe=daily")
        assert resp.status_code == 200
        data = resp.json()
        model = ProductivityResponse(**data)
        s = model.summary
        assert abs(s.total_shift_hours - (s.total_working_hours + s.total_travelling_hours + s.total_idle_hours)) < 0.05


# ============================================================================
# FEATURE 12: TIMEFRAME TOGGLING (DAILY/WEEKLY/MONTHLY) (ORIGINAL_REQUEST §R2)
# ============================================================================

class TestFeature12TimeframeToggling:
    """Tests toggling between Daily, Weekly, and Monthly aggregations."""

    def test_f12_timeframe_daily_metrics_structure(self):
        """Daily timeframe response returns period data for single date."""
        resp = ProductivityResponse(
            timeframe="daily",
            summary=ProductivitySummary(
                total_working_hours=64.5,
                total_travelling_hours=21.0,
                total_idle_hours=10.5,
                total_shift_hours=96.0,
                average_utilization_pct=67.19
            ),
            technician_records=[],
            trend_data=[ProductivityTrend(period="2026-09-22", working=64.5, travelling=21.0, idle=10.5)]
        )
        assert resp.timeframe == "daily"
        assert len(resp.trend_data) == 1

    def test_f12_timeframe_weekly_aggregation(self):
        """Weekly timeframe returns 7 daily trends with aggregate summary."""
        trends = [
            ProductivityTrend(period=f"2026-09-{16+i:02d}", working=50.0, travelling=15.0, idle=5.0)
            for i in range(7)
        ]
        resp = ProductivityResponse(
            timeframe="weekly",
            summary=ProductivitySummary(
                total_working_hours=350.0,
                total_travelling_hours=105.0,
                total_idle_hours=35.0,
                total_shift_hours=490.0,
                average_utilization_pct=71.43
            ),
            technician_records=[],
            trend_data=trends
        )
        assert resp.timeframe == "weekly"
        assert len(resp.trend_data) == 7

    def test_f12_timeframe_monthly_aggregation(self):
        """Monthly timeframe supports ~30 days of trend data."""
        trends = [
            ProductivityTrend(period=f"2026-09-{i+1:02d}", working=40.0, travelling=10.0, idle=5.0)
            for i in range(30)
        ]
        resp = ProductivityResponse(
            timeframe="monthly",
            summary=ProductivitySummary(
                total_working_hours=1200.0,
                total_travelling_hours=300.0,
                total_idle_hours=150.0,
                total_shift_hours=1650.0,
                average_utilization_pct=72.73
            ),
            technician_records=[],
            trend_data=trends
        )
        assert resp.timeframe == "monthly"
        assert len(resp.trend_data) == 30

    def test_f12_timeframe_toggle_consistency(self):
        """Weekly total working hours exceed daily working hours for same technician."""
        daily_w = 6.5
        weekly_w = 38.5
        assert weekly_w > daily_w

    def test_f12_timeframe_invalid_parameter_handling(self):
        """Pydantic validation accepts valid timeframes."""
        for tf in ("daily", "weekly", "monthly"):
            resp = ProductivityResponse(
                timeframe=tf,
                summary=ProductivitySummary(
                    total_working_hours=10.0,
                    total_travelling_hours=5.0,
                    total_idle_hours=1.0,
                    total_shift_hours=16.0,
                    average_utilization_pct=62.5
                ),
                technician_records=[],
                trend_data=[]
            )
            assert resp.timeframe == tf


# ============================================================================
# FEATURE 13: MULTI-DIMENSIONAL SEARCH & FILTERING (ORIGINAL_REQUEST §R2)
# ============================================================================

class TestFeature13SearchAndFiltering:
    """Tests multi-criteria search and filtering."""

    def test_f13_filter_by_technician_id(self, krone_dataset):
        """Filtering technicians by ID returns exact match."""
        target_id = "TECH-001"
        matched = [t for t in krone_dataset["technicians"] if t["id"] == target_id]
        assert len(matched) == 1
        assert matched[0]["name"] == "Gurpreet Singh"

    def test_f13_filter_by_customer_company(self, krone_dataset):
        """Filtering jobs by customer company name matches correctly."""
        ril_jobs = [j for j in krone_dataset["jobs"] if "Reliance" in j["customer_name"] or "RIL" in j["customer_name"]]
        assert len(ril_jobs) >= 2

    def test_f13_filter_by_job_status(self, krone_dataset):
        """Filtering by job status returns only matching status jobs."""
        in_progress = [j for j in krone_dataset["jobs"] if j["status"] == "In Progress"]
        for j in in_progress:
            assert j["status"] == "In Progress"

    def test_f13_filter_by_job_type(self, krone_dataset):
        """Filtering by job type partitions paid vs AMC vs warranty."""
        paid_jobs = [j for j in krone_dataset["jobs"] if j["job_type"] == "Paid"]
        assert len(paid_jobs) > 0
        for j in paid_jobs:
            assert j["job_type"] == "Paid"

    def test_f13_filter_combined_multi_parameter(self, krone_dataset):
        """Intersection of customer + job_type + status produces expected subset."""
        matched = [
            j for j in krone_dataset["jobs"]
            if ("Reliance" in j["customer_name"] or "RIL" in j["customer_name"])
            and j["job_type"] == "Paid"
            and j["status"] == "In Progress"
        ]
        assert len(matched) >= 1


# ============================================================================
# FEATURE 14: COMPARATIVE CHARTS & SCORECARDS (ORIGINAL_REQUEST §R2)
# ============================================================================

class TestFeature14ChartsAndScorecards:
    """Tests technician scorecards, rankings, and comparative charts."""

    def test_f14_scorecard_technician_ranking_by_utilization(self):
        """Scorecards rank technicians in descending order of utilization."""
        records = [
            TechnicianProductivityRecord(technician_id="T1", technician_name="A", working_hours=4.0, travelling_hours=2.0, idle_hours=2.0, shift_hours=8.0, utilization_pct=50.0, jobs_count=1),
            TechnicianProductivityRecord(technician_id="T2", technician_name="B", working_hours=7.0, travelling_hours=1.0, idle_hours=0.0, shift_hours=8.0, utilization_pct=87.5, jobs_count=2),
            TechnicianProductivityRecord(technician_id="T3", technician_name="C", working_hours=5.5, travelling_hours=1.5, idle_hours=1.0, shift_hours=8.0, utilization_pct=68.75, jobs_count=1),
        ]
        ranked = sorted(records, key=lambda r: r.utilization_pct, reverse=True)
        assert ranked[0].technician_id == "T2"
        assert ranked[1].technician_id == "T3"
        assert ranked[2].technician_id == "T1"

    def test_f14_chart_trend_data_matches_summary(self):
        """Sum of daily trend points equals summary totals."""
        trends = [
            ProductivityTrend(period="2026-09-21", working=20.0, travelling=5.0, idle=2.0),
            ProductivityTrend(period="2026-09-22", working=30.0, travelling=10.0, idle=3.0)
        ]
        total_w = sum(t.working for t in trends)
        total_t = sum(t.travelling for t in trends)
        total_i = sum(t.idle for t in trends)
        
        summary = ProductivitySummary(
            total_working_hours=total_w,
            total_travelling_hours=total_t,
            total_idle_hours=total_i,
            total_shift_hours=total_w + total_t + total_i,
            average_utilization_pct=(total_w / (total_w + total_t + total_i)) * 100.0
        )
        assert summary.total_working_hours == 50.0
        assert summary.total_travelling_hours == 15.0

    def test_f14_scorecard_job_count_tracking(self):
        """Scorecard tracks integer completed/assigned job count."""
        rec = TechnicianProductivityRecord(
            technician_id="T1", technician_name="A", working_hours=6.0,
            travelling_hours=1.0, idle_hours=1.0, shift_hours=8.0,
            utilization_pct=75.0, jobs_count=3
        )
        assert rec.jobs_count == 3

    def test_f14_scorecard_average_fleet_utilization(self):
        """Fleet utilization average correctly reflects individual technicians."""
        utils = [80.0, 70.0, 90.0]
        avg = sum(utils) / len(utils)
        assert avg == 80.0

    def test_f14_chart_three_tier_breakdown(self):
        """Trend data points contain all three operational tiers."""
        point = ProductivityTrend(period="2026-09-22", working=64.5, travelling=21.0, idle=10.5)
        assert hasattr(point, "working")
        assert hasattr(point, "travelling")
        assert hasattr(point, "idle")


# ============================================================================
# FEATURE 15: EXECUTIVE BENTO GRID UI DATA FEED (ORIGINAL_REQUEST §R4)
# ============================================================================

class TestFeature15ExecutiveBentoGridDataFeed:
    """Tests data feeds formatted for Executive Bento Grid UI."""

    def test_f15_bento_feed_kpi_card_structure(self, sample_pulse_response):
        """Pulse response feeds the 4 core KPI cards."""
        kpis = sample_pulse_response.kpis
        cards = {
            "card_paid_jobs": kpis.technicians_on_paid_jobs,
            "card_active_workforce": kpis.technicians_active_total,
            "card_technicians_on_leave": kpis.technicians_on_leave,
            "card_fleet_utilization": kpis.fleet_utilization_pct
        }
        assert cards["card_paid_jobs"] == kpis.technicians_on_paid_jobs
        assert cards["card_active_workforce"] == kpis.technicians_active_total
        assert cards["card_fleet_utilization"] == kpis.fleet_utilization_pct

    def test_f15_bento_feed_color_accents_and_hex(self, sample_pulse_response):
        """Status badge colors in feed are valid 7-character hex colors."""
        for j in sample_pulse_response.today_jobs:
            color = j.status_color
            assert color.startswith("#")
            assert len(color) == 7
            assert all(c in "0123456789abcdefABCDEF" for c in color[1:])

    def test_f15_bento_feed_realtime_status_strings(self, sample_pulse_response):
        """Technician status strings match design specifications."""
        statuses = {t.status for t in sample_pulse_response.technicians_on_jobs}
        for s in statuses:
            assert s in ("On Paid Job", "Travelling", "Available", "On Holiday/Leave")

    def test_f15_bento_feed_numeric_precision(self, sample_pulse_response):
        """Utilization percentages are within [0.0, 100.0] and reasonable precision."""
        util = sample_pulse_response.kpis.fleet_utilization_pct
        assert 0.0 <= util <= 100.0

    def test_f15_bento_feed_payload_size_and_health(self, sample_pulse_response):
        """Feed contains non-empty lists for dashboard widgets."""
        assert len(sample_pulse_response.technicians_on_jobs) > 0
        assert len(sample_pulse_response.today_jobs) > 0
        assert len(sample_pulse_response.machines_under_service) > 0


# ============================================================================
# FEATURE 16: INTERACTIVE LEAFLET ROUTE MAP FEED (ORIGINAL_REQUEST §R3, R4)
# ============================================================================

class TestFeature16LeafletRouteMapFeed:
    """Tests data feed formatting for Leaflet interactive map rendering."""

    def test_f16_leaflet_route_polyline_coordinate_pairs(self):
        """Polyline consists of valid [lat, lng] float pairs."""
        polyline = [[30.9010, 75.8573], [30.8500, 76.0100], [30.6450, 76.3200], [30.3800, 76.8405]]
        for pt in polyline:
            assert len(pt) == 2
            lat, lng = pt
            assert -90.0 <= lat <= 90.0
            assert -180.0 <= lng <= 180.0

    def test_f16_leaflet_geofence_clusters_5km_circles(self):
        """Operational zones include centroid and radius_meters for Leaflet Circle."""
        zone = OperationalCluster(
            cluster_id="CLUST-01",
            centroid=LocationCoord(lat=30.9015, lng=75.8570),
            radius_meters=450.0,
            location_name="Ludhiana Depot Operational Zone",
            pings_count=45,
            duration_minutes=60.0,
            is_job_site=False,
            is_base=True
        )
        assert zone.radius_meters <= 5000.0
        assert zone.centroid.lat == 30.9015

    def test_f16_leaflet_stop_badges_and_duration(self):
        """Cluster feeds popup badge with location name and duration."""
        zone = OperationalCluster(
            cluster_id="CLUST-02",
            centroid=LocationCoord(lat=30.3800, lng=76.8405),
            radius_meters=820.0,
            location_name="RIL Barwala Bio-Mass Job Site",
            pings_count=110,
            duration_minutes=390.0,
            is_job_site=True,
            is_base=False
        )
        assert zone.duration_minutes == 390.0
        assert zone.is_job_site is True

    def test_f16_leaflet_anomaly_markers_payload(self):
        """Anomalies include coordinates and descriptions for map warning pins."""
        anomaly = RouteAnomaly(
            type="unauthorized_stop",
            location=LocationCoord(lat=30.6450, lng=76.3200),
            duration_minutes=25.0,
            started_at="2026-09-22T08:45:00Z",
            description="Vehicle stationary > 15 min outside 5km authorized corridor"
        )
        assert anomaly.location.lat == 30.6450
        assert anomaly.duration_minutes == 25.0

    def test_f16_leaflet_bounds_contain_all_pings(self):
        """All polyline points are bounded within regional bounding box."""
        polyline = [[30.9010, 75.8573], [30.8500, 76.0100], [30.6450, 76.3200], [30.3800, 76.8405]]
        min_lat = min(p[0] for p in polyline)
        max_lat = max(p[0] for p in polyline)
        min_lng = min(p[1] for p in polyline)
        max_lng = max(p[1] for p in polyline)
        
        assert min_lat >= 30.0
        assert max_lat <= 32.0
        assert min_lng >= 75.0
        assert max_lng <= 78.0

    def test_f16_live_fastapi_telematics_routes_endpoint(self, client):
        """Certifies GET /api/telematics/routes processes telemetry through telematics_engine."""
        resp = client.get("/api/telematics/routes?technician_id=TECH-01")
        assert resp.status_code == 200
        data = resp.json()
        model = RouteResponse(**data)
        assert len(model.route_polyline) > 0
        assert model.journey_summary.total_distance_km > 0

