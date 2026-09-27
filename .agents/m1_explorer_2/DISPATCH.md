# Task Dispatch — M1 Explorer 2 (Telematics Engine: 5 km Clustering & Route Inspector)

## Mission
Analyze and provide the concrete implementation blueprint for the Telematics Engine (`backend/app/services/telematics_engine.py`) implementing clamped Haversine, 5 km leader clustering, duration-weighted centroids, jitter suppression, and route anomaly detection.

## Authoritative Inputs
- ORIGINAL_REQUEST.md: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\ORIGINAL_REQUEST.md
- PROJECT.md: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\PROJECT.md
- Survey Explorer 2 Report: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\survey_explorer_2\report.md

## Scope & Deliverables
1. Read `ORIGINAL_REQUEST.md`, `PROJECT.md`, and `survey_explorer_2\report.md`.
2. Provide the production-ready implementation design for `backend/app/services/telematics_engine.py`:
   - `haversine_distance_km(lat1, lon1, lat2, lon2)` with clamped domain $a^* \in [0, 1]$ and radius $R = 6371.0\text{ km}$.
   - `cluster_pings_5km(pings)`: incremental leader clustering capped at $5.0\text{ km}$ radius from centroid, duration-weighted 3D Cartesian spherical centroid projection.
   - `filter_stationary_jitter(pings, min_speed_kmh=1.5, deadband_meters=30)`: eliminating stationary GPS jitter.
   - `analyze_route_journey(pings, job_site_coords, base_coords)`: start/dest matching, designated transit vs unauthorized stop detection (>15 min outside 5 km zone), cross-track distance corridor calculation.
3. Detail the unit test specifications for `backend/tests/test_clustering.py` covering all 18 test vectors.
4. Output your detailed technical strategy to C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_explorer_2\report.md and handoff.md.

## 2026-09-22T12:48:07Z
<USER_REQUEST>
You are m1_explorer_2, an exploration specialist for Milestone 1 Telematics & 5 km Clustering Engine.
Your working directory is C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_explorer_2.
You MUST read C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\ORIGINAL_REQUEST.md before starting work.
Also read C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\PROJECT.md and C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_explorer_2\DISPATCH.md.
Review C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\survey_explorer_2\report.md.

Analyze and specify the exact implementation blueprint for:
1. `backend/app/services/telematics_engine.py`:
   - Clamped Haversine distance formula with $R=6371.0\text{ km}$ and domain safety $a^* \in [0, 1]$.
   - Duration-weighted 3D spherical Cartesian centroid projection.
   - Speed-gated stationary jitter suppression ($v < 1.5\text{ km/h}$, 30m deadband).
   - Incremental leader clustering capped at $5.0\text{ km}$ centroid-to-point radius.
   - Route inspector: Start location (base/depot) and destination customer site detection, designated route transit vs unauthorized halts (>15 min outside 5 km zone), corridor cross-track distance.
2. Complete test vectors and assertions for `backend/tests/test_clustering.py` covering all 18 test cases.
Write your full report to C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m1_explorer_2\report.md and create handoff.md.
Send a completion message back to parent orchestrator when finished.
</USER_REQUEST>
