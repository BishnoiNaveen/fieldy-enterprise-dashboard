"""
tests/test_challenger_m2_api_integration.py
Adversarial Verification Suite for Milestone 2:
1. 100% JSON Key Parity Validation between FastAPI Backend and TypeScript Interfaces (dashboard.ts)
2. Live Vite Proxy Routing Verification (/api/* -> http://localhost:8000)
"""
import json
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any, Set, List
import pytest
import requests
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import create_app

client = TestClient(create_app())

ROOT_DIR = Path(__file__).resolve().parent.parent
TS_TYPES_FILE = ROOT_DIR / "frontend" / "src" / "types" / "dashboard.ts"


# ============================================================================
# HELPER: TypeScript Interface AST-lite Parser with Brace Depth Tracking
# ============================================================================
def extract_ts_interface_fields(ts_content: str, interface_name: str) -> Set[str]:
    """
    Extracts top-level defined property keys for a given TypeScript interface from dashboard.ts,
    correctly handling nested object braces and comments.
    """
    pattern = rf"export\s+interface\s+{interface_name}\b[^\{{]*\{{"
    match = re.search(pattern, ts_content)
    if not match:
        raise ValueError(f"Interface {interface_name} not found in TypeScript definitions.")

    start = match.end()
    depth = 1
    i = start
    top_level_lines = []
    current_line = []

    while i < len(ts_content) and depth > 0:
        c = ts_content[i]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                break
        if depth == 1:
            if c == '\n':
                top_level_lines.append("".join(current_line))
                current_line = []
            else:
                current_line.append(c)
        i += 1

    if current_line:
        top_level_lines.append("".join(current_line))

    fields = set()
    for line in top_level_lines:
        line = line.strip()
        if not line or line.startswith("//") or line.startswith("/*") or line.startswith("*"):
            continue
        field_match = re.match(r"^([a-zA-Z0-9_]+)\??\s*:", line)
        if field_match:
            fields.add(field_match.group(1))
    return fields


@pytest.fixture(scope="module")
def ts_content() -> str:
    assert TS_TYPES_FILE.exists(), f"TypeScript definitions not found at {TS_TYPES_FILE}"
    return TS_TYPES_FILE.read_text(encoding="utf-8")


# ============================================================================
# PART 1: 100% JSON KEY PARITY VALIDATION ACROSS 6 ENDPOINTS
# ============================================================================

