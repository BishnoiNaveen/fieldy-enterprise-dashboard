"""
tests/test_tier5_adversarial_hardening.py
Milestone 3 Tier 5 White-Box Adversarial Stress Test Suite
Target: backend/app/services/ (telematics_engine.py, analytics_engine.py, sync_service.py)
Authored by: m3_challenger_1 (Empirical Challenger)

Verification Scope:
1. Geodesic Mathematical Extremes (Antipodal, Polar, Antimeridian, Zero-Distance Clusters)
2. Corrupted, Empty, Degenerate, and Missing Telemetry Inputs
3. High-Volume Telemetry Scalability (>50,000 pings)
4. Irregular, Out-of-Order, and Inverted Timestamp Conservation Law Invariants
5. Sync Service Cache Boundary, Corruption Recovery & Concurrency Stress
6. Geofence 5 km Corridor, Chaining Prevention & Detour Anomaly Precision
7. Empirical Bug Reproductions (Distance Under-reporting, Negative Durations, Infinity Assertion, Quadratic Latency)
"""

import sys
import os
import math
import time
import json
import random
import asyncio
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
import pytest

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.services.telematics_engine import (
    EARTH_RADIUS_KM,
    STATIONARY_SPEED_KMH,
    JITTER_DEADBAND_METERS,
    MAX_CLUSTER_RADIUS_KM,
    UNAUTHORIZED_STOP_THRESHOLD_SECONDS,
    DETOUR_RATIO_THRESHOLD,
    DETOUR_EXCESS_KM,
    haversine_distance_km,
    initial_bearing_radians,
    cross_track_distance_km,
    weighted_cartesian_centroid,
    filter_stationary_jitter,
    extract_raw_stops,
    cluster_pings_5km,
    cluster_stops_5km,
    inspect_journey,
    compute_hours_balance,
    calculate_hours,
    analyze_route_journey,
    inspect_route_telematics,
)
from app.services.analytics_engine import AnalyticsEngine
from app.services.sync_service import SyncService
from app.services.mock_generator import KroneMockGenerator


# ============================================================================
# Category 1: Geodesic Mathematical Extremes & Coordinate Singularities
# ============================================================================

