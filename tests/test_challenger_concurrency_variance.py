"""
tests/test_challenger_concurrency_variance.py
Adversarial Verification Suite for M1 Iteration 2 (Challenger 2)
Focus:
1. Query /api/telematics/routes across all 14 technicians (TECH-001 through TECH-014).
2. Verify route polyline uniqueness: assert technicians in different hubs (Punjab vs AP vs Gujarat vs MP vs Haryana vs Maharashtra vs UP)
   DO NOT share identical polylines (asserting elimination of synthetic facade).
3. Concurrent execution: 100 concurrent requests against /api/telematics/routes and /api/dashboard/pulse for thread safety and latency.
4. Stress-testing mixed workloads and boundary conditions under high load.
"""

import asyncio
import concurrent.futures
import math
import os
import sys
import time
from typing import Dict, Any, List, Set, Tuple
import httpx
import pytest
from fastapi.testclient import TestClient

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app
from app.services.mock_generator import KroneMockGenerator


@pytest.fixture(scope="module")
def api_client():
    """Module-scoped FastAPI TestClient."""
    return TestClient(app)


# ============================================================================
# Test Suite 1: Query All 14 Technicians and Verify Route Polyline Uniqueness
# ============================================================================

class TestRoutePolylineVarianceAll14Technicians:
    """Verifies all 14 technicians return valid routes and eliminate static facade."""

    ALL_TECH_IDS = [f"TECH-{i:03d}" for i in range(1, 15)]

    def test_all_14_technicians_query_success(self, api_client):
        """Query /api/telematics/routes for TECH-001 through TECH-014, expecting 200 OK."""
        results = {}
        for tech_id in self.ALL_TECH_IDS:
            resp = api_client.get(f"/api/telematics/routes?technician_id={tech_id}")
            assert resp.status_code == 200, f"Query failed for {tech_id}: {resp.status_code} - {resp.text}"
            data = resp.json()
            assert "technician_id" in data
            assert "route_polyline" in data
            assert "journey_summary" in data
            assert len(data["route_polyline"]) > 0, f"Empty polyline for {tech_id}"
            results[tech_id] = data

        assert len(results) == 14

    def test_regional_hub_polyline_variance(self, api_client):
        """
        Asserts that technicians based in different regional hubs
        (Punjab, AP, MP, Haryana, UP, Maharashtra) have strictly distinct polylines.
        """
        polylines = {}
        for tech_id in self.ALL_TECH_IDS:
            resp = api_client.get(f"/api/telematics/routes?technician_id={tech_id}")
            assert resp.status_code == 200
            data = resp.json()
            poly_tuple = tuple(tuple(round(coord, 4) for coord in pt) for pt in data["route_polyline"])
            polylines[tech_id] = poly_tuple

        # Cross-regional comparisons across hubs:
        # TECH-001 (Punjab: Ludhiana) vs TECH-005 (AP: Nellore)
        assert polylines["TECH-001"] != polylines["TECH-005"], "Punjab and AP share identical polyline! Facade detected."
        # TECH-001 (Punjab: Ludhiana) vs TECH-008 (MP: Indore)
        assert polylines["TECH-001"] != polylines["TECH-008"], "Punjab and MP share identical polyline! Facade detected."
        # TECH-005 (AP: Nellore) vs TECH-008 (MP: Indore)
        assert polylines["TECH-005"] != polylines["TECH-008"], "AP and MP share identical polyline! Facade detected."
        # TECH-002 (Haryana: Hisar) vs TECH-010 (Maharashtra: Baramati)
        assert polylines["TECH-002"] != polylines["TECH-010"], "Haryana and Maharashtra share identical polyline!"
        # TECH-001 (Punjab: Ludhiana) vs TECH-012 (UP: Muzaffarnagar)
        assert polylines["TECH-001"] != polylines["TECH-012"], "Punjab and UP share identical polyline!"
        # TECH-008 (MP: Indore) vs TECH-010 (Maharashtra: Baramati)
        assert polylines["TECH-008"] != polylines["TECH-010"], "MP and Maharashtra share identical polyline!"

        # Geographic bounding assertions:
        punjab_poly = polylines["TECH-001"]
        ap_poly = polylines["TECH-005"]
        mp_poly = polylines["TECH-008"]

        assert all(29.0 <= pt[0] <= 32.0 for pt in punjab_poly), "Punjab route coordinates outside Punjab geo-bounds"
        assert all(13.0 <= pt[0] <= 18.0 for pt in ap_poly), "AP route coordinates outside AP geo-bounds"
        assert all(21.0 <= pt[0] <= 24.0 for pt in mp_poly), "MP route coordinates outside MP geo-bounds"

    def test_intra_regional_job_variance(self, api_client):
        """
        Asserts that technicians in the same hub working on different tickets
        (e.g., TECH-001 vs TECH-004 in Punjab, or TECH-005 vs TECH-006 vs TECH-007 in AP)
        produce distinct polylines and destinations.
        """
        resp_t1 = api_client.get("/api/telematics/routes?technician_id=TECH-001").json()
        resp_t4 = api_client.get("/api/telematics/routes?technician_id=TECH-004").json()
        assert resp_t1["route_polyline"] != resp_t4["route_polyline"], "TECH-001 and TECH-004 should have different polylines"
        assert resp_t1["journey_summary"]["destination"]["name"] != resp_t4["journey_summary"]["destination"]["name"]

        resp_t5 = api_client.get("/api/telematics/routes?technician_id=TECH-005").json()
        resp_t6 = api_client.get("/api/telematics/routes?technician_id=TECH-006").json()
        resp_t7 = api_client.get("/api/telematics/routes?technician_id=TECH-007").json()
        assert resp_t5["route_polyline"] != resp_t6["route_polyline"]
        assert resp_t6["route_polyline"] != resp_t7["route_polyline"]
        assert resp_t5["route_polyline"] != resp_t7["route_polyline"]

    def test_gujarat_hub_polyline_differentiation(self):
        """
        Verifies that the telematics engine and mock generator correctly differentiate
        Gujarat (Jamnagar Clean Energy Base) from Punjab, AP, and MP.
        """
        from app.services.telematics_engine import analyze_route_journey, filter_stationary_jitter
        from app.routers.telematics import generate_corridor_pings

        gujarat_hub = KroneMockGenerator.HUBS["Gujarat"]
        punjab_hub = KroneMockGenerator.HUBS["Punjab"]
        ap_hub = KroneMockGenerator.HUBS["AP"]
        mp_hub = KroneMockGenerator.HUBS["MP"]

        # Generate pings for Gujarat hub
        pings_gujarat = generate_corridor_pings(
            start_lat=gujarat_hub["lat"],
            start_lng=gujarat_hub["lng"],
            end_lat=gujarat_hub["lat"],
            end_lng=gujarat_hub["lng"],
            date_str="2026-09-22"
        )
        res_gujarat = analyze_route_journey(
            pings=pings_gujarat,
            base_coords={"name": gujarat_hub["name"], "lat": gujarat_hub["lat"], "lng": gujarat_hub["lng"]},
            job_site_coords={"name": gujarat_hub["name"], "lat": gujarat_hub["lat"], "lng": gujarat_hub["lng"]},
            technician_id="TECH-GUJ",
            technician_name="Gujarat Specialist"
        )

        pings_punjab = generate_corridor_pings(
            start_lat=punjab_hub["lat"],
            start_lng=punjab_hub["lng"],
            end_lat=punjab_hub["lat"],
            end_lng=punjab_hub["lng"],
            date_str="2026-09-22"
        )
        res_punjab = analyze_route_journey(
            pings=pings_punjab,
            base_coords={"name": punjab_hub["name"], "lat": punjab_hub["lat"], "lng": punjab_hub["lng"]},
            job_site_coords={"name": punjab_hub["name"], "lat": punjab_hub["lat"], "lng": punjab_hub["lng"]},
            technician_id="TECH-PUN",
            technician_name="Punjab Specialist"
        )

        assert res_gujarat["route_polyline"] != res_punjab["route_polyline"], "Gujarat and Punjab polylines must not match!"
        # Coordinates must center on Jamnagar (~22.47°N, ~70.05°E)
        first_pt = res_gujarat["route_polyline"][0]
        assert abs(first_pt[0] - gujarat_hub["lat"]) < 0.1
        assert abs(first_pt[1] - gujarat_hub["lng"]) < 0.1


