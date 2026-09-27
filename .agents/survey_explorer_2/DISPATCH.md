# Task Dispatch — Survey Explorer 2 (Telematics, Route Inspection & 5 km Clustering)

## Mission
Investigate and specify the mathematical models, algorithmic designs, telematics data structures, and geofence clustering logic required for R3.

## Authoritative Inputs
- Original Request: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\ORIGINAL_REQUEST.md

## Scope & Objectives
1. Read `ORIGINAL_REQUEST.md`.
2. Detail the exact mathematical formulation and edge cases for:
   - 5 km radius intelligent location clustering using the Haversine formula:
     - Distance calculation between lat/long coordinates.
     - Merging GPS pings / stops within 5 km into a unified operational zone / cluster center.
     - Handling jitter, moving pings vs stationary pings, and sub-kilometer micro-moves.
   - Autonomous Route Inspection & Journey Analysis:
     - Identification of Start point (base/office/hotel) and Destination job site.
     - Separation of Transit Duration (on designated route) vs Time spent at 3rd-party / unauthorized locations.
     - Unscheduled / anomaly stop detection (e.g. stops > 15 min outside 5 km radius of known route/job site).
   - Time Tracking Aggregation (R2 metrics):
     - Total Working Hours (on-job / productive time at customer site).
     - Total Travelling Hours (transit telematics).
     - Total Idle Hours (unaccounted / inactive periods).
     - Daily / Weekly / Monthly aggregation formulas.
3. Propose programmatic unit test cases and verification formulas to be implemented in the test suite.
4. Write report to `C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\survey_explorer_2\report.md` and handoff to `handoff.md`.
5. Send your completion message to orchestrator parent.

## 2026-09-22T12:40:03Z
You are survey_explorer_2, an algorithmic & telematics specialist.
Your working directory is C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\survey_explorer_2.
You MUST read C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\ORIGINAL_REQUEST.md before starting work.
Also read C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\survey_explorer_2\DISPATCH.md.

Perform an in-depth mathematical, algorithmic, and data modeling analysis of:
1. 5 km radius intelligent location clustering using Haversine formula (formulas, coordinate precision, merging algorithm, centroid calculation, jitter dampening, stationary threshold).
2. Autonomous Route Inspection:
   - Automatic detection of starting location (base / office / hotel) and destination customer site.
   - Calculation of designated route transit duration vs time spent at 3rd-party/unauthorized locations.
   - Anomaly detection heuristics (e.g., unauthorized stops > 15 minutes, route deviations).
3. Productivity & Hours Analytics aggregation math (Daily, Weekly, Monthly for Working, Travelling, and Idle hours).
4. Concrete test cases and verification formulas to validate in automated tests.
Write your full findings to C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\survey_explorer_2\report.md and create your handoff at C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\survey_explorer_2\handoff.md.
When finished, send a completion message back to parent orchestrator.

