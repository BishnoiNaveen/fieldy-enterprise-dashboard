"""
tests/test_adversarial_telematics.py
Adversarial Stress Test Suite for Telematics Engine
Target: backend/app/services/telematics_engine.py
M1 Challenger 1 — Empirical Verification

Categories:
1. High-volume GPS breadcrumbs (1,000 to 5,000 pings)
2. Precision boundary tests (4.999 km vs 5.001 km)
3. Extreme coordinates (North Pole, South Pole, Equator, Antimeridian 180° / -180°)
4. Chaining vulnerability test (single-linkage linear chaining rejection)
5. Micro-moves jitter test (Gaussian noise < 30m odometer drift suppression)
"""

import math
import random
import time
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
import pytest

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.telematics_engine import (
    EARTH_RADIUS_KM,
    STATIONARY_SPEED_KMH,
    JITTER_DEADBAND_METERS,
    MAX_CLUSTER_RADIUS_KM,
    haversine_distance_km,
    initial_bearing_radians,
    cross_track_distance_km,
    weighted_cartesian_centroid,
    filter_stationary_jitter,
    extract_raw_stops,
    cluster_pings_5km,
    inspect_journey,
    compute_hours_balance,
    analyze_route_journey,
)


# ============================================================================
# Category 1: High-Volume GPS Breadcrumbs (1,000 to 5,000 pings)
# ============================================================================

