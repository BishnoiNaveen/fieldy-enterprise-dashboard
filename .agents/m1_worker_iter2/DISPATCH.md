# Task Dispatch — M1 Worker Iteration 2 (Audit Remediation Implementation)

## Mission
Apply the verified audit remediation code changes to `backend/app/services/telematics_engine.py`, `backend/app/routers/telematics.py`, and `tests/`.

## Authoritative Inputs
- ORIGINAL_REQUEST.md: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\ORIGINAL_REQUEST.md
- PROJECT.md: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\PROJECT.md
- Full Forensic Auditor Evidence: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_auditor\report.md
- Proposed Telematics Engine: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_remed_explorer_1\proposed_telematics_engine.py
- Remediation Explorer 1 Report: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_remed_explorer_1\report.md
- Remediation Explorer 2 Report (Router): C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_remed_explorer_2\report.md
- Remediation Explorer 3 Report (Tests Refactoring): C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_remed_explorer_3\report.md

## File Ownership
You exclusively own and write:
- `backend/app/services/telematics_engine.py`
- `backend/app/routers/telematics.py`
- `backend/app/models/schemas.py` (if any schema alignment needed)
- `tests/conftest.py`
- `tests/test_tier1_features.py`
- `tests/test_tier2_boundaries.py`
- `tests/test_tier3_combinations.py`
- `tests/test_tier4_scenarios.py`

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A forensic auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Detailed Tasks
1. Overwrite `backend/app/services/telematics_engine.py` with the complete, mathematically verified implementation from `C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_remed_explorer_1\proposed_telematics_engine.py`.
2. Update `backend/app/routers/telematics.py` using the exact code from `C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_remed_explorer_2\report.md` (lines 53-157). Ensure it calls `telematics_engine.analyze_route_journey(...)` dynamically and generates distinct, realistic GPS routes for each technician hub.
3. Refactor `tests/conftest.py` and `tests/test_tier*.py` per `C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_remed_explorer_3\report.md`. Ensure all tests import directly from `backend.app` models and services (`app.models.schemas`, `app.models.telematics`, `app.services.telematics_engine`).
4. Run:
   `pytest backend/tests/ -v`
   `pytest tests/ -v`
5. Verify that all tests pass 100%. Verify specifically that clean routes with 0 anomalies report `anomalies_detected: 0` and `unauthorized_stop_duration_minutes: 0.0`.
6. Write your report to `C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_worker_iter2\report.md` and `handoff.md`.
7. Send completion message to parent orchestrator.