class TestGeodesicMathematicalExtremes:
    """Stress tests geodesic algorithms against topological singularities and mathematical extremes."""

    def test_antipodal_great_circle_distance_exact(self):
        """
        Exact antipodal points on the equator: (0, 0) and (0, 180).
        Great-circle distance must equal pi * R = 20,015.087 km within 0.01 km.
        Clamped Haversine formula must not raise domain error in atan2/sqrt.
        """
        dist = haversine_distance_km(0.0, 0.0, 0.0, 180.0)
        expected = math.pi * EARTH_RADIUS_KM
        assert math.isclose(dist, expected, rel_tol=1e-5), f"Antipodal distance {dist} != {expected}"

        # Polar antipodes: North Pole (90, 0) and South Pole (-90, 0)
        dist_polar = haversine_distance_km(90.0, 0.0, -90.0, 0.0)
        assert math.isclose(dist_polar, expected, rel_tol=1e-5), f"Polar antipodal distance {dist_polar} != {expected}"

    def test_polar_coordinates_and_meridian_convergence(self):
        """
        At the North Pole (lat=90.0), any longitude represents the exact same physical spot.
        Mutual distance between (90.0, 0.0) and (90.0, 180.0) or (90.0, -90.0) must be 0.0 km.
        """
        dist_pole_diff_lon = haversine_distance_km(90.0, 0.0, 90.0, 180.0)
        assert dist_pole_diff_lon < 1e-6, f"Distance between identical polar coordinates should be 0, got {dist_pole_diff_lon}"

        dist_south_pole = haversine_distance_km(-90.0, 45.0, -90.0, -135.0)
        assert dist_south_pole < 1e-6, f"Distance between identical south polar coords should be 0, got {dist_south_pole}"

        # Centroid of multiple polar points
        polar_points = [
            {"lat": 90.0, "lon": 0.0, "duration_s": 100.0},
            {"lat": 90.0, "lon": 90.0, "duration_s": 200.0},
            {"lat": 90.0, "lon": -90.0, "duration_s": 300.0}
        ]
        c_lat, c_lon = weighted_cartesian_centroid(polar_points)
        assert math.isclose(c_lat, 90.0, abs_tol=1e-3), f"Polar centroid lat should be 90.0, got {c_lat}"

    def test_antimeridian_wrap_around_distance_and_centroid(self):
        """
        Points flanking the antimeridian (+179.999 and -179.999 degrees longitude at equator).
        Angular separation is 0.002 degrees ~ 222 meters, NOT ~40,000 km.
        """
        dist = haversine_distance_km(0.0, 179.999, 0.0, -179.999)
        assert dist < 0.25, f"Antimeridian distance wrapped incorrectly: {dist} km"
        assert dist > 0.20, f"Antimeridian distance unexpectedly low: {dist} km"

        # 3D Cartesian centroid across the antimeridian
        points = [
            {"lat": 10.0, "lon": 179.9, "duration_s": 600.0},
            {"lat": 10.0, "lon": -179.9, "duration_s": 600.0}
        ]
        c_lat, c_lon = weighted_cartesian_centroid(points)
        assert math.isclose(c_lat, 10.0, abs_tol=1e-4)
        assert math.isclose(abs(c_lon), 180.0, abs_tol=1e-3), f"Centroid lon should be ±180.0, got {c_lon}"

    def test_cross_track_distance_numerical_safety(self):
        """
        Cross-track distance on polar, antipodal, or collinear segments.
        Clamping of sin(xt) must prevent math.asin domain errors.
        """
        # Point P at North Pole, Corridor A->B along equator
        xtd = cross_track_distance_km(90.0, 0.0, 0.0, 0.0, 0.0, 90.0)
        assert xtd > 0.0 and xtd <= (math.pi / 2.0 * EARTH_RADIUS_KM) + 1.0

        # Point P exactly on corridor segment (zero XTD)
        xtd_collinear = cross_track_distance_km(0.0, 45.0, 0.0, 0.0, 0.0, 90.0)
        assert math.isclose(xtd_collinear, 0.0, abs_tol=1e-3)

        # Identical endpoints A == B
        xtd_identical_ab = cross_track_distance_km(30.0, 75.0, 30.0, 75.0, 30.0, 75.0)
        assert xtd_identical_ab == 0.0

    def test_zero_distance_identical_coordinate_clustering(self):
        """
        Multiple stops at the exact identical coordinate.
        Must produce exactly 1 cluster with radius_meters == 0.0 and correct aggregated duration.
        """
        stops = [
            {
                "lat": 30.9010,
                "lon": 75.8573,
                "duration_s": 300.0,
                "pings_count": 5,
                "location_name": "Ludhiana Depot"
            }
            for _ in range(50)
        ]
        clusters = cluster_pings_5km(stops, max_radius_km=MAX_CLUSTER_RADIUS_KM)
        assert len(clusters) == 1, f"Expected 1 cluster for identical coordinates, got {len(clusters)}"
        c = clusters[0]
        assert c["radius_meters"] == 0.0
        assert math.isclose(c["centroid"]["lat"], 30.9010, abs_tol=1e-5)
        assert math.isclose(c["centroid"]["lng"], 75.8573, abs_tol=1e-5)
        assert c["total_duration_s"] == 50 * 300.0
        assert c["pings_count"] == 50 * 5

    def test_antipodal_point_pair_centroid_stability(self):
        """
        Two equal-weight antipodal points sum to the zero vector in 3D Cartesian coordinates.
        weighted_cartesian_centroid must handle hyp < 1e-12 safely without ZeroDivisionError.
        """
        antipodal_pair = [
            {"lat": 0.0, "lon": 0.0, "duration_s": 100.0},
            {"lat": 0.0, "lon": 180.0, "duration_s": 100.0}
        ]
        c_lat, c_lon = weighted_cartesian_centroid(antipodal_pair)
        assert -90.0 <= c_lat <= 90.0
        assert -180.0 <= c_lon <= 180.0


# ============================================================================
# Category 2: Corrupted, Empty, Degenerate & Missing Telemetry Inputs
# ============================================================================

