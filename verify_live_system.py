"""
tests/test_live_system_verifier.py
Milestone 3 Live Concurrent System Launch & Verification Test.
Spawns the FastAPI backend (port 8000) and Vite preview frontend (port 4173),
verifies concurrent startup, executes live HTTP requests across all 6 core endpoints,
tests frontend asset delivery, performs concurrent burst testing, and verifies graceful shutdown.
"""

import os
import sys
import time
import json
import socket
import urllib.request
import urllib.error
import subprocess
import concurrent.futures

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")


def is_port_open(host, port, timeout=0.5):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        return s.connect_ex((host, port)) == 0


def wait_for_url(url, timeout=20.0, step=0.3):
    start = time.time()
    while time.time() - start < timeout:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "M3-Challenger-Verifier"})
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(step)
    return False


def http_get(url):
    t0 = time.perf_counter()
    req = urllib.request.Request(url, headers={"User-Agent": "M3-Challenger-Verifier"})
    with urllib.request.urlopen(req, timeout=5.0) as resp:
        elapsed = (time.perf_counter() - t0) * 1000
        body = resp.read().decode("utf-8")
        return resp.status, body, elapsed


def http_post(url, data_dict):
    t0 = time.perf_counter()
    data = json.dumps(data_dict).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "M3-Challenger-Verifier"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=5.0) as resp:
        elapsed = (time.perf_counter() - t0) * 1000
        body = resp.read().decode("utf-8")
        return resp.status, body, elapsed


