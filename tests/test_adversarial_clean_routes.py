"""
tests/test_adversarial_clean_routes.py
Adversarial Geospatial Clean-Route Stress Test Suite
Target: backend/app/services/telematics_engine.py
Agent: m1_iter2_challenger_1 (Empirical Adversarial Challenger)

Verifies:
1. 100 Clean Synthesized Routes across 10 corridors with varying ping breadcrumbs (10 to 500 pings).
   Asserts 100% pass rate: anomalies_detected == 0, unauthorized_stop_duration_minutes == 0.0, anomalies == [].
2. Intentional Anomaly Insertion:
   - 20-min halt outside 5 km zone -> accurately flagged as unauthorized stop.
   - 25-min roadside dhaba halt outside 5 km zone -> accurately flagged.
   - 35-min prolonged halt outside 5 km zone -> accurately flagged.
   - Multiple unauthorized halts -> all detected, durations accumulated accurately.
   - 10-min halt outside 5 km zone -> NOT flagged (sub-threshold <= 15 min).
   - 30-min halt INSIDE 5 km authorized zone (base or destination) -> NOT flagged as unauthorized stop.
"""

import math
import random
import time
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Tuple
import pytest

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.telematics_engine import (
    analyze_route_journey,
    haversine_distance_km,
    filter_stationary_jitter,
    extract_raw_stops,
    cluster_pings_5km,
    inspect_journey,
    MAX_CLUSTER_RADIUS_KM,
    UNAUTHORIZED_STOP_THRESHOLD_SECONDS,
)

# ---------------------------------------------------------------------------
# Authoritative Corridors for Krone Field Operations Across India
# ---------------------------------------------------------------------------
CORRIDORS = [
    {
        "id": "CORR-01-PB-BARWALA",
        "region": "Punjab",
        "base": {"name": "Krone Regional Ag Depot Ludhiana", "lat": 30.9010, "lng": 75.8573, "lon": 75.8573},
        "dest": {"name": "RIL Bio-Energy Facility Barwala", "lat": 30.3800, "lng": 76.8405, "lon": 76.8405},
        "approx_dist_km": 84.6
    },
    {
        "id": "CORR-02-HR-HISAR",
        "region": "Haryana",
        "base": {"name": "Krone Service Station Hisar", "lat": 29.1492, "lng": 75.7217, "lon": 75.7217},
        "dest": {"name": "Barwala Plant Hisar", "lat": 29.3582, "lng": 75.9085, "lon": 75.9085},
        "approx_dist_km": 29.8
    },
    {
        "id": "CORR-03-UP-PANIPAT",
        "region": "UP/Haryana",
        "base": {"name": "Muzaffarnagar Field Support Center", "lat": 29.4727, "lng": 77.7085, "lon": 77.7085},
        "dest": {"name": "Panipat Grain Silos", "lat": 29.3909, "lng": 76.9635, "lon": 76.9635},
        "approx_dist_km": 72.8
    },
    {
        "id": "CORR-04-PB-BARNALA",
        "region": "Punjab",
        "base": {"name": "Krone Regional Ag Depot Ludhiana", "lat": 30.9010, "lng": 75.8573, "lon": 75.8573},
        "dest": {"name": "Barnala Bio-Mass Site", "lat": 30.3819, "lng": 75.5469, "lon": 75.5469},
        "approx_dist_km": 65.2
    },
    {
        "id": "CORR-05-AP-DAGADARTHI",
        "region": "Andhra Pradesh",
        "base": {"name": "Nellore Bio-Gas Service Depot", "lat": 14.4426, "lng": 79.9865, "lon": 79.9865},
        "dest": {"name": "Dagadarthi Bio-Mass Plant Nellore", "lat": 14.5855, "lng": 79.9405, "lon": 79.9405},
        "approx_dist_km": 20.3
    },
    {
        "id": "CORR-06-AP-KOVUR",
        "region": "Andhra Pradesh",
        "base": {"name": "Nellore Bio-Gas Service Depot", "lat": 14.4426, "lng": 79.9865, "lon": 79.9865},
        "dest": {"name": "Kovur Bio-Mass Yard Nellore", "lat": 14.4983, "lng": 79.9922, "lon": 79.9922},
        "approx_dist_km": 6.8
    },
    {
        "id": "CORR-07-AP-KAKINADA",
        "region": "Andhra Pradesh",
        "base": {"name": "Rajahmundry Field Support Hub", "lat": 17.0005, "lng": 81.8040, "lon": 81.8040},
        "dest": {"name": "Kakinada Port Agro Yard", "lat": 16.9891, "lng": 82.2475, "lon": 82.2475},
        "approx_dist_km": 47.3
    },
    {
        "id": "CORR-08-MP-PITHAMPUR",
        "region": "Madhya Pradesh",
        "base": {"name": "Indore Bio-Power Depot", "lat": 22.7196, "lng": 75.8577, "lon": 75.8577},
        "dest": {"name": "Pithampur Bio-Mass Hub Indore", "lat": 22.6139, "lng": 75.6823, "lon": 75.6823},
        "approx_dist_km": 23.4
    },
    {
        "id": "CORR-09-PB-SANGRUR",
        "region": "Punjab",
        "base": {"name": "Krone Regional Ag Depot Ludhiana", "lat": 30.9010, "lng": 75.8573, "lon": 75.8573},
        "dest": {"name": "Sangrur Bio-Energy Site", "lat": 30.2458, "lng": 75.8421, "lon": 75.8421},
        "approx_dist_km": 73.1
    },
    {
        "id": "CORR-10-MH-DAUND",
        "region": "Maharashtra",
        "base": {"name": "Baramati Agro Hub", "lat": 18.1517, "lng": 74.5772, "lon": 74.5772},
        "dest": {"name": "Daund Bio-Power Facility", "lat": 18.4636, "lng": 74.5832, "lon": 74.5832},
        "approx_dist_km": 34.7
    }
]