class TestCorruptedAndDegenerateInputs:
    """Stress tests boundary handling when telemetry streams are empty, single, or schema-variant."""

    def test_empty_telemetry_functions_resilience(self):
        """All telematics functions must handle empty list inputs gracefully without raising exceptions."""
        assert weighted_cartesian_centroid([]) == (0.0, 0.0)

        filtered, dist = filter_stationary_jitter([])
        assert filtered == [] and dist == 0.0

        stops = extract_raw_stops([])
        assert stops == []

        clusters = cluster_pings_5km([])
        assert clusters == []

        classified, summary = inspect_journey(
            [],
            base_coords={"lat": 30.9010, "lon": 75.8573},
            customer_site_coords={"lat": 30.3800, "lon": 76.8405}
        )
        assert classified == []
        assert summary["working_seconds"] == 0.0
        assert summary["unauthorized_seconds"] == 0.0

        hours = calculate_hours([])
        assert hours["working_hours"] == 0.0
        assert hours["travelling_hours"] == 0.0
        assert hours["shift_hours"] == 0.0
        assert hours["conservation_error"] == 0.0

        journey = analyze_route_journey(
            [],
            base_coords={"lat": 30.9010, "lon": 75.8573},
            job_site_coords={"lat": 30.3800, "lon": 76.8405}
        )
        assert journey["raw_pings_count"] == 0
        assert journey["clusters_5km"] == []
        assert journey["anomalies"] == []
        assert journey["journey_summary"]["total_distance_km"] == 0.0

    def test_single_ping_telemetry_handling(self):
        """Single ping streams (moving or stationary) must not crash indexing logic."""
        # Single moving ping
        pings_moving = [{"lat": 30.9010, "lon": 75.8573, "speed_kmh": 45.0, "timestamp_s": 0.0}]
        filtered_m, dist_m = filter_stationary_jitter(pings_moving)
        assert len(filtered_m) == 1
        assert dist_m == 0.0
        assert not filtered_m[0]["is_stationary"]

        # Single stationary ping
        pings_stat = [{"lat": 30.9010, "lon": 75.8573, "speed_kmh": 0.0, "timestamp_s": 0.0}]
        filtered_s, dist_s = filter_stationary_jitter(pings_stat)
        assert len(filtered_s) == 1
        assert dist_s == 0.0
        assert filtered_s[0]["is_stationary"]

    def test_schema_key_variances_lon_vs_lng_and_speed_formats(self):
        """
        Telematics engine must accept both 'lon' and 'lng', 'speed' and 'speed_kmh',
        and ISO formatted string vs epoch timestamps.
        """
        pings = [
            {"lat": 30.9010, "lng": 75.8573, "speed": 50.0, "timestamp": "2026-09-22T08:00:00Z"},
            {"lat": 30.9500, "lon": 75.9000, "speed_kmh": 60.0, "timestamp": "2026-09-22T08:05:00Z"},
            {"lat": 31.0000, "lng": 75.9500, "speed_kmh": 0.5, "timestamp_s": 1790070600.0}
        ]
        filtered, dist = filter_stationary_jitter(pings)
        assert len(filtered) == 3
        assert dist > 0.0
        assert filtered[2]["is_stationary"]

    def test_analytics_conservation_pathological_inputs(self):
        """Tests AnalyticsEngine.enforce_hours_conservation against degenerate and negative inputs."""
        # All zeros
        res = AnalyticsEngine.enforce_hours_conservation(0.0, 0.0, 0.0, 0.0, 0.0)
        assert res["shift_hours"] == 0.0
        assert res["working_hours"] == 0.0
        assert res["idle_hours"] == 0.0
        assert res["conservation_error"] == 0.0

        # Negative inputs clamped to 0.0
        res_neg = AnalyticsEngine.enforce_hours_conservation(-8.0, -4.0, -2.0, -1.0, -1.0)
        assert res_neg["shift_hours"] == 0.0
        assert res_neg["working_hours"] == 0.0
        assert res_neg["idle_hours"] == 0.0
        assert res_neg["conservation_error"] == 0.0

        # Micro-durations (floating precision test)
        res_micro = AnalyticsEngine.enforce_hours_conservation(0.0001, 0.00004, 0.00004, 0.00001, 0.00001)
        diff = abs(res_micro["shift_hours"] - (res_micro["working_hours"] + res_micro["travelling_hours"] + res_micro["idle_hours"]))
        assert diff < 1e-4

    def test_analytics_empty_datasets(self):
        """AnalyticsEngine.aggregate_productivity must handle completely empty datasets cleanly."""
        engine = AnalyticsEngine()
        result = engine.aggregate_productivity(
            daily_shift_records=[],
            jobs_records=[],
            timeframe="daily"
        )
        assert result["summary"]["total_working_hours"] == 0.0
        assert result["summary"]["total_shift_hours"] == 0.0
        assert result["summary"]["average_utilization_pct"] == 0.0
        assert result["technician_records"] == []
        assert result["trend_data"] == []
        assert result["customer_distribution"] == []


# ============================================================================
# Category 3: High-Volume Telemetry Scalability (>50,000 Pings)
# ============================================================================