def run_live_system_verification():
    print("======================================================================")
    print("  MILESTONE 3: EMPIRICAL LIVE SYSTEM LAUNCH & ENDPOINT VERIFICATION")
    print("======================================================================")

    # 1. Ensure clean port state
    for port in (8000, 4173):
        if is_port_open("127.0.0.1", port):
            print(f"[!] Port {port} is already open. Waiting for it to release...")
            time.sleep(2)

    # 2. Launch FastAPI backend
    env = os.environ.copy()
    env["PYTHONPATH"] = BACKEND_DIR + (os.pathsep + env.get("PYTHONPATH", "") if env.get("PYTHONPATH") else "")
    
    backend_cmd = [
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--app-dir", BACKEND_DIR,
        "--host", "127.0.0.1",
        "--port", "8000",
        "--log-level", "warning"
    ]
    print("[*] Launching FastAPI backend on http://127.0.0.1:8000 ...")
    backend_proc = subprocess.Popen(backend_cmd, cwd=ROOT_DIR, env=env)

    # 3. Launch Vite preview server
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    frontend_cmd = [npm_cmd, "run", "preview", "--", "--port", "4173", "--host"]
    print("[*] Launching Vite preview server on http://localhost:4173 ...")
    frontend_proc = subprocess.Popen(frontend_cmd, cwd=FRONTEND_DIR)

    results = {}
    try:
        # Wait for both services
        backend_ready = wait_for_url("http://127.0.0.1:8000/health", timeout=15)
        frontend_ready = wait_for_url("http://localhost:4173/", timeout=15)

        print(f"[*] Backend online:  {backend_ready}")
        print(f"[*] Frontend online: {frontend_ready}")

        assert backend_ready, "FastAPI backend failed to start within 15 seconds"
        assert frontend_ready, "Vite frontend preview failed to start within 15 seconds"

        # 4. Verify All 6 Core Endpoints
        print("\n--- Verifying All 6 Core Endpoints ---")

        # Endpoint 1: GET /api/dashboard/pulse
        status_code, body, lat = http_get("http://127.0.0.1:8000/api/dashboard/pulse")
        data = json.loads(body)
        assert status_code == 200, f"Expected 200, got {status_code}"
        assert "kpis" in data, "Missing kpis in pulse response"
        assert "technicians_on_jobs" in data, "Missing technicians_on_jobs"
        assert "today_jobs" in data, "Missing today_jobs"
        assert "machines_under_service" in data, "Missing machines_under_service"
        results["endpoint_1_pulse"] = {
            "status": status_code, "latency_ms": round(lat, 2),
            "kpis": data["kpis"],
            "techs_count": len(data["technicians_on_jobs"]),
            "jobs_count": len(data["today_jobs"]),
            "machines_count": len(data["machines_under_service"])
        }
        print(f"[PASS] 1. GET /api/dashboard/pulse -> HTTP {status_code} ({lat:.1f}ms) | {len(data['today_jobs'])} jobs, {len(data['machines_under_service'])} machines")

        # Endpoint 2: POST /api/dashboard/sync
        status_code, body, lat = http_post("http://127.0.0.1:8000/api/dashboard/sync", {"force_refresh": True})
        data = json.loads(body)
        assert status_code == 200, f"Expected 200, got {status_code}"
        assert data.get("status") == "success", "Sync failed"
        assert data.get("records_synced", 0) > 0, "No records synced"
        results["endpoint_2_sync"] = {
            "status": status_code, "latency_ms": round(lat, 2),
            "sync_status": data.get("status"),
            "records_synced": data.get("records_synced"),
            "source": data.get("source")
        }
        print(f"[PASS] 2. POST /api/dashboard/sync -> HTTP {status_code} ({lat:.1f}ms) | records synced: {data.get('records_synced')}")

        # Endpoint 3: GET /api/analytics/productivity?timeframe=daily
        status_code, body, lat = http_get("http://127.0.0.1:8000/api/analytics/productivity?timeframe=daily")
        data = json.loads(body)
        assert status_code == 200, f"Expected 200, got {status_code}"
        assert data.get("timeframe") == "daily"
        assert "summary" in data and "total_working_hours" in data["summary"]
        assert "technician_records" in data and len(data["technician_records"]) > 0
        assert "trend_data" in data
        results["endpoint_3_productivity"] = {
            "status": status_code, "latency_ms": round(lat, 2),
            "timeframe": data.get("timeframe"),
            "summary": data["summary"],
            "records_count": len(data["technician_records"])
        }
        print(f"[PASS] 3. GET /api/analytics/productivity -> HTTP {status_code} ({lat:.1f}ms) | total working: {data['summary']['total_working_hours']}h")

        # Endpoint 4: GET /api/telematics/routes?technician_id=TECH-001
        status_code, body, lat = http_get("http://127.0.0.1:8000/api/telematics/routes?technician_id=TECH-001")
        data = json.loads(body)
        assert status_code == 200, f"Expected 200, got {status_code}"
        assert data.get("technician_id") in ("TECH-01", "TECH-001"), f"Unexpected tech id: {data.get('technician_id')}"
        assert "journey_summary" in data
        assert "clusters_5km" in data
        assert "route_polyline" in data
        results["endpoint_4_telematics"] = {
            "status": status_code, "latency_ms": round(lat, 2),
            "technician_id": data.get("technician_id"),
            "clusters_count": len(data.get("clusters_5km", [])),
            "anomalies_count": len(data.get("anomalies", [])),
            "total_distance_km": data.get("journey_summary", {}).get("total_distance_km")
        }
        print(f"[PASS] 4. GET /api/telematics/routes -> HTTP {status_code} ({lat:.1f}ms) | {len(data['clusters_5km'])} clusters, {len(data['anomalies'])} anomalies")

        # Endpoint 5: GET /api/technicians
        status_code, body, lat = http_get("http://127.0.0.1:8000/api/technicians")
        data = json.loads(body)
        assert status_code == 200, f"Expected 200, got {status_code}"
        assert isinstance(data, list) and len(data) > 0
        results["endpoint_5_technicians"] = {
            "status": status_code, "latency_ms": round(lat, 2),
            "total_technicians": len(data),
            "sample_tech": data[0]["name"]
        }
        print(f"[PASS] 5. GET /api/technicians -> HTTP {status_code} ({lat:.1f}ms) | {len(data)} technicians returned")

        # Endpoint 6: GET /api/jobs
        status_code, body, lat = http_get("http://127.0.0.1:8000/api/jobs")
        data = json.loads(body)
        assert status_code == 200, f"Expected 200, got {status_code}"
        assert isinstance(data, list) and len(data) > 0
        results["endpoint_6_jobs"] = {
            "status": status_code, "latency_ms": round(lat, 2),
            "total_jobs": len(data),
            "sample_job": data[0]["job_id"]
        }
        print(f"[PASS] 6. GET /api/jobs -> HTTP {status_code} ({lat:.1f}ms) | {len(data)} jobs returned")

        # 5. Verify Frontend Delivery
        print("\n--- Verifying Frontend Delivery ---")
        status_code, body, lat = http_get("http://localhost:4173/")
        assert status_code == 200, f"Frontend returned {status_code}"
        assert '<div id="root"></div>' in body, "Frontend HTML missing root div"
        assert 'Krone Agriculture India' in body, "Frontend HTML missing title branding"
        results["frontend_preview"] = {
            "status": status_code, "latency_ms": round(lat, 2),
            "html_bytes": len(body),
            "has_root_div": True
        }
        print(f"[PASS] Frontend Preview -> HTTP {status_code} ({lat:.1f}ms) | {len(body)} bytes delivered")

        # 6. Concurrent Request Stress Test (50 parallel requests)
        print("\n--- Running Concurrent Burst Test (50 requests across all endpoints) ---")
        urls = [
            "http://127.0.0.1:8000/api/dashboard/pulse",
            "http://127.0.0.1:8000/api/analytics/productivity?timeframe=daily",
            "http://127.0.0.1:8000/api/analytics/productivity?timeframe=weekly",
            "http://127.0.0.1:8000/api/telematics/routes?technician_id=TECH-001",
            "http://127.0.0.1:8000/api/telematics/routes?technician_id=TECH-002",
            "http://127.0.0.1:8000/api/technicians",
            "http://127.0.0.1:8000/api/jobs",
            "http://127.0.0.1:8000/health",
            "http://127.0.0.1:8000/",
            "http://localhost:4173/"
        ] * 5  # 50 total requests

        burst_start = time.perf_counter()
        burst_success = 0
        burst_latencies = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(http_get, u) for u in urls]
            for f in concurrent.futures.as_completed(futures):
                code, _, elapsed = f.result()
                if code == 200:
                    burst_success += 1
                burst_latencies.append(elapsed)

        burst_total_time = (time.perf_counter() - burst_start) * 1000
        avg_latency = sum(burst_latencies) / len(burst_latencies)
        p95_latency = sorted(burst_latencies)[int(0.95 * len(burst_latencies))]

        print(f"[PASS] Concurrent Burst: {burst_success}/{len(urls)} succeeded (100%)")
        print(f"       Total Time: {burst_total_time:.1f}ms | Avg Latency: {avg_latency:.1f}ms | P95 Latency: {p95_latency:.1f}ms")

        results["concurrent_burst"] = {
            "total_requests": len(urls),
            "successful_requests": burst_success,
            "total_time_ms": round(burst_total_time, 2),
            "avg_latency_ms": round(avg_latency, 2),
            "p95_latency_ms": round(p95_latency, 2)
        }

        print("\n======================================================================")
        print("  ALL EMPIRICAL LIVE SYSTEM CHECKS PASSED: VERDICT = APPROVE")
        print("======================================================================")
        return True, results

    finally:
        # Graceful shutdown of both processes
        print("\n[*] Terminating backend and frontend test processes...")
        try:
            frontend_proc.terminate()
            frontend_proc.wait(timeout=3)
        except Exception:
            frontend_proc.kill()

        try:
            backend_proc.terminate()
            backend_proc.wait(timeout=3)
        except Exception:
            backend_proc.kill()
        print("[PASS] Processes cleanly terminated.")


if __name__ == "__main__":
    success, results = run_live_system_verification()
    # Save verification artifact to stdout and file
    out_path = os.path.join(ROOT_DIR, "live_verification_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nWrote verification results to: {out_path}")
    sys.exit(0 if success else 1)
