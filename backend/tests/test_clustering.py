"""
backend/tests/test_clustering.py
Automated Verification Suite for 5 km Haversine Clustering, 3D Centroids,
Jitter Suppression, Cross-Track Distance & Route Anomalies.
Covers 18 definitive test cases (TC-GEO-01 to TC-HRS-18).
"""

import math
from datetime import datetime, timezone
import pytest
import os
import sys

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.telematics_engine import (
    EARTH_RADIUS_KM,
    haversine_distance_km,
    weighted_cartesian_centroid,
    filter_stationary_jitter,
    extract_raw_stops,
    cluster_pings_5km,
    cross_track_distance_km,
    inspect_journey,
    compute_hours_balance
)


# ===========================================================================
# Category 1: Geodesy Math & Boundary Assertions (TC-GEO-01 to TC-GEO-06)
# ===========================================================================

def test_tc_geo_01_haversine_accuracy():
    """TC-GEO-01: Gurugram HQ (28.4793, 77.0988) to IGI Airport (28.5562, 77.1000) = 8.551 km."""
    lat1, lon1 = 28.4793, 77.0988
    lat2, lon2 = 28.5562, 77.1000
    dist = haversine_distance_km(lat1, lon1, lat2, lon2)
    assert abs(dist - 8.551) <= 0.005
    assert 8.546 <= dist <= 8.556


def test_tc_geo_02_boundary_within_5km():
    """TC-GEO-02: Point A to Point B at +4.990 km North <= 5.0 km -> Merges into 1 cluster."""
    lat_a, lon_a = 16.9600, 82.2300
    lat_b = lat_a + (4.990 / EARTH_RADIUS_KM) * (180.0 / math.pi)
    lon_b = 82.2300

    dist = haversine_distance_km(lat_a, lon_a, lat_b, lon_b)
    assert dist <= 5.0
    assert abs(dist - 4.990) < 1e-4

    stops = [
        {"lat": lat_a, "lon": lon_a, "duration_s": 1800.0},
        {"lat": lat_b, "lon": lon_b, "duration_s": 1800.0}
    ]
    clusters = cluster_pings_5km(stops, max_radius_km=5.0)
    assert len(clusters) == 1
    assert clusters[0]["radius_meters"] <= 5000.0


def test_tc_geo_03_boundary_exceeding_5km():
    """TC-GEO-03: Point A to Point C at +5.010 km North > 5.0 km -> Splits into 2 clusters."""
    lat_a, lon_a = 16.9600, 82.2300
    lat_c = lat_a + (5.010 / EARTH_RADIUS_KM) * (180.0 / math.pi)
    lon_c = 82.2300

    dist = haversine_distance_km(lat_a, lon_a, lat_c, lon_c)
    assert dist > 5.0
    assert abs(dist - 5.010) < 1e-4

    stops = [
        {"lat": lat_a, "lon": lon_a, "duration_s": 1800.0},
        {"lat": lat_c, "lon": lon_c, "duration_s": 1800.0}
    ]
    clusters = cluster_pings_5km(stops, max_radius_km=5.0)
    assert len(clusters) == 2


def test_tc_geo_04_identical_coordinates():
    """TC-GEO-04: Identical Coordinates -> Distance = 0.0 km, zero division/NaN safe."""
    lat, lon = 28.4793, 77.0988
    dist = haversine_distance_km(lat, lon, lat, lon)
    assert dist == 0.0
    assert not math.isnan(dist)
    assert not math.isinf(dist)


def test_tc_geo_05_antipodal_numerical_stability():
    """TC-GEO-05: North Pole (90.0, 0.0) to South Pole (-90.0, 0.0) -> Clamped a* <= 1.0."""
    dist = haversine_distance_km(90.0, 0.0, -90.0, 0.0)
    expected = math.pi * EARTH_RADIUS_KM  # approx 20015.087 km
    assert abs(dist - expected) <= 0.01
    assert abs(dist - 20015.087) <= 0.1
    assert not math.isnan(dist)


