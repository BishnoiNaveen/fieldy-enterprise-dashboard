# Project: Krone Agriculture India — Field Service & Telematics Dashboard

## Architecture
Decoupled enterprise monorepo architecture combining a high-performance Python FastAPI backend engine with a modern Vite React 18 TypeScript frontend, styled with Tailwind CSS and powered by Leaflet and Recharts.

```
┌────────────────────────────────────────────────────────────────────────┐
│               Enterprise Reactive Frontend (Vite React + TS)           │
│  - Executive Bento Grid (4 Core KPIs)    - Live Operational Pulse Board│
│  - Machines Under Service Table          - Multi-tier Filter Bar       │
│  - Productivity Hours Analytics (Charts) - Leaflet Route Inspector Map │
│  - 5 km Geofence Zone Visualization      - Route Playback & Anomaly Log│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ REST API / JSON
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               Enterprise Backend Engine (FastAPI / Uvicorn)            │
│  - /api/dashboard/pulse      - /api/dashboard/sync                     │
│  - /api/analytics/productivity - /api/telematics/routes                │
│  - /api/technicians          - /api/jobs                               │
├────────────────────────────────────────────────────────────────────────┤
│  - Telematics Engine (Clamped Haversine, 5km Clustering, XTD Corridor) │
│  - Time Tracking Aggregator (Working, Travelling, Idle hours math)     │
│  - Fieldy Session Synchronizer & Background Poller                     │
│  - Calibrated Krone Agriculture India Synthetic Mock Engine            │
└────────────────────────────────────────────────────────────────────────┘
```

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Real-Time Operational Pulse KPIs | Daily counts of active technicians on paid jobs, technicians on holiday/leave, live job numbers | M1, M2 | R1, survey |
| 2 | Today's Jobs List | Detailed list with `SR-26-XXXX`, status pipeline, customer, assigned technicians | M1, M2 | R1, survey |
| 3 | Machinery Under Service Table | Machine Asset Name, 7-digit Serial Number, Customer Company, Site Contact Person | M1, M2 | R1, survey |
| 4 | Fieldy FSM Session Synchronizer | Background polling and manual "Fresh Sync" trigger with timestamp indicators | M1, M2 | R1, survey |
| 5 | Calibrated Krone Synthetic Generator | Resilient offline fallback with authentic Krone equipment, technicians, RIL bio-energy contracts | M1 | R4, survey |
| 6 | 5 km Radius Haversine Clustering | Clamped Haversine formula ($R=6371.0\text{ km}$), duration-weighted 3D centroid projection | M1 | R3, survey |
| 7 | Speed-Gated Jitter Dampening | Suppress stationary jitter ($v < 1.5\text{ km/h}$, 30m deadband) avoiding cluster fragmentation | M1 | R3, survey |
| 8 | Autonomous Route Inspector | Auto-detect Origin Base (office/hotel) and Destination job site within 5 km | M1 | R3, survey |
| 9 | Transit vs Unauthorized Stop Detection | Separate designated corridor travel from unscheduled stops (>15 min outside 5 km zone) | M1 | R3, survey |
| 10 | Route Anomaly Detection & Alerts | Anomaly flags for unauthorized halts, excessive detours ($>1.25$ ratio), GPS dropouts | M1, M2 | R3, survey |
| 11 | Multi-Tier Hours Analytics | Total Working, Travelling, and Idle hours with strict conservation $H_{shift} = H_w + H_t + H_i$ | M1 | R2, survey |
| 12 | Timeframe Toggling (Daily/Weekly/Monthly) | Seamless switching of productivity aggregation metrics across time horizons | M1, M2 | R2, survey |
| 13 | Multi-Dimensional Search & Filtering | Filter by technician, customer company, date range, job status, job type | M1, M2 | R2, survey |
| 14 | Comparative Charts & Scorecards | Visual hours distribution, technician utilization rates, and drill-down scorecards | M1, M2 | R2, survey |
| 15 | Executive Bento Grid UI/UX | High-density luxury industrial dashboard with dark obsidian substrate and level-3 glassmorphism | M2 | R4, survey |
| 16 | Interactive Leaflet Route Map | Dark CartoDB tiles, polyline journey path, 5 km geofence circles, stop badges, playback scrubber | M2 | R3, R4, survey |
| 17 | Automated Programmatic Test Suite | Unit tests verifying Haversine math, 5 km clustering, hours conservation, REST endpoints | E2E Track | Acceptance, survey |
| 18 | End-to-End System Integration & Hardening | 100% E2E test pass across Tiers 1-4 followed by Tier 5 adversarial stress testing | M3 | Final Milestone |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Enterprise Backend Engine | Complete FastAPI backend: Pydantic schemas, Fieldy sync service, calibrated Krone synthetic generator, 5 km Haversine clustering, duration-weighted centroids, jitter filter, route inspector & anomaly detection, hours analytics ($H_w, H_t, H_i$), all 6 REST endpoints, 380 unit/e2e/adversarial tests | none | DONE |
| M2 | Enterprise Reactive Frontend | Vite React 18 + TS + Tailwind CSS dashboard: Executive Bento Grid, Live Pulse board, Machinery Table, Leaflet Route Inspector with 5 km geofences & playback scrubber, Recharts analytics, Fresh Sync trigger | M1 | DONE |
| M3 | End-to-End Verification & Hardening | Phase 1: 100% pass of E2E test suite (Tiers 1-4). Phase 2: Adversarial coverage hardening (Tier 5) with Challenger-Worker-Reviewer-Auditor loop | M1, M2, TEST_READY | DONE |