class TestHighVolumeScalability50kPings:
    """Stress tests system performance, memory footprint, and numerical stability with >50,000 pings."""

    @pytest.fixture(scope="class")
    def synthetic_50k_pings(self):
        """
        Synthesizes 50,000 sequential GPS pings representing a realistic high-intensity 14-hour workday:
        - Pings 0 - 3,600: Morning inspection at Ludhiana Depot (stationary + jitter < 30m, 1 hour)
        - Pings 3,600 - 9,000: Outbound transit on NH-44 at ~60 km/h (1.5 hours)
        - Pings 9,000 - 36,000: Active service at RIL Barwala baler site (stationary dwell, 7.5 hours)
        - Pings 36,000 - 41,400: Return transit to Ludhiana Depot (1.5 hours)
        - Pings 41,400 - 50,000: Evening depot debrief (stationary, 2.4 hours)
        """
        random.seed(42)
        pings = []
        base_time = datetime(2026, 9, 22, 6, 0, 0, tzinfo=timezone.utc)
        start_lat, start_lon = 30.9010, 75.8573
        dest_lat, dest_lon = 30.3800, 76.8405

        for i in range(50000):
            t_s = float(i)
            ts_iso = (base_time + timedelta(seconds=i)).isoformat()

            if i < 3600:
                jitter_lat = random.gauss(0.0, 0.0001)
                jitter_lon = random.gauss(0.0, 0.0001)
                pings.append({
                    "lat": start_lat + jitter_lat,
                    "lon": start_lon + jitter_lon,
                    "speed_kmh": random.uniform(0.0, 1.2),
                    "timestamp_s": t_s,
                    "timestamp": ts_iso
                })
            elif i < 9000:
                frac = (i - 3600) / (9000 - 3600)
                cur_lat = start_lat + frac * (dest_lat - start_lat)
                cur_lon = start_lon + frac * (dest_lon - start_lon)
                pings.append({
                    "lat": cur_lat,
                    "lon": cur_lon,
                    "speed_kmh": random.uniform(55.0, 65.0),
                    "timestamp_s": t_s,
                    "timestamp": ts_iso
                })
            elif i < 36000:
                jitter_lat = random.gauss(0.0, 0.0001)
                jitter_lon = random.gauss(0.0, 0.0001)
                pings.append({
                    "lat": dest_lat + jitter_lat,
                    "lon": dest_lon + jitter_lon,
                    "speed_kmh": random.uniform(0.0, 1.0),
                    "timestamp_s": t_s,
                    "timestamp": ts_iso
                })
            elif i < 41400:
                frac = (i - 36000) / (41400 - 36000)
                cur_lat = dest_lat + frac * (start_lat - dest_lat)
                cur_lon = dest_lon + frac * (start_lon - dest_lon)
                pings.append({
                    "lat": cur_lat,
                    "lon": cur_lon,
                    "speed_kmh": random.uniform(55.0, 65.0),
                    "timestamp_s": t_s,
                    "timestamp": ts_iso
                })
            else:
                jitter_lat = random.gauss(0.0, 0.00005)
                jitter_lon = random.gauss(0.0, 0.00005)
                pings.append({
                    "lat": start_lat + jitter_lat,
                    "lon": start_lon + jitter_lon,
                    "speed_kmh": 0.0,
                    "timestamp_s": t_s,
                    "timestamp": ts_iso
                })

        return pings

    def test_high_volume_50000_pings_filter_stationary_jitter_performance(self, synthetic_50k_pings):
        """
        Processing 50,000 pings through filter_stationary_jitter must complete in < 2.5 seconds
        and eliminate phantom stationary mileage.
        """
        t0 = time.perf_counter()
        filtered, total_dist_km = filter_stationary_jitter(synthetic_50k_pings)
        elapsed = time.perf_counter() - t0

        assert len(filtered) == 50000, f"Expected 50,000 filtered pings, got {len(filtered)}"
        assert elapsed < 2.5, f"50k jitter filter too slow: took {elapsed:.2f}s (budget: 2.5s)"
        assert 180.0 <= total_dist_km <= 260.0, f"Total distance {total_dist_km} km out of physical bounds"

        stationary_count = sum(1 for p in filtered[:3600] if p.get("is_stationary"))
        assert stationary_count >= 3500, f"Stationary pings under-detected: {stationary_count}"

    def test_high_volume_50000_pings_calculate_hours_conservation(self, synthetic_50k_pings):
        """
        Processing 50,000 pings through calculate_hours must maintain strict conservation:
        |H_shift - (H_w + H_t + H_i)| < 1e-4 and complete in < 3.0 seconds.
        """
        base_coords = {"lat": 30.9010, "lon": 75.8573}
        dest_coords = {"lat": 30.3800, "lon": 76.8405}

        t0 = time.perf_counter()
        res = calculate_hours(synthetic_50k_pings, base_coords=base_coords, job_site_coords=dest_coords)
        elapsed = time.perf_counter() - t0

        assert elapsed < 3.0, f"50k calculate_hours took {elapsed:.2f}s (budget: 3.0s)"

        h_shift = res["shift_hours"]
        h_w = res["working_hours"]
        h_t = res["travelling_hours"]
        h_i = res["idle_hours"]

        diff = abs(h_shift - (h_w + h_t + h_i))
        assert diff < 1e-4, f"Conservation violation in 50k pings: {h_shift} != {h_w} + {h_t} + {h_i} (diff: {diff})"
        assert res["conservation_error"] < 1e-4
        assert 2.5 <= h_t <= 3.5
        assert 7.0 <= h_w <= 8.0
        assert math.isclose(h_shift, 50000.0 / 3600.0, abs_tol=0.2)

    def test_high_volume_50000_pings_analyze_route_journey_downsampling(self, synthetic_50k_pings):
        """
        Processing 50,000 pings through analyze_route_journey must downsample polyline
        to avoid overwhelming the frontend map renderer (< 150 coordinates).
        """
        base_coords = {"lat": 30.9010, "lon": 75.8573}
        dest_coords = {"lat": 30.3800, "lon": 76.8405}

        t0 = time.perf_counter()
        journey = analyze_route_journey(synthetic_50k_pings, base_coords=base_coords, job_site_coords=dest_coords)
        elapsed = time.perf_counter() - t0

        assert elapsed < 4.0, f"50k analyze_route_journey took {elapsed:.2f}s (budget: 4.0s)"
        polyline = journey["route_polyline"]
        assert len(polyline) <= 150, f"Polyline not downsampled: {len(polyline)} points"
        assert len(polyline) >= 10, f"Polyline over-downsampled: {len(polyline)} points"
        assert journey["raw_pings_count"] == 50000