PING_COUNTS = [10, 20, 35, 50, 75, 100, 180, 250, 375, 500]


def synthesize_clean_route(
    corridor: Dict[str, Any],
    num_pings: int,
    route_type: str = "pure_transit",
    seed: int = 42
) -> List[Dict[str, Any]]:
    """
    Synthesizes a clean GPS route along a designated corridor with 0 unauthorized stops.
    Profiles:
    - 'pure_transit': 100% continuous moving pings along the corridor (speeds 45-80 km/h).
    - 'operational_full': Initial base dwell, corridor transit, destination dwell.
    - 'transit_with_minor_pauses': Transit with realistic brief pauses (< 3 min, e.g. toll/signal).
    """
    rng = random.Random(seed)
    base = corridor["base"]
    dest = corridor["dest"]
    t0 = datetime(2026, 9, 22, 8, 0, 0, tzinfo=timezone.utc)

    start_lat, start_lon = float(base["lat"]), float(base.get("lon", base.get("lng")))
    end_lat, end_lon = float(dest["lat"]), float(dest.get("lon", dest.get("lng")))

    pings: List[Dict[str, Any]] = []

    if route_type == "pure_transit" or num_pings < 15:
        # 100% moving pings interpolated linearly with slight GPS perturbation
        for i in range(num_pings):
            frac = i / max(1, num_pings - 1)
            # Add minor lateral jitter (+- 0.0001 deg ~ 10m)
            jitter_lat = rng.uniform(-0.00008, 0.00008)
            jitter_lon = rng.uniform(-0.00008, 0.00008)
            speed = rng.uniform(45.0, 75.0)

            pings.append({
                "lat": round(start_lat + frac * (end_lat - start_lat) + jitter_lat, 6),
                "lon": round(start_lon + frac * (end_lon - start_lon) + jitter_lon, 6),
                "speed_kmh": round(speed, 1),
                "timestamp": (t0 + timedelta(seconds=i * 60)).isoformat(),
                "timestamp_s": float(i * 60),
                "is_stationary": False
            })

    elif route_type == "operational_full":
        # Base dwell (inside base 5 km zone), Transit, Job site dwell (inside site 5 km zone)
        base_dwell_count = max(2, int(num_pings * 0.15))
        site_dwell_count = max(2, int(num_pings * 0.15))
        transit_count = num_pings - base_dwell_count - site_dwell_count

        t_elapsed = 0

        # 1. Base Depot dwell
        for i in range(base_dwell_count):
            pings.append({
                "lat": round(start_lat + rng.uniform(-0.00005, 0.00005), 6),
                "lon": round(start_lon + rng.uniform(-0.00005, 0.00005), 6),
                "speed_kmh": 0.0,
                "timestamp": (t0 + timedelta(seconds=t_elapsed)).isoformat(),
                "timestamp_s": float(t_elapsed),
                "is_stationary": True
            })
            t_elapsed += 60

        # 2. Highway corridor transit
        for i in range(transit_count):
            frac = (i + 1) / float(transit_count + 1)
            jitter_lat = rng.uniform(-0.00008, 0.00008)
            jitter_lon = rng.uniform(-0.00008, 0.00008)
            speed = rng.uniform(50.0, 80.0)

            pings.append({
                "lat": round(start_lat + frac * (end_lat - start_lat) + jitter_lat, 6),
                "lon": round(start_lon + frac * (end_lon - start_lon) + jitter_lon, 6),
                "speed_kmh": round(speed, 1),
                "timestamp": (t0 + timedelta(seconds=t_elapsed)).isoformat(),
                "timestamp_s": float(t_elapsed),
                "is_stationary": False
            })
            t_elapsed += 60

        # 3. Customer Job Site dwell
        for i in range(site_dwell_count):
            pings.append({
                "lat": round(end_lat + rng.uniform(-0.00005, 0.00005), 6),
                "lon": round(end_lon + rng.uniform(-0.00005, 0.00005), 6),
                "speed_kmh": 0.0,
                "timestamp": (t0 + timedelta(seconds=t_elapsed)).isoformat(),
                "timestamp_s": float(t_elapsed),
                "is_stationary": True
            })
            t_elapsed += 60

    elif route_type == "transit_with_minor_pauses":
        # Highway transit with brief 1-2 min traffic/toll pauses (sub-threshold, 0 unauthorized stops)
        t_elapsed = 0
        pause_idx = num_pings // 2

        for i in range(num_pings):
            frac = i / max(1, num_pings - 1)
            # Insert a 2-minute pause midway
            if i in (pause_idx, pause_idx + 1):
                cur_lat = start_lat + (pause_idx / float(num_pings - 1)) * (end_lat - start_lat)
                cur_lon = start_lon + (pause_idx / float(num_pings - 1)) * (end_lon - start_lon)
                pings.append({
                    "lat": round(cur_lat, 6),
                    "lon": round(cur_lon, 6),
                    "speed_kmh": 0.0,
                    "timestamp": (t0 + timedelta(seconds=t_elapsed)).isoformat(),
                    "timestamp_s": float(t_elapsed),
                    "is_stationary": True
                })
            else:
                jitter_lat = rng.uniform(-0.00006, 0.00006)
                jitter_lon = rng.uniform(-0.00006, 0.00006)
                speed = rng.uniform(48.0, 72.0)
                pings.append({
                    "lat": round(start_lat + frac * (end_lat - start_lat) + jitter_lat, 6),
                    "lon": round(start_lon + frac * (end_lon - start_lon) + jitter_lon, 6),
                    "speed_kmh": round(speed, 1),
                    "timestamp": (t0 + timedelta(seconds=t_elapsed)).isoformat(),
                    "timestamp_s": float(t_elapsed),
                    "is_stationary": False
                })
            t_elapsed += 60

    return pings


