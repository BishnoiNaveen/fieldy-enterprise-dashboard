# Orchestration Plan — Field Service & Telematics Dashboard

## Objective
Deliver an enterprise-grade Field Service & Telematics Dashboard for Krone Agriculture India integrated with Fieldy FSM and telematics tracking data, meeting all requirements (R1-R4) and acceptance criteria.

## Phase 0: Survey & Scope Mapping
1. Spawn 3 specialized Explorers / Spec Miners in parallel:
   - Explorer 1 (Fieldy FSM & Krone Schemas Spec Miner): In-depth extraction of Fieldy REST API endpoints, session syncing, schema models for Jobs (`SR-26-XXXX`), Technicians, Machines/Assets, and Krone Agriculture India domain models referencing the `fieldy-management` skill.
   - Explorer 2 (Telematics & Geofence Clustering Specialist): Algorithms for 5 km Haversine clustering, route inspection, start/destination detection, transit duration vs unauthorized stops, jitter filtering.
   - Explorer 3 (Full-Stack Architecture & UI/UX Specialist): Architecture for high-performance FastAPI/Node backend + Next.js / Vite React frontend, Tailwind CSS, Leaflet/MapLibre map playback, charts, offline fallback generator, test harnesses.
2. Synthesize findings into `PROJECT.md § Feature Inventory` and `TEST_INFRA.md`.

## Phase 1: Architecture & Decomposition
1. Finalize `PROJECT.md` with:
   - System Architecture (Backend API, Frontend App, Telematics & Clustering Engine, Sync Service).
   - Complete Feature Inventory mapped to Milestones.
   - Interface Contracts between backend, frontend, and telematics modules.
   - Code Layout and verification guidelines.
2. Finalize `TEST_INFRA.md` for the E2E Testing Track.

## Phase 2: Dual Track Execution
- Implementation Track:
  - M1: Core Engine, Fieldy Sync Service & Mock Data Generator (FastAPI / Node backend, Fieldy schemas, caching/offline fallback).
  - M2: R1 Operational Pulse & Machine Health Board (Live KPIs, Technicians on jobs, Machine asset table, Fresh Sync).
  - M3: R2 Technician Productivity & Hours Analytics Engine (Daily/Weekly/Monthly hours breakdown, filters, charts, drill-downs).
  - M4: R3 Autonomous Route Inspector & 5 km Geofence Clustering Engine (Haversine clustering, transit vs unauthorized stops, map playback).
  - M5: R4 Enterprise UI/UX Integration & Polish (Executive theme, layout responsiveness, navigation, telemetry feeds).
- E2E Testing Track (Parallel):
  - Design and implement automated test suite across Tiers 1-4 (>= 50 test cases covering Haversine clustering, hours aggregation, sync triggers, edge cases).
  - Publish `TEST_READY.md`.

## Phase 3: Final Acceptance & Hardening
1. Pass 100% of E2E tests (Tiers 1-4).
2. Phase 2 Hardening (Tier 5): Challenger-driven adversarial coverage hardening.
3. Forensic Auditor integrity verification.

## Phase 4: Final Hand-off & Human Report
1. Verify clean build, zero console errors, complete functionality.
2. Prepare and send comprehensive completion report to Sentinel.