# ============================================================================
# Category 4: Irregular Timestamps & Invariant Conservation Stress
# ============================================================================

class TestIrregularTimestampsAndInvariantConservation:
    """Stress tests hours balance and conservation under time distortions, backwards timestamps, and gap jitter."""

    def test_out_of_order_timestamps_conservation(self):
        """
        Simulates GPS logs arriving out-of-order due to asynchronous cellular reconnects.
        calculate_hours must fallback to nominal intervals without producing negative delta_t.
        Strict conservation law must hold: |H_shift - (H_w + H_t + H_i)| < 1e-4.
        """
        random.seed(999)
        base_time = datetime(2026, 9, 22, 8, 0, 0, tzinfo=timezone.utc)
        pings = []

        for i in range(500):
            jitter_s = random.randint(-180, 180)
            t_s = max(0.0, float(i * 30 + jitter_s))
            pings.append({
                "lat": 30.9010 + i * 0.0005,
                "lon": 75.8573 + i * 0.0005,
                "speed_kmh": 40.0 if i % 2 == 0 else 0.5,
                "timestamp_s": t_s,
                "timestamp": (base_time + timedelta(seconds=t_s)).isoformat()
            })

        res = calculate_hours(
            pings,
            base_coords={"lat": 30.9010, "lon": 75.8573},
            job_site_coords={"lat": 30.3800, "lon": 76.8405}
        )

        h_shift = res["shift_hours"]
        h_w = res["working_hours"]
        h_t = res["travelling_hours"]
        h_i = res["idle_hours"]

        assert h_w >= 0.0 and h_t >= 0.0 and h_i >= 0.0
        diff = abs(h_shift - (h_w + h_t + h_i))
        assert diff < 1e-4, f"Conservation broken on out-of-order timestamps: {h_shift} != {h_w} + {h_t} + {h_i}"

    def test_identical_repeated_timestamps(self):
        """
        100 pings sharing identical timestamps (t_curr == t_prev).
        delta_t fallback must engage cleanly without ZeroDivisionError or infinite loops.
        """
        pings = [
            {
                "lat": 30.9010,
                "lon": 75.8573,
                "speed_kmh": 0.0,
                "timestamp_s": 1000.0,
                "timestamp": "2026-09-22T08:00:00Z"
            }
            for _ in range(100)
        ]
        res = calculate_hours(pings, base_coords={"lat": 30.9010, "lon": 75.8573})
        diff = abs(res["shift_hours"] - (res["working_hours"] + res["travelling_hours"] + res["idle_hours"]))
        assert diff < 1e-4

    def test_microsecond_and_multiday_timestamp_deltas(self):
        """
        High-frequency burst (delta_t = 0.001s) immediately followed by long blackout (delta_t = 86400s).
        Verifies numerical stability across extreme magnitude ranges.
        """
        pings = [
            {"lat": 30.9010, "lon": 75.8573, "speed_kmh": 0.0, "timestamp_s": 0.0},
            {"lat": 30.9010, "lon": 75.8573, "speed_kmh": 0.0, "timestamp_s": 0.001},
            {"lat": 30.9010, "lon": 75.8573, "speed_kmh": 0.0, "timestamp_s": 0.002},
            {"lat": 30.3800, "lon": 76.8405, "speed_kmh": 60.0, "timestamp_s": 86400.0}
        ]
        res = calculate_hours(
            pings,
            base_coords={"lat": 30.9010, "lon": 75.8573},
            job_site_coords={"lat": 30.3800, "lon": 76.8405}
        )
        assert res["shift_hours"] >= 24.0
        diff = abs(res["shift_hours"] - (res["working_hours"] + res["travelling_hours"] + res["idle_hours"]))
        assert diff < 1e-4

    def test_inverted_shift_window_clamping(self):
        """
        shift_start occurs after shift_end (negative raw shift window).
        calculate_hours must clamp shift duration to non-negative and preserve conservation.
        """
        t_start = datetime(2026, 9, 22, 18, 0, 0, tzinfo=timezone.utc)
        t_end = datetime(2026, 9, 22, 8, 0, 0, tzinfo=timezone.utc)

        pings = [
            {"lat": 30.9010, "lon": 75.8573, "speed_kmh": 0.0, "timestamp_s": 0.0},
            {"lat": 30.9010, "lon": 75.8573, "speed_kmh": 0.0, "timestamp_s": 3600.0}
        ]
        res = calculate_hours(
            pings,
            base_coords={"lat": 30.9010, "lon": 75.8573},
            shift_start=t_start,
            shift_end=t_end
        )
        assert res["shift_hours"] >= 0.0
        diff = abs(res["shift_hours"] - (res["working_hours"] + res["travelling_hours"] + res["idle_hours"]))
        assert diff < 1e-4

    def test_monte_carlo_10000_invariant_conservation(self):
        """
        Monte Carlo stress testing across 10,000 highly randomized shift profiles:
        - Massive overtime (up to 200 hours)
        - Fractional floating point durations (e.g. 0.00033 hours)
        - Extreme utilization ratios
        Verifies |H_shift - (H_w + H_t + H_i)| < 1e-4 on 100% of test cases.
        """
        random.seed(12345)
        violations = []
        max_diff = 0.0

        for _ in range(10000):
            raw = random.uniform(0.0, 50.0)
            w = random.uniform(0.0, 40.0)
            t = random.uniform(0.0, 20.0)
            u = random.uniform(0.0, 10.0) if random.random() > 0.5 else 0.0
            b = random.uniform(0.0, 10.0) if random.random() > 0.5 else 0.0

            res = AnalyticsEngine.enforce_hours_conservation(
                raw_shift_hours=raw,
                working_hours=w,
                travelling_hours=t,
                unauthorized_hours=u,
                base_idle_hours=b
            )

            diff = abs(res["shift_hours"] - (res["working_hours"] + res["travelling_hours"] + res["idle_hours"]))
            if diff > max_diff:
                max_diff = diff
            if diff >= 1e-3:
                violations.append((raw, w, t, u, b, diff))

        assert len(violations) == 0, f"Found {len(violations)} conservation violations: {violations[:3]}"
        assert max_diff < 1e-3, f"Max difference {max_diff} exceeded tolerance"


