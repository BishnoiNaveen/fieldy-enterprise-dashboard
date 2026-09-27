# Task Dispatch — M1 Challenger 2 (Analytics Conservation & API Concurrency Challenger)

## Mission
Adversarially stress-test the Hours Analytics Engine and REST API endpoints under concurrency and extreme data conditions.

## Authoritative Inputs
- ORIGINAL_REQUEST.md: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\ORIGINAL_REQUEST.md
- PROJECT.md: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\PROJECT.md

## Scope & Deliverables
1. Read `ORIGINAL_REQUEST.md` and `PROJECT.md`.
2. Write and execute stress-testing scripts:
   - Invariant conservation stress test: Generate 10,000 randomized shift intervals; verify $|H_{shift} - (H_w + H_t + H_i)| < 10^{-7}$ across every single record without exception.
   - Date range boundary tests: cross-month, cross-year, zero-length ranges, future dates.
   - Multi-dimensional filter permutations: random combinations of technician, customer, status, and job type.
   - API concurrency test: Concurrent requests against FastAPI endpoints using `TestClient` or `httpx` to verify thread-safety of sync and mock cache.
3. Provide an empirical verdict: `APPROVE` (correctness confirmed) or `REJECT` (failures found).
4. Write your report to `C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_challenger_2\report.md` and `handoff.md`.
5. Send your completion message to parent orchestrator.

## 2026-09-22T13:02:24Z
You are m1_challenger_2, analytics conservation & concurrency adversarial challenger.
Your working directory is C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_challenger_2.
You MUST read C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\ORIGINAL_REQUEST.md before starting work.
Also read C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\PROJECT.md and C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_challenger_2\DISPATCH.md.

Challenger tasks:
1. Adversarially stress-test `backend/app/services/analytics_engine.py` and FastAPI endpoints:
   - Invariant conservation stress test: Generate 10,000 randomized shift intervals; verify $|H_{shift} - (H_w + H_t + H_i)| < 10^{-7}$ across every single record without exception.
   - Date range boundary tests: cross-month, cross-year, zero-length ranges, future dates.
   - Multi-dimensional filter permutations: random combinations of technician, customer, status, and job type.
   - API concurrency test: Concurrent requests against FastAPI endpoints using `TestClient` or `httpx` to verify thread-safety of sync and mock cache.
2. Deliver an empirical verdict: APPROVE or REJECT.
Write report to C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_challenger_2\report.md and handoff.md.
Send completion message to parent orchestrator.