def test_tc_geo_06_duration_weighted_cartesian_centroid():
    """
    TC-GEO-06: 3 points in Kakinada. Duration weighting pulls centroid toward P1 (3h dwell).
    Centroid must strictly differ from arithmetic mean and equal (16.989556, 82.247444).
    """
    stops = [
        {"lat": 16.9890, "lon": 82.2475, "duration_s": 10800.0},  # 3.0 hrs
        {"lat": 16.9950, "lon": 82.2500, "duration_s": 3600.0},   # 1.0 hr (~770m away)
        {"lat": 16.9820, "lon": 82.2420, "duration_s": 1800.0},   # 0.5 hr (~920m away)
    ]
    c_lat, c_lon = weighted_cartesian_centroid(stops)
    assert c_lat == 16.989556
    assert c_lon == 82.247444

    # Verify arithmetic mean would be inaccurate
    arith_lat = round(sum(s["lat"] for s in stops) / 3.0, 6)
    arith_lon = round(sum(s["lon"] for s in stops) / 3.0, 6)
    assert c_lat != arith_lat
    assert c_lon != arith_lon

    # Centroid is closer to P1 than to P2
    d_to_p1 = haversine_distance_km(c_lat, c_lon, 16.9890, 82.2475)
    d_to_p2 = haversine_distance_km(c_lat, c_lon, 16.9950, 82.2500)
    assert d_to_p1 < d_to_p2


# ===========================================================================
# Category 2: Jitter Filter & Stop Extraction (TC-JIT-07 to TC-JIT-08)
# ===========================================================================

def test_tc_jit_07_stationary_jitter_dampening():
    """TC-JIT-07: 10 pings fluctuating within 25m circle at 0.4 km/h -> 0.0m phantom odometer."""
    base_lat, base_lon = 30.9010, 75.8573
    pings = [
        {
            "lat": base_lat + 0.0001 * (i % 3),
            "lon": base_lon + 0.0001 * (i % 2),
            "speed_kmh": 0.4,
            "timestamp_s": i * 120.0
        }
        for i in range(10)
    ]
    filtered, dist = filter_stationary_jitter(pings, min_speed_kmh=1.5, deadband_meters=30.0)
    assert dist == 0.0
    assert len(filtered) == 10
    # All pings pinned to anchor
    assert all(p["lat"] == base_lat and p["lon"] == base_lon for p in filtered)
    assert all(p["is_stationary"] is True for p in filtered)


def test_tc_jit_08_stop_extraction_duration_gating():
    """TC-JIT-08: Stationary sequence 240s (4 min) vs 360s (6 min) against 300s threshold."""
    # Sequence A: 240s dwell (< 300s)
    pings_a = [
        {"lat": 30.9010, "lon": 75.8573, "speed_kmh": 0.0, "timestamp_s": i * 10.0}
        for i in range(25)  # 0 to 240s
    ]
    stops_a = extract_raw_stops(pings_a, min_stop_duration_s=300.0)
    assert len(stops_a) == 0

    # Sequence B: 360s dwell (>= 300s)
    pings_b = [
        {"lat": 30.9010, "lon": 75.8573, "speed_kmh": 0.0, "timestamp_s": i * 10.0}
        for i in range(37)  # 0 to 360s
    ]
    stops_b = extract_raw_stops(pings_b, min_stop_duration_s=300.0)
    assert len(stops_b) == 1
    assert stops_b[0]["duration_s"] == 360.0
    assert stops_b[0]["pings_count"] == 37


# ===========================================================================
# Category 3: 5 km Clustering & Operational Zones (TC-CLU-09 to TC-CLU-10)
# ===========================================================================

def test_tc_clu_09_micro_move_field_merging():
    """TC-CLU-09: 3 farm plot stops during RIL Baler repair merged into 1 Operational Zone (5.1 hrs)."""
    stops = [
        {"lat": 30.3800, "lon": 76.8400, "duration_s": 7200.0, "pings_count": 40},  # Plot 1: 2.0h
        {"lat": 30.3880, "lon": 76.8480, "duration_s": 5400.0, "pings_count": 30},  # Plot 2: 1.5h (~1.16km)
        {"lat": 30.3750, "lon": 76.8350, "duration_s": 5760.0, "pings_count": 32},  # Plot 3: 1.6h (~0.75km)
    ]
    clusters = cluster_pings_5km(stops, max_radius_km=5.0)
    assert len(clusters) == 1
    c = clusters[0]
    assert c["cluster_id"] == "CLUST-01"
    assert c["total_duration_s"] == 18360.0  # 5.10 hours
    assert c["duration_minutes"] == 306.0
    assert c["pings_count"] == 102
    assert c["radius_meters"] <= 5000.0