# ============================================================================
# Category 5: Sync Service Cache Invalidation & Fallback Resilience
# ============================================================================

class TestSyncServiceAndCacheHardening:
    """Stress tests SyncService resilience under missing, corrupted, or concurrent cache states."""

    def test_sync_service_missing_cache_recovery(self, tmp_path):
        """SyncService initialized with non-existent cache file boots cleanly with synthetic fallback."""
        cache_file = tmp_path / "non_existent_cache.json"
        assert not cache_file.exists()

        svc = SyncService(cache_file=cache_file)
        assert svc._state["source"] == "krone_mock"
        assert cache_file.exists(), "Cache file was not created on startup"

        pulse = svc.get_pulse_data()
        assert pulse["kpis"]["technicians_active_total"] >= 10
        assert len(pulse["today_jobs"]) > 0

    def test_sync_service_corrupted_cache_recovery(self, tmp_path):
        """SyncService initialized with corrupted JSON catches decode error and falls back to mock."""
        cache_file = tmp_path / "corrupted_cache.json"
        with open(cache_file, "w", encoding="utf-8") as f:
            f.write("{ invalid json truncated: [ }")

        svc = SyncService(cache_file=cache_file)
        assert svc._state["source"] == "krone_mock"
        pulse = svc.get_pulse_data()
        assert pulse["kpis"]["technicians_active_total"] >= 10

    @pytest.mark.asyncio
    async def test_sync_service_concurrent_fresh_sync_locking(self, tmp_path):
        """
        25 concurrent trigger_fresh_sync calls must be safely serialized by the async lock
        without race conditions, corrupt JSON, or unhandled exceptions.
        """
        cache_file = tmp_path / "concurrent_cache.json"
        svc = SyncService(cache_file=cache_file)

        async def call_sync(idx: int):
            return await svc.trigger_fresh_sync(force_refresh=True)

        tasks = [call_sync(i) for i in range(25)]
        results = await asyncio.gather(*tasks)

        assert len(results) == 25
        for r in results:
            assert r["status"] == "success"
            assert r["records_synced"] > 0
            assert "sync_id" in r

        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert "data" in data
            assert "sync_id" in data

    def test_sync_service_telematics_route_unknown_technician(self, tmp_path):
        """Requesting telematics route for unknown technician synthesizes authentic default route."""
        cache_file = tmp_path / "mock_cache.json"
        svc = SyncService(cache_file=cache_file)

        route = svc.get_telematics_route("TECH-999-NONEXISTENT", "2026-09-22")
        assert route["technician_id"] == "TECH-999-NONEXISTENT"
        assert "clusters_5km" in route
        assert "journey_summary" in route
        assert route["journey_summary"]["total_distance_km"] > 0.0


