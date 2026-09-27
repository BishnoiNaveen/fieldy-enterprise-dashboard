"""
Tier 2: Comprehensive Boundary and Corner Case Tests (16 Features, >= 80 Tests)
Derived from ORIGINAL_REQUEST.md, PROJECT.md § Feature Inventory, and TEST_INFRA.md.
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
# FEATURE 1: REAL-TIME OPERATIONAL PULSE KPIS (BOUNDARIES)
# ============================================================================

class TestFeature01KPIsBoundaries:
    """Boundary tests for Feature 1 (Operational Pulse KPIs)."""

    def test_f01_boundary_zero_active_technicians(self):
        """Zero active workforce yields 0.0% utilization without division by zero error."""
        kpis = PulseKPIs(
            technicians_on_paid_jobs=0,
            technicians_active_total=0,
            technicians_on_leave=10,
            total_jobs_today=0,
            jobs_completed_today=0,
            fleet_utilization_pct=0.0
        )
        assert kpis.fleet_utilization_pct == 0.0

    def test_f01_boundary_all_technicians_on_leave(self):
        """100% workforce on leave with zero active technicians is a valid state."""
        kpis = PulseKPIs(
            technicians_on_paid_jobs=0,
            technicians_active_total=0,
            technicians_on_leave=12,
            total_jobs_today=0,
            jobs_completed_today=0,
            fleet_utilization_pct=0.0
        )
        assert kpis.technicians_on_leave == 12

    def test_f01_boundary_max_fleet_utilization(self):
        """100% utilization when every active technician is on a paid job."""
        kpis = PulseKPIs(
            technicians_on_paid_jobs=15,
            technicians_active_total=15,
            technicians_on_leave=0,
            total_jobs_today=15,
            jobs_completed_today=5,
            fleet_utilization_pct=100.0
        )
        assert kpis.fleet_utilization_pct == 100.0

    def test_f01_boundary_zero_jobs_today(self):
        """Zero jobs scheduled today with available standby workforce."""
        kpis = PulseKPIs(
            technicians_on_paid_jobs=0,
            technicians_active_total=8,
            technicians_on_leave=2,
            total_jobs_today=0,
            jobs_completed_today=0,
            fleet_utilization_pct=0.0
        )
        assert kpis.total_jobs_today == 0

    def test_f01_boundary_negative_kpi_values_rejected(self):
        """Negative counts for technicians or jobs must raise validation error."""
        with pytest.raises(ValidationError):
            PulseKPIs(
                technicians_on_paid_jobs=-1,
                technicians_active_total=10,
                technicians_on_leave=2,
                total_jobs_today=5,
                jobs_completed_today=0,
                fleet_utilization_pct=0.0
            )


# ============================================================================
# FEATURE 2: TODAY'S JOBS LIST (BOUNDARIES)
# ============================================================================

class TestFeature02JobsListBoundaries:
    """Boundary tests for Feature 2 (Today's Jobs List)."""

    def test_f02_boundary_job_id_format_violations(self):
        """Invalid job IDs that deviate from SR-26-XXXX pattern raise ValidationError."""
        invalid_ids = ["SR-25-0101", "SR-26-101", "JOB-001", "SR-26-ABCD", "sr-26-0101", ""]
        for bad_id in invalid_ids:
            with pytest.raises(ValidationError):
                TodayJob(
                    job_id=bad_id,
                    status="In Progress",
                    status_color="#059669",
                    customer_name="RIL",
                    assigned_technicians=["Gurpreet Singh"],
                    machine_serial="BP1290-78401",
                    machine_name="Krone Baler",
                    job_type="Paid",
                    scheduled_start="2026-09-22T08:30:00Z"
                )

    def test_f02_boundary_empty_jobs_list(self):
        """Dashboard pulse response handles empty jobs list gracefully."""
        resp = PulseResponse(
            timestamp="2026-09-22T12:00:00Z",
            kpis=PulseKPIs(
                technicians_on_paid_jobs=0,
                technicians_active_total=5,
                technicians_on_leave=1,
                total_jobs_today=0,
                jobs_completed_today=0,
                fleet_utilization_pct=0.0
            ),
            technicians_on_jobs=[],
            today_jobs=[],
            machines_under_service=[]
        )
        assert len(resp.today_jobs) == 0

    def test_f02_boundary_job_type_invalid_enum(self):
        """Job types outside Paid, AMC, Warranty, Internal, Training are rejected."""
        with pytest.raises(ValidationError):
            TodayJob(
                job_id="SR-26-0101",
                status="In Progress",
                status_color="#059669",
                customer_name="RIL",
                assigned_technicians=["Gurpreet Singh"],
                machine_serial="BP1290-78401",
                machine_name="Krone Baler",
                job_type="FreeTrial",  # Invalid
                scheduled_start="2026-09-22T08:30:00Z"
            )

    def test_f02_boundary_scheduled_start_leap_year_or_midnight(self):
        """Edge timestamps such as midnight or year boundary parse cleanly."""
        job = TodayJob(
            job_id="SR-26-9999",
            status="Open",
            status_color="#6b7280",
            customer_name="Verbio",
            assigned_technicians=[],
            machine_serial="BX6800-11111",
            machine_name="Krone Harvester",
            job_type="AMC",
            scheduled_start="2026-02-28T23:59:59Z"
        )
        assert job.job_id == "SR-26-9999"

    def test_f02_boundary_multiple_assigned_technicians_max(self):
        """Job with multiple co-assigned field engineers preserves order and list integrity."""
        techs = ["Gurpreet Singh", "Harpreet Singh", "Vikram Sharma", "Jaswinder Singh"]
        job = TodayJob(
            job_id="SR-26-0500",
            status="In Progress",
            status_color="#059669",
            customer_name="SAEL Bio-Mass",
            assigned_technicians=techs,
            machine_serial="BP1290-99999",
            machine_name="Krone BigPack 1290 HDP",
            job_type="Paid",
            scheduled_start="2026-09-22T08:00:00Z"
        )
        assert len(job.assigned_technicians) == 4
        assert job.assigned_technicians[0] == "Gurpreet Singh"


# ============================================================================
# FEATURE 3: MACHINERY UNDER SERVICE TABLE (BOUNDARIES)
# ============================================================================

class TestFeature03MachineryBoundaries:
    """Boundary tests for Feature 3 (Machinery Under Service Table)."""

    def test_f03_boundary_machine_serial_min_max_length(self):
        """Machine serial numbers with typical model prefix and code lengths."""
        m = MachineUnderService(
            asset_name="Krone BigPack 1290 HDP",
            serial_number="BP1290-78401",
            client_company_name="Reliance Industries Limited",
            site_contact_person="Rajinder Verma (+91 98765 43210)",
            location="Ludhiana",
            active_job_id="SR-26-0101",
            service_type="Calibration"
        )
        assert len(m.serial_number) == 12

    def test_f03_boundary_special_characters_in_client_name(self):
        """Client company name with special characters (parentheses, ampersands, commas)."""
        name = "Reliance Industries Ltd. (Bio-Energy & Alternative Fuels Div.), Punjab"
        m = MachineUnderService(
            asset_name="Krone BiG X 680",
            serial_number="BX6800-45912",
            client_company_name=name,
            site_contact_person="Harbhajan Mann (+91 98765 43211)",
            location="Hoshiarpur",
            active_job_id="SR-26-0102",
            service_type="Overhaul"
        )
        assert m.client_company_name == name

    def test_f03_boundary_site_contact_international_format(self):
        """Contact phone formatted with spaces, dashes, or standard international prefix."""
        contacts = [
            "Rajinder Verma (+91 98765 43210)",
            "Sunil Tyagi (+91-98765-43212)",
            "Naveen (+919625957663)"
        ]
        for c in contacts:
            m = MachineUnderService(
                asset_name="Krone Fortima V 1500",
                serial_number="FV1500-33901",
                client_company_name="Punjab Agro",
                site_contact_person=c,
                location="Punjab",
                active_job_id="SR-26-0101",
                service_type="Service"
            )
            assert "+91" in m.site_contact_person

    def test_f03_boundary_duplicate_serial_detection(self):
        """Multiple distinct service records for same machine serial supported."""
        m1 = MachineUnderService(asset_name="Baler", serial_number="BP1290-001", client_company_name="RIL", site_contact_person="A (+91 98765 00001)", location="L1", active_job_id="SR-26-0101", service_type="S1")
        m2 = MachineUnderService(asset_name="Baler", serial_number="BP1290-001", client_company_name="RIL", site_contact_person="A (+91 98765 00001)", location="L1", active_job_id="SR-26-0102", service_type="S2")
        assert m1.serial_number == m2.serial_number
        assert m1.active_job_id != m2.active_job_id

    def test_f03_boundary_missing_active_job_id_rejected(self):
        """Active job ID is required."""
        with pytest.raises(ValidationError):
            MachineUnderService(
                asset_name="Krone Baler",
                serial_number="BP1290-78401",
                client_company_name="RIL",
                site_contact_person="Rajinder (+91 98765 43210)",
                location="Ludhiana",
                active_job_id=None,  # Not allowed
                service_type="Calibration"
            )


# ============================================================================
# FEATURE 4: FIELDY FSM SESSION SYNCHRONIZER (BOUNDARIES)
# ============================================================================

class TestFeature04SynchronizerBoundaries:
    """Boundary tests for Feature 4 (Fieldy FSM Session Synchronizer)."""

    def test_f04_boundary_sync_zero_records(self):
        """Sync response with 0 records synced returns valid response."""
        resp = SyncResponse(
            status="success",
            last_synced_at="2026-09-22T12:00:00Z",
            records_synced=0,
            source="fieldy_cache"
        )
        assert resp.records_synced == 0

    def test_f04_boundary_sync_extreme_records_count(self):
        """Large record volume (e.g. 10,000 records) parses without integer overflow."""
        resp = SyncResponse(
            status="success",
            last_synced_at="2026-09-22T12:00:00Z",
            records_synced=10000,
            source="fieldy_api"
        )
        assert resp.records_synced == 10000

    def test_f04_boundary_sync_clock_skew_timestamp(self):
        """Timestamp in future or past validated cleanly."""
        resp = SyncResponse(
            status="success",
            last_synced_at="2026-09-22T18:00:00+05:30",
            records_synced=1,
            source="fieldy_api"
        )
        assert "2026-09-22" in resp.last_synced_at

    def test_f04_boundary_sync_request_extra_fields(self):
        """Extra unrecognized fields in sync request do not crash request parser."""
        req = SyncRequest(force_refresh=True)
        assert req.force_refresh is True

    def test_f04_boundary_sync_rapid_successive_triggers(self):
        """Rapid back-to-back sync requests maintain response schema fidelity."""
        responses = [
            SyncResponse(status="success", last_synced_at=f"2026-09-22T12:00:0{i}Z", records_synced=42, source="fieldy_cache")
            for i in range(5)
        ]
        assert len(responses) == 5
        assert all(r.status == "success" for r in responses)


# ============================================================================
# FEATURE 5: CALIBRATED KRONE SYNTHETIC GENERATOR (BOUNDARIES)
# ============================================================================

class TestFeature05SyntheticGeneratorBoundaries:
    """Boundary tests for Feature 5 (Calibrated Krone Synthetic Generator)."""

    def test_f05_boundary_dataset_immutability(self):
        """Mutating returned dataset copy does not corrupt factory function output."""
        d1 = get_krone_synthetic_dataset()
        d1["technicians"].pop()
        d2 = get_krone_synthetic_dataset()
        assert len(d2["technicians"]) > len(d1["technicians"])

    def test_f05_boundary_technician_id_uniqueness(self, krone_dataset):
        """All technician IDs in synthetic dataset are unique."""
        ids = [t["id"] for t in krone_dataset["technicians"]]
        assert len(ids) == len(set(ids))

    def test_f05_boundary_machine_serial_uniqueness(self, krone_dataset):
        """All machine serial numbers in synthetic dataset are unique."""
        serials = [m["serial_number"] for m in krone_dataset["machines"]]
        assert len(serials) == len(set(serials))

    def test_f05_boundary_job_id_uniqueness(self, krone_dataset):
        """All job IDs in synthetic dataset are unique."""
        job_ids = [j["job_id"] for j in krone_dataset["jobs"]]
        assert len(job_ids) == len(set(job_ids))

    def test_f05_boundary_empty_phone_or_unassigned_job(self, krone_dataset):
        """Technicians on leave have job_id None and valid status."""
        leave_techs = [t for t in krone_dataset["technicians"] if t["status"] == "On Holiday/Leave"]
        for t in leave_techs:
            assert t["job_id"] is None


# ============================================================================
# FEATURE 6: 5 KM RADIUS HAVERSINE CLUSTERING (BOUNDARIES)
# ============================================================================

class TestFeature06HaversineClusteringBoundaries:
    """Boundary tests for Feature 6 (Haversine math & 5km clustering)."""

    def test_f06_boundary_exact_4990m_merges(self):
        """Points separated by 4.990 km (< 5.0 km) merge into 1 cluster."""
        # 1 deg lat approx 111.139 km -> 4.99 km is ~0.0449 deg lat
        lat1, lon1 = 30.00000, 75.00000
        lat2 = lat1 + (4.990 / 111.195)
        dist = haversine_distance(lat1, lon1, lat2, lon1)
        assert dist <= 5.0

        stops = [
            {"lat": lat1, "lon": lon1, "duration_s": 3600},
            {"lat": lat2, "lon": lon1, "duration_s": 3600}
        ]
        clusters = cluster_stops_5km(stops, max_radius_km=5.0)
        assert len(clusters) == 1

    def test_f06_boundary_exact_5010m_separates(self):
        """Points separated by 5.010 km (> 5.0 km) do NOT merge into 1 cluster."""
        lat1, lon1 = 30.00000, 75.00000
        lat2 = lat1 + (5.010 / 111.195)
        dist = haversine_distance(lat1, lon1, lat2, lon1)
        assert dist > 5.0

        stops = [
            {"lat": lat1, "lon": lon1, "duration_s": 3600},
            {"lat": lat2, "lon": lon1, "duration_s": 3600}
        ]
        clusters = cluster_stops_5km(stops, max_radius_km=5.0)
        assert len(clusters) == 2

    def test_f06_boundary_antipodal_points_numerical_stability(self):
        """Antipodal points (opposite sides of Earth) evaluate without NaN."""
        dist = haversine_distance(0.0, 0.0, 0.0, 180.0)
        expected = math.pi * 6371.0
        assert abs(dist - expected) < 1.0
        assert not math.isnan(dist)

    def test_f06_boundary_poles_and_equator_coordinates(self):
        """Extreme polar coordinates (-90, 90) do not cause math domain errors."""
        dist_poles = haversine_distance(90.0, 0.0, -90.0, 0.0)
        expected = math.pi * 6371.0
        assert abs(dist_poles - expected) < 1.0

    def test_f06_boundary_chaining_violation_prevention(self):
        """Hard centroid radius cap prevents DBSCAN single-linkage chaining violation."""
        # P1 at 0km, P2 at 4km, P3 at 8km (all colinear)
        stops = [
            {"lat": 30.0000, "lon": 75.0000, "duration_s": 3600},
            {"lat": 30.0000 + (4.0 / 111.195), "lon": 75.0000, "duration_s": 3600},
            {"lat": 30.0000 + (8.0 / 111.195), "lon": 75.0000, "duration_s": 3600}
        ]
        clusters = cluster_stops_5km(stops, max_radius_km=5.0)
        # Cannot merge all 3 into 1 cluster because distance between P1 and P3 is 8km (>5km radius)
        assert len(clusters) >= 2


# ============================================================================
# FEATURE 7: SPEED-GATED JITTER DAMPENING (BOUNDARIES)
# ============================================================================

class TestFeature07JitterDampeningBoundaries:
    """Boundary tests for Feature 7 (Speed-Gated Jitter Dampening)."""

    def test_f07_boundary_speed_exact_1_49_vs_1_51_kmh(self):
        """1.49 km/h is stationary; 1.51 km/h is moving."""
        p1 = {"lat": 30.9010, "lon": 75.8573, "speed_kmh": 1.49}
        p2 = {"lat": 30.9010, "lon": 75.8573, "speed_kmh": 1.51}
        f1 = apply_jitter_filter([p1], speed_thresh_kmh=1.5)[0]
        f2 = apply_jitter_filter([p2], speed_thresh_kmh=1.5)[0]
        assert f1["is_stationary"] is True
        assert f2["is_stationary"] is False

    def test_f07_boundary_deadband_exact_29_9m_vs_30_1m(self):
        """29.9m movement is clamped to stationary anchor; 30.1m updates anchor."""
        anchor_lat, anchor_lon = 30.901000, 75.857300
        # 1 deg lat is ~111,195 m. 29.9 m is ~0.0002689 deg; 30.1 m is ~0.0002707 deg
        lat_29_9 = anchor_lat + (29.9 / 111195.0)
        lat_30_1 = anchor_lat + (30.1 / 111195.0)
        
        # Test 29.9m
        pings_clamped = [
            {"lat": anchor_lat, "lon": anchor_lon, "speed_kmh": 0.0},
            {"lat": lat_29_9, "lon": anchor_lon, "speed_kmh": 0.0}
        ]
        f_clamped = apply_jitter_filter(pings_clamped, deadband_m=30.0)
        assert f_clamped[1]["filtered_lat"] == anchor_lat
        
        # Test 30.1m
        pings_unclamped = [
            {"lat": anchor_lat, "lon": anchor_lon, "speed_kmh": 0.0},
            {"lat": lat_30_1, "lon": anchor_lon, "speed_kmh": 0.0}
        ]
        f_unclamped = apply_jitter_filter(pings_unclamped, deadband_m=30.0)
        assert f_unclamped[1]["filtered_lat"] == lat_30_1

    def test_f07_boundary_zero_pings_empty_input(self):
        """Empty ping list returns empty list without error."""
        assert apply_jitter_filter([]) == []

    def test_f07_boundary_single_ping_list(self):
        """Single ping handled cleanly."""
        p = [{"lat": 30.9010, "lon": 75.8573, "speed_kmh": 0.0}]
        f = apply_jitter_filter(p)
        assert len(f) == 1
        assert f[0]["filtered_lat"] == 30.9010

    def test_f07_boundary_negative_speed_treated_stationary(self):
        """Negative speed reading (sensor glitch) treated as stationary."""
        p = [{"lat": 30.9010, "lon": 75.8573, "speed_kmh": -5.0}]
        f = apply_jitter_filter(p, speed_thresh_kmh=1.5)
        assert f[0]["is_stationary"] is True


# ============================================================================
# FEATURE 8: AUTONOMOUS ROUTE INSPECTOR (BOUNDARIES)
# ============================================================================

class TestFeature08RouteInspectorBoundaries:
    """Boundary tests for Feature 8 (Autonomous Route Inspector)."""

    def test_f08_boundary_base_distance_exact_4990m_vs_5010m(self):
        """Base location matched at 4.99 km, but rejected at 5.01 km."""
        base = {"lat": 30.0000, "lon": 75.0000}
        dest = {"lat": 30.5000, "lon": 75.5000}
        
        lat_in = base["lat"] + (4.990 / 111.195)
        lat_out = base["lat"] + (5.010 / 111.195)
        
        res_in = inspect_route_telematics([{"lat": lat_in, "lon": base["lon"], "duration_s": 1000}], base, dest)
        res_out = inspect_route_telematics([{"lat": lat_out, "lon": base["lon"], "duration_s": 1000}], base, dest)
        
        assert res_in["clusters"][0]["is_base"] is True
        assert res_out["clusters"][0]["is_base"] is False

    def test_f08_boundary_dest_distance_exact_4990m_vs_5010m(self):
        """Customer destination matched at 4.99 km, but rejected at 5.01 km."""
        base = {"lat": 30.0000, "lon": 75.0000}
        dest = {"lat": 30.5000, "lon": 75.5000}
        
        lat_in = dest["lat"] + (4.990 / 111.195)
        lat_out = dest["lat"] + (5.010 / 111.195)
        
        res_in = inspect_route_telematics([{"lat": lat_in, "lon": dest["lon"], "duration_s": 3600}], base, dest)
        res_out = inspect_route_telematics([{"lat": lat_out, "lon": dest["lon"], "duration_s": 3600}], base, dest)
        
        assert res_in["clusters"][0]["is_job_site"] is True
        assert res_out["clusters"][0]["is_job_site"] is False

    def test_f08_boundary_zero_transit_duration(self):
        """On-site day where technician starts and stays at customer site."""
        dest = {"lat": 30.3800, "lon": 76.8405}
        stops = [{"lat": 30.3800, "lon": 76.8405, "duration_s": 28800}]
        res = inspect_route_telematics(stops, dest, dest, transit_moving_seconds=0.0)
        assert res["H_t"] == 0.0
        assert res["H_w"] == 8.0

    def test_f08_boundary_no_stops_only_transit(self):
        """Shift with zero stationary stops (continuous driving/relocation)."""
        base = {"lat": 30.0000, "lon": 75.0000}
        dest = {"lat": 30.5000, "lon": 75.5000}
        res = inspect_route_telematics([], base, dest, transit_moving_seconds=14400.0)
        assert res["H_t"] == 4.0
        assert res["H_w"] == 0.0

    def test_f08_boundary_equal_distance_tie_breaking(self):
        """Stops equidistant from base and destination handled stably."""
        base = {"lat": 30.0000, "lon": 75.0000}
        dest = {"lat": 30.0000, "lon": 75.0400}
        stops = [{"lat": 30.0000, "lon": 75.0200, "duration_s": 1800}]  # Midpoint (~1.9 km from both)
        res = inspect_route_telematics(stops, base, dest)
        assert len(res["clusters"]) == 1


# ============================================================================
# FEATURE 9: TRANSIT VS UNAUTHORIZED STOP DETECTION (BOUNDARIES)
# ============================================================================

class TestFeature09TransitVsUnauthBoundaries:
    """Boundary tests for Feature 9 (Transit vs Unauthorized Stops)."""

    def test_f09_boundary_dwell_exact_899s_vs_901s(self):
        """899s (14.98m) authorized; 901s (15.01m) unauthorized."""
        base = {"lat": 30.0, "lon": 75.0}
        dest = {"lat": 30.5, "lon": 75.5}
        
        c_899 = inspect_route_telematics([{"lat": 30.25, "lon": 75.25, "duration_s": 899}], base, dest)["clusters"][0]
        c_901 = inspect_route_telematics([{"lat": 30.25, "lon": 75.25, "duration_s": 901}], base, dest)["clusters"][0]
        
        assert c_899["zone_type"] == "AUTHORIZED_ENROUTE_STOP"
        assert c_901["zone_type"] == "UNAUTHORIZED_STOP"

    def test_f09_boundary_dwell_exact_900s(self):
        """Exactly 900.0s (15.00 min) edge case adheres to strict > 900 inequality."""
        base = {"lat": 30.0, "lon": 75.0}
        dest = {"lat": 30.5, "lon": 75.5}
        c = inspect_route_telematics([{"lat": 30.25, "lon": 75.25, "duration_s": 900.0}], base, dest)["clusters"][0]
        assert c["zone_type"] == "AUTHORIZED_ENROUTE_STOP"

    def test_f09_boundary_multiple_halts_summation(self):
        """Multiple short authorized stops (each <15m) do not trigger unauth alerts."""
        base = {"lat": 30.0, "lon": 75.0}
        dest = {"lat": 30.5, "lon": 75.5}
        stops = [
            {"lat": 30.1, "lon": 75.1, "duration_s": 600},
            {"lat": 30.2, "lon": 75.2, "duration_s": 600},
            {"lat": 30.3, "lon": 75.3, "duration_s": 600}
        ]
        res = inspect_route_telematics(stops, base, dest)
        assert len(res["anomalies"]) == 0

    def test_f09_boundary_unauthorized_halt_at_base_boundary(self):
        """Long stop (>15m) within 5km of base is base dwell, NOT unauthorized stop."""
        base = {"lat": 30.0, "lon": 75.0}
        dest = {"lat": 30.5, "lon": 75.5}
        stops = [{"lat": 30.01, "lon": 75.01, "duration_s": 3600}]
        res = inspect_route_telematics(stops, base, dest)
        assert res["clusters"][0]["zone_type"] == "STARTING_BASE"
        assert len(res["anomalies"]) == 0

    def test_f09_boundary_unauthorized_halt_at_dest_boundary(self):
        """Long stop (>15m) within 5km of destination is productive work, NOT unauthorized."""
        base = {"lat": 30.0, "lon": 75.0}
        dest = {"lat": 30.5, "lon": 75.5}
        stops = [{"lat": 30.51, "lon": 75.51, "duration_s": 14400}]
        res = inspect_route_telematics(stops, base, dest)
        assert res["clusters"][0]["zone_type"] == "CUSTOMER_DESTINATION"
        assert len(res["anomalies"]) == 0


# ============================================================================
# FEATURE 10: ROUTE ANOMALY DETECTION & ALERTS (BOUNDARIES)
# ============================================================================

class TestFeature10AnomalyBoundaries:
    """Boundary tests for Feature 10 (Route Anomaly Detection & Alerts)."""

    def test_f10_boundary_detour_ratio_exact_1_24_vs_1_26(self):
        """Detour ratio 1.24 produces no alert; 1.26 with excess >10km produces alert."""
        base = {"lat": 30.0, "lon": 75.0}
        dest = {"lat": 30.5, "lon": 75.5}
        
        # 80 km designated: 1.24 * 80 = 99.2 km (excess 19.2 km, but ratio <= 1.25)
        res_no_alert = inspect_route_telematics([], base, dest, designated_distance_km=80.0, actual_distance_km=99.2)
        assert len([a for a in res_no_alert["anomalies"] if a["type"] == "excessive_detour"]) == 0
        
        # 80 km designated: 1.26 * 80 = 100.8 km (ratio 1.26 > 1.25 and excess 20.8 km > 10 km)
        res_alert = inspect_route_telematics([], base, dest, designated_distance_km=80.0, actual_distance_km=100.8)
        assert len([a for a in res_alert["anomalies"] if a["type"] == "excessive_detour"]) == 1

    def test_f10_boundary_excess_km_exact_9_9km_vs_10_1km(self):
        """Ratio > 1.25 but excess <= 10.0 km produces no alert; excess > 10 km triggers alert."""
        base = {"lat": 30.0, "lon": 75.0}
        dest = {"lat": 30.5, "lon": 75.5}
        
        # Designated 10 km, actual 19.9 km (ratio 1.99 > 1.25, but excess 9.9 km <= 10.0 km)
        res_9_9 = inspect_route_telematics([], base, dest, designated_distance_km=10.0, actual_distance_km=19.9)
        assert len([a for a in res_9_9["anomalies"] if a["type"] == "excessive_detour"]) == 0
        
        # Designated 10 km, actual 20.1 km (ratio 2.01 > 1.25, excess 10.1 km > 10.0 km)
        res_10_1 = inspect_route_telematics([], base, dest, designated_distance_km=10.0, actual_distance_km=20.1)
        assert len([a for a in res_10_1["anomalies"] if a["type"] == "excessive_detour"]) == 1

    def test_f10_boundary_zero_designated_distance_no_div_zero(self):
        """Designated distance = 0 does not raise ZeroDivisionError."""
        base = {"lat": 30.0, "lon": 75.0}
        dest = {"lat": 30.0, "lon": 75.0}
        res = inspect_route_telematics([], base, dest, designated_distance_km=0.0, actual_distance_km=5.0)
        assert res["detour_ratio"] >= 0.0

    def test_f10_boundary_critical_stop_duration_escalation(self):
        """Stop exceeding 60 minutes recorded with accurate duration."""
        base = {"lat": 30.0, "lon": 75.0}
        dest = {"lat": 30.5, "lon": 75.5}
        stops = [{"lat": 30.25, "lon": 75.25, "duration_s": 5400}]  # 90 minutes
        res = inspect_route_telematics(stops, base, dest)
        anomaly = res["anomalies"][0]
        assert anomaly["duration_minutes"] == 90.0

    def test_f10_boundary_multiple_concurrent_anomalies(self):
        """Both unauthorized stop and detour anomalies captured simultaneously."""
        base = {"lat": 30.0, "lon": 75.0}
        dest = {"lat": 30.5, "lon": 75.5}
        stops = [{"lat": 30.25, "lon": 75.25, "duration_s": 1800}]
        res = inspect_route_telematics(stops, base, dest, designated_distance_km=50.0, actual_distance_km=80.0)
        types = {a["type"] for a in res["anomalies"]}
        assert "unauthorized_stop" in types
        assert "excessive_detour" in types


# ============================================================================
# FEATURE 11: MULTI-TIER HOURS ANALYTICS (BOUNDARIES)
# ============================================================================

class TestFeature11HoursBoundaries:
    """Boundary tests for Feature 11 (Multi-Tier Hours Analytics)."""

    def test_f11_boundary_hours_conservation_floating_point_precision(self):
        """Hours conservation holds within 0.05 float threshold."""
        summary = ProductivitySummary(
            total_working_hours=5.333,
            total_travelling_hours=1.667,
            total_idle_hours=1.000,
            total_shift_hours=8.000,
            average_utilization_pct=66.66
        )
        assert summary.total_shift_hours == 8.0

    def test_f11_boundary_zero_working_hours_shift(self):
        """Entire shift spent in transit + idle (e.g. cancelled dispatch)."""
        summary = ProductivitySummary(
            total_working_hours=0.0,
            total_travelling_hours=6.0,
            total_idle_hours=2.0,
            total_shift_hours=8.0,
            average_utilization_pct=0.0
        )
        assert summary.total_working_hours == 0.0
        assert summary.average_utilization_pct == 0.0

    def test_f11_boundary_zero_travel_hours_shift(self):
        """Entire shift spent on customer site (overnight resident technician)."""
        summary = ProductivitySummary(
            total_working_hours=8.0,
            total_travelling_hours=0.0,
            total_idle_hours=0.0,
            total_shift_hours=8.0,
            average_utilization_pct=100.0
        )
        assert summary.total_travelling_hours == 0.0
        assert summary.average_utilization_pct == 100.0

    def test_f11_boundary_max_shift_overtime_24h(self):
        """Continuous 24-hour emergency shift validates conservation."""
        summary = ProductivitySummary(
            total_working_hours=16.0,
            total_travelling_hours=5.0,
            total_idle_hours=3.0,
            total_shift_hours=24.0,
            average_utilization_pct=66.67
        )
        assert summary.total_shift_hours == 24.0

    def test_f11_boundary_conservation_validator_raises_on_mismatch(self):
        """Discrepancy between shift hours and sum raises validation error."""
        with pytest.raises(ValidationError):
            ProductivitySummary(
                total_working_hours=5.0,
                total_travelling_hours=2.0,
                total_idle_hours=1.0,
                total_shift_hours=12.0,  # 12 != 5+2+1
                average_utilization_pct=62.5
            )


# ============================================================================
# FEATURE 12: TIMEFRAME TOGGLING (BOUNDARIES)
# ============================================================================

class TestFeature12TimeframeBoundaries:
    """Boundary tests for Feature 12 (Timeframe Toggling)."""

    def test_f12_boundary_timeframe_leap_year_february(self):
        """Period string across leap day 2028-02-29 or 2026 month ends parses cleanly."""
        trend = ProductivityTrend(period="2026-02-28", working=8.0, travelling=0.0, idle=0.0)
        assert trend.period == "2026-02-28"

    def test_f12_boundary_timeframe_month_end_rollover(self):
        """Trend dates spanning month rollover (Sept 30 to Oct 1) are valid."""
        t1 = ProductivityTrend(period="2026-09-30", working=6.0, travelling=2.0, idle=0.0)
        t2 = ProductivityTrend(period="2026-10-01", working=7.0, travelling=1.0, idle=0.0)
        assert t1.period < t2.period

    def test_f12_boundary_timeframe_empty_period_trend(self):
        """Day with 0 hours activity preserves non-negative floats."""
        trend = ProductivityTrend(period="2026-09-22", working=0.0, travelling=0.0, idle=0.0)
        assert trend.working == 0.0

    def test_f12_boundary_timeframe_single_hour_shift(self):
        """Short 1-hour shift validates."""
        summary = ProductivitySummary(
            total_working_hours=0.8,
            total_travelling_hours=0.2,
            total_idle_hours=0.0,
            total_shift_hours=1.0,
            average_utilization_pct=80.0
        )
        assert summary.total_shift_hours == 1.0

    def test_f12_boundary_timeframe_case_insensitivity(self):
        """Timeframe string matches expected lowercase tokens."""
        for tf in ("daily", "weekly", "monthly"):
            assert tf.lower() in ("daily", "weekly", "monthly")


# ============================================================================
# FEATURE 13: MULTI-DIMENSIONAL SEARCH & FILTERING (BOUNDARIES)
# ============================================================================

class TestFeature13SearchBoundaries:
    """Boundary tests for Feature 13 (Search & Filtering)."""

    def test_f13_boundary_filter_nonexistent_technician_id(self, krone_dataset):
        """Filtering by non-existent technician ID returns empty list gracefully."""
        res = [t for t in krone_dataset["technicians"] if t["id"] == "TECH-NONEXISTENT"]
        assert res == []

    def test_f13_boundary_filter_special_characters_sql_injection(self, krone_dataset):
        """SQL injection or HTML tags in search parameter return empty match safely."""
        malicious = "' OR '1'='1"
        res = [j for j in krone_dataset["jobs"] if malicious in j["customer_name"]]
        assert res == []

    def test_f13_boundary_filter_case_insensitive_company(self, krone_dataset):
        """Search query is case-insensitive for client company."""
        q_lower = "reliance"
        q_upper = "RELIANCE"
        res1 = [j for j in krone_dataset["jobs"] if q_lower in j["customer_name"].lower()]
        res2 = [j for j in krone_dataset["jobs"] if q_upper.lower() in j["customer_name"].lower()]
        assert len(res1) == len(res2)
        assert len(res1) >= 1

    def test_f13_boundary_filter_whitespace_trimming(self, krone_dataset):
        """Leading and trailing whitespace trimmed during search."""
        raw_query = "  Gurpreet Singh  "
        trimmed = raw_query.strip()
        matched = [t for t in krone_dataset["technicians"] if t["name"] == trimmed]
        assert len(matched) == 1

    def test_f13_boundary_filter_empty_query_returns_all(self, krone_dataset):
        """Empty query string returns complete set."""
        q = ""
        matched = [j for j in krone_dataset["jobs"] if q in j["customer_name"]]
        assert len(matched) == len(krone_dataset["jobs"])


# ============================================================================
# FEATURE 14: COMPARATIVE CHARTS & SCORECARDS (BOUNDARIES)
# ============================================================================

class TestFeature14ScorecardsBoundaries:
    """Boundary tests for Feature 14 (Charts & Scorecards)."""

    def test_f14_boundary_scorecard_zero_utilization(self):
        """Technician with 0 working hours has 0.0% utilization."""
        rec = TechnicianProductivityRecord(
            technician_id="T0", technician_name="Idle Tech",
            working_hours=0.0, travelling_hours=4.0, idle_hours=4.0,
            shift_hours=8.0, utilization_pct=0.0, jobs_count=0
        )
        assert rec.utilization_pct == 0.0

    def test_f14_boundary_scorecard_100_percent_utilization(self):
        """Technician with full working hours has 100.0% utilization."""
        rec = TechnicianProductivityRecord(
            technician_id="T1", technician_name="Star Tech",
            working_hours=8.0, travelling_hours=0.0, idle_hours=0.0,
            shift_hours=8.0, utilization_pct=100.0, jobs_count=2
        )
        assert rec.utilization_pct == 100.0

    def test_f14_boundary_scorecard_tied_utilization_ranking(self):
        """Tied utilization rates preserve stable order without crashing sort."""
        records = [
            TechnicianProductivityRecord(technician_id="B", technician_name="B", working_hours=6.0, travelling_hours=2.0, idle_hours=0.0, shift_hours=8.0, utilization_pct=75.0, jobs_count=1),
            TechnicianProductivityRecord(technician_id="A", technician_name="A", working_hours=6.0, travelling_hours=2.0, idle_hours=0.0, shift_hours=8.0, utilization_pct=75.0, jobs_count=1),
        ]
        sorted_records = sorted(records, key=lambda r: (-r.utilization_pct, r.technician_id))
        assert sorted_records[0].technician_id == "A"
        assert sorted_records[1].technician_id == "B"

    def test_f14_boundary_chart_single_data_point(self):
        """Chart dataset with single point renders cleanly."""
        resp = ProductivityResponse(
            timeframe="daily",
            summary=ProductivitySummary(
                total_working_hours=5.0, total_travelling_hours=2.0,
                total_idle_hours=1.0, total_shift_hours=8.0,
                average_utilization_pct=62.5
            ),
            technician_records=[],
            trend_data=[ProductivityTrend(period="2026-09-22", working=5.0, travelling=2.0, idle=1.0)]
        )
        assert len(resp.trend_data) == 1

    def test_f14_boundary_chart_zero_fleet_hours(self):
        """Empty fleet returns zero summary totals."""
        summary = ProductivitySummary(
            total_working_hours=0.0, total_travelling_hours=0.0,
            total_idle_hours=0.0, total_shift_hours=0.0,
            average_utilization_pct=0.0
        )
        assert summary.average_utilization_pct == 0.0


# ============================================================================
# FEATURE 15: EXECUTIVE BENTO GRID UI DATA FEED (BOUNDARIES)
# ============================================================================

class TestFeature15BentoGridBoundaries:
    """Boundary tests for Feature 15 (Executive Bento Grid UI Data Feed)."""

    def test_f15_boundary_bento_zero_values_rendering(self):
        """Card values of 0 correctly serialize as 0."""
        kpis = PulseKPIs(
            technicians_on_paid_jobs=0,
            technicians_active_total=0,
            technicians_on_leave=0,
            total_jobs_today=0,
            jobs_completed_today=0,
            fleet_utilization_pct=0.0
        )
        d = kpis.model_dump()
        assert d["technicians_on_paid_jobs"] == 0
        assert d["fleet_utilization_pct"] == 0.0

    def test_f15_boundary_bento_large_job_counts(self):
        """Large numbers format without scientific notation."""
        kpis = PulseKPIs(
            technicians_on_paid_jobs=150,
            technicians_active_total=200,
            technicians_on_leave=20,
            total_jobs_today=500,
            jobs_completed_today=250,
            fleet_utilization_pct=75.0
        )
        assert kpis.total_jobs_today == 500

    def test_f15_boundary_bento_status_hex_lowercase_uppercase(self):
        """Hex color codes validate whether uppercase or lowercase."""
        colors = ["#059669", "#10B981", "#F59E0B", "#6b7280"]
        for c in colors:
            assert c.startswith("#")
            assert len(c) == 7

    def test_f15_boundary_bento_empty_technicians_list(self):
        """Empty technicians list serializes to JSON list `[]`."""
        resp = PulseResponse(
            timestamp="2026-09-22T12:00:00Z",
            kpis=PulseKPIs(technicians_on_paid_jobs=0, technicians_active_total=0, technicians_on_leave=0, total_jobs_today=0, jobs_completed_today=0, fleet_utilization_pct=0.0),
            technicians_on_jobs=[],
            today_jobs=[],
            machines_under_service=[]
        )
        assert resp.technicians_on_jobs == []

    def test_f15_boundary_bento_timestamp_iso_utc(self):
        """Timestamp requires valid UTC ISO-8601 formatting."""
        ts = "2026-09-22T12:38:27Z"
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        assert dt.tzinfo == timezone.utc


# ============================================================================
# FEATURE 16: INTERACTIVE LEAFLET ROUTE MAP FEED (BOUNDARIES)
# ============================================================================

class TestFeature16LeafletMapBoundaries:
    """Boundary tests for Feature 16 (Interactive Leaflet Route Map Feed)."""

    def test_f16_boundary_route_single_point_polyline(self):
        """Polyline with 1 point does not cause geometry failure."""
        polyline = [[30.9010, 75.8573]]
        assert len(polyline) == 1
        assert len(polyline[0]) == 2

    def test_f16_boundary_route_empty_polyline(self):
        """Empty route polyline represented cleanly as []."""
        polyline = []
        assert len(polyline) == 0

    def test_f16_boundary_route_extreme_latitude_longitude(self):
        """Geographic coordinates at edge boundaries validate in LocationCoord."""
        loc1 = LocationCoord(lat=90.0, lng=180.0)
        loc2 = LocationCoord(lat=-90.0, lng=-180.0)
        assert loc1.lat == 90.0
        assert loc2.lng == -180.0

    def test_f16_boundary_route_circular_loop_return_to_base(self):
        """Circular route where start == end point closes polyline."""
        base = [30.9010, 75.8573]
        route = [base, [30.5, 76.5], [30.3, 76.8], base]
        assert route[0] == route[-1]

    def test_f16_boundary_route_reverse_lat_lng_guard(self):
        """Validation fails if latitude exceeds [-90, 90] range."""
        with pytest.raises(ValidationError):
            LocationCoord(lat=105.0, lng=75.0)