def test_tc_clu_10_intermediate_highway_stop_isolation():
    """TC-CLU-10: En-route highway Dhaba at 45km from base, 55km from customer -> Forms distinct ZONE-2."""
    stops = [
        {"lat": 30.9010, "lon": 75.8573, "duration_s": 3600.0, "location_name": "Ludhiana Depot Base"},
        {"lat": 30.4840, "lon": 76.5940, "duration_s": 1680.0, "location_name": "Rajpura Highway Dhaba"},
        {"lat": 30.3800, "lon": 76.8405, "duration_s": 18000.0, "location_name": "RIL Barwala Customer Site"},
    ]
    clusters = cluster_pings_5km(stops, max_radius_km=5.0)
    assert len(clusters) == 3
    assert clusters[0]["cluster_id"] == "CLUST-01"
    assert clusters[1]["cluster_id"] == "CLUST-02"
    assert clusters[2]["cluster_id"] == "CLUST-03"
    assert clusters[1]["location_name"] == "Rajpura Highway Dhaba"
    assert clusters[1]["total_duration_s"] == 1680.0


# ===========================================================================
# Category 4: Route Inspection & Landmark Matching (TC-ROU-11 to TC-ROU-12)
# ===========================================================================

def test_tc_rou_11_starting_base_identification():
    """TC-ROU-11: Morning cluster at (16.9600, 82.2300) matched to Kakinada Depot Base within 5km."""
    base_coords = {"lat": 16.9600, "lon": 82.2300}
    customer_coords = {"lat": 16.5052, "lon": 81.8039}
    clusters = [
        {
            "cluster_id": "CLUST-01",
            "centroid": {"lat": 16.9600, "lng": 82.2300},
            "total_duration_s": 3600.0
        }
    ]
    classified, summary = inspect_journey(clusters, base_coords, customer_coords)
    assert classified[0]["zone_type"] == "STARTING_BASE"
    assert classified[0]["is_base"] is True
    assert classified[0]["is_anomaly"] is False
    assert summary["base_seconds"] == 3600.0


def test_tc_rou_12_customer_destination_identification():
    """TC-ROU-12: Afternoon cluster at (16.5052, 81.8039) matched to RIL Bio-Energy Customer Site."""
    base_coords = {"lat": 16.9600, "lon": 82.2300}
    customer_coords = {"lat": 16.5052, "lon": 81.8039}
    clusters = [
        {
            "cluster_id": "CLUST-02",
            "centroid": {"lat": 16.5052, "lng": 81.8039},
            "total_duration_s": 18000.0
        }
    ]
    classified, summary = inspect_journey(clusters, base_coords, customer_coords)
    assert classified[0]["zone_type"] == "CUSTOMER_DESTINATION"
    assert classified[0]["is_job_site"] is True
    assert classified[0]["is_anomaly"] is False
    assert summary["working_seconds"] == 18000.0


# ===========================================================================
# Category 5: Cross-Track Distance & Corridor Conformance (TC-XTD-13 to TC-XTD-14)
# ===========================================================================

def test_tc_xtd_13_on_designated_corridor():
    """TC-XTD-13: Highway ping with XTD = 100.6m <= 1.5 km -> ON_DESIGNATED_ROUTE."""
    # Route: Gurugram HQ (28.4793, 77.0988) to Alwar (27.5530, 76.6346)
    lat_a, lon_a = 28.4793, 77.0988
    lat_b, lon_b = 27.5530, 76.6346
    ping_lat, ping_lon = 28.068644, 76.890802

    xtd_km = cross_track_distance_km(ping_lat, ping_lon, lat_a, lon_a, lat_b, lon_b)
    xtd_meters = xtd_km * 1000.0
    assert abs(xtd_meters - 100.6) <= 5.0
    assert xtd_km <= 1.5  # within 1.5 km highway corridor


def test_tc_xtd_14_route_deviation_detour():
    """TC-XTD-14: Detour ping diverged to unauthorized town with XTD = 13.86 km > 1.5 km."""
    lat_a, lon_a = 28.4793, 77.0988
    lat_b, lon_b = 27.5530, 76.6346
    detour_lat, detour_lon = 28.118863, 76.762605

    xtd_km = cross_track_distance_km(detour_lat, detour_lon, lat_a, lon_a, lat_b, lon_b)
    assert abs(xtd_km - 13.86) <= 0.5
    assert xtd_km > 1.5  # triggers ROUTE_DEVIATION flag