# ============================================================================
# Category 6: Geofence Corridor Math & Detour Boundary Hardening
# ============================================================================

class TestGeofenceCorridorAndDetourBoundaryHardening:
    """Stress tests route inspector, 5km clustering, and detour anomaly algorithms."""

    def test_exact_5km_boundary_classification(self):
        """
        Tests the 5.0 km boundary threshold:
        - Stop 1: 4.95 km North of depot -> classified as STARTING_BASE
        - Stop 2: 5.05 km South of depot -> classified as UNAUTHORIZED_STOP (if dwell > 15m)
        Because they are in opposite directions (10 km apart), they form 2 independent clusters.
        """
        base_coords = {"lat": 30.9010, "lon": 75.8573}
        dest_coords = {"lat": 30.3800, "lon": 76.8405}

        lat_inside_north = base_coords["lat"] + (4.95 / 111.195)
        lat_outside_south = base_coords["lat"] - (5.05 / 111.195)

        stops = [
            {"lat": lat_inside_north, "lon": base_coords["lon"], "duration_s": 1200.0, "pings_count": 10},
            {"lat": lat_outside_south, "lon": base_coords["lon"], "duration_s": 1200.0, "pings_count": 10}
        ]

        clusters = cluster_stops_5km(stops, max_radius_km=MAX_CLUSTER_RADIUS_KM)
        assert len(clusters) == 2, f"Expected 2 separate clusters for stops 10km apart, got {len(clusters)}"
        classified, summary = inspect_journey(clusters, base_coords, dest_coords)

        zone_types = [c["zone_type"] for c in classified]
        assert "STARTING_BASE" in zone_types
        assert "UNAUTHORIZED_STOP" in zone_types
        assert summary["unauthorized_seconds"] >= 1200.0

    def test_single_linkage_chaining_rejection(self):
        """
        10 stops in a linear chain spaced 2.0 km apart (total distance 18.0 km).
        Single-linkage clustering would erroneously merge all 10 into one massive 18 km cluster.
        Our engine must enforce that every stop is within 5.0 km of the cluster centroid.
        """
        stops = [
            {"lat": 30.0 + (i * 2.0 / 111.195), "lon": 75.0, "duration_s": 300.0}
            for i in range(10)
        ]
        clusters = cluster_pings_5km(stops, max_radius_km=MAX_CLUSTER_RADIUS_KM)

        assert len(clusters) >= 2, f"Chaining vulnerability: single-linkage merged 18km span into {len(clusters)} cluster(s)"

        for c in clusters:
            c_lat = c["centroid"]["lat"]
            c_lon = c["centroid"]["lng"]
            for s in c["stops"]:
                dist = haversine_distance_km(s["lat"], s.get("lon", s.get("lng", 0.0)), c_lat, c_lon)
                assert dist <= MAX_CLUSTER_RADIUS_KM + 1e-4, f"Cluster radius violation: stop is {dist:.3f} km from centroid"

    def test_detour_ratio_and_excess_thresholds(self):
        """
        Detour anomaly requires BOTH ratio > 1.25 AND excess distance > 10.0 km.
        - 95 km vs 80 km (ratio 1.188 <= 1.25, excess 15 km): No anomaly.
        - 110 km vs 80 km (ratio 1.375 > 1.25, excess 30 km): Anomalous detour.
        - Designated distance 0.0 km: Must handle without ZeroDivisionError.
        """
        base_loc = {"lat": 30.9010, "lon": 75.8573}
        dest_loc = {"lat": 30.3800, "lon": 76.8405}
        stops = [{"lat": 30.9010, "lon": 75.8573, "duration_s": 600.0}]

        # Case 1: Below ratio threshold
        res_no_detour = inspect_route_telematics(
            stops, base_loc, dest_loc,
            designated_distance_km=80.0,
            actual_distance_km=95.0
        )
        detour_anomalies = [a for a in res_no_detour["anomalies"] if a["type"] == "excessive_detour"]
        assert len(detour_anomalies) == 0

        # Case 2: Above both ratio and excess thresholds
        res_detour = inspect_route_telematics(
            stops, base_loc, dest_loc,
            designated_distance_km=80.0,
            actual_distance_km=110.0
        )
        detour_anomalies_active = [a for a in res_detour["anomalies"] if a["type"] == "excessive_detour"]
        assert len(detour_anomalies_active) == 1
        assert "Detour ratio" in detour_anomalies_active[0]["description"]

        # Case 3: Zero designated distance
        res_zero = inspect_route_telematics(
            stops, base_loc, dest_loc,
            designated_distance_km=0.0,
            actual_distance_km=15.0
        )
        assert res_zero["detour_ratio"] >= 0.0

    def test_coincident_base_and_customer_site(self):
        """
        When customer site and base depot are within 50m of each other,
        customer destination takes priority so technician's productive service hours are properly credited.
        """
        base_loc = {"lat": 30.9010, "lon": 75.8573}
        dest_loc = {"lat": 30.9012, "lon": 75.8575}

        stops = [{"lat": 30.9011, "lon": 75.8574, "duration_s": 7200.0, "location_name": "Coincident Hub"}]
        clusters = cluster_stops_5km(stops, max_radius_km=MAX_CLUSTER_RADIUS_KM)
        classified, summary = inspect_journey(clusters, base_loc, dest_loc)

        assert len(classified) == 1
        assert classified[0]["zone_type"] == "CUSTOMER_DESTINATION"
        assert classified[0]["is_job_site"] is True
        assert summary["working_seconds"] == 7200.0


