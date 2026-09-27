"""
backend/tests/test_api.py
Integration tests for FastAPI REST routers verifying HTTP status codes and contract schemas.
"""
import pytest
import os
import sys

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_pulse_endpoint_200():
    """TC-API-01: GET /api/dashboard/pulse returns 200 with complete KPI block."""
    resp = client.get("/api/dashboard/pulse")
    assert resp.status_code == 200
    data = resp.json()
    assert "kpis" in data
    assert "technicians_on_jobs" in data
    assert "machines_under_service" in data
    assert "sync_meta" in data
    assert data["kpis"]["technicians_on_paid_jobs"] >= 0


def test_pulse_machines_table_schema():
    """TC-API-02: Verifies machines under service contain serial numbers and site contacts."""
    resp = client.get("/api/dashboard/pulse")
    assert resp.status_code == 200
    machines = resp.json()["machines_under_service"]
    assert len(machines) > 0
    first = machines[0]
    assert "serial_number" in first
    assert "asset_name" in first
    assert "client_company_name" in first
    assert "site_contact_person" in first


def test_sync_endpoint_trigger():
    """TC-API-03: POST /api/dashboard/sync executes fresh synchronization cycle."""
    resp = client.post("/api/dashboard/sync", json={"force_refresh": True})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "sync_id" in data
    assert "last_synced_at" in data
    assert "records_updated" in data


def test_productivity_daily_default():
    """TC-API-04: GET /api/analytics/productivity defaults to daily timeframe."""
    resp = client.get("/api/analytics/productivity")
    assert resp.status_code == 200
    data = resp.json()
    assert data["timeframe"] == "daily"
    assert "summary" in data
    assert "technician_records" in data
    assert "trend_data" in data


def test_productivity_weekly_timeframe():
    """TC-API-05: GET /api/analytics/productivity?timeframe=weekly returns weekly rollups."""
    resp = client.get("/api/analytics/productivity?timeframe=weekly")
    assert resp.status_code == 200
    assert resp.json()["timeframe"] == "weekly"


def test_productivity_filter_technician():
    """TC-API-06: Filters productivity by technician_id."""
    resp = client.get("/api/analytics/productivity?technician_id=TECH-01")
    assert resp.status_code == 200
    records = resp.json()["technician_records"]
    assert len(records) <= 1
    if records:
        assert records[0]["technician_id"] == "TECH-01"


def test_productivity_invalid_timeframe_422():
    """TC-API-07: Rejects invalid timeframe parameter with HTTP 422."""
    resp = client.get("/api/analytics/productivity?timeframe=yearly")
    assert resp.status_code == 422


def test_telematics_routes_valid_technician():
    """TC-API-08: GET /api/telematics/routes returns journey summary and 5km clusters."""
    resp = client.get("/api/telematics/routes?technician_id=TECH-01")
    assert resp.status_code == 200
    data = resp.json()
    assert data["technician_id"] == "TECH-01"
    assert "journey_summary" in data
    assert "clusters_5km" in data
    assert "anomalies" in data
    assert "route_polyline" in data


def test_telematics_routes_missing_tech_id_422():
    """TC-API-09: Rejects call when required technician_id is missing."""
    resp = client.get("/api/telematics/routes")
    assert resp.status_code == 422


def test_technicians_list():
    """TC-API-10: GET /api/technicians returns 14 Krone technicians."""
    resp = client.get("/api/technicians")
    assert resp.status_code == 200
    techs = resp.json()
    assert len(techs) == 14
    assert any(t["name"] == "Gurpreet Singh" for t in techs)


def test_technicians_filter_status():
    """TC-API-11: GET /api/technicians?status=On%20Paid%20Job filters active engineers."""
    resp = client.get("/api/technicians?status=On%20Paid%20Job")
    assert resp.status_code == 200
    techs = resp.json()
    assert len(techs) == 8
    assert all(t["status"] == "On Paid Job" for t in techs)


def test_jobs_list():
    """TC-API-12: GET /api/jobs returns Fieldy jobs formatted as SR-26-XXXX."""
    resp = client.get("/api/jobs")
    assert resp.status_code == 200
    jobs = resp.json()
    assert len(jobs) > 0
    assert jobs[0]["job_id"].startswith("SR-26-")