class TestCategory1HighVolumeGPS:
    """Stress tests high-volume GPS breadcrumb feeds (1,000 to 5,000 pings)."""

    def test_adv_01_high_volume_1000_pings_transit_performance(self):
        """1,000 pings through filter_stationary_jitter and analyze_route_journey."""
        start_lat, start_lon = 30.9010, 75.8573
        end_lat, end_lon = 30.3800, 76.8405
        
        pings = []
        base_time = datetime(2026, 9, 22, 8, 0, 0, tzinfo=timezone.utc)
        
        # 100 stationary pings at base
        for i in range(100):
            pings.append({
                "lat": start_lat + random.uniform(-0.0001, 0.0001),
                "lon": start_lon + random.uniform(-0.0001, 0.0001),
                "speed_kmh": 0.0,
                "timestamp": (base_time + timedelta(seconds=i * 10)).isoformat(),
                "timestamp_s": i * 10.0
            })
            
        # 800 moving pings
        for i in range(800):
            frac = i / 800.0
            cur_lat = start_lat + frac * (end_lat - start_lat)
            cur_lon = start_lon + frac * (end_lon - start_lon)
            pings.append({
                "lat": cur_lat,
                "lon": cur_lon,
                "speed_kmh": 55.0 + random.uniform(-5.0, 5.0),
                "timestamp": (base_time + timedelta(seconds=1000 + i * 10)).isoformat(),
                "timestamp_s": 1000.0 + i * 10.0
            })
            
        # 100 stationary pings at destination
        for i in range(100):
            pings.append({
                "lat": end_lat + random.uniform(-0.0001, 0.0001),
                "lon": end_lon + random.uniform(-0.0001, 0.0001),
                "speed_kmh": 0.0,
                "timestamp": (base_time + timedelta(seconds=9000 + i * 10)).isoformat(),
                "timestamp_s": 9000.0 + i * 10.0
            })

        t0 = time.perf_counter()
        filtered, dist_km = filter_stationary_jitter(pings)
        t_jitter = time.perf_counter() - t0

        assert len(filtered) == 1000
        assert dist_km > 50.0  # Real movement measured
        assert t_jitter < 0.5  # Sub-second execution for 1k pings

        # Full journey analysis
        base_coords = {"name": "Ludhiana Depot", "lat": start_lat, "lon": start_lon}
        dest_coords = {"name": "Barwala Job Site", "lat": end_lat, "lon": end_lon}
        
        t1 = time.perf_counter()
        result = analyze_route_journey(pings, base_coords, dest_coords)
        t_total = time.perf_counter() - t1

        assert result["raw_pings_count"] == 1000
        assert len(result["clusters_5km"]) >= 2
        assert t_total < 1.0  # Entire route analysis under 1 second

    def test_adv_02_extreme_volume_5000_pings_scalability(self):
        """5,000 pings stress-testing memory, floating-point stability, and execution time."""
        start_lat, start_lon = 30.9010, 75.8573
        pings = []
        base_time = datetime(2026, 9, 22, 6, 0, 0, tzinfo=timezone.utc)
        
        # 5,000 pings: continuous 12-hour telemetry stream
        for i in range(5000):
            speed = 0.0 if (i % 500 < 100) else (40.0 + (i % 20))
            pings.append({
                "lat": start_lat + (i * 0.0001),
                "lon": start_lon + (i * 0.00008),
                "speed_kmh": speed,
                "timestamp": (base_time + timedelta(seconds=i * 8)).isoformat(),
                "timestamp_s": i * 8.0
            })

        t0 = time.perf_counter()
        filtered, total_km = filter_stationary_jitter(pings)
        t_elapsed = time.perf_counter() - t0

        assert len(filtered) == 5000
        assert not math.isnan(total_km)
        assert not math.isinf(total_km)
        assert t_elapsed < 1.5, f"Jitter filter on 5,000 pings took too long: {t_elapsed:.3f}s"

    def test_adv_03_clustering_500_stops_runtime(self):
        """Stress test cluster_pings_5km on 500 stops to verify stability and polynomial bounds."""
        stops = [
            {
                "lat": 30.0 + (i * 0.0003),
                "lon": 75.0 + (i * 0.0003),
                "duration_s": 600.0,
                "pings_count": 10
            }
            for i in range(500)
        ]
        t0 = time.perf_counter()
        clusters = cluster_pings_5km(stops, max_radius_km=5.0)
        t_elapsed = time.perf_counter() - t0

        assert len(clusters) > 0
        assert t_elapsed < 5.0, f"Clustering 500 stops took {t_elapsed:.2f}s"
        # Invariant: Every point in every cluster is within 5km of its centroid
        for c in clusters:
            c_lat = c["centroid"]["lat"]
            c_lon = c["centroid"]["lng"]
            for s in c["stops"]:
                d = haversine_distance_km(s["lat"], s["lon"], c_lat, c_lon)
                assert d <= 5.00001, f"Point {s} at distance {d} exceeds 5km from centroid {c['centroid']}"

    def test_adv_04_end_to_end_5000_pings_full_journey_analysis(self):
        """Full end-to-end analyze_route_journey with 5,000 pings including stops and movement."""
        base_lat, base_lon = 30.9010, 75.8573
        dest_lat, dest_lon = 30.3800, 76.8405
        base_coords = {"name": "Ludhiana Depot", "lat": base_lat, "lon": base_lon}
        dest_coords = {"name": "Barwala Job Site", "lat": dest_lat, "lon": dest_lon}

        pings = []
        base_time = datetime(2026, 9, 22, 6, 0, 0, tzinfo=timezone.utc)

        # 1,000 pings stationary at base
        for i in range(1000):
            pings.append({
                "lat": base_lat + ((i % 10) * 0.00001),
                "lon": base_lon + ((i % 5) * 0.00001),
                "speed_kmh": 0.0,
                "timestamp": (base_time + timedelta(seconds=i * 5)).isoformat(),
                "timestamp_s": i * 5.0
            })

        # 3,000 pings moving
        for i in range(3000):
            frac = i / 3000.0
            pings.append({
                "lat": base_lat + frac * (dest_lat - base_lat),
                "lon": base_lon + frac * (dest_lon - base_lon),
                "speed_kmh": 50.0 + (i % 10),
                "timestamp": (base_time + timedelta(seconds=5000 + i * 5)).isoformat(),
                "timestamp_s": 5000.0 + i * 5.0
            })

        # 1,000 pings stationary at destination
        for i in range(1000):
            pings.append({
                "lat": dest_lat + ((i % 10) * 0.00001),
                "lon": dest_lon + ((i % 5) * 0.00001),
                "speed_kmh": 0.0,
                "timestamp": (base_time + timedelta(seconds=20000 + i * 5)).isoformat(),
                "timestamp_s": 20000.0 + i * 5.0
            })

        t0 = time.perf_counter()
        result = analyze_route_journey(pings, base_coords, dest_coords)
        t_elapsed = time.perf_counter() - t0

        assert result["raw_pings_count"] == 5000
        assert len(result["clusters_5km"]) >= 2
        assert len(result["route_polyline"]) <= 100  # Properly downsampled
        assert t_elapsed < 3.0, f"Full 5,000 ping analysis took {t_elapsed:.2f}s"


