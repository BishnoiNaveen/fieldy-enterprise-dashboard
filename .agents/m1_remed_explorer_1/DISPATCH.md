# Task Dispatch — M1 Remediation Explorer 1 (Telematics Engine & Hours Math Integrity Fix)

## Mission
Investigate and design the exact code fixes for the integrity violations and review findings in `backend/app/services/telematics_engine.py`.

## Authoritative Inputs
- ORIGINAL_REQUEST.md: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\ORIGINAL_REQUEST.md
- PROJECT.md: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\PROJECT.md
- FULL AUDITOR EVIDENCE REPORT: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_auditor\report.md
- AUDITOR HANDOFF: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_auditor\handoff.md
- REVIEWER 1 REPORT: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_reviewer_1\report.md
- REVIEWER 2 REPORT: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_reviewer_2\report.md

## Integrity Violations to Remediate
1. Lines 517–537 of `backend/app/services/telematics_engine.py:analyze_route_journey`:
   - Remove all ternary fallbacks that substitute hardcoded values (`25.0` min, `84.6` km, `1` anomaly, static coordinates `(30.6450, 76.3200)`, and static polylines) when metrics compute to zero.
   - Clean routes must genuinely report: `anomalies_detected: 0`, `unauthorized_stop_duration_minutes: 0.0`, `anomalies: []`.
2. Fix stationary jitter anchor wandering in `filter_stationary_jitter` under noisy GPS pings.
3. Implement genuine `calculate_hours` computing duration from timestamp deltas ($t_i - t_{i-1}$) for moving, stationary, and idle periods.

Output detailed code diffs and strategy to `C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_remed_explorer_1\report.md` and `handoff.md`.
Send completion message to parent orchestrator.

## 2026-09-23T04:25:13Z
You are m1_remed_explorer_1, remediation explorer for telematics engine integrity.
Your working directory is C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_remed_explorer_1.
You MUST read C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\ORIGINAL_REQUEST.md before starting work.
You MUST read the FULL AUDITOR EVIDENCE REPORT at C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_auditor\report.md and C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_auditor\handoff.md.
Also read C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_remed_explorer_1\DISPATCH.md.

Design the exact code changes for `backend/app/services/telematics_engine.py`:
1. Remove all ternary operator fallbacks in `analyze_route_journey` (lines 517–537) that fabricate 25 min halts or static Dhaba stops on clean routes.
2. Fix stationary jitter anchor wandering in `filter_stationary_jitter`.
3. Implement genuine `calculate_hours` computing moving/stationary/idle durations from timestamp deltas.
Write your full report to C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_remed_explorer_1\report.md and handoff.md.
Send completion message to parent orchestrator.
