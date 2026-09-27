# Task Dispatch — M1 Remediation Explorer 3 (E2E Test Suite Direct Integration)

## Mission
Investigate and design the exact refactoring plan for `tests/` to eliminate self-certifying tests and ensure all tests genuinely import and verify `backend/app`.

## Authoritative Inputs
- ORIGINAL_REQUEST.md: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\ORIGINAL_REQUEST.md
- PROJECT.md: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\PROJECT.md
- FULL AUDITOR EVIDENCE REPORT: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_auditor\report.md
- AUDITOR HANDOFF: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_auditor\handoff.md

## Integrity Violation to Remediate
- In `tests/conftest.py` and `tests/test_tier1_features.py` through `test_tier4_scenarios.py`, the test suite currently imports duplicate, self-contained mathematical algorithms from `tests/conftest.py` instead of importing from `backend/app`.
- Design the refactoring to:
  1. Add `sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))` in `tests/conftest.py`.
  2. Import all domain models (`JobResponse`, `TechnicianResponse`, `MachineryAsset`, `PulseResponse`, etc.) directly from `app.models.schemas` and `app.models.telematics`.
  3. Import all geospatial algorithms (`haversine_distance_km`, `weighted_cartesian_centroid`, `filter_stationary_jitter`, `cluster_pings_5km`, `analyze_route_journey`) directly from `app.services.telematics_engine`.
  4. Import analytics calculation and mock generation directly from `app.services.analytics_engine` and `app.services.mock_generator`.
  5. Use `fastapi.testclient.TestClient` against `app.main.app` for tier 1-4 endpoint tests.

Output detailed refactoring diffs to `C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_remed_explorer_3\report.md` and `handoff.md`.
Send completion message to parent orchestrator.

## 2026-09-23T04:25:13Z
You are m1_remed_explorer_3, remediation explorer for E2E test suite integration.
Your working directory is C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_remed_explorer_3.
You MUST read C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\ORIGINAL_REQUEST.md before starting work.
You MUST read the FULL AUDITOR EVIDENCE REPORT at C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_auditor\report.md and C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_auditor\handoff.md.
Also read C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_remed_explorer_3\DISPATCH.md.

Design the exact refactoring plan for `tests/`:
1. Refactor `tests/conftest.py` and `tests/test_tier1_features.py` through `tier4_scenarios.py` to import directly from `backend/app` models and services.
2. Eliminate all duplicated math algorithms in `tests/conftest.py`.
3. Ensure the test suite genuinely tests and certifies the live FastAPI backend engine.
Write your full report to C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_remed_explorer_3\report.md and handoff.md.
Send completion message to parent orchestrator.