## Interface Contracts

### 1. `GET /api/dashboard/pulse`
- Response:
```json
{
  "timestamp": "2026-09-22T12:00:00Z",
  "kpis": {
    "technicians_on_paid_jobs": 8,
    "technicians_active_total": 12,
    "technicians_on_leave": 2,
    "total_jobs_today": 10,
    "jobs_completed_today": 4,
    "fleet_utilization_pct": 83.3
  },
  "technicians_on_jobs": [
    {
      "technician_id": "TECH-001",
      "name": "Gurpreet Singh",
      "status": "On Paid Job",
      "live_job_id": "SR-26-0101",
      "customer_company": "Reliance Industries Limited (Bio-Energy Division)",
      "machine_asset": "Krone BigPack 1290 HDP",
      "current_location": { "lat": 30.901, "lng": 75.8573 }
    }
  ],
  "today_jobs": [
    {
      "job_id": "SR-26-0101",
      "status": "In Progress",
      "status_color": "#059669",
      "customer_name": "Reliance Industries Limited (Bio-Energy Division)",
      "assigned_technicians": ["Gurpreet Singh"],
      "machine_serial": "BP1290-78401",
      "machine_name": "Krone BigPack 1290 HDP High Density Baler",
      "job_type": "Paid",
      "scheduled_start": "2026-09-22T08:30:00Z"
    }
  ],
  "machines_under_service": [
    {
      "asset_name": "Krone BigPack 1290 HDP High Density Baler",
      "serial_number": "BP1290-78401",
      "client_company_name": "Reliance Industries Limited (Bio-Energy Division)",
      "site_contact_person": "Rajinder Verma (+91 98765 43210)",
      "location": "Ludhiana Bio-Mass Hub, Punjab",
      "active_job_id": "SR-26-0101",
      "service_type": "Emergency Knotter Timing Calibration"
    }
  ]
}
```

### 2. `POST /api/dashboard/sync`
- Request: `{ "force_refresh": true }`
- Response: `{ "status": "success", "last_synced_at": "2026-09-22T12:00:00Z", "records_synced": 42, "source": "fieldy_cache" }`

### 3. `GET /api/analytics/productivity`
- Query Params: `timeframe` (daily | weekly | monthly), `technician_id`, `customer_company`, `job_status`, `job_type`, `start_date`, `end_date`
- Response:
```json
{
  "timeframe": "daily",
  "summary": {
    "total_working_hours": 64.5,
    "total_travelling_hours": 21.0,
    "total_idle_hours": 10.5,
    "total_shift_hours": 96.0,
    "average_utilization_pct": 67.2
  },
  "technician_records": [
    {
      "technician_id": "TECH-001",
      "technician_name": "Gurpreet Singh",
      "working_hours": 6.5,
      "travelling_hours": 1.5,
      "idle_hours": 0.0,
      "shift_hours": 8.0,
      "utilization_pct": 81.25,
      "jobs_count": 1
    }
  ],
  "trend_data": [
    { "period": "2026-09-22", "working": 64.5, "travelling": 21.0, "idle": 10.5 }
  ]
}
```