# ============================================================================
# Category 2: Precision Boundary Tests (4.999 km vs 5.001 km)
# ============================================================================

class TestCategory2PrecisionBoundary:
    """Rigorous boundary tests at 4.999 km (must cluster) vs 5.001 km (must separate)."""

    def test_adv_05_meridian_boundary_4999_vs_5001_meters(self):
        """Verify strict clustering split at 5.000 km along north-south meridian."""
        lat0, lon0 = 30.000000, 75.000000
        deg_per_km = 180.0 / (math.pi * EARTH_RADIUS_KM)
        
        delta_lat_4999 = 4.999 * deg_per_km
        delta_lat_5001 = 5.001 * deg_per_km

        p_inside = {"lat": lat0 + delta_lat_4999, "lon": lon0, "duration_s": 3600.0}
        p_outside = {"lat": lat0 + delta_lat_5001, "lon": lon0, "duration_s": 3600.0}

        d_inside = haversine_distance_km(lat0, lon0, p_inside["lat"], p_inside["lon"])
        d_outside = haversine_distance_km(lat0, lon0, p_outside["lat"], p_outside["lon"])

        assert 4.9989 <= d_inside <= 4.9991, f"Expected ~4.999 km, got {d_inside}"
        assert 5.0009 <= d_outside <= 5.0011, f"Expected ~5.001 km, got {d_outside}"

        # Test A: Point at 4.999 km MUST cluster with Anchor
        stops_inside = [
            {"lat": lat0, "lon": lon0, "duration_s": 3600.0},
            p_inside
        ]
        clusters_in = cluster_pings_5km(stops_inside, max_radius_km=5.0)
        assert len(clusters_in) == 1, f"Expected 1 cluster for 4.999 km, got {len(clusters_in)}"
        assert clusters_in[0]["radius_meters"] <= 5000.0

        # Test B: Point at 5.001 km MUST NOT cluster with Anchor
        stops_outside = [
            {"lat": lat0, "lon": lon0, "duration_s": 3600.0},
            p_outside
        ]
        clusters_out = cluster_pings_5km(stops_outside, max_radius_km=5.0)
        assert len(clusters_out) == 2, f"Expected 2 separate clusters for 5.001 km, got {len(clusters_out)}"

    def test_adv_06_parallel_boundary_east_west_at_latitude_45(self):
        """Verify boundary precision along east-west parallel at 45° latitude."""
        lat0, lon0 = 45.000000, 10.000000
        rad_lat = math.radians(lat0)
        deg_lon_per_km = 180.0 / (math.pi * EARTH_RADIUS_KM * math.cos(rad_lat))

        lon_4999 = lon0 + (4.999 * deg_lon_per_km)
        lon_5001 = lon0 + (5.001 * deg_lon_per_km)

        d_in = haversine_distance_km(lat0, lon0, lat0, lon_4999)
        d_out = haversine_distance_km(lat0, lon0, lat0, lon_5001)

        assert abs(d_in - 4.999) < 0.001
        assert abs(d_out - 5.001) < 0.001

        stops_in = [{"lat": lat0, "lon": lon0, "duration_s": 600.0}, {"lat": lat0, "lon": lon_4999, "duration_s": 600.0}]
        stops_out = [{"lat": lat0, "lon": lon0, "duration_s": 600.0}, {"lat": lat0, "lon": lon_5001, "duration_s": 600.0}]

        assert len(cluster_pings_5km(stops_in, max_radius_km=5.0)) == 1
        assert len(cluster_pings_5km(stops_out, max_radius_km=5.0)) == 2

    def test_adv_07_boundary_at_equator(self):
        """Verify boundary precision at Equator (lat 0.0°)."""
        deg_per_km = 180.0 / (math.pi * EARTH_RADIUS_KM)
        
        stops_in = [{"lat": 0.0, "lon": 0.0, "duration_s": 100}, {"lat": 0.0, "lon": 4.999 * deg_per_km, "duration_s": 100}]
        stops_out = [{"lat": 0.0, "lon": 0.0, "duration_s": 100}, {"lat": 0.0, "lon": 5.001 * deg_per_km, "duration_s": 100}]

        assert len(cluster_pings_5km(stops_in, max_radius_km=5.0)) == 1
        assert len(cluster_pings_5km(stops_out, max_radius_km=5.0)) == 2

    def test_adv_08_diagonal_precision_boundary_45_deg_azimuth(self):
        """Precision boundary test at 45° diagonal azimuth: 4.999 km vs 5.001 km."""
        lat0, lon0 = 25.000000, 80.000000
        azimuth = math.radians(45.0)
        
        deg_per_km_lat = 180.0 / (math.pi * EARTH_RADIUS_KM)
        deg_per_km_lon = deg_per_km_lat / math.cos(math.radians(lat0))
        
        d_lat_4999 = 4.999 * math.cos(azimuth) * deg_per_km_lat
        d_lon_4999 = 4.999 * math.sin(azimuth) * deg_per_km_lon

        d_lat_5001 = 5.001 * math.cos(azimuth) * deg_per_km_lat
        d_lon_5001 = 5.001 * math.sin(azimuth) * deg_per_km_lon

        dist_in = haversine_distance_km(lat0, lon0, lat0 + d_lat_4999, lon0 + d_lon_4999)
        dist_out = haversine_distance_km(lat0, lon0, lat0 + d_lat_5001, lon0 + d_lon_5001)

        assert abs(dist_in - 4.999) < 0.005
        assert abs(dist_out - 5.001) < 0.005

        stops_diag_in = [
            {"lat": lat0, "lon": lon0, "duration_s": 600.0},
            {"lat": lat0 + d_lat_4999, "lon": lon0 + d_lon_4999, "duration_s": 600.0}
        ]
        stops_diag_out = [
            {"lat": lat0, "lon": lon0, "duration_s": 600.0},
            {"lat": lat0 + d_lat_5001, "lon": lon0 + d_lon_5001, "duration_s": 600.0}
        ]

        assert len(cluster_pings_5km(stops_diag_in, max_radius_km=5.0)) == 1
        assert len(cluster_pings_5km(stops_diag_out, max_radius_km=5.0)) == 2


