"""
Tier 5 Adversarial Stress Test Suite: Analytics Conservation, Date Boundaries,
Multi-Dimensional Filtering, and API Concurrency.
Authored by m1_challenger_2.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import asyncio
import random
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List
import pytest
import httpx
from fastapi.testclient import TestClient

from app.main import create_app
from app.services.analytics_engine import AnalyticsEngine
from app.services.mock_generator import KroneMockGenerator
from app.services.sync_service import SyncService


# ============================================================================
# 1. INVARIANT CONSERVATION STRESS TESTS (10,000+ SAMPLES)
# ============================================================================

class TestInvariantConservationStress:
    """
    Stress-tests the Conservation Law of Hours:
    H_shift = H_w + H_t + H_i
    Verifies that |H_shift - (H_w + H_t + H_i)| < 1e-7 across all records.
    """

    def test_invariant_conservation_10000_random_records(self):
        """
        Generates 10,000 randomized shift intervals with varied distributions:
        - raw shift: [0.0, 24.0] hours
        - working hours: [0.0, 16.0] hours
        - travelling hours: [0.0, 8.0] hours
        - unauthorized & base idle hours: [0.0, 4.0] hours
        Enforces tolerance: |H_shift - (H_w + H_t + H_i)| < 1e-7.
        """
        random.seed(42)
        tolerance = 1e-7
        max_diff = 0.0
        violations = []

        for i in range(10000):
            raw_shift = random.uniform(0.0, 24.0)
            w = random.uniform(0.0, 16.0)
            t = random.uniform(0.0, 8.0)
            u = random.uniform(0.0, 4.0) if random.random() > 0.5 else 0.0
            b = random.uniform(0.0, 4.0) if random.random() > 0.5 else 0.0

            res = AnalyticsEngine.enforce_hours_conservation(
                raw_shift_hours=raw_shift,
                working_hours=w,
                travelling_hours=t,
                unauthorized_hours=u,
                base_idle_hours=b
            )

            h_shift = res["shift_hours"]
            h_w = res["working_hours"]
            h_t = res["travelling_hours"]
            h_i = res["idle_hours"]

            diff = abs(h_shift - (h_w + h_t + h_i))
            if diff > max_diff:
                max_diff = diff

            if diff >= tolerance:
                violations.append((i, raw_shift, w, t, u, b, diff))

        assert len(violations) == 0, f"Found {len(violations)} conservation violations: {violations[:3]}"
        assert max_diff < tolerance, f"Max difference {max_diff} exceeded tolerance {tolerance}"

    def test_invariant_conservation_pathological_edge_cases(self):
        """
        Adversarially tests boundary conditions:
        - Zero hours
        - Fractional micro-durations (0.00005)
        - Heavy overtime (W + T >> raw_shift)
        - High-magnitude hours (10,000 hours)
        - Floating precision rounding edge values (.99995, .00005)
        - Negative inputs clamped to 0.0
        """
        edge_cases = [
            (0.0, 0.0, 0.0, 0.0, 0.0),
            (8.0, 0.0, 0.0, 0.0, 0.0),
            (8.0, 8.0, 0.0, 0.0, 0.0),
            (8.0, 4.0, 4.0, 0.0, 0.0),
            (8.0, 6.0, 3.0, 0.0, 0.0),  # Overtime: 6 + 3 = 9 > 8
            (0.0001, 0.00005, 0.00005, 0.0, 0.0),
            (8.0, 7.99995, 0.00005, 0.0, 0.0),
            (10000.0, 6000.0, 3000.0, 500.0, 500.0),
            (12.0, 4.333333, 2.666667, 1.111111, 0.888889),
            (-8.0, -4.0, -2.0, 0.0, 0.0),  # Negatives should clamp to 0
        ]

        tolerance = 1e-7
        for c in edge_cases:
            res = AnalyticsEngine.enforce_hours_conservation(*c)
            diff = abs(res["shift_hours"] - (res["working_hours"] + res["travelling_hours"] + res["idle_hours"]))
            assert diff < tolerance, f"Edge case {c} failed with diff {diff}: {res}"
            assert res["idle_hours"] >= 0.0
            assert res["shift_hours"] >= 0.0


# ============================================================================
# 2. DATE RANGE BOUNDARY TESTS
# ============================================================================

class TestDateRangeBoundaries:
    """
    Verifies analytics filtering across diverse date range boundaries:
    - Cross-month
    - Cross-year
    - Leap year (February 29)
    - Zero-length ranges
    - Future dates
    - Inverted date ranges
    """

    @pytest.fixture
    def engine(self):
        return AnalyticsEngine()

    def test_cross_month_aggregation(self, engine):
        """Cross-month range spanning August 28 to September 2."""
        shifts = []
        base = datetime(2026, 8, 25)
        for d in range(12):
            cur = (base + timedelta(days=d)).strftime("%Y-%m-%d")
            shifts.append({
                "technician_id": "TECH-01",
                "date": cur,
                "shift_hours": 8.0,
                "working_hours": 6.0,
                "travelling_hours": 1.5,
                "distance_km": 50.0
            })

        res = engine.aggregate_productivity(
            daily_shift_records=shifts,
            jobs_records=[],
            start_date="2026-08-28",
            end_date="2026-09-02"
        )
        periods = [t["period"] for t in res["trend_data"]]
        assert len(periods) == 6
        assert "2026-08-31" in periods
        assert "2026-09-01" in periods
        assert res["summary"]["total_shift_hours"] == 48.0

    def test_cross_year_aggregation(self, engine):
        """Cross-year range spanning December 30, 2025 to January 2, 2026."""
        shifts = []
        base = datetime(2025, 12, 28)
        for d in range(8):
            cur = (base + timedelta(days=d)).strftime("%Y-%m-%d")
            shifts.append({
                "technician_id": "TECH-01",
                "date": cur,
                "shift_hours": 8.0,
                "working_hours": 5.0,
                "travelling_hours": 2.0,
                "distance_km": 40.0
            })

        res = engine.aggregate_productivity(
            daily_shift_records=shifts,
            jobs_records=[],
            start_date="2025-12-30",
            end_date="2026-01-02"
        )
        periods = [t["period"] for t in res["trend_data"]]
        assert len(periods) == 4
        assert "2025-12-31" in periods
        assert "2026-01-01" in periods
        assert res["summary"]["total_shift_hours"] == 32.0

    def test_leap_year_boundary(self, engine):
        """Leap year range containing Feb 29 (2024-02-28 to 2024-03-01)."""
        shifts = []
        base = datetime(2024, 2, 27)
        for d in range(5):
            cur = (base + timedelta(days=d)).strftime("%Y-%m-%d")
            shifts.append({
                "technician_id": "TECH-01",
                "date": cur,
                "shift_hours": 8.0,
                "working_hours": 6.0,
                "travelling_hours": 1.0,
                "distance_km": 30.0
            })

        res = engine.aggregate_productivity(
            daily_shift_records=shifts,
            jobs_records=[],
            start_date="2024-02-28",
            end_date="2024-03-01"
        )
        periods = [t["period"] for t in res["trend_data"]]
        assert "2024-02-29" in periods
        assert len(periods) == 3
        assert res["summary"]["total_shift_hours"] == 24.0

    def test_zero_length_range(self, engine):
        """Zero-length range where start_date == end_date."""
        shifts = [
            {"technician_id": "TECH-01", "date": "2026-09-22", "shift_hours": 8.0, "working_hours": 6.0, "travelling_hours": 2.0},
            {"technician_id": "TECH-01", "date": "2026-09-21", "shift_hours": 8.0, "working_hours": 5.0, "travelling_hours": 2.0},
        ]
        res = engine.aggregate_productivity(
            daily_shift_records=shifts,
            jobs_records=[],
            start_date="2026-09-22",
            end_date="2026-09-22"
        )
        assert len(res["trend_data"]) == 1
        assert res["summary"]["total_shift_hours"] == 8.0

    def test_future_and_inverted_date_ranges(self, engine):
        """Future and inverted date ranges should cleanly return empty/zero results without crashing."""
        shifts = [
            {"technician_id": "TECH-01", "date": "2026-09-22", "shift_hours": 8.0, "working_hours": 6.0, "travelling_hours": 2.0},
        ]
        # Future dates
        res_future = engine.aggregate_productivity(shifts, [], start_date="2035-01-01", end_date="2035-12-31")
        assert res_future["summary"]["total_shift_hours"] == 0.0
        assert len(res_future["technician_records"]) == 0

        # Inverted dates (start > end)
        res_inv = engine.aggregate_productivity(shifts, [], start_date="2026-10-01", end_date="2026-09-01")
        assert res_inv["summary"]["total_shift_hours"] == 0.0
        assert len(res_inv["technician_records"]) == 0


# ============================================================================
# 3. MULTI-DIMENSIONAL FILTER PERMUTATIONS
# ============================================================================

class TestMultiDimensionalFilterPermutations:
    """
    Randomized multi-dimensional filter permutations across technician,
    customer, job status, and job type.
    """

    @pytest.fixture
    def test_client(self):
        app = create_app()
        return TestClient(app)

    def test_filter_permutations_engine(self):
        """Tests 200 randomized filter combinations directly against AnalyticsEngine."""
        gen = KroneMockGenerator()
        dataset = gen.generate_all()
        shifts = dataset["daily_shifts"]
        jobs = dataset["jobs"]
        engine = AnalyticsEngine()

        techs = [None, "ALL", "TECH-01", "TECH-02", "TECH-05", "TECH-999"]
        customers = [None, "ALL", "Reliance", "Adani", "SAEL", "NonExistent"]
        statuses = [None, "ALL", "In Progress", "Completed", "Hold"]
        types = [None, "ALL", "Paid", "AMC", "Warranty"]
        timeframes = ["daily", "weekly", "monthly"]

        random.seed(123)
        for _ in range(200):
            t = random.choice(techs)
            c = random.choice(customers)
            s = random.choice(statuses)
            jt = random.choice(types)
            tf = random.choice(timeframes)

            res = engine.aggregate_productivity(
                daily_shift_records=shifts,
                jobs_records=jobs,
                timeframe=tf,
                technician_id=t,
                customer_company=c,
                job_status=s,
                job_type=jt
            )

            # Check individual technician records satisfy conservation
            for tr in res["technician_records"]:
                w = tr["working_hours"]
                trv = tr["travelling_hours"]
                idl = tr["idle_hours"]
                sh = tr["shift_hours"]
                assert abs(sh - (w + trv + idl)) <= 0.05

    def test_filter_permutations_via_fastapi_client(self, test_client):
        """Executes 50 random filter queries through the FastAPI /api/analytics/productivity endpoint."""
        random.seed(456)
        techs = [None, "ALL", "TECH-01", "TECH-03", "TECH-999"]
        customers = [None, "ALL", "Reliance", "Adani", "SAEL"]
        statuses = [None, "ALL", "In Progress", "Completed"]
        types = [None, "ALL", "Paid", "AMC"]

        for _ in range(50):
            params = {"timeframe": random.choice(["daily", "weekly", "monthly"])}
            t = random.choice(techs)
            if t: params["technician_id"] = t
            c = random.choice(customers)
            if c: params["customer_company"] = c
            s = random.choice(statuses)
            if s: params["job_status"] = s
            jt = random.choice(types)
            if jt: params["job_type"] = jt

            resp = test_client.get("/api/analytics/productivity", params=params)
            assert resp.status_code == 200, f"Query failed for params {params}: {resp.text}"
            data = resp.json()
            assert "summary" in data
            assert "technician_records" in data


# ============================================================================
# 4. API CONCURRENCY & THREAD-SAFETY STRESS TESTS
# ============================================================================

class TestApiConcurrencyAndThreadSafety:
    """
    Stress-tests FastAPI endpoints and mock cache under concurrent execution:
    - Async concurrency (httpx.AsyncClient with ASGITransport)
    - Cache integrity verification
    - Cross-event-loop lock boundary analysis
    """

    @pytest.mark.asyncio
    async def test_async_concurrent_requests_all_endpoints(self):
        """
        Sends 120 concurrent asynchronous requests interleaving:
        - POST /api/dashboard/sync (force_refresh=True)
        - GET /api/dashboard/pulse
        - GET /api/analytics/productivity
        - GET /api/telematics/routes
        Verifies all 120 requests succeed (HTTP 200) without unhandled exceptions.
        """
        app = create_app()
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
            tasks = []
            for i in range(120):
                mod = i % 4
                if mod == 0:
                    tasks.append(client.post("/api/dashboard/sync", json={"force_refresh": True}))
                elif mod == 1:
                    tasks.append(client.get("/api/dashboard/pulse"))
                elif mod == 2:
                    tasks.append(client.get("/api/analytics/productivity?timeframe=daily"))
                else:
                    tasks.append(client.get("/api/telematics/routes?technician_id=TECH-01&date=2026-09-22"))

            responses = await asyncio.gather(*tasks, return_exceptions=True)

            exceptions = [r for r in responses if isinstance(r, Exception)]
            bad_statuses = [r for r in responses if not isinstance(r, Exception) and r.status_code != 200]

            assert len(exceptions) == 0, f"Encountered async exceptions: {exceptions}"
            assert len(bad_statuses) == 0, f"Encountered non-200 responses: {bad_statuses}"

    def test_mock_cache_persistence_integrity_after_concurrency(self):
        """Verifies that the disk cache file remains valid, non-empty JSON after concurrent syncs."""
        cache_path = Path(__file__).parent.parent / "backend" / "cache" / "fieldy_cache.json"
        assert cache_path.exists(), "Cache file must exist after sync"
        import json
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "data" in data
        assert "sync_id" in data
        assert "last_synced_at" in data
        assert len(data["data"].get("jobs", [])) > 0

    def test_sync_service_asyncio_lock_event_loop_boundary_documented(self):
        """
        Adversarial architectural verification:
        Empirically checks that SyncService._lock is an asyncio.Lock.
        Documents that in Python's asyncio model, asyncio.Lock is scoped to a single
        event loop. Cross-thread concurrent invocation with independent event loops
        requires an application-level thread lock if executed outside the ASGI event loop.
        """
        service = SyncService()
        assert isinstance(service._lock, asyncio.Lock), "SyncService._lock is an asyncio.Lock"
