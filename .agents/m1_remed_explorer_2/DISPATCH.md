# Task Dispatch — M1 Remediation Explorer 2 (Telematics Router Dynamic Wiring)

## Mission
Investigate and design the exact code fixes to eliminate the facade implementation in `backend/app/routers/telematics.py`.

## Authoritative Inputs
- ORIGINAL_REQUEST.md: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\ORIGINAL_REQUEST.md
- PROJECT.md: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\PROJECT.md
- FULL AUDITOR EVIDENCE REPORT: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_auditor\report.md
- AUDITOR HANDOFF: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_auditor\handoff.md

## Integrity Violation to Remediate
- In `backend/app/routers/telematics.py:18-31`, the endpoint `GET /api/telematics/routes` currently bypasses `telematics_engine.py` and returns a static mock route from `KroneMockGenerator.generate_default_route` for all technicians across India.
- Remediate by wiring the router to:
  1. Retrieve the technician's actual journey GPS pings from the data store / mock generator based on `technician_id` and `date`.
  2. Dynamically execute `telematics_engine.analyze_route_journey(...)` with the technician's destination job site coordinates and origin depot coordinates.
  3. Return the genuinely computed `RouteInspectionResponse`.
  4. Ensure distinct technicians (e.g. Punjab `TECH-001` vs AP `TECH-005` vs MP `TECH-008`) receive distinct, authentic routes and telemetry.

Output detailed code diffs and strategy to `C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_remed_explorer_2\report.md` and `handoff.md`.
Send completion message to parent orchestrator.