class TestEndpointKeyParity:
    """
    Adversarially validates that every key returned by the FastAPI backend
    is 100% covered and typed in frontend/src/types/dashboard.ts.
    """

    def test_pulse_endpoint_keys(self, ts_content: str):
        """Validates GET /api/dashboard/pulse against PulseResponse and sub-interfaces."""
        resp = client.get("/api/dashboard/pulse")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()

        # Top-level PulseResponse
        pulse_ts_fields = extract_ts_interface_fields(ts_content, "PulseResponse")
        for k in data.keys():
            assert k in pulse_ts_fields, f"Backend returned key '{k}' not found in TypeScript PulseResponse interface!"

        # kpis: PulseKpis
        assert "kpis" in data
        kpi_ts_fields = extract_ts_interface_fields(ts_content, "PulseKpis")
        for k in data["kpis"].keys():
            assert k in kpi_ts_fields, f"Backend returned KPI '{k}' not in TypeScript PulseKpis!"

        # technicians_on_jobs: TechnicianLiveOnJob[]
        assert "technicians_on_jobs" in data
        assert len(data["technicians_on_jobs"]) > 0
        tech_ts_fields = extract_ts_interface_fields(ts_content, "TechnicianLiveOnJob")
        for item in data["technicians_on_jobs"]:
            for k in item.keys():
                assert k in tech_ts_fields, f"Backend returned TechnicianLiveOnJob key '{k}' not in TypeScript interface!"
            if item.get("current_location"):
                geo_ts_fields = extract_ts_interface_fields(ts_content, "GeoPoint")
                for gk in item["current_location"].keys():
                    assert gk in geo_ts_fields, f"Backend returned GeoPoint key '{gk}' not in TypeScript GeoPoint!"

        # today_jobs: JobItem[]
        assert "today_jobs" in data
        assert len(data["today_jobs"]) > 0
        job_item_ts_fields = extract_ts_interface_fields(ts_content, "JobItem")
        for item in data["today_jobs"]:
            for k in item.keys():
                assert k in job_item_ts_fields, f"Backend returned JobItem key '{k}' not in TypeScript JobItem!"

        # machines_under_service: MachineryUnderService[]
        assert "machines_under_service" in data
        assert len(data["machines_under_service"]) > 0
        machinery_ts_fields = extract_ts_interface_fields(ts_content, "MachineryUnderService")
        for item in data["machines_under_service"]:
            for k in item.keys():
                assert k in machinery_ts_fields, f"Backend returned MachineryUnderService key '{k}' not in TypeScript interface!"

        # technicians_on_leave: TechnicianOnLeave[]
        if data.get("technicians_on_leave"):
            leave_ts_fields = extract_ts_interface_fields(ts_content, "TechnicianOnLeave")
            for item in data["technicians_on_leave"]:
                for k in item.keys():
                    assert k in leave_ts_fields, f"Backend returned TechnicianOnLeave key '{k}' not in TypeScript interface!"

    def test_sync_endpoint_keys(self, ts_content: str):
        """Validates POST /api/dashboard/sync against SyncResponse."""
        resp = client.post("/api/dashboard/sync", json={"force_refresh": True})
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()

        sync_ts_fields = extract_ts_interface_fields(ts_content, "SyncResponse")
        for k in data.keys():
            assert k in sync_ts_fields, f"Backend returned SyncResponse key '{k}' not in TypeScript interface!"

        # Check required fields
        required_fields = ["status", "last_synced_at", "records_synced", "source"]
        for rf in required_fields:
            assert rf in data, f"Required SyncResponse key '{rf}' missing from backend response!"

    def test_productivity_endpoint_keys_daily_weekly_monthly(self, ts_content: str):
        """Validates GET /api/analytics/productivity across daily, weekly, and monthly timeframes."""
        prod_ts_fields = extract_ts_interface_fields(ts_content, "ProductivityResponse")
        summary_ts_fields = extract_ts_interface_fields(ts_content, "ProductivitySummary")
        tech_rec_ts_fields = extract_ts_interface_fields(ts_content, "TechnicianProductivityRecord")
        trend_ts_fields = extract_ts_interface_fields(ts_content, "TrendDataPoint")
        cust_ts_fields = extract_ts_interface_fields(ts_content, "CustomerDistribution")

        for tf in ["daily", "weekly", "monthly"]:
            resp = client.get(f"/api/analytics/productivity?timeframe={tf}")
            assert resp.status_code == 200, f"Failed for timeframe {tf}: {resp.text}"
            data = resp.json()

            # Top-level keys
            for k in data.keys():
                assert k in prod_ts_fields, f"ProductivityResponse returned unexpected key '{k}' for {tf}"

            # Summary keys
            assert "summary" in data
            for k in data["summary"].keys():
                assert k in summary_ts_fields, f"ProductivitySummary returned unexpected key '{k}' for {tf}"

            # Technician records keys
            assert "technician_records" in data
            assert len(data["technician_records"]) > 0
            for rec in data["technician_records"]:
                for k in rec.keys():
                    assert k in tech_rec_ts_fields, f"TechnicianProductivityRecord unexpected key '{k}'"

            # Trend data keys
            assert "trend_data" in data
            assert len(data["trend_data"]) > 0
            for pt in data["trend_data"]:
                for k in pt.keys():
                    assert k in trend_ts_fields, f"TrendDataPoint unexpected key '{k}'"

            # Customer distribution keys
            if data.get("customer_distribution"):
                for cd in data["customer_distribution"]:
                    for k in cd.keys():
                        assert k in cust_ts_fields, f"CustomerDistribution unexpected key '{k}'"

    def test_telematics_routes_endpoint_keys(self, ts_content: str):
        """Validates GET /api/telematics/routes against RouteResponse and sub-interfaces."""
        route_ts_fields = extract_ts_interface_fields(ts_content, "RouteResponse")
        journey_ts_fields = extract_ts_interface_fields(ts_content, "JourneySummary")
        cluster_ts_fields = extract_ts_interface_fields(ts_content, "Cluster5km")
        anomaly_ts_fields = extract_ts_interface_fields(ts_content, "RouteAnomaly")
        geo_ts_fields = extract_ts_interface_fields(ts_content, "GeoPoint")

        # Test with multiple technicians
        for tech_id in ["TECH-01", "TECH-02", "TECH-03"]:
            resp = client.get(f"/api/telematics/routes?technician_id={tech_id}&date=2026-09-22")
            assert resp.status_code == 200, f"Failed route for {tech_id}: {resp.text}"
            data = resp.json()

            # Top-level RouteResponse keys
            for k in data.keys():
                assert k in route_ts_fields, f"RouteResponse returned unexpected key '{k}' for {tech_id}"

            # JourneySummary keys
            assert "journey_summary" in data
            for k in data["journey_summary"].keys():
                assert k in journey_ts_fields, f"JourneySummary returned unexpected key '{k}'"

            start_loc = data["journey_summary"]["start_location"]
            for k in start_loc.keys():
                assert k in geo_ts_fields or k in ["name", "departed_at", "arrived_at"], f"Start location key '{k}' invalid"

            dest_loc = data["journey_summary"]["destination"]
            for k in dest_loc.keys():
                assert k in geo_ts_fields or k in ["name", "departed_at", "arrived_at"], f"Dest location key '{k}' invalid"

            # 5km Clusters
            assert "clusters_5km" in data
            assert len(data["clusters_5km"]) > 0
            for cl in data["clusters_5km"]:
                for k in cl.keys():
                    assert k in cluster_ts_fields, f"Cluster5km returned unexpected key '{k}'"
                # Centroid
                assert "centroid" in cl
                for ck in cl["centroid"].keys():
                    assert ck in geo_ts_fields, f"Cluster centroid key '{ck}' not in GeoPoint"

            # Anomalies
            assert "anomalies" in data
            for an in data["anomalies"]:
                for k in an.keys():
                    assert k in anomaly_ts_fields, f"RouteAnomaly returned unexpected key '{k}'"
                assert "location" in an
                for lk in an["location"].keys():
                    assert lk in geo_ts_fields, f"Anomaly location key '{lk}' not in GeoPoint"

            # Route polyline
            assert "route_polyline" in data
            assert isinstance(data["route_polyline"], list)
            if data["route_polyline"]:
                assert len(data["route_polyline"][0]) == 2
                assert isinstance(data["route_polyline"][0][0], (float, int))
                assert isinstance(data["route_polyline"][0][1], (float, int))

    def test_technicians_endpoint_keys(self, ts_content: str):
        """Validates GET /api/technicians against TechnicianDetail[]."""
        tech_detail_fields = extract_ts_interface_fields(ts_content, "TechnicianDetail")
        geo_fields = extract_ts_interface_fields(ts_content, "GeoPoint")

        resp = client.get("/api/technicians")
        assert resp.status_code == 200, f"Expected 200: {resp.text}"
        techs = resp.json()
        assert isinstance(techs, list)
        assert len(techs) > 0

        for t in techs:
            for k in t.keys():
                assert k in tech_detail_fields, f"TechnicianDetail returned unexpected key '{k}'"
            if t.get("current_location"):
                for gk in t["current_location"].keys():
                    assert gk in geo_fields, f"Technician current_location key '{gk}' not in GeoPoint"
            if t.get("last_coordinates"):
                for gk in t["last_coordinates"].keys():
                    assert gk in geo_fields, f"Technician last_coordinates key '{gk}' not in GeoPoint"

    def test_jobs_endpoint_keys(self, ts_content: str):
        """Validates GET /api/jobs against JobDetail[]."""
        job_detail_fields = extract_ts_interface_fields(ts_content, "JobDetail")

        resp = client.get("/api/jobs")
        assert resp.status_code == 200, f"Expected 200: {resp.text}"
        jobs = resp.json()
        assert isinstance(jobs, list)
        assert len(jobs) > 0

        for j in jobs:
            for k in j.keys():
                assert k in job_detail_fields, f"JobDetail returned unexpected key '{k}'"

    def test_mandatory_fields_presence(self):
        """
        Adversarially validates that mandatory fields in TypeScript interfaces
        are never omitted or null in backend responses.
        """
        # Pulse mandatory fields
        pulse = client.get("/api/dashboard/pulse").json()
        assert isinstance(pulse["timestamp"], str) and pulse["timestamp"]
        assert isinstance(pulse["kpis"]["technicians_on_paid_jobs"], int)
        assert isinstance(pulse["kpis"]["technicians_active_total"], int)
        assert isinstance(pulse["kpis"]["technicians_on_leave"], int)
        assert isinstance(pulse["kpis"]["total_jobs_today"], int)
        assert isinstance(pulse["kpis"]["jobs_completed_today"], int)
        assert isinstance(pulse["kpis"]["fleet_utilization_pct"], (int, float))

        for tech in pulse["technicians_on_jobs"]:
            assert isinstance(tech["technician_id"], str) and tech["technician_id"]
            assert isinstance(tech["name"], str) and tech["name"]
            assert isinstance(tech["status"], str)
            assert isinstance(tech["is_paid_job"], bool)

        for job in pulse["today_jobs"]:
            assert isinstance(job["job_id"], str) and job["job_id"].startswith("SR-26-")
            assert isinstance(job["status"], str)
            assert isinstance(job["customer_name"], str)
            assert isinstance(job["assigned_technicians"], list)
            assert isinstance(job["job_type"], str)

        for m in pulse["machines_under_service"]:
            assert isinstance(m["asset_name"], str)
            assert isinstance(m["serial_number"], str)
            assert isinstance(m["client_company_name"], str)
            assert isinstance(m["site_contact_person"], str)
            assert isinstance(m["location"], str)
            assert isinstance(m["active_job_id"], str)
            assert isinstance(m["service_type"], str)

        # Sync mandatory fields
        sync_res = client.post("/api/dashboard/sync", json={"force_refresh": True}).json()
        assert sync_res["status"] == "success"
        assert isinstance(sync_res["last_synced_at"], str)
        assert isinstance(sync_res["records_synced"], int)
        assert isinstance(sync_res["source"], str)

        # Productivity mandatory fields
        prod = client.get("/api/analytics/productivity?timeframe=daily").json()
        assert prod["timeframe"] in ("daily", "weekly", "monthly")
        summary = prod["summary"]
        assert isinstance(summary["total_working_hours"], (int, float))
        assert isinstance(summary["total_travelling_hours"], (int, float))
        assert isinstance(summary["total_idle_hours"], (int, float))
        assert isinstance(summary["total_shift_hours"], (int, float))
        assert isinstance(summary["average_utilization_pct"], (int, float))

        for rec in prod["technician_records"]:
            assert isinstance(rec["technician_id"], str)
            assert isinstance(rec["technician_name"], str)
            assert isinstance(rec["working_hours"], (int, float))
            assert isinstance(rec["travelling_hours"], (int, float))
            assert isinstance(rec["idle_hours"], (int, float))
            assert isinstance(rec["shift_hours"], (int, float))
            assert isinstance(rec["utilization_pct"], (int, float))
            assert isinstance(rec["jobs_count"], int)

        for trend in prod["trend_data"]:
            assert isinstance(trend["period"], str)
            assert isinstance(trend["working"], (int, float))
            assert isinstance(trend["travelling"], (int, float))
            assert isinstance(trend["idle"], (int, float))

        # Telematics mandatory fields
        route = client.get("/api/telematics/routes?technician_id=TECH-01").json()
        assert isinstance(route["technician_id"], str)
        assert isinstance(route["technician_name"], str)
        assert isinstance(route["date"], str)
        js = route["journey_summary"]
        assert isinstance(js["transit_duration_minutes"], (int, float))
        assert isinstance(js["unauthorized_stop_duration_minutes"], (int, float))
        assert isinstance(js["total_distance_km"], (int, float))
        assert isinstance(js["anomalies_detected"], int)
        assert isinstance(route["raw_pings_count"], int)
        assert isinstance(route["clusters_5km"], list)
        assert isinstance(route["anomalies"], list)
        assert isinstance(route["route_polyline"], list)

        for cl in route["clusters_5km"]:
            assert isinstance(cl["cluster_id"], str)
            assert isinstance(cl["centroid"]["lat"], (int, float))
            assert isinstance(cl["centroid"]["lng"], (int, float))
            assert isinstance(cl["radius_meters"], (int, float))
            assert isinstance(cl["location_name"], str)
            assert isinstance(cl["pings_count"], int)
            assert isinstance(cl["duration_minutes"], (int, float))
            assert isinstance(cl["is_job_site"], bool)
            assert isinstance(cl["is_base"], bool)

        for an in route["anomalies"]:
            assert isinstance(an["type"], str)
            assert isinstance(an["location"]["lat"], (int, float))
            assert isinstance(an["location"]["lng"], (int, float))
            assert isinstance(an["duration_minutes"], (int, float))
            assert isinstance(an["description"], str)

        # Technicians mandatory fields
        techs = client.get("/api/technicians").json()
        for t in techs:
            assert isinstance(t["technician_id"], str)
            assert isinstance(t["name"], str)
            assert isinstance(t["role"], str)
            assert isinstance(t["region"], str)
            assert isinstance(t["phone"], str)
            assert isinstance(t["status"], str)
            assert isinstance(t["deputation_rate_per_day"], (int, float))
            assert isinstance(t["da_rate_per_day"], (int, float))

        # Jobs mandatory fields
        jobs = client.get("/api/jobs").json()
        for j in jobs:
            assert isinstance(j["job_id"], str)
            assert isinstance(j["title"], str)
            assert isinstance(j["status"], str)
            assert isinstance(j["assigned_technicians"], list)

    def test_parameter_permutations_schema_integrity(self, ts_content: str):
        """
        Adversarially validates that query permutations preserve 100% schema integrity.
        """
        prod_ts = extract_ts_interface_fields(ts_content, "ProductivityResponse")
        job_ts = extract_ts_interface_fields(ts_content, "JobDetail")
        tech_ts = extract_ts_interface_fields(ts_content, "TechnicianDetail")

        # Productivity with filters
        res = client.get("/api/analytics/productivity?timeframe=weekly&technician_id=TECH-01&customer_company=Reliance").json()
        for k in res.keys():
            assert k in prod_ts

        # Jobs with filters
        res_jobs = client.get("/api/jobs?status=Completed&job_type=Paid").json()
        assert isinstance(res_jobs, list)
        for j in res_jobs:
            for k in j.keys():
                assert k in job_ts

        # Technicians with search
        res_techs = client.get("/api/technicians?search=Gurpreet&region=Punjab").json()
        assert isinstance(res_techs, list)
        assert len(res_techs) >= 1
        for t in res_techs:
            for k in t.keys():
                assert k in tech_ts



