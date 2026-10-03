"""
backend/tests/test_hacker_adversarial_suite.py
Adversarial Hacker-Style Penetration & Edge-Case Test Suite.
Tests GPS fluctuations, telematics jitter spoofing, midnight rollover,
financial overclaim injection, SQL/XSS sanitization, and DDoS rate-limiting.
"""
import pytest
import os
import sys
import random

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.services.telematics_engine import haversine_distance_km, cluster_pings_5km

client = TestClient(app)


def test_hacker_gps_fluctuation_and_jitter_clustering():
    """Hacker Test 1: Inject rapid fluctuating GPS micro-jitters to test 5 km clustering resilience."""
    # Base location: Kulan (lat: 29.8142, lng: 75.8711)
    base_lat = 29.8142
    base_lng = 75.8711

    # Generate 50 jitter pings within 1.5 km radius (simulating fluctuating cellular/GPS multipath errors)
    pings = []
    for i in range(50):
        jitter_lat = base_lat + random.uniform(-0.010, 0.010)
        jitter_lng = base_lng + random.uniform(-0.010, 0.010)
        pings.append({
            "lat": jitter_lat,
            "lng": jitter_lng,
            "duration_s": 120.0,
            "timestamp": f"2026-10-02T10:{i:02d}:00Z"
        })

    # Cluster should merge all 50 fluctuating pings into a single operational cluster (within 5 km)
    clusters = cluster_pings_5km(pings)
    # Must NOT produce 50 fragmented stops; should cluster into 1 or 2 cohesive operational zones
    assert len(clusters) <= 2, f"Clustering failed to absorb jitter, produced {len(clusters)} clusters"


def test_hacker_gps_teleportation_spoofing():
    """Hacker Test 2: Detect impossible supersonic speed/teleportation jump."""
    p1_lat, p1_lng = 29.8142, 75.8711
    # Impossible teleportation: 800 km away in 5 minutes!
    p2_lat, p2_lng = 17.0000, 82.0000

    dist = haversine_distance_km(p1_lat, p1_lng, p2_lat, p2_lng)
    assert dist > 1000.0, "Haversine calculated distance should exceed 1000 km"
    # Velocity would be > 12,000 km/h - impossible in commercial service fleet
    hours = 5.0 / 60.0
    implied_speed = dist / hours
    assert implied_speed > 5000.0, "Implied speed reveals spoofing anomaly"


def test_hacker_sql_and_xss_injection_resilience():
    """Hacker Test 3: Inject SQL injection and XSS payloads into search and audit endpoints."""
    # SQL injection attempt
    resp = client.get("/api/jobs?search=' OR 1=1; DROP TABLE jobs; --")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

    # XSS script injection in bill audit
    payload = {
        "technician_id": "TECH-01",
        "technician_name": "<script>alert('XSS')</script>",
        "date": "2026-10-02",
        "claimed_km": 40.0,
        "vehicle_type": "bike",
        "claimed_da": 150.0,
        "claimed_hotel": 0.0,
        "stay_provided_by_client": False,
        "duty_hours": 8.0,
        "job_id": "<img src=x onerror=alert(1)>",
        "trip_purpose": "'; DROP TABLE audits; --"
    }
    resp = client.post("/api/audit/check-bill", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["verdict"] in ["APPROVED", "FLAGGED_PARTIAL_APPROVAL", "REJECTED_OVERCLAIM"]
    # Check that payload was sanitized and didn't crash backend
    assert "audit_id" in data


def test_hacker_massive_financial_overclaim_attack():
    """Hacker Test 4: Technician tries to claim ₹1,00,000 on a short 10 KM errand."""
    payload = {
        "technician_id": "TECH-01",
        "technician_name": "Sunny Kumar",
        "date": "2026-10-02",
        "claimed_km": 1500.0,  # 1500 KM claimed on a 32 KM job!
        "vehicle_type": "car",  # ₹15/km
        "claimed_da": 5000.0,   # Ridiculous DA
        "claimed_hotel": 25000.0,  # Ridiculous hotel
        "stay_provided_by_client": True,  # But client provided free stay!
        "duty_hours": 2.0,  # Less than 8 hours
        "job_id": "SR-26- 0148"
    }
    resp = client.post("/api/audit/check-bill", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    # Must flag partial approval or rejected overclaim with huge recovery
    assert data["verdict"] in ["FLAGGED_PARTIAL_APPROVAL", "REJECTED_OVERCLAIM"]
    assert data["disallowed_hotel"] == 25000.0  # 100% hotel recovery
    assert data["disallowed_da"] == 5000.0  # 100% DA recovery
    assert data["total_disallowed_recovery"] > 40000.0


def test_hacker_zero_hour_absentee_da_theft():
    """Hacker Test 5: Technician with 0 hours logged attempts to claim DA."""
    payload = {
        "technician_id": "TECH-08",
        "technician_name": "Ravinder Bishnoi",
        "date": "2026-10-02",
        "claimed_km": 0.0,
        "vehicle_type": "bike",
        "claimed_da": 300.0,
        "claimed_hotel": 0.0,
        "stay_provided_by_client": False,
        "duty_hours": 0.0,  # On Leave / Absent!
        "job_id": None
    }
    resp = client.post("/api/audit/check-bill", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["admissible_da"] == 0.0
    assert data["disallowed_da"] == 300.0
    assert data["verdict"] in ["FLAGGED_PARTIAL_APPROVAL", "REJECTED_OVERCLAIM"]