# ===========================================================================
# Category 6: Anomaly Detection (TC-ANO-15 to TC-ANO-16)
# ===========================================================================

def test_tc_ano_15_unauthorized_stop_anomaly():
    """TC-ANO-15: Stop at highway dhaba for 28 min (> 15 min) outside 5km -> UNAUTHORIZED_STOP."""
    base = {"lat": 30.9010, "lng": 75.8573}
    cust = {"lat": 30.3800, "lng": 76.8405}
    clusters = [
        {
            "cluster_id": "CLUST-DHABA",
            "centroid": {"lat": 30.4840, "lng": 76.5940},  # ~48 km from base, ~37 km from cust
            "total_duration_s": 1680.0  # 28 minutes
        }
    ]
    classified, summary = inspect_journey(clusters, base, cust)
    assert classified[0]["zone_type"] == "UNAUTHORIZED_STOP"
    assert classified[0]["is_anomaly"] is True
    assert summary["unauthorized_seconds"] == 1680.0
    assert "exceeds 15 min" in classified[0]["anomaly_reason"]


def test_tc_ano_16_authorized_toll_stop():
    """TC-ANO-16: Stop at highway toll plaza for 6 min (<= 15 min) -> AUTHORIZED_TRANSIT_STOP."""
    base = {"lat": 30.9010, "lng": 75.8573}
    cust = {"lat": 30.3800, "lng": 76.8405}
    clusters = [
        {
            "cluster_id": "CLUST-TOLL",
            "centroid": {"lat": 30.7000, "lng": 76.2000},  # En route
            "total_duration_s": 360.0  # 6 minutes
        }
    ]
    classified, summary = inspect_journey(clusters, base, cust)
    assert classified[0]["zone_type"] == "AUTHORIZED_TRANSIT_STOP"
    assert classified[0]["is_anomaly"] is False
    assert summary["unauthorized_seconds"] == 0.0


# ===========================================================================
# Category 7: Hours Conservation & Commercial Billing Math (TC-HRS-17 to TC-HRS-18)
# ===========================================================================

def test_tc_hrs_17_conservation_of_hours_law():
    """TC-HRS-17: Full 8.00h shift: Work 5.10h, Travel 2.10h, Idle 0.80h. Error = 0.00000000."""
    t_start = datetime(2026, 9, 22, 8, 0, 0, tzinfo=timezone.utc)
    t_end = datetime(2026, 9, 22, 16, 0, 0, tzinfo=timezone.utc)

    balance = compute_hours_balance(
        shift_start=t_start,
        shift_end=t_end,
        working_seconds=5.10 * 3600.0,
        active_transit_seconds=2.10 * 3600.0,
        unauthorized_seconds=0.80 * 3600.0
    )
    assert balance["shift_hours"] == 8.0
    assert balance["working_hours"] == 5.10
    assert balance["travelling_hours"] == 2.10
    assert balance["idle_hours"] == 0.80
    assert balance["conservation_error"] < 1e-6
    assert abs((balance["working_hours"] + balance["travelling_hours"] + balance["idle_hours"]) - 8.0) < 1e-6
    assert balance["productive_efficiency_pct"] == 63.75
    assert balance["utilization_pct"] == 90.0


def test_tc_hrs_18_weekly_man_day_aggregation():
    """
    TC-HRS-18: Weekly Working Hours Mon-Sat = [6.5, 7.0, 8.0, 8.5, 5.0, 6.0].
    Total = 41.0 hrs. Billable Man-Days = 5.125. Overtime = 1.0 hr.
    """
    daily_hours = [6.5, 7.0, 8.0, 8.5, 5.0, 6.0]
    total_working_hours = sum(daily_hours)
    assert total_working_hours == 41.0

    man_days = total_working_hours / 8.0
    assert man_days == 5.125

    standard_target = 40.0
    overtime_hours = total_working_hours - standard_target
    assert overtime_hours == 1.0

    # RIL AMC Contract additional billing rate: INR 5000 / full man-day
    billable_additional_inr = math.floor(total_working_hours / 8.0) * 5000.0
    assert billable_additional_inr == 25000.0