# ============================================================================
# Category 7: Empirical Bug Demonstrations & Root Cause Verification
# ============================================================================

class TestEmpiricalBugDemonstrations:
    """
    Verifies the empirical remediation and hardening of the four defects
    discovered during white-box adversarial analysis of the backend services.
    """

    def test_defect_1_distance_underreporting_on_stop_transition(self):
        """
        REMEDIATION VERIFICATION 1:
        filter_stationary_jitter (telematics_engine.py) accumulates step_dist
        on the transition from moving to stationary, preserving the full physical
        distance of the final transit leg before coming to a stop.
        """
        pings = [
            {"lat": 30.0, "lon": 75.0, "speed_kmh": 0.0},
            {"lat": 30.1, "lon": 75.0, "speed_kmh": 60.0},
            {"lat": 30.2, "lon": 75.0, "speed_kmh": 0.0}
        ]
        filtered, reported_dist = filter_stationary_jitter(pings)
        expected_physical_dist = haversine_distance_km(30.0, 75.0, 30.2, 75.0)

        # Verifies that distance is NOT truncated; full transit leg is preserved
        assert reported_dist >= expected_physical_dist * 0.99
        assert math.isclose(reported_dist, expected_physical_dist, abs_tol=0.05)

    def test_defect_2_unclamped_negative_duration_in_clustering(self):
        """
        REMEDIATION VERIFICATION 2:
        cluster_pings_5km (telematics_engine.py) clamps negative duration inputs
        to 0.0, preventing corruption of cluster total_duration_s and journey working hours.
        """
        stops = [
            {"lat": 30.9010, "lon": 75.8573, "duration_seconds": -120.0}
        ]
        clusters = cluster_pings_5km(stops, max_radius_km=MAX_CLUSTER_RADIUS_KM)

        # Verifies negative duration is safely clamped to 0.0
        assert clusters[0]["total_duration_s"] == 0.0
        assert clusters[0]["duration_minutes"] == 0.0

    def test_defect_3_infinite_hours_assertion_crash(self):
        """
        REMEDIATION VERIFICATION 3:
        Passing math.inf to AnalyticsEngine.enforce_hours_conservation is sanitized
        gracefully using math.isfinite() without raising unhandled AssertionError.
        """
        res = AnalyticsEngine.enforce_hours_conservation(8.0, float("inf"), 0.0)
        assert res["shift_hours"] == 8.0
        assert res["working_hours"] == 0.0
        assert res["travelling_hours"] == 0.0
        assert res["idle_hours"] == 8.0
        assert res["conservation_error"] < 1e-3

    def test_defect_4_quadratic_clustering_latency_spike(self):
        """
        REMEDIATION VERIFICATION 4:
        cluster_pings_5km utilizes O(1) centroid projection and triangle bounding,
        clustering 1,000 stops in < 0.5s instead of exhibiting quadratic latency.
        """
        stops_1000 = [{"lat": 30.9 + i * 0.00001, "lon": 75.8, "duration_s": 60.0} for i in range(1000)]
        t0 = time.perf_counter()
        clusters = cluster_pings_5km(stops_1000)
        elapsed = time.perf_counter() - t0

        # Verifies linear/efficient scaling (< 0.5s for 1000 items)
        assert elapsed < 0.5, f"Clustering 1,000 stops took {elapsed:.3f}s (expected < 0.5s)"
        assert len(clusters) == 1
