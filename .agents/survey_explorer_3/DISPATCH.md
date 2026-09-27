# Task Dispatch — Survey Explorer 3 (Full-Stack Architecture & Enterprise UI/UX)

## Mission
Investigate and design the full-stack architecture, technology stack, API contracts, interactive map integration, and UI/UX design specifications for the enterprise dashboard.

## Authoritative Inputs
- Original Request: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\ORIGINAL_REQUEST.md
- Skill References:
  - C:\Users\Naveen\.gemini\config\skills\ui-ux-pro-max-skill\SKILL.md
  - C:\Users\Naveen\.gemini\config\skills\bento-motion-master\SKILL.md

## Scope & Objectives
1. Read `ORIGINAL_REQUEST.md`.
2. Propose optimal technical stack for both backend and frontend:
   - Backend API: FastAPI (Python) or Express/Node.js with clean modular architecture, high-performance endpoints, background task polling, mock data generator, and automated test runners.
   - Frontend: Modern React (Vite or Next.js) with Tailwind CSS, Lucide icons, Leaflet/MapLibre for interactive route playback and geofence cluster visualization, Recharts or Chart.js for productivity analytics.
   - Resilient Offline & Mock Data Engine: Realistic Krone Agriculture India dataset (technicians across Indian territories e.g. Punjab, Haryana, Maharashtra, Gujarat, real Krone balers/harvesters, GPS coordinates, historical logs).
3. Specify API endpoint contracts:
   - `/api/dashboard/pulse` (today's KPIs, active technicians, machines under service)
   - `/api/dashboard/sync` (POST manual trigger, background status)
   - `/api/analytics/productivity` (daily/weekly/monthly hours, filtering by tech, customer, status)
   - `/api/telematics/routes` (technician journey, GPS pings, 5km clusters, transit vs unauthorized stops)
   - `/api/technicians` and `/api/jobs`
4. Design UI layout and components matching enterprise dashboard standards (executive KPI summary cards, filter bars, tabbed analytics, interactive route map with playback scrubber, anomaly alert drawer).
5. Write report to `C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\survey_explorer_3\report.md` and handoff to `handoff.md`.
6. Send your completion message to orchestrator parent.

## 2026-09-22T12:40:03Z
You are survey_explorer_3, a Full-Stack Architecture and UI/UX Specialist.
Your working directory is C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\survey_explorer_3.
You MUST read C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\ORIGINAL_REQUEST.md before starting work.
Also read C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\survey_explorer_3\DISPATCH.md and review ui-ux-pro-max-skill / bento-motion-master skill guidelines if applicable.

Perform an in-depth architectural and UI/UX design investigation:
1. Technical stack selection & directory structure for enterprise dashboard:
   - Self-contained, robust backend API server (e.g. FastAPI with Pydantic & Uvicorn, or Node.js / Express) + fast, reactive frontend (Vite React + Tailwind CSS + Lucide + Leaflet for map route playback + Recharts for analytics).
   - Real-world synthetic dataset generator calibrated to Krone Agriculture India (Punjab, Haryana, UP, Maharashtra, MP, Gujarat field operations).
2. REST API contract definitions:
   - `/api/dashboard/pulse`, `/api/dashboard/sync`, `/api/analytics/productivity`, `/api/telematics/routes`, `/api/technicians`, `/api/jobs`.
3. UI/UX component architecture:
   - Executive KPI cards, Live Pulse board, Machinery Table, Filter controls, Date Range selector (Daily/Weekly/Monthly), Route Inspector map with playback & stop badges, Anomaly alert panel.
4. Build, run, and test setup requirements to ensure 100% clean automated execution.
Write your full findings to C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\survey_explorer_3\report.md and create your handoff at C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\survey_explorer_3\handoff.md.
When finished, send a completion message back to parent orchestrator.

