# Task Dispatch — M2 Worker (Enterprise Reactive Frontend Implementation)

## Mission
Build and verify the complete, enterprise-grade reactive frontend dashboard for Krone Agriculture India in `frontend/` using Vite React 18, TypeScript, Tailwind CSS, Leaflet, and Recharts.

## Authoritative Inputs
- ORIGINAL_REQUEST.md: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\ORIGINAL_REQUEST.md
- PROJECT.md: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\PROJECT.md
- M2 Explorer 1 Report (Foundation & Bento): C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m2_explorer_1\report.md
- M2 Explorer 2 Report (Pulse & Analytics): C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m2_explorer_2\report.md
- M2 Explorer 3 Report (Map & Playback): C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m2_explorer_3\report.md

## File Ownership
You exclusively own and write all files under `frontend/`:
- `frontend/package.json`
- `frontend/vite.config.ts`
- `frontend/tsconfig.json` & `frontend/tsconfig.node.json`
- `frontend/tailwind.config.js` & `frontend/postcss.config.js`
- `frontend/index.html`
- `frontend/src/index.css`
- `frontend/src/main.tsx`
- `frontend/src/App.tsx`
- `frontend/src/types/dashboard.ts`
- `frontend/src/services/api.ts`
- `frontend/src/components/Header.tsx`
- `frontend/src/components/BentoKpis.tsx`
- `frontend/src/components/LivePulseBoard.tsx`
- `frontend/src/components/MachineryTable.tsx`
- `frontend/src/components/FilterBar.tsx`
- `frontend/src/components/ProductivityCharts.tsx`
- `frontend/src/components/RouteInspectorMap.tsx`
- `frontend/src/components/AnomalyAlerts.tsx`
- `frontend/src/utils/formatters.ts`

DO NOT modify files in `backend/` or `tests/`.

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A forensic auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Detailed Tasks
1. Initialize `frontend/package.json` with React 18, Vite, TypeScript, Tailwind CSS, Lucide React, Leaflet, @types/leaflet, Recharts, Axios.
2. Configure `vite.config.ts` with proxy to backend (`http://localhost:8000`), `tailwind.config.js` with Krone theme tokens, and `index.html`.
3. Implement `types/dashboard.ts` strictly matching backend Pydantic models.
4. Implement `services/api.ts` connecting to `/api/dashboard/pulse`, `/api/dashboard/sync`, `/api/analytics/productivity`, `/api/telematics/routes`, with automatic resilient fallback to local Krone dataset when backend is not reached.
5. Implement `Header.tsx` with Krone Agriculture India branding, live status beacon, and "Fresh Sync" trigger with timestamp indicators.
6. Implement `BentoKpis.tsx` with 4 executive KPI cards (Active on Paid Jobs, Total Active vs Leave, Total Jobs Today, Fleet Utilization %).
7. Implement `LivePulseBoard.tsx` with active technicians on paid jobs, machine bindings, and Today's Jobs table (`SR-26-XXXX`, status pipeline, customer, assigned technicians).
8. Implement `MachineryTable.tsx` with machines under service today (Asset Name, 7-digit Serial, Customer Company, Site Contact Person).
9. Implement `FilterBar.tsx` with multi-dimensional search & filtering (by technician, customer company, date range, job status, job type) and timeframe switcher (Daily/Weekly/Monthly) executing without page reload.
10. Implement `ProductivityCharts.tsx` with Recharts stacked bar & trend charts for working, travelling, and idle hours, and drill-down scorecards.
11. Implement `RouteInspectorMap.tsx` using Leaflet with CartoDB Dark Matter tiles, start/destination markers, route polyline playback scrubber, 5 km geofence circles ($R = 5000\text{m}$) with centroid badges, and stop duration badges.
12. Implement `AnomalyAlerts.tsx` with interactive drawer for unauthorized stops (>15 min outside 5 km zone), route deviations, and map coordinate inspection.
13. Integrate everything cohesively into `App.tsx`.
14. Run `npm install` and `npm run build` in `frontend/`. Verify build succeeds with zero errors.
15. Write report to `C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m2_worker\report.md` and handoff to `C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m2_worker\handoff.md`.
16. Send completion message to parent orchestrator.

## 2026-09-23T09:30:43Z
**Context**: Milestone 2 Frontend Implementation
**Content**: All 3 explorer reports are complete and available in .agents/m2_explorer_1, .agents/m2_explorer_2, and .agents/m2_explorer_3.
**Action**: Please proceed immediately with creating frontend/package.json, configs, components, and running npm install and npm run build.

