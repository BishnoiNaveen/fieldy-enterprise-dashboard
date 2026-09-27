import os
import sys

# Ensure backend directory is in sys.path
backend_dir = r"C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\backend"
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.services.analytics_engine import AnalyticsEngine
from app.services.telematics_engine import (
    haversine_distance_km,
    weighted_cartesian_centroid,
    filter_stationary_jitter,
    cluster_pings_5km,
    inspect_journey,
    compute_hours_balance,
    cross_track_distance_km,
    analyze_route_journey,
)

c = TestClient(app)

print("--- Running Adversarial Test Suite ---")

# 1. SQL Injection strings
r1 = c.get("/api/technicians", params={"search": "' OR 1=1 --"})
assert r1.status_code == 200, f"Expected 200, got {r1.status_code}"
assert len(r1.json()) == 0, "Should return empty on unmatched SQL injection"
print("Test 1 Passed: SQL Injection safely handled by in-memory filter")

# 2. XSS string in customer filter
r2 = c.get("/api/jobs", params={"customer": "<script>alert(1)</script>"})
assert r2.status_code == 200
assert len(r2.json()) == 0
print("Test 2 Passed: XSS string safely handled")

# 3. Nonexistent technician in routes
r3 = c.get("/api/telematics/routes", params={"technician_id": "NONEXISTENT_999"})
assert r3.status_code == 200
assert r3.json()["technician_id"] == "NONEXISTENT_999"
print("Test 3 Passed: Fallback route generated for unknown technician")

# 4. Empty sync body
r4 = c.post("/api/dashboard/sync", json={})
assert r4.status_code == 200
print("Test 4 Passed: Empty sync body accepted with default force_refresh=True")

# 5. Invalid sync body type
r5 = c.post("/api/dashboard/sync", json={"force_refresh": "not_a_bool"})
assert r5.status_code == 422
print("Test 5 Passed: Invalid type rejected with 422")

# 6. Extreme date range in productivity
r6 = c.get("/api/analytics/productivity", params={"start_date": "1970-01-01", "end_date": "2099-12-31"})
assert r6.status_code == 200
assert r6.json()["summary"]["total_shift_hours"] > 0
print("Test 6 Passed: Wide date range aggregates correctly")

# 7. Empty date range in productivity (future only)
r7 = c.get("/api/analytics/productivity", params={"start_date": "2099-01-01", "end_date": "2099-12-31"})
assert r7.status_code == 200
assert r7.json()["summary"]["total_shift_hours"] == 0.0
assert len(r7.json()["technician_records"]) == 0
print("Test 7 Passed: Out-of-bounds date range returns empty records with 0 hours")

# 8. Hours conservation under extreme values
eng = AnalyticsEngine()
res_ext = eng.enforce_hours_conservation(
    raw_shift_hours=100.0,
    working_hours=80.0,
    travelling_hours=20.0,
    unauthorized_hours=0.0
)
assert abs(res_ext["shift_hours"] - 100.0) < 1e-4
assert abs(res_ext["working_hours"] + res_ext["travelling_hours"] + res_ext["idle_hours"] - 100.0) < 1e-4
print("Test 8 Passed: 100-hour shift conservation strictly balanced")

# 9. Single point clustering
p_single = [{"lat": 28.5, "lon": 77.0, "duration_s": 600.0}]
c_single = cluster_pings_5km(p_single)
assert len(c_single) == 1
assert c_single[0]["radius_meters"] == 0.0
print("Test 9 Passed: Single point creates valid cluster with 0m radius")

print("--- ALL ADVERSARIAL TESTS COMPLETED SUCCESSFULLY ---")
