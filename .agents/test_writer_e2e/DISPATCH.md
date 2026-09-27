# Task Dispatch — E2E Test Writer (Opaque-Box E2E Test Suite)

## Mission
Design and implement the comprehensive 4-Tier automated test suite in `tests/` per `TEST_INFRA.md` and `PROJECT.md § Feature Inventory`.

## Authoritative Inputs
- ORIGINAL_REQUEST.md: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\ORIGINAL_REQUEST.md
- PROJECT.md: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\PROJECT.md
- TEST_INFRA.md: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\TEST_INFRA.md

## Scope & File Ownership
- Exclusively owns: `tests/` directory at project root (`tests/test_tier1_features.py`, `tests/test_tier2_boundaries.py`, `tests/test_tier3_combinations.py`, `tests/test_tier4_scenarios.py`, `tests/conftest.py`).
- DO NOT modify files in `backend/` or `frontend/`.

## Scope & Deliverables
1. Read `ORIGINAL_REQUEST.md`, `PROJECT.md`, and `TEST_INFRA.md`.
2. Write comprehensive, executable Pytest test files:
   - `tests/test_tier1_features.py`: Feature coverage (≥5 tests per feature across all 16 features, ≥80 tests). Tests import and verify backend API models, telematics functions, sync routines, and hours aggregations.
   - `tests/test_tier2_boundaries.py`: Boundary and corner cases (≥5 tests per feature, e.g., 4.99 km vs 5.01 km boundary, zero duration, missing GPS, max shift, extreme coordinates, empty datasets).
   - `tests/test_tier3_combinations.py`: Cross-feature pairwise combinations (sync + filter, route clustering + time aggregation, anomaly alert + multi-stop journey).
   - `tests/test_tier4_scenarios.py`: 5 real-world Krone Agriculture India field service scenarios (RIL Barwala emergency knotter repair, Hoshiarpur commissioning, Western UP fleet inspection, offline replay, unauthorized dhaba halt).
3. Verify tests compile cleanly and can execute against backend models/services.
4. When complete, publish `TEST_READY.md` at project root with coverage summary.
5. Report to `C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\test_writer_e2e\report.md` and `handoff.md`.
6. Send completion message to orchestrator parent.

## 2026-09-22T12:48:07Z
You are test_writer_e2e, the E2E Test Suite Creator.
Your working directory is C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\test_writer_e2e.
You MUST read C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\ORIGINAL_REQUEST.md before starting work.
Also read C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\PROJECT.md, C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\TEST_INFRA.md, and C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\test_writer_e2e\DISPATCH.md.

File Ownership: You exclusively own and write to `C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\tests/`. DO NOT write or edit code in `backend/` or `frontend/`.

Deliverables:
Implement the complete 4-Tier test suite in `tests/`:
1. `tests/conftest.py`: Test fixtures, mock generators, API client helpers.
2. `tests/test_tier1_features.py`: Happy-path feature coverage (≥5 tests per feature, ≥80 tests) for all 16 features.
3. `tests/test_tier2_boundaries.py`: Boundary and corner cases (≥5 tests per feature, ≥80 tests, e.g., 4.99 km vs 5.01 km, zero duration, extreme coordinates, missing GPS).
4. `tests/test_tier3_combinations.py`: Cross-feature pairwise interactions (≥20 tests).
5. `tests/test_tier4_scenarios.py`: 5 real-world Krone field service scenarios.
When tests are implemented and verified, publish `TEST_READY.md` at project root `C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\TEST_READY.md`.
Write your report to C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\test_writer_e2e\report.md and handoff.md.
Send completion message to parent orchestrator.
