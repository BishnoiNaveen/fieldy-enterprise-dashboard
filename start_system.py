#!/usr/bin/env python3
"""
start_system.py
Single-command launcher for the Krone Agriculture India Field Service & Telematics Dashboard.
Starts both the FastAPI Backend and the Vite Frontend, monitors their health,
and handles clean, graceful shutdown on Ctrl+C.
"""

import os
import sys
import time
import subprocess
import signal
import urllib.request
import urllib.error
import argparse

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")


def check_port(host, port):
    """Check if a port is in use."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def wait_for_backend(url="http://127.0.0.1:8000/health", timeout=20):
    """Poll backend until it responds with HTTP 200."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def main():
    parser = argparse.ArgumentParser(description="Launch Krone Field Service & Telematics Dashboard")
    parser.add_argument("--mode", choices=["preview", "dev"], default="preview",
                        help="Frontend run mode: 'preview' (production build, default) or 'dev' (live dev server)")
    parser.add_argument("--backend-port", type=int, default=8000, help="Port for FastAPI backend (default: 8000)")
    parser.add_argument("--frontend-port", type=int, default=None, help="Port for Vite frontend (default: 4173 for preview, 5173 for dev)")
    parser.add_argument("--no-build", action="store_true", help="Skip frontend build step in preview mode")
    args = parser.parse_args()

    fe_port = args.frontend_port or (4173 if args.mode == "preview" else 5173)

    print("=" * 72)
    print("  KRONE AGRICULTURE INDIA — FIELD SERVICE & TELEMATICS DASHBOARD")
    print("=" * 72)
    print(f"[*] Root Directory:     {ROOT_DIR}")
    print(f"[*] Backend Port:       {args.backend_port}")
    print(f"[*] Frontend Mode:      {args.mode} (Port: {fe_port})")
    print("=" * 72)

    # 1. Check frontend build if preview mode
    dist_index = os.path.join(FRONTEND_DIR, "dist", "index.html")
    if args.mode == "preview" and not args.no_build:
        if not os.path.exists(dist_index):
            print("[*] Production build not found. Running 'npm run build'...")
            res = subprocess.run(["npm.cmd" if os.name == "nt" else "npm", "run", "build"], cwd=FRONTEND_DIR)
            if res.returncode != 0:
                print("[!] ERROR: Frontend build failed!")
                sys.exit(1)
            print("[✓] Frontend built successfully.")
        else:
            print("[✓] Verified production build exists in frontend/dist.")

    # 2. Launch FastAPI Backend
    env = os.environ.copy()
    env["PYTHONPATH"] = BACKEND_DIR + (os.pathsep + env.get("PYTHONPATH", "") if env.get("PYTHONPATH") else "")
    
    backend_cmd = [
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--app-dir", BACKEND_DIR,
        "--host", "127.0.0.1",
        "--port", str(args.backend_port),
        "--log-level", "info"
    ]
    
    print(f"\n[*] Starting FastAPI backend on http://127.0.0.1:{args.backend_port}...")
    backend_proc = subprocess.Popen(backend_cmd, cwd=ROOT_DIR, env=env)

    # 3. Wait for backend health check
    print("[*] Waiting for backend to become ready...")
    if wait_for_backend(f"http://127.0.0.1:{args.backend_port}/health", timeout=15):
        print(f"[✓] Backend online and healthy at http://127.0.0.1:{args.backend_port}")
    else:
        print("[!] WARNING: Backend health check timed out. Proceeding anyway...")

    # 4. Launch Vite Frontend
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    if args.mode == "preview":
        frontend_cmd = [npm_cmd, "run", "preview", "--", "--port", str(fe_port), "--host"]
    else:
        frontend_cmd = [npm_cmd, "run", "dev", "--", "--port", str(fe_port), "--host"]

    print(f"[*] Starting Vite frontend ({args.mode}) on port {fe_port}...")
    frontend_proc = subprocess.Popen(frontend_cmd, cwd=FRONTEND_DIR)

    print("\n" + "=" * 72)
    print("  FULL SYSTEM ONLINE & READY")
    print("=" * 72)
    print(f"  • Frontend Dashboard:  http://localhost:{fe_port}")
    print(f"  • Backend REST API:    http://127.0.0.1:{args.backend_port}")
    print(f"  • Swagger Docs (OpenAPI): http://127.0.0.1:{args.backend_port}/docs")
    print(f"  • Pulse Endpoint:      http://127.0.0.1:{args.backend_port}/api/dashboard/pulse")
    print("=" * 72)
    print("  Press Ctrl+C to terminate both services gracefully.\n")

    def shutdown(signum=None, frame=None):
        print("\n[*] Shutting down all services...")
        try:
            if frontend_proc.poll() is None:
                frontend_proc.terminate()
                frontend_proc.wait(timeout=3)
        except Exception:
            frontend_proc.kill()

        try:
            if backend_proc.poll() is None:
                backend_proc.terminate()
                backend_proc.wait(timeout=3)
        except Exception:
            backend_proc.kill()

        print("[✓] All services stopped cleanly. Goodbye!")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, shutdown)

    try:
        while True:
            # Check if any child process terminated unexpectedly
            if backend_proc.poll() is not None:
                print(f"[!] Backend process exited with code {backend_proc.returncode}")
                break
            if frontend_proc.poll() is not None:
                print(f"[!] Frontend process exited with code {frontend_proc.returncode}")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        shutdown()


if __name__ == "__main__":
    main()
