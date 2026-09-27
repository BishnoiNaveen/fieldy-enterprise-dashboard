# DISPATCH — m3_worker_remed (Milestone 3 Hardening Remediation Worker)

**Mission**: Implement the four (4) surgical code remediations identified and documented by `m3_challenger_1` in `backend/app/services/telematics_engine.py` and `backend/app/services/analytics_engine.py`.

**Context & Inputs**:
- Read `C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\ORIGINAL_REQUEST.md`
- Read `C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\PROJECT.md`
- Read `C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m3_challenger_1\report.md` (Contains exact line numbers, root causes, and surgical diffs).

**MANDATORY INTEGRITY WARNING**:
> DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A forensic auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

**Tasks**:
1. **Defect 1 (`backend/app/services/telematics_engine.py:filter_stationary_jitter`)**:
   Accumulate `step_dist` from `filtered[-1]` to `(cur_lat, cur_lon)` when transitioning from moving (`not filtered[-1].get("is_stationary")`) to stationary (`speed < min_speed_kmh`), ensuring distance of the final leg is never dropped.
2. **Defect 2 (`backend/app/services/telematics_engine.py:cluster_pings_5km`)**:
   Clamp `dur = max(0.0, float(item.get("duration_s", item.get("duration_seconds", 0.0))))` so negative durations cannot corrupt cluster or journey working hours.
3. **Defect 3 (`backend/app/services/analytics_engine.py:enforce_hours_conservation`)**:
   Add `math.isfinite(...)` guard on input shift, working, and travelling hours to sanitize non-finite/infinite numbers and prevent `AssertionError` crashes.
4. **Defect 4 (`backend/app/services/telematics_engine.py:cluster_pings_5km`)**:
   Optimize distance checks when adding stops to clusters to ensure linear/efficient scaling.
5. Run the full test suite:
   ```powershell
   pytest tests/ backend/tests/ -v
   ```
6. Run frontend build to verify no regressions:
   ```powershell
   cd frontend
   npm run build
   ```
7. Deliver a complete handoff report to `handoff.md` and send a message to parent orchestrator.

## 2026-09-23T09:55:03Z
User Request:
Implement Milestone 3 Hardening Remediation:
1. telematics_engine.py: Defect 1 (filter_stationary_jitter transition accumulation)
2. telematics_engine.py: Defect 2 (cluster_pings_5km duration clamp)
3. telematics_engine.py: Defect 4 (cluster_pings_5km quadratic scaling check)
4. analytics_engine.py: Defect 3 (enforce_hours_conservation math.isfinite guard)
5. Run full test suite: pytest tests/ backend/tests/ -v
6. Run frontend build: npm run build
7. Write report.md and handoff.md, notify parent orchestrator.
