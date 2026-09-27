# Task Dispatch — M1 Worker (Enterprise Backend Engine)

## Mission
Implement the complete, production-grade FastAPI backend for Krone Agriculture India Field Service & Telematics Dashboard per Milestone 1 specifications.

## Authoritative Inputs
- ORIGINAL_REQUEST.md: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\ORIGINAL_REQUEST.md
- PROJECT.md: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\PROJECT.md
- M1 Explorer 1 Report (Architecture & Schemas): C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_explorer_1\report.md
- M1 Explorer 2 Report (Telematics & 5 km Clustering): C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_explorer_2\report.md
- M1 Explorer 3 Report (Analytics, Sync & Mock Generator): C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_explorer_3\report.md

## File Ownership
You exclusively own and write all files under `backend/`:
- `backend/app/main.py`
- `backend/app/config.py`
- `backend/app/models/schemas.py`, `backend/app/models/telematics.py`
- `backend/app/services/telematics_engine.py` (clamped Haversine, 5km clustering, duration centroids, jitter filter, route inspector)
- `backend/app/services/analytics_engine.py` (hours math, rollups, filters)
- `backend/app/services/sync_service.py` (background poller, fresh sync trigger)
- `backend/app/services/mock_generator.py` (calibrated Krone synthetic dataset)
- `backend/app/routers/dashboard.py`, `analytics.py`, `telematics.py`, `entities.py`
- `backend/tests/test_clustering.py`, `backend/tests/test_analytics.py`, `backend/tests/test_api.py`
- `backend/requirements.txt`, `backend/run.py`

DO NOT modify files outside `backend/`!

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. An auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Verification Requirements
Run the test suite via `pytest backend/tests/ -v`.
Document all test outcomes in your handoff report.
Output handoff to `C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_worker\handoff.md`.
Send completion message to parent orchestrator.

## 2026-09-22T12:54:47Z
You are m1_worker, the implementation worker for Milestone 1: Enterprise Backend Engine.
Your working directory is C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_worker.
Implementation Tasks:
1. Implement `backend/requirements.txt` and `backend/run.py`.
2. Implement `backend/app/config.py` and `backend/app/main.py` with CORS, routers, and health check.
3. Implement `backend/app/models/schemas.py` and `backend/app/models/telematics.py`.
4. Implement `backend/app/services/telematics_engine.py`:
   - Clamped Haversine formula ($R=6371.0\text{ km}$, $a^* \in [0, 1]$).
   - Duration-weighted 3D Cartesian spherical centroid projection.
   - Speed-gated jitter suppression ($v < 1.5\text{ km/h}$, 30m deadband).
   - Incremental leader clustering capped at $5.0\text{ km}$ radius.
   - Route inspector: Start location, destination job site, designated transit vs unauthorized stops (>15 min outside 5 km zone), corridor cross-track distance.
5. Implement `backend/app/services/analytics_engine.py` ($H_{shift} = H_w + H_t + H_i$, rollups, filters).
6. Implement `backend/app/services/sync_service.py` (polling, manual fresh sync trigger, offline cache).
7. Implement `backend/app/services/mock_generator.py` (calibrated Krone Agriculture India dataset across Punjab, Haryana, UP, Maharashtra, MP, Gujarat, AP).
8. Implement `backend/app/routers/` (`dashboard.py`, `analytics.py`, `telematics.py`, `entities.py`).
9. Implement comprehensive unit and integration tests:
   - `backend/tests/test_clustering.py` (all 18 test cases from Explorer 2).
   - `backend/tests/test_analytics.py` (conservation, rollups, filters).
   - `backend/tests/test_api.py` (all 6 REST endpoints).
10. Execute the test suite using `pytest backend/tests/ -v` and verify 100% passing tests.