### 4. `GET /api/telematics/routes`
- Query Params: `technician_id`, `date`
- Response:
```json
{
  "technician_id": "TECH-001",
  "technician_name": "Gurpreet Singh",
  "date": "2026-09-22",
  "journey_summary": {
    "start_location": { "name": "Krone Regional Hub Ludhiana", "lat": 30.9010, "lng": 75.8573, "departed_at": "2026-09-22T08:00:00Z" },
    "destination": { "name": "RIL Bio-Energy Facility Barwala", "lat": 30.3801, "lng": 76.8402, "arrived_at": "2026-09-22T09:45:00Z" },
    "transit_duration_minutes": 105,
    "unauthorized_stop_duration_minutes": 25,
    "total_distance_km": 84.6,
    "anomalies_detected": 1
  },
  "raw_pings_count": 180,
  "clusters_5km": [
    {
      "cluster_id": "CLUST-01",
      "centroid": { "lat": 30.9015, "lng": 75.8570 },
      "radius_meters": 450,
      "location_name": "Ludhiana Depot Operational Zone",
      "pings_count": 45,
      "duration_minutes": 60,
      "is_job_site": false,
      "is_base": true
    },
    {
      "cluster_id": "CLUST-02",
      "centroid": { "lat": 30.3800, "lng": 76.8405 },
      "radius_meters": 820,
      "location_name": "RIL Barwala Bio-Mass Job Site",
      "pings_count": 110,
      "duration_minutes": 390,
      "is_job_site": true,
      "is_base": false
    }
  ],
  "anomalies": [
    {
      "type": "unauthorized_stop",
      "location": { "lat": 30.6450, "lng": 76.3200 },
      "duration_minutes": 25,
      "started_at": "2026-09-22T08:45:00Z",
      "description": "Vehicle stationary > 15 min outside 5km authorized corridor"
    }
  ],
  "route_polyline": [[30.9010, 75.8573], [30.8500, 76.0100], [30.6450, 76.3200], [30.3800, 76.8405]]
}
```

## Code Layout
```
fieldy-enterprise-dashboard/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI entrypoint, CORS, routers
│   │   ├── config.py                   # Environment & settings
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py              # Pydantic models for Jobs, Techs, Assets, Analytics
│   │   │   └── telematics.py           # GPS ping, cluster, anomaly models
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── sync_service.py         # Fieldy REST polling & manual fresh sync
│   │   │   ├── telematics_engine.py    # 5km Haversine clustering, route inspector, corridor math
│   │   │   ├── analytics_engine.py     # Working/Travelling/Idle hours aggregator & filters
│   │   │   └── mock_generator.py       # Krone Agriculture India synthetic dataset
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── dashboard.py            # /api/dashboard/pulse, /api/dashboard/sync
│   │       ├── analytics.py            # /api/analytics/productivity
│   │       ├── telematics.py           # /api/telematics/routes
│   │       └── entities.py             # /api/technicians, /api/jobs
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_clustering.py          # 18 test cases for 5km Haversine & centroids
│   │   ├── test_analytics.py           # Hours conservation & aggregation tests
│   │   └── test_api.py                 # Endpoint integration tests
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── index.html
│   ├── vite.config.ts
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── index.css
│       ├── types/
│       │   └── dashboard.ts            # TypeScript interfaces matching backend models
│       ├── services/
│       │   └── api.ts                  # Axios/Fetch API client
│       ├── components/
│       │   ├── Header.tsx              # Executive header, brand badges, Fresh Sync trigger
│       │   ├── BentoKpis.tsx           # 4 Executive KPI cards
│       │   ├── LivePulseBoard.tsx      # Technicians active/leave & today's jobs table
│       │   ├── MachineryTable.tsx      # Krone machines under service today
│       │   ├── ProductivityCharts.tsx  # Daily/Weekly/Monthly hours breakdown & charts
│       │   ├── RouteInspectorMap.tsx   # Leaflet map, 5km clusters, route playback, scrubber
│       │   ├── AnomalyAlerts.tsx       # Unauthorized stops & detour warning drawer
│       │   └── FilterBar.tsx           # Technician, customer, date, status filters
│       └── utils/
│           └── formatters.ts
├── tests/                              # E2E Test Suite (Dual Track)
│   ├── test_tier1_features.py
│   ├── test_tier2_boundaries.py
│   ├── test_tier3_combinations.py
│   └── test_tier4_scenarios.py
├── test_all.ps1                        # Complete test runner
├── run_all.ps1                         # Development launch script
├── PROJECT.md
├── TEST_INFRA.md
└── ORIGINAL_REQUEST.md
```