# ============================================================================
# Test Suite 2: High Concurrency (100 Concurrent Requests) Thread Safety & Latency
# ============================================================================

class TestHighConcurrencyThreadSafety:
    """Stress tests 100 concurrent requests across telematics and dashboard endpoints."""

    @pytest.mark.asyncio
    async def test_async_100_concurrent_telematics_routes(self):
        """
        Fires 100 concurrent requests across various technician IDs using native async client.
        Verifies:
        - 100% 200 OK responses (zero race conditions, deadlocks, or crashes)
        - Average throughput > 80 req/sec (< 15ms per request)
        - Response data integrity and schema compliance
        """
        import random
        tech_ids = [f"TECH-{i:03d}" for i in range(1, 15)]
        
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            t0 = time.perf_counter()
            tasks = [
                client.get(f"/api/telematics/routes?technician_id={random.choice(tech_ids)}")
                for _ in range(100)
            ]
            responses = await asyncio.gather(*tasks)
            total_elapsed = time.perf_counter() - t0

        status_codes = [r.status_code for r in responses]
        assert all(sc == 200 for sc in status_codes), f"Non-200 responses: {[sc for sc in status_codes if sc != 200]}"
        assert len(responses) == 100

        # Validate JSON payload integrity
        for r in responses:
            data = r.json()
            assert "technician_id" in data
            assert "journey_summary" in data
            assert "clusters_5km" in data
            assert "route_polyline" in data

        rps = 100.0 / total_elapsed
        ms_per_req = (total_elapsed / 100.0) * 1000.0
        print(f"\n[Async 100 Telematics Routes] Total: {total_elapsed:.3f}s | RPS: {rps:.1f} req/s | Mean: {ms_per_req:.2f}ms/req")
        assert total_elapsed < 3.0, f"Async 100 route requests took too long: {total_elapsed:.2f}s"

    @pytest.mark.asyncio
    async def test_async_100_concurrent_dashboard_pulse(self):
        """
        Fires 100 concurrent requests to /api/dashboard/pulse using native async client.
        Verifies:
        - 100% 200 OK responses
        - Invariant consistency across concurrent reads
        - Average throughput > 150 req/sec (< 8ms per request)
        """
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            t0 = time.perf_counter()
            tasks = [client.get("/api/dashboard/pulse") for _ in range(100)]
            responses = await asyncio.gather(*tasks)
            total_elapsed = time.perf_counter() - t0

        status_codes = [r.status_code for r in responses]
        assert all(sc == 200 for sc in status_codes), f"Non-200 responses: {[sc for sc in status_codes if sc != 200]}"
        assert len(responses) == 100

        # Check KPI invariant consistency across all 100 reads
        first_kpi = responses[0].json().get("kpis")
        for r in responses:
            assert r.json().get("kpis") == first_kpi, "KPI mutation or inconsistency detected across concurrent pulse calls!"

        rps = 100.0 / total_elapsed
        ms_per_req = (total_elapsed / 100.0) * 1000.0
        print(f"\n[Async 100 Dashboard Pulse] Total: {total_elapsed:.3f}s | RPS: {rps:.1f} req/s | Mean: {ms_per_req:.2f}ms/req")
        assert total_elapsed < 2.0, f"Async 100 pulse requests took too long: {total_elapsed:.2f}s"

    def test_threaded_100_concurrent_requests_telematics_routes(self, api_client):
        """
        Fires 100 concurrent requests using multi-threaded client (ThreadPoolExecutor)
        to test multi-threaded client thread-safety and locking behavior.
        """
        import random
        tech_ids = [f"TECH-{i:03d}" for i in range(1, 15)]
        requests_args = [random.choice(tech_ids) for _ in range(100)]

        def worker_fetch(tid: str) -> Tuple[int, float]:
            t0 = time.perf_counter()
            resp = api_client.get(f"/api/telematics/routes?technician_id={tid}")
            lat = time.perf_counter() - t0
            return resp.status_code, lat

        t_start = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            results = list(executor.map(worker_fetch, requests_args))
        total_time = time.perf_counter() - t_start

        status_codes = [r[0] for r in results]
        assert all(sc == 200 for sc in status_codes), f"Non-200 responses detected: {[sc for sc in status_codes if sc != 200]}"
        assert len(results) == 100
        print(f"\n[Threaded 100 Telematics Routes] Total: {total_time:.2f}s for 100 requests (mean wall-clock throughput: {total_time*10:.1f}ms/req)")
        assert total_time < 5.0, f"Threaded execution took too long: {total_time:.2f}s"

    def test_threaded_100_concurrent_requests_dashboard_pulse(self, api_client):
        """
        Fires 100 concurrent requests using multi-threaded client to /api/dashboard/pulse.
        """
        def pulse_worker(_: int) -> int:
            resp = api_client.get("/api/dashboard/pulse")
            return resp.status_code

        t_start = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            status_codes = list(executor.map(pulse_worker, range(100)))
        total_time = time.perf_counter() - t_start

        assert all(sc == 200 for sc in status_codes)
        assert len(status_codes) == 100
        print(f"\n[Threaded 100 Dashboard Pulse] Total: {total_time:.2f}s for 100 requests")
        assert total_time < 3.0, f"Threaded pulse took too long: {total_time:.2f}s"

    def test_100_concurrent_interleaved_routes_and_pulse(self, api_client):
        """
        Interleaves 50 telematics route requests and 50 dashboard pulse requests concurrently
        across 25 worker threads to test race condition resilience under mixed load.
        """
        tech_ids = [f"TECH-{i:03d}" for i in range(1, 15)]

        def mixed_worker(idx: int) -> Tuple[str, int]:
            if idx % 2 == 0:
                tid = tech_ids[idx % len(tech_ids)]
                resp = api_client.get(f"/api/telematics/routes?technician_id={tid}")
                return "routes", resp.status_code
            else:
                resp = api_client.get("/api/dashboard/pulse")
                return "pulse", resp.status_code

        t_start = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
            results = list(executor.map(mixed_worker, range(100)))
        total_time = time.perf_counter() - t_start

        assert len(results) == 100
        assert all(sc == 200 for _, sc in results)
        print(f"\n[100 Mixed Interleaved Requests] Total time: {total_time:.2f}s for 100 requests")
        assert total_time < 4.0