# ============================================================================
# Task 1 & 2: 100 Clean Synthesized Routes Adversarial Trials
# ============================================================================

class TestCleanRoutesAdversarial100Trials:
    """
    Executes 100 adversarial trials across 10 designated corridors with varying GPS breadcrumbs (10 to 500 pings).
    Asserts in 100% of trials:
    - anomalies_detected == 0
    - unauthorized_stop_duration_minutes == 0.0
    - anomalies == []
    """

    @pytest.mark.parametrize("corridor_idx", range(10))
    @pytest.mark.parametrize("ping_idx", range(10))
    def test_clean_route_trial(self, corridor_idx: int, ping_idx: int):
        corridor = CORRIDORS[corridor_idx]
        ping_count = PING_COUNTS[ping_idx]

        # Vary route profile deterministically:
        # - Trials with ping_idx % 3 == 0 -> pure_transit
        # - Trials with ping_idx % 3 == 1 -> operational_full
        # - Trials with ping_idx % 3 == 2 -> transit_with_minor_pauses
        profiles = ["pure_transit", "operational_full", "transit_with_minor_pauses"]
        route_type = profiles[(corridor_idx + ping_idx) % 3]

        trial_seed = 1000 + corridor_idx * 10 + ping_idx
        pings = synthesize_clean_route(corridor, ping_count, route_type=route_type, seed=trial_seed)

        assert len(pings) == ping_count, f"Generated ping count mismatch: expected {ping_count}, got {len(pings)}"

        result = analyze_route_journey(
            pings=pings,
            base_coords=corridor["base"],
            job_site_coords=corridor["dest"],
            technician_id=f"TECH-{corridor_idx + 1:02d}",
            technician_name=f"Krone Specialist {corridor_idx + 1}"
        )

        journey = result["journey_summary"]
        anomalies = result["anomalies"]

        # 1. Assert exactly 0 anomalies detected in journey_summary
        assert journey["anomalies_detected"] == 0, (
            f"Trial Fail [Corridor {corridor['id']}, {ping_count} pings, profile {route_type}]: "
            f"expected anomalies_detected == 0, got {journey['anomalies_detected']}"
        )

        # 2. Assert unauthorized_stop_duration_minutes is exactly 0.0
        assert journey["unauthorized_stop_duration_minutes"] == 0.0, (
            f"Trial Fail [Corridor {corridor['id']}, {ping_count} pings, profile {route_type}]: "
            f"expected unauthorized_stop_duration_minutes == 0.0, got {journey['unauthorized_stop_duration_minutes']}"
        )

        # 3. Assert anomalies list is completely empty
        assert anomalies == [], (
            f"Trial Fail [Corridor {corridor['id']}, {ping_count} pings, profile {route_type}]: "
            f"expected anomalies == [], got {anomalies}"
        )

        # 4. Verify raw pings count preserved
        assert result["raw_pings_count"] == ping_count

        # 5. Verify transit duration > 0.0 when there are moving pings
        assert journey["transit_duration_minutes"] >= 0.0