# ============================================================================
# Category 3: Extreme Coordinates (Poles, Equator, Antimeridian)
# ============================================================================

class TestCategory3ExtremeCoordinates:
    """Adversarial testing at North Pole, South Pole, Equator, and Antimeridian."""

    def test_adv_09_north_pole_convergence_and_clustering(self):
        """North pole: all longitudes meet at 90.0° N. Distance between (90, 0) and (90, 180) is ~0.0."""
        d_same_pole = haversine_distance_km(90.0, 0.0, 90.0, 180.0)
        assert abs(d_same_pole) < 1e-9, f"Expected ~0.0 km, got {d_same_pole}"

        deg_per_km = 180.0 / (math.pi * EARTH_RADIUS_KM)
        lat_1km_south = 90.0 - (1.0 * deg_per_km)

        d_across_pole = haversine_distance_km(lat_1km_south, 0.0, lat_1km_south, 180.0)
        assert abs(d_across_pole - 2.0) < 0.01

        stops = [
            {"lat": lat_1km_south, "lon": 0.0, "duration_s": 1800.0},
            {"lat": lat_1km_south, "lon": 180.0, "duration_s": 1800.0},
            {"lat": 90.0, "lon": 0.0, "duration_s": 3600.0}
        ]
        clusters = cluster_pings_5km(stops, max_radius_km=5.0)
        assert len(clusters) == 1
        assert not math.isnan(clusters[0]["centroid"]["lat"])
        assert not math.isnan(clusters[0]["centroid"]["lng"])

    def test_adv_10_south_pole_cartesian_centroid(self):
        """South Pole: weighted_cartesian_centroid at -90.0° must not divide by zero."""
        stops = [
            {"lat": -90.0, "lon": 0.0, "duration_s": 1000.0},
            {"lat": -90.0, "lon": 90.0, "duration_s": 2000.0},
            {"lat": -90.0, "lon": -90.0, "duration_s": 1000.0}
        ]
        c_lat, c_lon = weighted_cartesian_centroid(stops)
        assert c_lat == -90.0
        assert not math.isnan(c_lon)

    def test_adv_11_antimeridian_crossing_haversine_and_clustering(self):
        """Points spanning longitude +179.99° and -179.99° across the 180° antimeridian."""
        lat = 10.0
        lon_west = 179.990000   # Just west of 180°
        lon_east = -179.990000  # Just east of -180°
        
        d = haversine_distance_km(lat, lon_west, lat, lon_east)
        assert d < 3.0, f"Antimeridian distance failed: got {d} km instead of ~2.19 km"

        stops = [
            {"lat": lat, "lon": lon_west, "duration_s": 3600.0},
            {"lat": lat, "lon": lon_east, "duration_s": 3600.0}
        ]
        c_lat, c_lon = weighted_cartesian_centroid(stops)
        assert abs(c_lat - lat) < 1e-4
        assert abs(abs(c_lon) - 180.0) < 1e-4, f"Centroid longitude should be ±180.0, got {c_lon}"

        clusters = cluster_pings_5km(stops, max_radius_km=5.0)
        assert len(clusters) == 1
        assert clusters[0]["radius_meters"] <= 5000.0

    def test_adv_12_bearing_and_cross_track_at_extreme_coordinates(self):
        """Cross-track distance and bearing across antimeridian and near poles."""
        xtd = cross_track_distance_km(0.01, 180.0, 0.0, 179.0, 0.0, -179.0)
        assert not math.isnan(xtd)
        assert xtd < 2.0

        xtd_zero = cross_track_distance_km(10.0, 10.0, 10.0, 10.0, 10.0, 10.0)
        assert xtd_zero == 0.0
        assert not math.isnan(xtd_zero)

    def test_adv_13_multi_cross_antimeridian_polyline(self):
        """Route zigzagging across the 180° antimeridian (+179.98 to -179.98)."""
        pings = [
            {"lat": 0.0, "lon": 179.98, "speed_kmh": 60.0, "timestamp_s": 0.0},
            {"lat": 0.0, "lon": -179.98, "speed_kmh": 60.0, "timestamp_s": 60.0},
            {"lat": 0.0, "lon": 179.99, "speed_kmh": 60.0, "timestamp_s": 120.0},
            {"lat": 0.0, "lon": -179.99, "speed_kmh": 60.0, "timestamp_s": 180.0},
        ]
        filtered, total_km = filter_stationary_jitter(pings)
        assert 10.0 < total_km < 16.0, f"Antimeridian journey distance wrong: {total_km} km"


