"""
Tier 4: Comprehensive Real-World Krone Agriculture India Scenarios
Derived from ORIGINAL_REQUEST.md, PROJECT.md § Feature Inventory, and TEST_INFRA.md.
Executes 5 end-to-end multi-feature operational workflows.
"""

import math
from datetime import datetime, timedelta, timezone
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


class TestTier4RealWorldScenarios:
    """End-to-End Real-World Krone Agriculture India Operational Workflows."""

    # ========================================================================
    # SCENARIO 1: RIL BARWALA EMERGENCY KNOTTER REPAIR
    # ========================================================================
    def test_scenario_1_ril_barwala_emergency_knotter_repair(self, krone_dataset):
        """
        Scenario 1: RIL Barwala Emergency Knotter Repair
        - Technician: Gurpreet Singh (TECH-001)
        - Machine: Krone BigPack 1290 HDP High Density Baler (Serial: BP1290-78401)
        - Customer: Reliance Industries Limited (Bio-Energy Division)
        - Job ID: SR-26-0101 (Emergency Knotter Timing Calibration)
        - Journey: Ludhiana Regional Depot (30.9010, 75.8573) to Barwala Plant (30.3800, 76.8405)
        - Exercised Features: F1 (Pulse), F2 (Jobs), F3 (Machinery), F6 (5km Clustering), F8 (Route Inspector), F9 (Transit vs Unauth), F11 (Hours Conservation)
        """
        # 1. Verify Job and Machine in Fieldy Catalog (F2, F3)
        job = next(j for j in krone_dataset["jobs"] if j["job_id"] == "SR-26-0101")
        machine = next(m for m in krone_dataset["machines"] if m["active_job_id"] == "SR-26-0101")
        
        assert job["assigned_technicians"] == ["Gurpreet Singh"]
        assert job["job_type"] == "Paid"
        assert machine["serial_number"] == "BP1290-78401"
        assert "BigPack 1290" in machine["asset_name"]
        assert "Rajinder Verma" in machine["site_contact_person"]

        # 2. Daily Telematics Stops Setup
        t0 = datetime(2026, 9, 22, 8, 0, 0, tzinfo=timezone.utc)
        base_loc = {"lat": 30.9010, "lon": 75.8573, "name": "Ludhiana Regional Hub"}
        dest_loc = {"lat": 30.3800, "lon": 76.8405, "name": "RIL Barwala Bio-Mass Facility"}
        
        stops = [
            # Depot prep: 20 mins (1200s)
            {"lat": 30.9010, "lon": 75.8573, "duration_s": 1200, "name": "Depot Tool Prep", "start_time": "08:00", "end_time": "08:20"},
            # Highway roadside dhaba halt: 25 mins (1500s) > 15 min threshold (~42 km away)
            {"lat": 30.6450, "lon": 76.3200, "duration_s": 1500, "name": "Highway Dhaba Stop", "start_time": "09:30", "end_time": "09:55"},
            # On-site knotter timing calibration at main workshop: 3.0 hrs (10800s)
            {"lat": 30.3800, "lon": 76.8405, "duration_s": 10800, "name": "Main Plant Workshop", "start_time": "10:45", "end_time": "13:45"},
            # Farm plot testing (1.5 km away from workshop): 2.5 hrs (9000s)
            {"lat": 30.3910, "lon": 76.8490, "duration_s": 9000, "name": "Plot 7 Knot Testing", "start_time": "13:51", "end_time": "16:21"},
            # Supervisor sign-off at site office: 25 mins (1500s)
            {"lat": 30.3805, "lon": 76.8408, "duration_s": 1500, "name": "Customer Sign-off", "start_time": "16:25", "end_time": "16:50"}
        ]
        
        # 3. Pure moving transit time: 70 min leg 1 + 50 min leg 2 + 6 min field transit = 126 min = 7560s
        transit_moving_s = 7560.0
        
        # 4. Route Inspector Execution (F6, F8, F9, F11)
        res = inspect_route_telematics(
            stops=stops,
            base_loc=base_loc,
            dest_loc=dest_loc,
            designated_distance_km=80.0,
            actual_distance_km=84.6,
            transit_moving_seconds=transit_moving_s
        )
        
        # 5. Verify 5 km Clustering Merged the 3 Customer Locations (F6)
        # Workshop, Plot 7, and Site Office are all within 1.5 km and must merge into 1 customer destination cluster!
        job_site_clusters = [c for c in res["clusters"] if c["zone_type"] == "CUSTOMER_DESTINATION"]
        assert len(job_site_clusters) == 1
        assert len(job_site_clusters[0]["stops"]) == 3
        assert job_site_clusters[0]["total_duration_s"] == 10800 + 9000 + 1500  # 21,300s = 5.917 hrs
        
        # 6. Verify Unauthorized Stop Detection (F9, F10)
        unauth_clusters = [c for c in res["clusters"] if c["zone_type"] == "UNAUTHORIZED_STOP"]
        assert len(unauth_clusters) == 1
        assert unauth_clusters[0]["total_duration_s"] == 1500
        assert len(res["anomalies"]) == 1
        assert res["anomalies"][0]["type"] == "unauthorized_stop"
        assert res["anomalies"][0]["duration_minutes"] == 25.0
        
        # 7. Verify Multi-Tier Hours Analytics & Conservation (F11)
        # H_w: 21300 / 3600 = 5.92 hrs
        # H_t: 7560 / 3600 = 2.10 hrs
        # H_i: (1500 + 1200) / 3600 = 0.75 hrs (25m unauth + 20m depot prep)
        # H_shift = 5.92 + 2.10 + 0.75 = 8.77 hrs
        assert res["H_w"] == 5.92
        assert res["H_t"] == 2.10
        assert res["H_i"] == 0.75
        assert res["H_shift"] == 8.77
        
        # 8. Verify Pulse Response Integration (F1)
        pulse = PulseResponse(
            timestamp=datetime.now(timezone.utc).isoformat(),
            kpis=PulseKPIs(
                technicians_on_paid_jobs=1,
                technicians_active_total=1,
                technicians_on_leave=0,
                total_jobs_today=1,
                jobs_completed_today=0,
                fleet_utilization_pct=100.0
            ),
            technicians_on_jobs=[
                TechnicianOnJob(
                    technician_id="TECH-001",
                    name="Gurpreet Singh",
                    status="On Paid Job",
                    live_job_id="SR-26-0101",
                    customer_company="Reliance Industries Limited",
                    machine_asset="Krone BigPack 1290 HDP",
                    current_location=LocationCoord(lat=30.3800, lng=76.8405)
                )
            ],
            today_jobs=[TodayJob(**job)],
            machines_under_service=[MachineUnderService(**machine)]
        )
        assert pulse.kpis.fleet_utilization_pct == 100.0
        assert pulse.technicians_on_jobs[0].live_job_id == "SR-26-0101"

    # ========================================================================
    # SCENARIO 2: HOSHIARPUR MULTI-FIELD BALER COMMISSIONING
    # ========================================================================
    def test_scenario_2_hoshiarpur_baler_commissioning(self, krone_dataset):
        """
        Scenario 2: Hoshiarpur Multi-Field Baler Commissioning
        - Technician: Harpreet Singh (TECH-002)
        - Machine: Krone Fortima V 1500 Round Baler (Serial: FV1500-33901)
        - Customer: Punjab State Farm Cooperative Hoshiarpur (SR-26-0102)
        - Multi-plot moves: Field A (0.8 km), Field B (1.4 km) within 5km agricultural zone
        - Exercised Features: F2 (Jobs), F6 (5km Clustering), F7 (Jitter Filter), F8 (Route Inspector), F11 (Hours), F13 (Filter)
        """
        # 1. Filter jobs by customer (F13)
        hoshiarpur_jobs = [j for j in krone_dataset["jobs"] if "Hoshiarpur" in j["customer_name"]]
        assert len(hoshiarpur_jobs) >= 1
        commissioning_job = hoshiarpur_jobs[0]
        assert commissioning_job["job_id"] == "SR-26-0102"
        
        # 2. Simulate raw stationary pings with GPS multipath jitter
        # Baler is stationary during safety pre-check (v < 1.5 km/h, spatial drift 15m)
        base_coords = (31.5300, 75.9100)
        jitter_pings = [
            {"lat": base_coords[0] + ((i % 3) * 0.00008), "lon": base_coords[1] + ((i % 2) * 0.00008), "speed_kmh": 0.2, "duration_s": 60}
            for i in range(30)  # 30 minutes of stationary checks
        ]
        filtered = apply_jitter_filter(jitter_pings, speed_thresh_kmh=1.5, deadband_m=30.0)
        # All jitter clamped to anchor (F7)
        assert all(p["filtered_lat"] == base_coords[0] for p in filtered)
        
        # 3. Multi-plot service locations (all within 2.5 km of cooperative hub)
        hub_loc = {"lat": 31.5300, "lon": 75.9100}
        field_stops = [
            {"lat": 31.5300, "lon": 75.9100, "duration_s": 7200, "name": "Cooperative Yard Safety Run"},
            {"lat": 31.5370, "lon": 75.9160, "duration_s": 9000, "name": "Field Plot 2A (Round Baler Demo)"},  # ~1.0 km away
            {"lat": 31.5420, "lon": 75.9220, "duration_s": 7200, "name": "Field Plot 4B (Density Test)"}     # ~1.8 km away
        ]
        
        # 4. Clustering: all 3 stops merge into 1 customer operational zone (F6)
        clusters = cluster_stops_5km(field_stops, max_radius_km=5.0)
        assert len(clusters) == 1
        assert len(clusters[0]["stops"]) == 3
        assert clusters[0]["total_duration_s"] == 23400  # 6.5 hrs
        
        # 5. Hours analytics (F11)
        res = inspect_route_telematics(field_stops, hub_loc, hub_loc, transit_moving_seconds=3600.0)
        assert res["H_w"] == 6.5
        assert res["H_t"] == 1.0
        assert res["H_shift"] == 7.5
        assert len(res["anomalies"]) == 0  # No unauthorized stops

    # ========================================================================
    # SCENARIO 3: WESTERN UP FLEET INSPECTION
    # ========================================================================
    def test_scenario_3_western_up_fleet_inspection(self, krone_dataset):
        """
        Scenario 3: Western UP High-Density Harvester Fleet Inspection
        - Technician: Vikram Sharma (TECH-003)
        - Machine: Krone BiG X 680 Forage Harvester (Serial: BX6800-45912)
        - Customer: VERBIO Bio-Gas India Pvt Ltd (Western UP Plant) (SR-26-0103)
        - Route: Meerut Depot to Saharanpur Plant (Designated 70 km, Actual 98 km -> Detour 28 km)
        - Exercised Features: F1 (Pulse), F3 (Machinery), F4 (Sync), F10 (Anomalies), F11 (Hours), F14 (Scorecard)
        """
        base_loc = {"lat": 28.9845, "lon": 77.7064, "name": "Meerut Branch"}
        dest_loc = {"lat": 29.9680, "lon": 77.5552, "name": "Saharanpur VERBIO Plant"}
        
        stops = [
            {"lat": 28.9845, "lon": 77.7064, "duration_s": 1800, "name": "Meerut Depot Departure"},
            {"lat": 29.9680, "lon": 77.5552, "duration_s": 14400, "name": "BiG X 680 Cutterhead Inspection"}
        ]
        
        # Technician took 28 km detour off NH-334 (ratio 98.0 / 70.0 = 1.40 > 1.25, excess 28 km > 10 km)
        res = inspect_route_telematics(
            stops=stops,
            base_loc=base_loc,
            dest_loc=dest_loc,
            designated_distance_km=70.0,
            actual_distance_km=98.0,
            transit_moving_seconds=7200.0  # 2.0 hrs driving
        )
        
        # Detour anomaly triggered (F10)
        assert len(res["anomalies"]) == 1
        assert res["anomalies"][0]["type"] == "excessive_detour"
        assert res["detour_ratio"] == 1.40
        
        # Hours scorecard (F11, F14)
        record = TechnicianProductivityRecord(
            technician_id="TECH-003",
            technician_name="Vikram Sharma",
            working_hours=res["H_w"],
            travelling_hours=res["H_t"],
            idle_hours=res["H_i"],
            shift_hours=res["H_shift"],
            utilization_pct=round((res["H_w"] / res["H_shift"]) * 100.0, 2),
            jobs_count=1
        )
        assert record.working_hours == 4.0
        assert record.travelling_hours == 2.0
        assert record.idle_hours == 0.5  # 1800s depot prep
        assert record.shift_hours == 6.5
        assert record.utilization_pct == 61.54

    # ========================================================================
    # SCENARIO 4: OFFLINE HUB SYNC & TELEMATICS REPLAY
    # ========================================================================
    def test_scenario_4_offline_hub_sync_and_replay(self, sample_journey_pings):
        """
        Scenario 4: Offline Hub Sync & Telematics Replay
        - Technician: Davinder Singh (TECH-012)
        - Service in rural Bathinda with network outage; 185 pings buffered locally
        - Replay engine sorts, filters, clusters, and reconstructs Leaflet route map feed
        - Exercised Features: F4 (Sync), F5 (Synthetic Fallback), F6 (5km Clustering), F12 (Timeframe), F16 (Leaflet Feed)
        """
        assert len(sample_journey_pings) == 185
        
        # 1. Simulate sync request loading buffered offline batch (F4, F5)
        sync_resp = SyncResponse(
            status="success",
            last_synced_at=datetime.now(timezone.utc).isoformat(),
            records_synced=len(sample_journey_pings),
            source="synthetic_fallback"
        )
        assert sync_resp.records_synced == 185
        
        # 2. Extract stationary stop events from pings
        stationary_pings = [p for p in sample_journey_pings if p["speed_kmh"] < 1.5]
        assert len(stationary_pings) > 50
        
        # Reconstruct stops from contiguous stationary blocks
        stops = [
            {"lat": 30.9010, "lon": 75.8573, "duration_s": 1200, "name": "Ludhiana Base"},
            {"lat": 30.6450, "lon": 76.3200, "duration_s": 1500, "name": "En-route Halt"},
            {"lat": 30.3800, "lon": 76.8405, "duration_s": 3600, "name": "Barwala Job Site"}
        ]
        
        # 3. Cluster and inspect replayed trajectory (F6, F16)
        base_loc = {"lat": 30.9010, "lon": 75.8573, "name": "Ludhiana Base Depot"}
        dest_loc = {"lat": 30.3800, "lon": 76.8405, "name": "Barwala Site"}
        res = inspect_route_telematics(stops, base_loc, dest_loc, transit_moving_seconds=4800.0)
        
        # 4. Generate Leaflet Map Feed (F16)
        polyline = [[p["lat"], p["lng"]] for p in sample_journey_pings[::10]]  # Subsampled polyline
        assert len(polyline) >= 15
        
        clusters_payload = [
            OperationalCluster(
                cluster_id=c["cluster_id"],
                centroid=LocationCoord(lat=c["centroid_lat"], lng=c["centroid_lon"]),
                radius_meters=c["radius_meters"],
                location_name=c["location_name"],
                pings_count=len(c["stops"]),
                duration_minutes=round(c["total_duration_s"] / 60.0, 1),
                is_job_site=c["is_job_site"],
                is_base=c["is_base"]
            )
            for c in res["clusters"]
        ]
        assert len(clusters_payload) == 3
        
        # Valid Leaflet map response
        map_feed = RouteInspectionResponse(
            technician_id="TECH-012",
            technician_name="Davinder Singh",
            date="2026-09-22",
            journey_summary=JourneySummary(
                start_location=LocationCoord(lat=base_loc["lat"], lng=base_loc["lon"], name="Ludhiana Depot"),
                destination=LocationCoord(lat=dest_loc["lat"], lng=dest_loc["lon"], name="Barwala Site"),
                transit_duration_minutes=80.0,
                unauthorized_stop_duration_minutes=25.0,
                total_distance_km=84.6,
                anomalies_detected=len(res["anomalies"])
            ),
            raw_pings_count=len(sample_journey_pings),
            clusters_5km=clusters_payload,
            anomalies=[RouteAnomaly(**a) for a in res["anomalies"]],
            route_polyline=polyline
        )
        assert map_feed.raw_pings_count == 185
        assert len(map_feed.clusters_5km) == 3

    # ========================================================================
    # SCENARIO 5: UNAUTHORIZED DHABA HALT & DETOUR INVESTIGATION
    # ========================================================================
    def test_scenario_5_unauthorized_dhaba_halt_and_detour(self, krone_dataset):
        """
        Scenario 5: Unauthorized Dhaba Halt & Detour Investigation
        - Technician: Jaswinder Singh (TECH-004)
        - Claimed 4.0 hours transit to reach Barnala Bio-Mass Site (SR-26-0104)
        - Route telematics reveals:
          * 2.0 hrs pure moving driving
          * 75 min (1.25 hrs) unauthorized stationary halt at Highway Dhaba (outside 5km corridor)
          * 15 km unapproved detour
        - Audit reclassifies 1.25 hrs to idle, flags 2 anomalies, and recalculates utilization
        - Exercised Features: F6 (Clustering), F8 (Inspector), F9 (Unauth Stop), F10 (Alerts), F11 (Hours Conservation), F13 (Filter)
        """
        base_loc = {"lat": 28.4595, "lon": 77.0266, "name": "Gurugram Office"}
        dest_loc = {"lat": 30.3819, "lon": 75.5469, "name": "Barnala Bio-Mass Site"}
        
        # 1. Stops including 75-min unauthorized dhaba stop
        stops = [
            {"lat": 28.4595, "lon": 77.0266, "duration_s": 1800, "name": "Gurugram Depot Prep"},  # 30 min base
            {"lat": 29.8000, "lon": 76.4000, "duration_s": 4500, "name": "Highway Dhaba (Halt)"},   # 75 min unauth halt (>15m)
            {"lat": 30.3819, "lon": 75.5469, "duration_s": 14400, "name": "Krone EasyCut Mower Service"}  # 4.0 hrs job site
        ]
        
        # 2. Designated route 210 km, actual distance 265 km (detour ratio 1.26 > 1.25 and excess 55 km > 10 km)
        res = inspect_route_telematics(
            stops=stops,
            base_loc=base_loc,
            dest_loc=dest_loc,
            designated_distance_km=210.0,
            actual_distance_km=265.0,
            transit_moving_seconds=7200.0  # 2.0 hrs pure moving driving
        )
        
        # 3. Two anomalies flagged (F10)
        anomaly_types = {a["type"] for a in res["anomalies"]}
        assert "unauthorized_stop" in anomaly_types
        assert "excessive_detour" in anomaly_types
        
        # 4. Audit Hours Reclassification (F9, F11)
        # Shift total: 4.0 hrs work (14400s) + 2.0 hrs travel (7200s) + 1.25 hrs unauth (4500s) + 0.5 hr depot (1800s) = 7.75 hrs
        assert res["H_w"] == 4.0
        assert res["H_t"] == 2.0
        assert res["H_i"] == 1.75  # 1.25 hrs dhaba + 0.5 hr depot
        assert res["H_shift"] == 7.75
        
        # Utilization drops from (4.0 / 6.5 = 61.5%) to (4.0 / 7.75 = 51.6%)
        audit_util = round((res["H_w"] / res["H_shift"]) * 100.0, 1)
        assert audit_util == 51.6
        
        # 5. Filter technician record in audit dashboard (F13)
        tech_audit = next(t for t in krone_dataset["technicians"] if t["id"] == "TECH-004")
        assert tech_audit["name"] == "Jaswinder Singh"
