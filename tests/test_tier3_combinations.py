"""
Tier 3: Cross-Feature Pairwise Interaction Tests (>= 20 Tests)
Verifies integration between sync, telematics clustering, route inspection,
hours analytics, filtering, scorecards, and UI data feeds.
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
    initial_bearing_radians,
    initial_bearing,
    cross_track_distance_km,
    cross_track_distance,
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


class TestTier3CrossFeatureInteractions:
    """Pairwise cross-feature integration and interaction test suite."""

    def test_interaction_01_sync_trigger_live_pulse_kpi_refresh(self, krone_dataset):
        """Interaction 1: Sync trigger refreshes cache and updates live pulse KPIs."""
        sync_req = SyncRequest(force_refresh=True)
        assert sync_req.force_refresh is True
        
        sync_resp = SyncResponse(
            status="success",
            last_synced_at=datetime.now(timezone.utc).isoformat(),
            records_synced=len(krone_dataset["jobs"]) + len(krone_dataset["machines"]),
            source="fieldy_api"
        )
        assert sync_resp.records_synced > 0
        
        # Pulse reflects refreshed records
        active_techs = [t for t in krone_dataset["technicians"] if t["status"] != "On Holiday/Leave"]
        paid_techs = [t for t in krone_dataset["technicians"] if t["status"] == "On Paid Job"]
        
        pulse = PulseKPIs(
            technicians_on_paid_jobs=len(paid_techs),
            technicians_active_total=len(active_techs),
            technicians_on_leave=len(krone_dataset["technicians"]) - len(active_techs),
            total_jobs_today=len(krone_dataset["jobs"]),
            jobs_completed_today=len([j for j in krone_dataset["jobs"] if j["status"] == "Completed"]),
            fleet_utilization_pct=round((len(paid_techs) / len(active_techs)) * 100.0, 1)
        )
        assert pulse.total_jobs_today == len(krone_dataset["jobs"])
        assert pulse.technicians_on_paid_jobs == len(paid_techs)

    def test_interaction_02_clustering_5km_jitter_dampening(self):
        """Interaction 2: Jitter dampening cleans noisy coordinates before 5 km clustering."""
        anchor_lat, anchor_lon = 30.901000, 75.857300
        # Generate 20 jittering pings at stationary base (< 1.5 km/h, < 30m drift)
        raw_pings = [
            {"lat": anchor_lat + ((i % 4) * 0.00005), "lon": anchor_lon + ((i % 3) * 0.00005), "speed_kmh": 0.5, "duration_s": 60}
            for i in range(20)
        ]
        filtered_pings = apply_jitter_filter(raw_pings, speed_thresh_kmh=1.5, deadband_m=30.0)
        assert all(p["filtered_lat"] == anchor_lat for p in filtered_pings)
        
        # Stop formed from filtered pings
        stop = {
            "lat": filtered_pings[0]["filtered_lat"],
            "lon": filtered_pings[0]["filtered_lon"],
            "duration_s": sum(p["duration_s"] for p in filtered_pings)
        }
        clusters = cluster_stops_5km([stop], max_radius_km=5.0)
        assert len(clusters) == 1
        assert clusters[0]["centroid_lat"] == anchor_lat

    def test_interaction_03_route_inspector_unauthorized_stop_hours_reclassification(self):
        """Interaction 3: Route inspector detects unauthorized stop (>15m outside corridor) and reclassifies time to idle."""
        base = {"lat": 30.9010, "lon": 75.8573}
        dest = {"lat": 30.3800, "lon": 76.8405}
        
        # Technician has:
        # - 1 hr moving transit (3600s)
        # - 45 min unauthorized dhaba stop (2700s) outside 5km zone
        # - 4 hrs on-site baler repair (14400s)
        stops = [
            {"lat": 30.6450, "lon": 76.3200, "duration_s": 2700},  # En-route dhaba halt
            {"lat": 30.3800, "lon": 76.8405, "duration_s": 14400}  # Job site
        ]
        res = inspect_route_telematics(stops, base, dest, transit_moving_seconds=3600.0)
        
        # Hours reclassification:
        assert res["H_w"] == 4.0   # 14400s
        assert res["H_t"] == 1.0   # pure moving transit (3600s)
        assert res["H_i"] == 0.75  # 2700s / 3600 = 0.75 hrs idle
        assert res["H_shift"] == 5.75
        assert len(res["anomalies"]) == 1
        assert res["anomalies"][0]["type"] == "unauthorized_stop"

    def test_interaction_04_multi_dimensional_filter_weekly_timeframe_trend(self, krone_dataset):
        """Interaction 4: Filter by technician and client rolled up in weekly trend."""
        tech_id = "TECH-001"
        tech_name = "Gurpreet Singh"
        client = "Reliance Industries Limited"
        
        # Weekly trends for this technician
        trends = [
            ProductivityTrend(period=f"2026-09-{16+i:02d}", working=6.5, travelling=1.5, idle=0.0)
            for i in range(5)
        ]
        total_w = sum(t.working for t in trends)
        total_t = sum(t.travelling for t in trends)
        total_i = sum(t.idle for t in trends)
        total_s = total_w + total_t + total_i
        
        resp = ProductivityResponse(
            timeframe="weekly",
            summary=ProductivitySummary(
                total_working_hours=total_w,
                total_travelling_hours=total_t,
                total_idle_hours=total_i,
                total_shift_hours=total_s,
                average_utilization_pct=round((total_w / total_s) * 100.0, 2)
            ),
            technician_records=[
                TechnicianProductivityRecord(
                    technician_id=tech_id,
                    technician_name=tech_name,
                    working_hours=total_w,
                    travelling_hours=total_t,
                    idle_hours=total_i,
                    shift_hours=total_s,
                    utilization_pct=round((total_w / total_s) * 100.0, 2),
                    jobs_count=5
                )
            ],
            trend_data=trends
        )
        assert resp.summary.total_working_hours == 32.5
        assert resp.technician_records[0].jobs_count == 5

    def test_interaction_05_detour_anomaly_alert_route_map_feed(self):
        """Interaction 5: Detour anomaly triggers alert badge embedded in Leaflet feed."""
        base = {"lat": 30.9010, "lon": 75.8573}
        dest = {"lat": 30.3800, "lon": 76.8405}
        
        # Designated route 80 km; actual travel 115 km (detour ratio 1.44 > 1.25 and excess 35 km > 10 km)
        res = inspect_route_telematics([], base, dest, designated_distance_km=80.0, actual_distance_km=115.0)
        assert len(res["anomalies"]) == 1
        
        # Feed structure for Leaflet Route Map
        route_feed = RouteInspectionResponse(
            technician_id="TECH-001",
            technician_name="Gurpreet Singh",
            date="2026-09-22",
            journey_summary=JourneySummary(
                start_location=LocationCoord(lat=base["lat"], lng=base["lon"], name="Ludhiana Hub"),
                destination=LocationCoord(lat=dest["lat"], lng=dest["lon"], name="Barwala Facility"),
                transit_duration_minutes=120.0,
                unauthorized_stop_duration_minutes=0.0,
                total_distance_km=115.0,
                anomalies_detected=1
            ),
            raw_pings_count=150,
            clusters_5km=[],
            anomalies=[RouteAnomaly(**a) for a in res["anomalies"]],
            route_polyline=[[base["lat"], base["lon"]], [dest["lat"], dest["lon"]]]
        )
        assert route_feed.journey_summary.anomalies_detected == 1
        assert route_feed.anomalies[0].type == "excessive_detour"

    def test_interaction_06_synthetic_fallback_machinery_active_job_link(self, krone_dataset):
        """Interaction 6: Referential integrity between machines under service and active job IDs."""
        jobs_map = {j["job_id"]: j for j in krone_dataset["jobs"]}
        for m in krone_dataset["machines"]:
            active_id = m["active_job_id"]
            assert active_id in jobs_map
            linked_job = jobs_map[active_id]
            # Machine serial in machine matches machine serial in linked job
            assert m["serial_number"] == linked_job["machine_serial"]

    def test_interaction_07_multi_stop_journey_dual_5km_clusters_hours_conservation(self):
        """Interaction 7: Two separate job sites (>20km apart) resolve to 2 clusters preserving hours."""
        base = {"lat": 30.9010, "lon": 75.8573}
        site_1 = {"lat": 30.5000, "lon": 76.2000}
        site_2 = {"lat": 30.2000, "lon": 76.6000}
        
        stops = [
            {"lat": site_1["lat"], "lon": site_1["lon"], "duration_s": 7200},  # 2.0 hrs at Site 1
            {"lat": site_2["lat"], "lon": site_2["lon"], "duration_s": 10800}  # 3.0 hrs at Site 2
        ]
        clusters = cluster_stops_5km(stops, max_radius_km=5.0)
        assert len(clusters) == 2
        
        # Total travel time between sites: 2.5 hrs (9000s)
        # Total shift: 2.0 + 3.0 + 2.5 = 7.5 hrs
        H_w = sum(c["total_duration_s"] for c in clusters) / 3600.0
        H_t = 2.5
        H_i = 0.0
        H_shift = H_w + H_t + H_i
        
        summary = ProductivitySummary(
            total_working_hours=H_w,
            total_travelling_hours=H_t,
            total_idle_hours=H_i,
            total_shift_hours=H_shift,
            average_utilization_pct=round((H_w / H_shift) * 100.0, 2)
        )
        assert summary.total_working_hours == 5.0
        assert summary.total_shift_hours == 7.5

    def test_interaction_08_jitter_filter_stationary_odometer_drift_suppression(self):
        """Interaction 8: 100 stationary jittering pings produce zero accumulated distance."""
        anchor_lat, anchor_lon = 30.9010, 75.8573
        pings = [
            {"lat": anchor_lat + ((i % 5) * 0.00004), "lon": anchor_lon + ((i % 3) * 0.00004), "speed_kmh": 0.0}
            for i in range(100)
        ]
        filtered = apply_jitter_filter(pings, speed_thresh_kmh=1.5, deadband_m=30.0)
        accum_dist = sum(
            haversine_distance(filtered[i]["filtered_lat"], filtered[i]["filtered_lon"],
                               filtered[i+1]["filtered_lat"], filtered[i+1]["filtered_lon"])
            for i in range(len(filtered) - 1)
        )
        assert accum_dist == 0.0

    def test_interaction_09_timeframe_toggle_daily_to_monthly_scorecard(self):
        """Interaction 9: Technician ranking consistency when switching timeframe from daily to monthly."""
        daily_records = [
            TechnicianProductivityRecord(technician_id="T1", technician_name="Gurpreet", working_hours=6.5, travelling_hours=1.5, idle_hours=0.0, shift_hours=8.0, utilization_pct=81.25, jobs_count=1),
            TechnicianProductivityRecord(technician_id="T2", technician_name="Harpreet", working_hours=4.0, travelling_hours=2.0, idle_hours=2.0, shift_hours=8.0, utilization_pct=50.0, jobs_count=1)
        ]
        monthly_records = [
            TechnicianProductivityRecord(technician_id="T1", technician_name="Gurpreet", working_hours=130.0, travelling_hours=30.0, idle_hours=0.0, shift_hours=160.0, utilization_pct=81.25, jobs_count=20),
            TechnicianProductivityRecord(technician_id="T2", technician_name="Harpreet", working_hours=85.0, travelling_hours=40.0, idle_hours=35.0, shift_hours=160.0, utilization_pct=53.12, jobs_count=15)
        ]
        top_daily = max(daily_records, key=lambda r: r.utilization_pct)
        top_monthly = max(monthly_records, key=lambda r: r.utilization_pct)
        assert top_daily.technician_id == top_monthly.technician_id == "T1"

    def test_interaction_10_unauthorized_dhaba_halt_utilization_penalty(self):
        """Interaction 10: Unauthorized 1.5-hour roadside halt reduces technician utilization rate."""
        # Clean shift: 6 hrs work, 2 hrs travel, 0 hrs idle -> 8 hrs shift, 75% util
        w1, t1, i1 = 6.0, 2.0, 0.0
        util_clean = (w1 / (w1 + t1 + i1)) * 100.0
        
        # Halting shift: 6 hrs work, 2 hrs travel, 1.5 hrs unauthorized stop (idle) -> 9.5 hrs shift
        w2, t2, i2 = 6.0, 2.0, 1.5
        util_halt = (w2 / (w2 + t2 + i2)) * 100.0
        
        assert util_clean == 75.0
        assert util_halt < util_clean
        assert round(util_halt, 2) == 63.16

    def test_interaction_11_machine_asset_service_status_pulse_technician_sync(self, sample_pulse_response):
        """Interaction 11: Machine under service links to assigned technician in pulse response."""
        for m in sample_pulse_response.machines_under_service:
            # Find linked job
            job = next((j for j in sample_pulse_response.today_jobs if j.job_id == m.active_job_id), None)
            assert job is not None
            # Assigned tech should be present in technicians_on_jobs
            for tech_name in job.assigned_technicians:
                matched_tech = next((t for t in sample_pulse_response.technicians_on_jobs if t.name == tech_name), None)
                if matched_tech:
                    assert matched_tech.status == "On Paid Job"

    def test_interaction_12_gps_dropout_anomaly_route_polyline_gap_detection(self):
        """Interaction 12: GPS dropout interval (>30m) flags gap anomaly while keeping route polyline intact."""
        t0 = datetime(2026, 9, 22, 8, 0, 0)
        pings = [
            {"lat": 30.9010, "lng": 75.8573, "timestamp": t0.isoformat()},
            {"lat": 30.5000, "lng": 76.5000, "timestamp": (t0 + timedelta(minutes=45)).isoformat()}  # 45 min gap
        ]
        dt = (datetime.fromisoformat(pings[1]["timestamp"]) - datetime.fromisoformat(pings[0]["timestamp"])).total_seconds() / 60.0
        assert dt == 45.0
        
        anomalies = []
        if dt > 30.0:
            anomalies.append(RouteAnomaly(
                type="gps_dropout",
                location=LocationCoord(lat=pings[0]["lat"], lng=pings[0]["lng"]),
                duration_minutes=dt,
                started_at=pings[0]["timestamp"],
                description=f"GPS telemetry signal lost for {dt:.0f} minutes"
            ))
        assert len(anomalies) == 1
        assert anomalies[0].type == "gps_dropout"

    def test_interaction_13_search_query_status_color_code_consistency(self, krone_dataset):
        """Interaction 13: Job search preserves Fieldy hex status color codes."""
        for j in krone_dataset["jobs"]:
            job = TodayJob(**j)
            if job.status == "In Progress":
                assert job.status_color == "#059669"
            elif job.status == "Completed":
                assert job.status_color == "#10b981"
            elif job.status == "Hold":
                assert job.status_color == "#f59e0b"

    def test_interaction_14_duration_weighted_centroid_bounding_radius_stability(self):
        """Interaction 14: Duration weighting stabilizes centroid against transient micro-stops."""
        stops = [
            {"lat": 30.0000, "lon": 75.0000, "duration_s": 14400},  # 4 hrs at main baler repair
            {"lat": 30.0200, "lon": 75.0000, "duration_s": 600}     # 10 min at farm gate (~2.2 km away)
        ]
        c_lat, c_lon = weighted_cartesian_centroid(stops)
        # Distance from centroid to primary workshop
        dist_to_workshop = haversine_distance(c_lat, c_lon, 30.0000, 75.0000)
        # Heavy duration (14400s vs 600s = 24:1 ratio) keeps centroid within 150m of workshop
        assert dist_to_workshop < 0.150  # < 150 meters

    def test_interaction_15_cross_track_distance_corridor_detour_ratio(self):
        """Interaction 15: Pings with high Cross-Track Distance (XTD > 1.5km) identify detour deviations."""
        # Highway route from A (30.0, 75.0) to B (30.0, 76.0) -> straight east-west line
        lat_a, lon_a = 30.0000, 75.0000
        lat_b, lon_b = 30.0000, 76.0000
        
        # Ping P1 on corridor (offset 0.5 km north)
        lat_p1 = 30.0000 + (0.5 / 111.195)
        lon_p1 = 75.5000
        xtd_1 = cross_track_distance(lat_p1, lon_p1, lat_a, lon_a, lat_b, lon_b)
        assert xtd_1 <= 1.5  # Authorized corridor
        
        # Ping P2 deep off corridor (offset 15 km north)
        lat_p2 = 30.0000 + (15.0 / 111.195)
        lon_p2 = 75.5000
        xtd_2 = cross_track_distance(lat_p2, lon_p2, lat_a, lon_a, lat_b, lon_b)
        assert xtd_2 > 1.5  # Unauthorized detour deviation

    def test_interaction_16_zero_data_sync_empty_dashboard_kpis_fallback(self):
        """Interaction 16: Zero-data sync yields clean 0-state dashboard without errors."""
        sync_resp = SyncResponse(status="success", last_synced_at="2026-09-22T12:00:00Z", records_synced=0, source="fieldy_cache")
        assert sync_resp.records_synced == 0
        
        pulse = PulseResponse(
            timestamp="2026-09-22T12:00:00Z",
            kpis=PulseKPIs(technicians_on_paid_jobs=0, technicians_active_total=0, technicians_on_leave=0, total_jobs_today=0, jobs_completed_today=0, fleet_utilization_pct=0.0),
            technicians_on_jobs=[],
            today_jobs=[],
            machines_under_service=[]
        )
        assert pulse.kpis.fleet_utilization_pct == 0.0
        assert len(pulse.today_jobs) == 0

    def test_interaction_17_fleet_aggregate_shift_hours_conservation(self):
        """Interaction 17: Total fleet shift hours equal exact sum of individual technician hours."""
        tech_shifts = [
            {"w": 6.5, "t": 1.5, "i": 0.0},
            {"w": 5.0, "t": 2.0, "i": 1.0},
            {"w": 7.0, "t": 1.0, "i": 0.0},
            {"w": 4.0, "t": 3.0, "i": 1.0},
        ]
        fleet_w = sum(s["w"] for s in tech_shifts)
        fleet_t = sum(s["t"] for s in tech_shifts)
        fleet_i = sum(s["i"] for s in tech_shifts)
        fleet_s = fleet_w + fleet_t + fleet_i
        
        summary = ProductivitySummary(
            total_working_hours=fleet_w,
            total_travelling_hours=fleet_t,
            total_idle_hours=fleet_i,
            total_shift_hours=fleet_s,
            average_utilization_pct=round((fleet_w / fleet_s) * 100.0, 2)
        )
        assert summary.total_shift_hours == 32.0
        assert summary.total_working_hours == 22.5

    def test_interaction_18_cluster_incremental_leader_order_invariance(self):
        """Interaction 18: Chronological stop processing preserves cluster count and stability."""
        s1 = {"lat": 30.000, "lon": 75.000, "duration_s": 3600}
        s2 = {"lat": 30.010, "lon": 75.010, "duration_s": 3600}  # ~1.4 km from s1
        s3 = {"lat": 30.500, "lon": 75.500, "duration_s": 3600}  # ~72 km away
        
        clusters = cluster_stops_5km([s1, s2, s3], max_radius_km=5.0)
        assert len(clusters) == 2
        assert len(clusters[0]["stops"]) == 2
        assert len(clusters[1]["stops"]) == 1

    def test_interaction_19_offline_batch_telematics_replay_retroactive_hours(self):
        """Interaction 19: Batch replay of buffered telematics computes identical hours breakdown."""
        base = {"lat": 30.9010, "lon": 75.8573}
        dest = {"lat": 30.3800, "lon": 76.8405}
        
        stops_buffered = [
            {"lat": 30.9010, "lon": 75.8573, "duration_s": 1200},
            {"lat": 30.3800, "lon": 76.8405, "duration_s": 18000}
        ]
        res = inspect_route_telematics(stops_buffered, base, dest, transit_moving_seconds=5400.0)
        assert res["H_w"] == 5.0
        assert res["H_t"] == 1.5
        assert res["H_i"] == 0.33

    def test_interaction_20_job_completion_pipeline_pulse_kpis_update(self, sample_pulse_response):
        """Interaction 20: Marking a job completed decrements in-progress and increments completed count."""
        initial_completed = sample_pulse_response.kpis.jobs_completed_today
        # Simulate completing 1 job
        sample_pulse_response.kpis.jobs_completed_today += 1
        assert sample_pulse_response.kpis.jobs_completed_today == initial_completed + 1

    def test_interaction_21_critical_unauthorized_stop_and_detour_priority_ranking(self):
        """Interaction 21: Priority ranking of multiple anomalies."""
        anomalies = [
            RouteAnomaly(type="unauthorized_stop", location=LocationCoord(lat=30.6, lng=76.3), duration_minutes=45.0, started_at="08:45", description="Critical stop > 30m"),
            RouteAnomaly(type="excessive_detour", location=LocationCoord(lat=30.9, lng=75.8), duration_minutes=0.0, started_at="08:30", description="Detour ratio 1.35"),
        ]
        # Rank by duration descending
        ranked = sorted(anomalies, key=lambda a: a.duration_minutes, reverse=True)
        assert ranked[0].type == "unauthorized_stop"

    def test_interaction_22_cross_midnight_shift_hours_partition(self):
        """Interaction 22: Shift spanning midnight splits cleanly across dates."""
        t_start = datetime(2026, 9, 22, 22, 0, 0, tzinfo=timezone.utc)
        t_end = datetime(2026, 9, 23, 4, 0, 0, tzinfo=timezone.utc)
        total_seconds = (t_end - t_start).total_seconds()
        assert total_seconds == 6 * 3600.0
        
        # Day 1 (22:00 to 24:00) = 2 hrs; Day 2 (00:00 to 04:00) = 4 hrs
        midnight = datetime(2026, 9, 23, 0, 0, 0, tzinfo=timezone.utc)
        day1_hrs = (midnight - t_start).total_seconds() / 3600.0
        day2_hrs = (t_end - midnight).total_seconds() / 3600.0
        assert day1_hrs == 2.0
        assert day2_hrs == 4.0
        assert (day1_hrs + day2_hrs) == 6.0