# ============================================================================
# Category 4: Chaining Vulnerability Test (Rejection of Single-Linkage Chaining)
# ============================================================================

class TestCategory4ChainingVulnerability:
    """Verifies that the algorithm DOES NOT chain points linearly beyond 5.0 km radius."""

    def test_adv_14_linear_chain_10_points_3km_spacing(self):
        """
        Adversarial chain: 10 points placed in a straight line, each 3.0 km from previous.
        Total span: 27.0 km. Rejects single-linkage chaining; strictly partitions into >= 3 clusters.
        """
        deg_per_km = 180.0 / (math.pi * EARTH_RADIUS_KM)
        lat0, lon0 = 30.0, 75.0
        
        stops = [
            {
                "lat": lat0 + (i * 3.0 * deg_per_km),
                "lon": lon0,
                "duration_s": 3600.0,
                "location_name": f"Chain Point {i}"
            }
            for i in range(10)
        ]

        clusters = cluster_pings_5km(stops, max_radius_km=5.0)

        assert len(clusters) > 1, f"Chaining vulnerability detected! Merged into {len(clusters)} cluster."
        assert len(clusters) >= 3, f"Expected at least 3 clusters for 27km span, got {len(clusters)}"

        for c in clusters:
            c_lat = c["centroid"]["lat"]
            c_lon = c["centroid"]["lng"]
            assert c["radius_meters"] <= 5000.0
            for s in c["stops"]:
                d = haversine_distance_km(s["lat"], s["lon"], c_lat, c_lon)
                assert d <= 5.00001, f"Radius violation: {d:.4f} km from centroid"

    def test_adv_15_dense_continuous_chain_50_points_500m_spacing(self):
        """Dense chain: 50 points spaced 500m apart over a 24.5 km corridor."""
        deg_per_km = 180.0 / (math.pi * EARTH_RADIUS_KM)
        lat0, lon0 = 31.0, 76.0
        
        stops = [
            {
                "lat": lat0 + (i * 0.5 * deg_per_km),
                "lon": lon0,
                "duration_s": 600.0,
                "pings_count": 5
            }
            for i in range(50)
        ]

        clusters = cluster_pings_5km(stops, max_radius_km=5.0)
        assert len(clusters) >= 3, f"Expected at least 3 clusters for 24.5 km span, got {len(clusters)}"

        for c in clusters:
            assert c["radius_meters"] <= 5000.0
            c_lat = c["centroid"]["lat"]
            c_lon = c["centroid"]["lng"]
            for s in c["stops"]:
                d = haversine_distance_km(s["lat"], s["lon"], c_lat, c_lon)
                assert d <= 5.00001

    def test_adv_16_star_constellation_hub_and_spoke(self):
        """Hub-and-spoke: 1 central hub with 8 peripheral stops 4.5 km away in 8 directions (9.0 km span)."""
        lat0, lon0 = 30.5, 76.0
        deg_per_km = 180.0 / (math.pi * EARTH_RADIUS_KM)
        
        stops = [
            {"lat": lat0, "lon": lon0, "duration_s": 36000.0, "pings_count": 100}
        ]
        for angle_deg in [0, 45, 90, 135, 180, 225, 270, 315]:
            rad = math.radians(angle_deg)
            d_lat = 4.5 * math.cos(rad) * deg_per_km
            d_lon = 4.5 * math.sin(rad) * deg_per_km / math.cos(math.radians(lat0))
            stops.append({
                "lat": lat0 + d_lat,
                "lon": lon0 + d_lon,
                "duration_s": 600.0,
                "pings_count": 5
            })

        clusters = cluster_pings_5km(stops, max_radius_km=5.0)
        assert len(clusters) == 1, f"Star constellation within 4.5 km should merge to 1 cluster, got {len(clusters)}"
        assert clusters[0]["radius_meters"] <= 5000.0
        assert clusters[0]["pings_count"] == 140

    def test_adv_17_chaining_rejection_under_reversed_order(self):
        """Verify chaining is rejected regardless of input order (reversed array)."""
        deg_per_km = 180.0 / (math.pi * EARTH_RADIUS_KM)
        lat0, lon0 = 29.0, 74.0
        
        stops = [
            {"lat": lat0 + (i * 2.5 * deg_per_km), "lon": lon0, "duration_s": 1200.0}
            for i in range(12)
        ]

        stops_rev = list(reversed(stops))
        clusters_rev = cluster_pings_5km(stops_rev, max_radius_km=5.0)
        for c in clusters_rev:
            assert c["radius_meters"] <= 5000.0
            for s in c["stops"]:
                d = haversine_distance_km(s["lat"], s["lon"], c["centroid"]["lat"], c["centroid"]["lng"])
                assert d <= 5.00001

    def test_adv_18_chaining_rejection_100_points_linear_array(self):
        """Massive linear chain: 100 points placed 1.0 km apart over a 99 km highway corridor."""
        deg_per_km = 180.0 / (math.pi * EARTH_RADIUS_KM)
        lat0, lon0 = 28.0, 77.0
        
        stops = [
            {"lat": lat0 + (i * 1.0 * deg_per_km), "lon": lon0, "duration_s": 600.0, "pings_count": 10}
            for i in range(100)
        ]

        clusters = cluster_pings_5km(stops, max_radius_km=5.0)
        assert len(clusters) >= 10, f"Expected >= 10 clusters for 99km corridor, got {len(clusters)}"

        for c in clusters:
            c_lat = c["centroid"]["lat"]
            c_lon = c["centroid"]["lng"]
            assert c["radius_meters"] <= 5000.0
            for s in c["stops"]:
                d = haversine_distance_km(s["lat"], s["lon"], c_lat, c_lon)
                assert d <= 5.00001


