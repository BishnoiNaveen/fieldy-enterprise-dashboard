# Task Dispatch — M1 Explorer 3 (Analytics Engine, Sync Service & Mock Generator)

## Mission
Analyze and provide the concrete implementation blueprint for the Hours Analytics Engine, Fieldy Sync Service, calibrated Krone Synthetic Mock Generator, and all 6 FastAPI REST routers.

## Authoritative Inputs
- ORIGINAL_REQUEST.md: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\ORIGINAL_REQUEST.md
- PROJECT.md: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\PROJECT.md
- Survey Spec Miner 1 Report: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\survey_spec_miner_1\report.md
- Survey Explorer 3 Report: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\survey_explorer_3\report.md

## Scope & Deliverables
1. Read `ORIGINAL_REQUEST.md` and `PROJECT.md`.
2. Provide the production-ready implementation design for:
   - `backend/app/services/analytics_engine.py`: Working, Travelling, Idle hours aggregation enforcing $H_{shift} = H_w + H_t + H_i$, Daily/Weekly/Monthly rollups, multi-dimensional search & filtering.
   - `backend/app/services/sync_service.py`: Background poller, manual "Fresh Sync" trigger, timestamp tracker, offline cache storage.
   - `backend/app/services/mock_generator.py`: Realistic Krone Agriculture India dataset across Punjab, Haryana, UP, Maharashtra, MP, Gujarat, and AP; real Krone balers and RIL bio-energy contracts.
   - `backend/app/routers/`:
     - `dashboard.py`: `/api/dashboard/pulse`, `/api/dashboard/sync`
     - `analytics.py`: `/api/analytics/productivity`
     - `telematics.py`: `/api/telematics/routes`
     - `entities.py`: `/api/technicians`, `/api/jobs`
3. Detail the unit test specifications for `backend/tests/test_analytics.py` and `backend/tests/test_api.py`.
4. Output your detailed technical strategy to `C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_explorer_3\report.md` and `handoff.md`.
5. Send your completion message to orchestrator parent.

## 2026-09-22T12:48:07Z
You are m1_explorer_3, an exploration specialist for Milestone 1 Analytics, Sync & Mock Generator.
Your working directory is C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_explorer_3.
You MUST read C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\ORIGINAL_REQUEST.md before starting work.
Also read C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\PROJECT.md and C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_explorer_3\DISPATCH.md.

Analyze and specify the exact implementation blueprint for:
1. `backend/app/services/analytics_engine.py`:
   - Hours aggregation for Working, Travelling, and Idle hours with strict conservation $H_{shift} = H_w + H_t + H_i$.
   - Daily, Weekly, and Monthly rollups.
   - Multi-dimensional search & filtering (by technician, customer company, date range, status, job type).
2. `backend/app/services/sync_service.py`:
   - Background polling task, manual "Fresh Sync" trigger with timestamp indicators, offline cache persistence.
3. `backend/app/services/mock_generator.py`:
   - Calibrated Krone Agriculture India synthetic dataset across Punjab, Haryana, UP, Maharashtra, MP, Gujarat, and AP; real Krone balers/harvesters, 14 technicians, RIL bio-energy contracts.
4. `backend/app/routers/` (dashboard, analytics, telematics, entities) and unit tests `backend/tests/test_analytics.py`, `backend/tests/test_api.py`.
Write your full report to C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_explorer_3\report.md and create handoff.md.
Send a completion message back to parent orchestrator when finished.

