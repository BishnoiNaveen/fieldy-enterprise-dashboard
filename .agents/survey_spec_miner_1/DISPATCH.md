# Task Dispatch — Survey Spec Miner 1 (Fieldy FSM & Krone Schemas)

## Mission
Investigate and document all technical specifications, domain models, APIs, and data structures for the Fieldy FSM integration and Krone Agriculture India operations.

## Authoritative Inputs
- Original Request: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\ORIGINAL_REQUEST.md
- Skill Reference: C:\Users\Naveen\.gemini\config\skills\fieldy-management\SKILL.md

## Scope & Objectives
1. Read `ORIGINAL_REQUEST.md` and `C:\Users\Naveen\.gemini\config\skills\fieldy-management\SKILL.md`.
2. Extract exact domain models and data schemas for:
   - Fieldy Jobs: job numbering (`SR-26-XXXX`), status pipeline (e.g. Assigned, En Route, In Progress, Completed, Pending Parts, Cancelled), customer details, assigned technicians, timestamps.
   - Technicians: ID, name, status (On Paid Job, Available, Leave/Holiday), active job ID, current GPS coordinates/last ping.
   - Machines / Assets: Asset Name, Serial Number, Client Company Name, Site Contact Person, Krone machine types (e.g., Big Pack balers, BiG X forage harvesters, mowers, rakes).
   - Sync Mechanism: REST API endpoints, session syncing, auth header requirements, automatic background polling, manual "Fresh Sync" trigger, offline fallback cache.
3. Write a comprehensive survey report to `C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\survey_spec_miner_1\report.md` and handoff to `handoff.md`.
4. Send your completion message to orchestrator parent.

## 2026-09-22T12:40:02Z
Perform an in-depth investigation and specification extraction of:
1. Fieldy FSM data structures, REST endpoints, session synchronizer protocols, and mock data models for Krone Agriculture India operations.
2. Exact schemas for:
   - Jobs: numbering `SR-26-XXXX`, status pipeline, customer, assigned technicians, machine linkage.
   - Technicians: on paid job, active vs holiday/leave, location telemetry.
   - Machines/Assets: Asset Name, Serial Number, Client Company Name, Site Contact Person, Krone equipment lines (BiG Pack, BiG X, EasyCut, Comprima, etc.).
   - Synchronization & offline cache mechanisms with "Fresh Sync" trigger and automatic background polling.
Write your full findings to C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\survey_spec_miner_1\report.md and create your handoff at C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\survey_spec_miner_1\handoff.md.
When finished, send a completion message back to parent orchestrator.
