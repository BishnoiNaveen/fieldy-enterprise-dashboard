"""
backend/tests/test_analytics.py
Unit tests verifying the Hours Conservation Law, Multi-Tier Rollups, and Multi-Dimensional Filtering.
"""
import pytest
import os
import sys

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.analytics_engine import AnalyticsEngine


@pytest.fixture
def engine():
    return AnalyticsEngine()


@pytest.fixture
def sample_shifts():
    return [
        {
            "technician_id": "TECH-01",
            "technician_name": "Gurpreet Singh",
            "region": "Punjab",
            "customer_company": "Reliance Industries Limited",
            "date": "2026-09-22",
            "shift_hours": 8.0,
            "working_hours": 5.5,
            "travelling_hours": 1.5,
            "unauthorized_hours": 0.5,
            "base_idle_hours": 0.5,
            "distance_km": 80.0
        },
        {
            "technician_id": "TECH-02",
            "technician_name": "Vikram Sharma",
            "region": "Haryana",
            "customer_company": "Adani Agri Logistics Ltd",
            "date": "2026-09-22",
            "shift_hours": 8.0,
            "working_hours": 6.0,
            "travelling_hours": 1.0,
            "unauthorized_hours": 0.0,
            "base_idle_hours": 1.0,
            "distance_km": 50.0
        }
    ]


@pytest.fixture
def sample_jobs():
    return [
        {
            "job_id": "SR-26-0101",
            "technician_id": "TECH-01",
            "assigned_technician_ids": ["TECH-01"],
            "customer_name": "Reliance Industries Limited",
            "status": "In Progress",
            "job_type": "Paid",
            "date": "2026-09-22",
            "duration_hours": 5.5
        },
        {
            "job_id": "SR-26-0102",
            "technician_id": "TECH-02",
            "assigned_technician_ids": ["TECH-02"],
            "customer_name": "Adani Agri Logistics Ltd",
            "status": "Completed",
            "job_type": "Paid",
            "date": "2026-09-22",
            "duration_hours": 6.0
        }
    ]


def test_hours_conservation_exact_sum(engine):
    """TC-HRS-01: Verifies exact conservation law H_shift = H_w + H_t + H_i."""
    res = engine.enforce_hours_conservation(
        raw_shift_hours=8.0,
        working_hours=5.25,
        travelling_hours=1.75,
        unauthorized_hours=0.5
    )
    assert abs(res["shift_hours"] - (res["working_hours"] + res["travelling_hours"] + res["idle_hours"])) < 1e-6
    assert res["working_hours"] == 5.25
    assert res["travelling_hours"] == 1.75
    assert res["idle_hours"] == 1.0
    assert res["utilization_pct"] == 87.5


def test_hours_conservation_overtime_clamp(engine):
    """TC-HRS-02: Clamps shift hours when overtime work exceeds scheduled shift duration."""
    res = engine.enforce_hours_conservation(
        raw_shift_hours=8.0,
        working_hours=7.5,
        travelling_hours=2.0
    )
    # Total work + travel = 9.5, which exceeds raw 8.0
    assert res["shift_hours"] == 9.5
    assert res["idle_hours"] == 0.0
    assert res["utilization_pct"] == 100.0


def test_hours_conservation_zero_hours(engine):
    """TC-HRS-03: Handles technicians with zero working hours (e.g. idle all day)."""
    res = engine.enforce_hours_conservation(
        raw_shift_hours=8.0,
        working_hours=0.0,
        travelling_hours=0.0
    )
    assert res["shift_hours"] == 8.0
    assert res["working_hours"] == 0.0
    assert res["travelling_hours"] == 0.0
    assert res["idle_hours"] == 8.0
    assert res["utilization_pct"] == 0.0


def test_daily_rollup_aggregation(engine, sample_shifts, sample_jobs):
    """TC-HRS-04: Daily aggregation sums fleet hours and computes average utilization."""
    res = engine.aggregate_productivity(
        daily_shift_records=sample_shifts,
        jobs_records=sample_jobs,
        timeframe="daily"
    )
    summary = res["summary"]
    assert summary["total_working_hours"] == 11.5  # 5.5 + 6.0
    assert summary["total_travelling_hours"] == 2.5 # 1.5 + 1.0
    assert summary["total_idle_hours"] == 2.0       # 1.0 + 1.0
    assert summary["total_shift_hours"] == 16.0     # 8.0 + 8.0
    assert summary["total_distance_km"] == 130.0
    assert len(res["technician_records"]) == 2


def test_filter_by_technician_id(engine, sample_shifts, sample_jobs):
    """TC-HRS-05: Filters records accurately by technician_id."""
    res = engine.aggregate_productivity(
        daily_shift_records=sample_shifts,
        jobs_records=sample_jobs,
        timeframe="daily",
        technician_id="TECH-01"
    )
    assert len(res["technician_records"]) == 1
    assert res["technician_records"][0]["technician_id"] == "TECH-01"
    assert res["summary"]["total_working_hours"] == 5.5


def test_filter_by_customer_company(engine, sample_shifts, sample_jobs):
    """TC-HRS-06: Filters records by customer substring."""
    res = engine.aggregate_productivity(
        daily_shift_records=sample_shifts,
        jobs_records=sample_jobs,
        timeframe="daily",
        customer_company="Reliance"
    )
    assert len(res["technician_records"]) == 1
    assert res["technician_records"][0]["technician_id"] == "TECH-01"


def test_filter_by_job_status(engine, sample_shifts, sample_jobs):
    """TC-HRS-07: Filters jobs by status pipeline."""
    res = engine.aggregate_productivity(
        daily_shift_records=sample_shifts,
        jobs_records=sample_jobs,
        timeframe="daily",
        job_status="Completed"
    )
    assert res["summary"]["jobs_count"] == 1


def test_weekly_man_days_calculation(engine, sample_shifts, sample_jobs):
    """TC-HRS-08: Verifies billable man-day calculation (H_w / 8.0)."""
    res = engine.aggregate_productivity(
        daily_shift_records=sample_shifts,
        jobs_records=sample_jobs,
        timeframe="weekly"
    )
    tech1 = next(r for r in res["technician_records"] if r["technician_id"] == "TECH-01")
    assert tech1["man_days"] == round(5.5 / 8.0, 3)
    assert tech1["billable_revenue_inr"] == round(5.5 * 625.0, 2)


def test_trend_data_generation(engine, sample_shifts, sample_jobs):
    """TC-HRS-09: Generates valid chronological trend data series."""
    res = engine.aggregate_productivity(
        daily_shift_records=sample_shifts,
        jobs_records=sample_jobs,
        timeframe="daily"
    )
    trend = res["trend_data"]
    assert len(trend) == 1
    assert trend[0]["period"] == "2026-09-22"
    assert trend[0]["working"] == 11.5


def test_customer_distribution_percentage(engine, sample_shifts, sample_jobs):
    """TC-HRS-10: Customer distribution percentages sum up to 100%."""
    res = engine.aggregate_productivity(
        daily_shift_records=sample_shifts,
        jobs_records=sample_jobs,
        timeframe="daily"
    )
    cust_dist = res["customer_distribution"]
    assert len(cust_dist) == 2
    total_pct = sum(c["percentage"] for c in cust_dist)
    assert abs(total_pct - 100.0) < 0.5
