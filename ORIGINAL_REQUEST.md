# Original User Request

## 2026-09-22T12:38:27Z

Build an enterprise-grade Field Service & Telematics Dashboard for Krone Agriculture India integrated with Fieldy FSM and telematics tracking data. The platform provides real-time operational visibility into technicians' daily paid jobs, machine asset servicing, multi-tier time tracking (working, idle, traveling), and autonomous GPS route inspection with a 5 km radius clustering engine.

Working directory: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard
Integrity mode: development

## Requirements

### R1. Live Operational Pulse & Machine Health Board
- Display real-time KPIs for today:
  - Technicians actively on paid jobs (with technician names and live job IDs).
  - Total active technicians vs technicians on holiday/leave today.
  - List of today's jobs with job numbers (`SR-26-XXXX`), status pipeline, customer, and assigned technicians.
  - Machines/assets under service today: Asset Name, Serial Number, Client Company Name, and Site Contact Person.
- Integrate with Fieldy REST API / session synchronizer with automatic background polling and a manual "Fresh Sync" trigger to ensure zero stale data.

### R2. Technician Productivity & Hours Analytics Engine (Daily / Weekly / Monthly)
- Provide historical and date-range filtered metrics (Daily, Weekly, Monthly) per technician:
  - Total Working Hours (on-job / productive time).
  - Total Travelling Hours (transit telematics).
  - Total Idle Hours (unaccounted / inactive periods).
- Multi-dimensional search and filtering (by technician, customer company, date range, job status, and job type).
- Interactive comparative charts, exportable summaries, and drill-down technician scorecards.

### R3. Autonomous Route Inspector & 5 km Geofence Clustering Engine
- Specialized autonomous route inspection module:
  - Automatic detection of starting location (base / office / hotel) and destination job site.
  - Calculation of transit duration on designated route vs time spent at 3rd-party/unauthorized locations.
  - 5 km radius intelligent location clustering: GPS pings/stops within 5 km distance are merged as a single operational zone (preventing jitter or sub-kilometer micro-moves from fragmenting site stays).
  - Visual interactive map with route playback, stop duration badges, and anomaly alerts for unauthorized stops.

### R4. Enterprise UI/UX & Resilient Architecture
- High-end enterprise dashboard design (executive KPI cards, interactive tables, responsive layouts, dark/light theme accents).
- Self-contained, robust backend API server (FastAPI/Node.js) paired with a modern reactive frontend (Next.js / Vite React / Tailwind CSS).
- Resilient offline fallback and synthetic mock data generator calibrated to Krone Agriculture India real-world schemas if Fieldy cloud session is refreshing.

## Acceptance Criteria

### Live Operational Pulse
- [ ] Today's dashboard renders count and list of technicians on paid jobs, total active, and on holiday.
- [ ] Active machinery table accurately lists machine name, serial number, customer company, and contact person.
- [ ] "Fresh Sync" button fetches the latest data with clear timestamp indicators.

### Productivity Analytics
- [ ] Time breakdown shows working, travelling, and idle hours broken down per technician.
- [ ] Timeframe switcher seamlessly toggles between Daily, Weekly, and Monthly views.
- [ ] Technician search and multi-criteria filters execute without page reload.

### Route & Geofence Intelligence
- [ ] Route inspector visualizes technician journey with start point, travel path, and job destination.
- [ ] Stops within 5 km of each other are clustered into a single location entry.
- [ ] Unscheduled / 3rd-party stop durations are flagged and reported separately from verified route transit time.

### System Verification & Code Quality
- [ ] Programmatic automated test suite verifies 5 km Haversine clustering and time aggregation math.
- [ ] End-to-end dashboard builds and launches with zero console errors.