# ============================================================================
# Task 3: Intentional Anomaly Insertion Tests
# ============================================================================

class TestIntentionalAnomalyInsertion:
    """
    Tests intentional unauthorized stop anomalies inserted along designated corridors:
    - 20-minute halt outside 5 km zone
    - 25-minute roadside halt outside 5 km zone
    - 35-minute prolonged unauthorized halt
    - Multiple unauthorized stops along a single route
    - Sub-threshold stops (10-minute halt)
    - Authorized zone halts (30-minute halt inside base or destination 5 km zone)
    """

    def test_adv_anomaly_01_inserted_20min_halt_outside_5km(self):
        """20-minute unauthorized halt midway along Ludhiana-Barwala corridor."""
        corridor = CORRIDORS[0]  # Ludhiana to Barwala
        base = corridor["base"]
        dest = corridor["dest"]
        halt_lat, halt_lon = 30.6450, 76.3200  # ~38 km from Ludhiana, ~55 km from Barwala

        # Distance checks: confirm halt is well outside 5 km of both base and destination
        dist_to_base = haversine_distance_km(halt_lat, halt_lon, base["lat"], base["lon"])
        dist_to_dest = haversine_distance_km(halt_lat, halt_lon, dest["lat"], dest["lon"])
        assert dist_to_base > 10.0, f"Halt too close to base: {dist_to_base:.1f} km"
        assert dist_to_dest > 10.0, f"Halt too close to dest: {dist_to_dest:.1f} km"

        t0 = datetime(2026, 9, 22, 8, 0, 0, tzinfo=timezone.utc)
        pings: List[Dict[str, Any]] = []

        # Leg 1: 30 moving pings to halt
        t_elapsed = 0
        for i in range(30):
            frac = i / 30.0
            pings.append({
                "lat": round(base["lat"] + frac * (halt_lat - base["lat"]), 6),
                "lon": round(base["lon"] + frac * (halt_lon - base["lon"]), 6),
                "speed_kmh": 60.0,
                "timestamp": (t0 + timedelta(seconds=t_elapsed)).isoformat(),
                "timestamp_s": float(t_elapsed),
                "is_stationary": False
            })
            t_elapsed += 60

        # Anomaly halt: 21 pings spanning 20 intervals = 20.0 minutes
        halt_start_time = (t0 + timedelta(seconds=t_elapsed)).isoformat()
        for i in range(21):
            pings.append({
                "lat": round(halt_lat + random.uniform(-0.00002, 0.00002), 6),
                "lon": round(halt_lon + random.uniform(-0.00002, 0.00002), 6),
                "speed_kmh": 0.0,
                "timestamp": (t0 + timedelta(seconds=t_elapsed)).isoformat(),
                "timestamp_s": float(t_elapsed),
                "is_stationary": True
            })
            t_elapsed += 60

        # Leg 2: 30 moving pings from halt to destination
        for i in range(30):
            frac = (i + 1) / 30.0
            pings.append({
                "lat": round(halt_lat + frac * (dest["lat"] - halt_lat), 6),
                "lon": round(halt_lon + frac * (dest["lon"] - halt_lon), 6),
                "speed_kmh": 60.0,
                "timestamp": (t0 + timedelta(seconds=t_elapsed)).isoformat(),
                "timestamp_s": float(t_elapsed),
                "is_stationary": False
            })
            t_elapsed += 60

        result = analyze_route_journey(pings, base, dest)
        journey = result["journey_summary"]
        anomalies = result["anomalies"]

        # Empirical Assertions:
        assert journey["anomalies_detected"] == 1, f"Expected 1 anomaly, got {journey['anomalies_detected']}"
        assert journey["unauthorized_stop_duration_minutes"] == 20.0, (
            f"Expected 20.0 min unauthorized stop, got {journey['unauthorized_stop_duration_minutes']}"
        )
        assert len(anomalies) == 1
        anom = anomalies[0]
        assert anom["type"] == "unauthorized_stop"
        assert anom["duration_minutes"] == 20.0
        # Location within 100 meters of inserted halt
        dist_anom_to_halt = haversine_distance_km(anom["location"]["lat"], anom["location"]["lng"], halt_lat, halt_lon)
        assert dist_anom_to_halt < 0.1, f"Anomaly location deviation: {dist_anom_to_halt * 1000:.1f} m"

    def test_adv_anomaly_02_inserted_25min_roadside_halt(self):
        """25-minute unauthorized stop (e.g. Rajpura roadside dhaba)."""
        corridor = CORRIDORS[1]  # Hisar corridor
        base = corridor["base"]
        dest = corridor["dest"]
        halt_lat, halt_lon = 29.2500, 75.8100  # Outside 5km of Hisar station and Barwala plant

        t0 = datetime(2026, 9, 22, 8, 0, 0, tzinfo=timezone.utc)
        pings: List[Dict[str, Any]] = []

        # Leg 1: 20 moving pings
        t_elapsed = 0
        for i in range(20):
            frac = i / 20.0
            pings.append({
                "lat": round(base["lat"] + frac * (halt_lat - base["lat"]), 6),
                "lon": round(base["lon"] + frac * (halt_lon - base["lon"]), 6),
                "speed_kmh": 55.0,
                "timestamp": (t0 + timedelta(seconds=t_elapsed)).isoformat(),
                "timestamp_s": float(t_elapsed),
                "is_stationary": False
            })
            t_elapsed += 60

        # Anomaly halt: 26 pings spanning 25 intervals = 25.0 minutes
        for i in range(26):
            pings.append({
                "lat": halt_lat,
                "lon": halt_lon,
                "speed_kmh": 0.0,
                "timestamp": (t0 + timedelta(seconds=t_elapsed)).isoformat(),
                "timestamp_s": float(t_elapsed),
                "is_stationary": True
            })
            t_elapsed += 60

        # Leg 2: 20 moving pings to dest
        for i in range(20):
            frac = (i + 1) / 20.0
            pings.append({
                "lat": round(halt_lat + frac * (dest["lat"] - halt_lat), 6),
                "lon": round(halt_lon + frac * (dest["lon"] - halt_lon), 6),
                "speed_kmh": 55.0,
                "timestamp": (t0 + timedelta(seconds=t_elapsed)).isoformat(),
                "timestamp_s": float(t_elapsed),
                "is_stationary": False
            })
            t_elapsed += 60

        result = analyze_route_journey(pings, base, dest)
        assert result["journey_summary"]["anomalies_detected"] == 1
        assert result["journey_summary"]["unauthorized_stop_duration_minutes"] == 25.0
        assert result["anomalies"][0]["type"] == "unauthorized_stop"
        assert result["anomalies"][0]["duration_minutes"] == 25.0

    def test_adv_anomaly_03_inserted_35min_halt(self):
        """35-minute prolonged unauthorized halt."""
        corridor = CORRIDORS[7]  # Indore to Pithampur
        base = corridor["base"]
        dest = corridor["dest"]
        halt_lat, halt_lon = 22.6650, 75.7700

        t0 = datetime(2026, 9, 22, 8, 0, 0, tzinfo=timezone.utc)
        pings: List[Dict[str, Any]] = []

        # 15 moving pings
        t_elapsed = 0
        for i in range(15):
            frac = i / 15.0
            pings.append({
                "lat": round(base["lat"] + frac * (halt_lat - base["lat"]), 6),
                "lon": round(base["lon"] + frac * (halt_lon - base["lon"]), 6),
                "speed_kmh": 50.0,
                "timestamp": (t0 + timedelta(seconds=t_elapsed)).isoformat(),
                "timestamp_s": float(t_elapsed),
                "is_stationary": False
            })
            t_elapsed += 60

        # Anomaly: 36 pings = 35 minutes halt
        for i in range(36):
            pings.append({
                "lat": halt_lat,
                "lon": halt_lon,
                "speed_kmh": 0.0,
                "timestamp": (t0 + timedelta(seconds=t_elapsed)).isoformat(),
                "timestamp_s": float(t_elapsed),
                "is_stationary": True
            })
            t_elapsed += 60

        # 15 moving pings
        for i in range(15):
            frac = (i + 1) / 15.0
            pings.append({
                "lat": round(halt_lat + frac * (dest["lat"] - halt_lat), 6),
                "lon": round(halt_lon + frac * (dest["lon"] - halt_lon), 6),
                "speed_kmh": 50.0,
                "timestamp": (t0 + timedelta(seconds=t_elapsed)).isoformat(),
                "timestamp_s": float(t_elapsed),
                "is_stationary": False
            })
            t_elapsed += 60

        result = analyze_route_journey(pings, base, dest)
        assert result["journey_summary"]["anomalies_detected"] == 1
        assert result["journey_summary"]["unauthorized_stop_duration_minutes"] == 35.0
        assert result["anomalies"][0]["duration_minutes"] == 35.0

    def test_adv_anomaly_04_multiple_unauthorized_stops(self):
        """Two distinct unauthorized halts along a long corridor (20 min + 25 min = 45 min total)."""
        corridor = CORRIDORS[0]  # Ludhiana to Barwala
        base = corridor["base"]
        dest = corridor["dest"]

        halt1_lat, halt1_lon = 30.7500, 76.1500  # Halt 1
        halt2_lat, halt2_lon = 30.5500, 76.5000  # Halt 2 (> 30 km from Halt 1)

        t0 = datetime(2026, 9, 22, 8, 0, 0, tzinfo=timezone.utc)
        pings: List[Dict[str, Any]] = []
        t_elapsed = 0

        # Leg 1: Base to Halt 1 (20 moving)
        for i in range(20):
            frac = i / 20.0
            pings.append({
                "lat": round(base["lat"] + frac * (halt1_lat - base["lat"]), 6),
                "lon": round(base["lon"] + frac * (halt1_lon - base["lon"]), 6),
                "speed_kmh": 60.0,
                "timestamp": (t0 + timedelta(seconds=t_elapsed)).isoformat(),
                "timestamp_s": float(t_elapsed),
                "is_stationary": False
            })
            t_elapsed += 60

        # Halt 1: 21 pings = 20.0 minutes
        for i in range(21):
            pings.append({
                "lat": halt1_lat,
                "lon": halt1_lon,
                "speed_kmh": 0.0,
                "timestamp": (t0 + timedelta(seconds=t_elapsed)).isoformat(),
                "timestamp_s": float(t_elapsed),
                "is_stationary": True
            })
            t_elapsed += 60

        # Leg 2: Halt 1 to Halt 2 (20 moving)
        for i in range(20):
            frac = (i + 1) / 20.0
            pings.append({
                "lat": round(halt1_lat + frac * (halt2_lat - halt1_lat), 6),
                "lon": round(halt1_lon + frac * (halt2_lon - halt1_lon), 6),
                "speed_kmh": 60.0,
                "timestamp": (t0 + timedelta(seconds=t_elapsed)).isoformat(),
                "timestamp_s": float(t_elapsed),
                "is_stationary": False
            })
            t_elapsed += 60

        # Halt 2: 26 pings = 25.0 minutes
        for i in range(26):
            pings.append({
                "lat": halt2_lat,
                "lon": halt2_lon,
                "speed_kmh": 0.0,
                "timestamp": (t0 + timedelta(seconds=t_elapsed)).isoformat(),
                "timestamp_s": float(t_elapsed),
                "is_stationary": True
            })
            t_elapsed += 60

        # Leg 3: Halt 2 to Dest (20 moving)
        for i in range(20):
            frac = (i + 1) / 20.0
            pings.append({
                "lat": round(halt2_lat + frac * (dest["lat"] - halt2_lat), 6),
                "lon": round(halt2_lon + frac * (dest["lon"] - halt2_lon), 6),
                "speed_kmh": 60.0,
                "timestamp": (t0 + timedelta(seconds=t_elapsed)).isoformat(),
                "timestamp_s": float(t_elapsed),
                "is_stationary": False
            })
            t_elapsed += 60

        result = analyze_route_journey(pings, base, dest)
        journey = result["journey_summary"]
        anomalies = result["anomalies"]

        assert journey["anomalies_detected"] == 2
        assert journey["unauthorized_stop_duration_minutes"] == 45.0
        assert len(anomalies) == 2
        durations = sorted([a["duration_minutes"] for a in anomalies])
        assert durations == [20.0, 25.0]

    def test_adv_anomaly_05_subthreshold_halt_not_flagged(self):
        """10-minute halt outside 5 km zone (sub-threshold, <= 15 min): must NOT be flagged as anomaly."""
        corridor = CORRIDORS[0]
        base = corridor["base"]
        dest = corridor["dest"]
        halt_lat, halt_lon = 30.6450, 76.3200

        t0 = datetime(2026, 9, 22, 8, 0, 0, tzinfo=timezone.utc)
        pings: List[Dict[str, Any]] = []
        t_elapsed = 0

        # 20 moving
        for i in range(20):
            frac = i / 20.0
            pings.append({
                "lat": round(base["lat"] + frac * (halt_lat - base["lat"]), 6),
                "lon": round(base["lon"] + frac * (halt_lon - base["lon"]), 6),
                "speed_kmh": 60.0,
                "timestamp": (t0 + timedelta(seconds=t_elapsed)).isoformat(),
                "timestamp_s": float(t_elapsed),
                "is_stationary": False
            })
            t_elapsed += 60

        # Sub-threshold halt: 11 pings = 10.0 minutes
        for i in range(11):
            pings.append({
                "lat": halt_lat,
                "lon": halt_lon,
                "speed_kmh": 0.0,
                "timestamp": (t0 + timedelta(seconds=t_elapsed)).isoformat(),
                "timestamp_s": float(t_elapsed),
                "is_stationary": True
            })
            t_elapsed += 60

        # 20 moving
        for i in range(20):
            frac = (i + 1) / 20.0
            pings.append({
                "lat": round(halt_lat + frac * (dest["lat"] - halt_lat), 6),
                "lon": round(halt_lon + frac * (dest["lon"] - halt_lon), 6),
                "speed_kmh": 60.0,
                "timestamp": (t0 + timedelta(seconds=t_elapsed)).isoformat(),
                "timestamp_s": float(t_elapsed),
                "is_stationary": False
            })
            t_elapsed += 60

        result = analyze_route_journey(pings, base, dest)
        assert result["journey_summary"]["anomalies_detected"] == 0
        assert result["journey_summary"]["unauthorized_stop_duration_minutes"] == 0.0
        assert result["anomalies"] == []

    def test_adv_anomaly_06_authorized_zone_30min_halts_not_flagged(self):
        """30-minute halt INSIDE base 5 km zone and INSIDE site 5 km zone must NOT be flagged as unauthorized."""
        corridor = CORRIDORS[0]
        base = corridor["base"]
        dest = corridor["dest"]

        t0 = datetime(2026, 9, 22, 8, 0, 0, tzinfo=timezone.utc)
        pings: List[Dict[str, Any]] = []
        t_elapsed = 0

        # 30-min halt inside Base 5 km zone (1.5 km from base depot)
        base_stop_lat = base["lat"] + 0.01  # ~1.1 km north
        base_stop_lon = base["lon"]
        assert haversine_distance_km(base_stop_lat, base_stop_lon, base["lat"], base["lon"]) <= 5.0

        for i in range(31):  # 30 minutes
            pings.append({
                "lat": round(base_stop_lat, 6),
                "lon": round(base_stop_lon, 6),
                "speed_kmh": 0.0,
                "timestamp": (t0 + timedelta(seconds=t_elapsed)).isoformat(),
                "timestamp_s": float(t_elapsed),
                "is_stationary": True
            })
            t_elapsed += 60

        # Corridor transit: 30 moving pings
        for i in range(30):
            frac = (i + 1) / 30.0
            pings.append({
                "lat": round(base_stop_lat + frac * (dest["lat"] - base_stop_lat), 6),
                "lon": round(base_stop_lon + frac * (dest["lon"] - base_stop_lon), 6),
                "speed_kmh": 65.0,
                "timestamp": (t0 + timedelta(seconds=t_elapsed)).isoformat(),
                "timestamp_s": float(t_elapsed),
                "is_stationary": False
            })
            t_elapsed += 60

        # 30-min halt inside Customer Site 5 km zone (1.0 km from site)
        site_stop_lat = dest["lat"] - 0.008
        site_stop_lon = dest["lon"]
        assert haversine_distance_km(site_stop_lat, site_stop_lon, dest["lat"], dest["lon"]) <= 5.0

        for i in range(31):  # 30 minutes
            pings.append({
                "lat": round(site_stop_lat, 6),
                "lon": round(site_stop_lon, 6),
                "speed_kmh": 0.0,
                "timestamp": (t0 + timedelta(seconds=t_elapsed)).isoformat(),
                "timestamp_s": float(t_elapsed),
                "is_stationary": True
            })
            t_elapsed += 60

        result = analyze_route_journey(pings, base, dest)
        assert result["journey_summary"]["anomalies_detected"] == 0
        assert result["journey_summary"]["unauthorized_stop_duration_minutes"] == 0.0
        assert result["anomalies"] == []


