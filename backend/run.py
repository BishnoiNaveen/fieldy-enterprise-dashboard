"""
backend/run.py
Development and production entrypoint for Krone Agriculture India Dashboard API server.
"""
import uvicorn
import os
import sys

# Ensure backend directory is in sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)


def main():
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "127.0.0.1")
    reload = os.environ.get("RELOAD", "false").lower() in ("true", "1", "yes")

    print(f"Starting Krone Field Service & Telematics Backend on http://{host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    main()