# ============================================================================
# PART 2: LIVE VITE DEV SERVER REVERSE PROXY VERIFICATION
# ============================================================================

def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


class TestViteDevServerProxy:
    """
    Spawns live FastAPI backend on port 8000 and Vite dev server on port 5173,
    and executes real HTTP requests to http://localhost:5173/api/* to confirm
    transparent end-to-end proxying.
    """

    @pytest.fixture(scope="class")
    def live_servers(self):
        """Spawns FastAPI (8000) and Vite (5173), waiting for readiness, then terminates."""
        backend_proc = None
        vite_proc = None

        backend_started_by_us = False
        vite_started_by_us = False

        try:
            # 1. Start Backend if not already running on port 8000
            if not is_port_in_use(8000):
                print("\n[ViteProxyTest] Launching FastAPI backend on http://127.0.0.1:8000...")
                backend_proc = subprocess.Popen(
                    [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
                    cwd=str(backend_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                backend_started_by_us = True

            # Wait for backend readiness (up to 12s)
            backend_ready = False
            for _ in range(24):
                if is_port_in_use(8000):
                    try:
                        r = requests.get("http://127.0.0.1:8000/health", timeout=1)
                        if r.status_code == 200:
                            backend_ready = True
                            break
                    except Exception:
                        pass
                time.sleep(0.5)
            assert backend_ready, "FastAPI backend failed to start on port 8000 within 12s"

            # 2. Start Vite Dev Server if not already running on port 5173
            frontend_dir = ROOT_DIR / "frontend"
            if not is_port_in_use(5173):
                print("[ViteProxyTest] Launching Vite dev server on http://localhost:5173...")
                npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
                vite_proc = subprocess.Popen(
                    [npm_cmd, "run", "dev", "--", "--port", "5173", "--host", "127.0.0.1"],
                    cwd=str(frontend_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                vite_started_by_us = True

            # Wait for Vite readiness (up to 15s)
            vite_ready = False
            for _ in range(30):
                if is_port_in_use(5173):
                    try:
                        r = requests.get("http://127.0.0.1:5173", timeout=2)
                        if r.status_code in (200, 304):
                            vite_ready = True
                            break
                    except Exception:
                        pass
                time.sleep(0.5)
            assert vite_ready, "Vite dev server failed to start on port 5173 within 15s"

            # Warm-up proxy with health check or pulse
            for _ in range(5):
                try:
                    warmup = requests.get("http://127.0.0.1:5173/api/health", timeout=5)
                    if warmup.status_code == 200:
                        break
                except Exception:
                    time.sleep(0.5)

            print("[ViteProxyTest] Both Backend (:8000) and Vite Dev Server (:5173) are ready.")
            yield "http://127.0.0.1:5173"

        finally:
            # Clean teardown
            print("\n[ViteProxyTest] Cleaning up spawned processes...")
            if vite_started_by_us and vite_proc:
                try:
                    subprocess.run(f"taskkill /F /T /PID {vite_proc.pid}", shell=True, capture_output=True)
                except Exception:
                    vite_proc.terminate()
            if backend_started_by_us and backend_proc:
                try:
                    subprocess.run(f"taskkill /F /T /PID {backend_proc.pid}", shell=True, capture_output=True)
                except Exception:
                    backend_proc.terminate()

    def test_vite_proxy_pulse_endpoint(self, live_servers):
        """Verifies http://localhost:5173/api/dashboard/pulse routes cleanly through Vite proxy to backend."""
        vite_url = live_servers
        resp = requests.get(f"{vite_url}/api/dashboard/pulse", timeout=10)
        assert resp.status_code == 200, f"Vite proxy returned status {resp.status_code}"
        data = resp.json()
        assert "kpis" in data
        assert "technicians_on_jobs" in data
        assert "today_jobs" in data
        assert "machines_under_service" in data
        assert data["kpis"]["technicians_active_total"] >= 12

    def test_vite_proxy_sync_endpoint(self, live_servers):
        """Verifies POST http://localhost:5173/api/dashboard/sync routes cleanly through Vite proxy to backend."""
        vite_url = live_servers
        resp = requests.post(f"{vite_url}/api/dashboard/sync", json={"force_refresh": True}, timeout=10)
        assert resp.status_code == 200, f"Vite proxy returned status {resp.status_code}"
        data = resp.json()
        assert data["status"] == "success"
        assert data["records_synced"] > 0
        assert "last_synced_at" in data

    def test_vite_proxy_productivity_endpoint(self, live_servers):
        """Verifies http://localhost:5173/api/analytics/productivity routes cleanly through Vite proxy."""
        vite_url = live_servers
        resp = requests.get(f"{vite_url}/api/analytics/productivity?timeframe=daily", timeout=10)
        assert resp.status_code == 200, f"Vite proxy returned status {resp.status_code}"
        data = resp.json()
        assert data["timeframe"] == "daily"
        assert "summary" in data
        assert "technician_records" in data
        assert data["summary"]["total_shift_hours"] > 0

    def test_vite_proxy_telematics_routes_endpoint(self, live_servers):
        """Verifies http://localhost:5173/api/telematics/routes routes cleanly through Vite proxy."""
        vite_url = live_servers
        resp = requests.get(f"{vite_url}/api/telematics/routes?technician_id=TECH-01&date=2026-09-22", timeout=10)
        assert resp.status_code == 200, f"Vite proxy returned status {resp.status_code}"
        data = resp.json()
        assert data["technician_id"] == "TECH-01"
        assert "journey_summary" in data
        assert "clusters_5km" in data
        assert len(data["clusters_5km"]) > 0
        assert "route_polyline" in data

    def test_vite_proxy_technicians_endpoint(self, live_servers):
        """Verifies http://localhost:5173/api/technicians routes cleanly through Vite proxy."""
        vite_url = live_servers
        resp = requests.get(f"{vite_url}/api/technicians", timeout=10)
        assert resp.status_code == 200, f"Vite proxy returned status {resp.status_code}"
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 10
        assert any(t["name"] == "Gurpreet Singh" for t in data)

    def test_vite_proxy_jobs_endpoint(self, live_servers):
        """Verifies http://localhost:5173/api/jobs routes cleanly through Vite proxy."""
        vite_url = live_servers
        resp = requests.get(f"{vite_url}/api/jobs", timeout=10)
        assert resp.status_code == 200, f"Vite proxy returned status {resp.status_code}"
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 10
        assert any(j["job_id"] == "SR-26-0101" for j in data)

    def test_vite_proxy_error_propagation(self, live_servers):
        """
        Verifies that HTTP errors (404, 422) generated by FastAPI backend
        propagate unmolested through the Vite dev server proxy to the client.
        """
        vite_url = live_servers

        # 404 for unknown technician
        r404 = requests.get(f"{vite_url}/api/telematics/routes?technician_id=TECH-UNKNOWN-999", timeout=10)
        assert r404.status_code == 404, f"Expected 404 through proxy, got {r404.status_code}"
        err_data = r404.json()
        assert err_data.get("status") == "error" or "detail" in err_data or "message" in err_data

        # 422 for invalid timeframe
        r422 = requests.get(f"{vite_url}/api/analytics/productivity?timeframe=annual_invalid", timeout=10)
        assert r422.status_code == 422, f"Expected 422 through proxy, got {r422.status_code}"
        val_data = r422.json()
        assert val_data.get("status") == "validation_error" or "errors" in val_data

    def test_vite_proxy_post_with_body(self, live_servers):
        """
        Verifies that POST requests with JSON body and custom parameters
        are correctly forwarded by Vite proxy to the backend without dropping payload.
        """
        vite_url = live_servers
        payload = {"force_refresh": True, "modules": ["jobs", "technicians"]}
        resp = requests.post(f"{vite_url}/api/dashboard/sync", json=payload, timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert data["status"] == "success"
        assert "records_updated" in data
        assert data["records_synced"] > 0