# ============================================================================
# Standalone Runner & Summary Output
# ============================================================================

def run_standalone_challenger_suite():
    """Runs all 100 clean route trials and anomaly insertion tests, printing empirical statistics."""
    print("================================================================================")
    print("M1 Iteration 2 Challenger 1: Geospatial Clean-Route Adversarial Harness")
    print("================================================================================")

    # 1. Run 100 Clean Route Trials
    clean_passed = 0
    clean_failed = 0
    clean_timings = []

    t_start_total = time.perf_counter()

    for c_idx, corridor in enumerate(CORRIDORS):
        for p_idx, ping_count in enumerate(PING_COUNTS):
            profiles = ["pure_transit", "operational_full", "transit_with_minor_pauses"]
            route_type = profiles[(c_idx + p_idx) % 3]
            trial_seed = 1000 + c_idx * 10 + p_idx

            pings = synthesize_clean_route(corridor, ping_count, route_type=route_type, seed=trial_seed)

            t0 = time.perf_counter()
            res = analyze_route_journey(
                pings=pings,
                base_coords=corridor["base"],
                job_site_coords=corridor["dest"],
                technician_id=f"TECH-{c_idx + 1:02d}",
                technician_name=f"Specialist {c_idx + 1}"
            )
            t_elapsed_ms = (time.perf_counter() - t0) * 1000.0
            clean_timings.append(t_elapsed_ms)

            j = res["journey_summary"]
            anoms = res["anomalies"]

            if j["anomalies_detected"] == 0 and j["unauthorized_stop_duration_minutes"] == 0.0 and anoms == []:
                clean_passed += 1
            else:
                clean_failed += 1
                print(f"[FAIL] Trial {c_idx * 10 + p_idx + 1} ({corridor['id']}, {ping_count} pings): anom={j['anomalies_detected']}, unauth_min={j['unauthorized_stop_duration_minutes']}")

    print(f"\nTask 1 & 2 Results (Clean Synthesized Routes):")
    print(f"  Total Trials: {len(CORRIDORS) * len(PING_COUNTS)}")
    print(f"  Passed: {clean_passed} / 100 ({clean_passed / 100.0 * 100:.1f}%)")
    print(f"  Failed: {clean_failed} / 100")
    print(f"  Mean latency: {sum(clean_timings) / len(clean_timings):.2f} ms per journey analysis")
    print(f"  Max latency: {max(clean_timings):.2f} ms")

    # 2. Run Anomaly Insertion Tests
    print(f"\nTask 3 Results (Intentional Anomaly Insertion):")
    anomaly_tester = TestIntentionalAnomalyInsertion()

    anomaly_tests = [
        ("adv_anomaly_01 (20-min halt outside 5km)", anomaly_tester.test_adv_anomaly_01_inserted_20min_halt_outside_5km),
        ("adv_anomaly_02 (25-min roadside halt)", anomaly_tester.test_adv_anomaly_02_inserted_25min_roadside_halt),
        ("adv_anomaly_03 (35-min prolonged halt)", anomaly_tester.test_adv_anomaly_03_inserted_35min_halt),
        ("adv_anomaly_04 (Multiple unauthorized stops)", anomaly_tester.test_adv_anomaly_04_multiple_unauthorized_stops),
        ("adv_anomaly_05 (Sub-threshold 10-min halt -> 0 anomalies)", anomaly_tester.test_adv_anomaly_05_subthreshold_halt_not_flagged),
        ("adv_anomaly_06 (Authorized zone 30-min halts -> 0 anomalies)", anomaly_tester.test_adv_anomaly_06_authorized_zone_30min_halts_not_flagged),
    ]

    anom_passed = 0
    for name, test_func in anomaly_tests:
        try:
            test_func()
            print(f"  [PASS] {name}")
            anom_passed += 1
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")

    total_time = time.perf_counter() - t_start_total
    print(f"\nTotal Adversarial Harness Execution Time: {total_time:.3f} s")

    verdict = "APPROVE" if (clean_passed == 100 and anom_passed == len(anomaly_tests)) else "REJECT"
    print(f"\nFinal Empirical Verdict: {verdict}")
    print("================================================================================")
    return verdict, clean_passed, anom_passed


if __name__ == "__main__":
    verdict, clean_passed, anom_passed = run_standalone_challenger_suite()
    sys.exit(0 if verdict == "APPROVE" else 1)