# ============================================================================
# Category 5: Micro-Moves Jitter Test (Stationary Pings with Noise < 30m)
# ============================================================================

class TestCategory5MicroMovesJitter:
    """Verifies stationary pings with random Gaussian noise < 30m do not create spurious odometer drift."""

    def test_adv_19_pure_stationary_gaussian_noise_zero_drift(self):
        """500 stationary pings with random Gaussian noise (< 28m displacement). Odometer must be 0.000 km."""
        anchor_lat, anchor_lon = 30.901000, 75.857300
        deg_per_meter = 180.0 / (math.pi * EARTH_RADIUS_KM * 1000.0)
        
        pings = [{"lat": anchor_lat, "lon": anchor_lon, "speed_kmh": 0.0, "timestamp_s": 0.0}]
        random.seed(42)
        
        for i in range(1, 500):
            r = min(28.0, abs(random.gauss(8.0, 5.0)))
            theta = random.uniform(0, 2 * math.pi)
            noise_x = r * math.cos(theta)
            noise_y = r * math.sin(theta)
            
            pings.append({
                "lat": anchor_lat + (noise_y * deg_per_meter),
                "lon": anchor_lon + (noise_x * deg_per_meter / math.cos(math.radians(anchor_lat))),
                "speed_kmh": abs(random.gauss(0.2, 0.1)),
                "timestamp_s": i * 10.0
            })

        filtered, total_distance_km = filter_stationary_jitter(pings, min_speed_kmh=1.5, deadband_meters=30.0)

        assert len(filtered) == 500
        assert total_distance_km == 0.0, f"Odometer drift detected! Expected 0.0 km, got {total_distance_km} km"
        for p in filtered:
            assert p["lat"] == anchor_lat
            assert p["lon"] == anchor_lon
            assert p["is_stationary"] is True

    def test_adv_20_tripartite_shift_zero_drift_during_extended_halts(self):
        """
        Full shift with 3 phases:
        Phase 1: 3 hours stationary at base depot with Gaussian jitter (180 pings).
        Phase 2: 1 hour transit driving 60 km at 60 km/h (60 pings).
        Phase 3: 4 hours stationary at customer field with Gaussian jitter (240 pings).
        """
        base_lat, base_lon = 30.901000, 75.857300
        dest_lat, dest_lon = 30.380000, 76.840500
        deg_per_meter = 180.0 / (math.pi * EARTH_RADIUS_KM * 1000.0)

        pings = []
        random.seed(99)

        # Phase 1: 180 pings at base depot (3 hrs)
        for i in range(180):
            nx = max(-22.0, min(22.0, random.gauss(0.0, 5.0)))
            ny = max(-22.0, min(22.0, random.gauss(0.0, 5.0)))
            pings.append({
                "lat": base_lat + (ny * deg_per_meter),
                "lon": base_lon + (nx * deg_per_meter / math.cos(math.radians(base_lat))),
                "speed_kmh": 0.1,
                "timestamp_s": i * 60.0
            })

        # Phase 2: 60 pings transit from base to dest (1 hr at 60 km/h)
        for i in range(1, 61):
            f = i / 60.0
            cur_lat = base_lat + f * (dest_lat - base_lat)
            cur_lon = base_lon + f * (dest_lon - base_lon)
            pings.append({
                "lat": cur_lat,
                "lon": cur_lon,
                "speed_kmh": 60.0,
                "timestamp_s": 10800.0 + (i * 60.0)
            })

        # Phase 3: 240 pings at customer field (4 hrs)
        for i in range(240):
            nx = max(-22.0, min(22.0, random.gauss(0.0, 5.0)))
            ny = max(-22.0, min(22.0, random.gauss(0.0, 5.0)))
            pings.append({
                "lat": dest_lat + (ny * deg_per_meter),
                "lon": dest_lon + (nx * deg_per_meter / math.cos(math.radians(dest_lat))),
                "speed_kmh": 0.05,
                "timestamp_s": 14400.0 + (i * 60.0)
            })

        filtered, total_km = filter_stationary_jitter(pings, min_speed_kmh=1.5, deadband_meters=30.0)
        true_transit_km = haversine_distance_km(base_lat, base_lon, dest_lat, dest_lon)

        dist_diff = abs(total_km - true_transit_km)
        assert dist_diff < 0.5, f"Spurious odometer drift detected! total_km={total_km}, true_transit={true_transit_km}, diff={dist_diff}"

        stops = extract_raw_stops(filtered, min_stop_duration_s=300.0)
        assert len(stops) == 2, f"Expected exactly 2 stops, got {len(stops)}"

    def test_adv_21_deadband_exact_boundary_29m_vs_31m(self):
        """Test exact deadband threshold: 29.0m (snaps to anchor) vs 31.0m (resets anchor)."""
        anchor_lat, anchor_lon = 30.000000, 75.000000
        deg_per_meter = 180.0 / (math.pi * EARTH_RADIUS_KM * 1000.0)

        p_29m = {
            "lat": anchor_lat + (29.0 * deg_per_meter),
            "lon": anchor_lon,
            "speed_kmh": 0.5,
            "timestamp_s": 60.0
        }
        p_31m = {
            "lat": anchor_lat + (31.0 * deg_per_meter),
            "lon": anchor_lon,
            "speed_kmh": 0.5,
            "timestamp_s": 120.0
        }

        # Sequence 1: anchor + 29m ping -> snapped to anchor
        pings_seq1 = [{"lat": anchor_lat, "lon": anchor_lon, "speed_kmh": 0.0, "timestamp_s": 0.0}, p_29m]
        filtered1, dist1 = filter_stationary_jitter(pings_seq1, min_speed_kmh=1.5, deadband_meters=30.0)
        assert dist1 == 0.0
        assert filtered1[1]["lat"] == anchor_lat
        assert filtered1[1]["is_stationary"] is True

        # Sequence 2: anchor + 31m ping -> exceeds deadband, resets anchor, but STILL stationary (speed < 1.5)
        pings_seq2 = [{"lat": anchor_lat, "lon": anchor_lon, "speed_kmh": 0.0, "timestamp_s": 0.0}, p_31m]
        filtered2, dist2 = filter_stationary_jitter(pings_seq2, min_speed_kmh=1.5, deadband_meters=30.0)
        assert dist2 == 0.0
        assert filtered2[1]["lat"] == p_31m["lat"]
        assert filtered2[1]["is_stationary"] is True

    def test_adv_22_large_spread_noise_zero_odometer_drift(self):
        """Stationary pings with high variance noise (sigma=15m, some > 30m) at 0 km/h: zero odometer drift."""
        anchor_lat, anchor_lon = 30.000000, 75.000000
        deg_per_meter = 180.0 / (math.pi * EARTH_RADIUS_KM * 1000.0)

        pings = [{"lat": anchor_lat, "lon": anchor_lon, "speed_kmh": 0.0, "timestamp_s": 0.0}]
        random.seed(123)

        for i in range(1, 300):
            nx = random.gauss(0.0, 15.0)
            ny = random.gauss(0.0, 15.0)
            pings.append({
                "lat": anchor_lat + (ny * deg_per_meter),
                "lon": anchor_lon + (nx * deg_per_meter / math.cos(math.radians(anchor_lat))),
                "speed_kmh": 0.0,
                "timestamp_s": i * 10.0
            })

        filtered, total_km = filter_stationary_jitter(pings, min_speed_kmh=1.5, deadband_meters=30.0)

        assert total_km == 0.0, f"Odometer drift detected under stationary conditions: {total_km} km"
        assert all(p["is_stationary"] is True for p in filtered)
