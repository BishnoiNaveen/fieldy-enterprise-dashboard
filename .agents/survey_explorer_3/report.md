# Full-Stack Architecture & Enterprise UI/UX Design Specification
**Project**: Krone Agriculture India — Field Service & Telematics Dashboard  
**Author**: survey_explorer_3 (Full-Stack Architecture and UI/UX Specialist)  
**Date**: 2026-09-22  
**Working Directory**: `C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard`  
**Reference Standards**: `ORIGINAL_REQUEST.md`, `fieldy-management` (v4.0 Master), `bento-motion-master`, `ui-ux-pro-max-skill`

---

## Executive Summary

This document defines the complete technical architecture, software stack, directory hierarchy, REST API contracts, domain dataset modeling, and UI/UX design specifications for the **Krone Agriculture India Field Service & Telematics Dashboard**.

The dashboard bridges enterprise Field Service Management (**Fieldy FSM**) with high-resolution telematics tracking, delivering:
1. **Live Operational Pulse & Machinery Health Board** (R1): Real-time visibility into technicians on paid jobs, active machinery under service, and automated/manual synchronization with Fieldy cloud.
2. **Technician Productivity & Hours Analytics Engine** (R2): Dynamic breakdown of Working, Travelling, and Idle hours across Daily, Weekly, and Monthly frames with multi-criteria filtering.
3. **Autonomous Route Inspector & 5 km Geofence Clustering Studio** (R3): Intelligent merging of GPS pings within 5 km into unified operational zones, route corridor transit calculation, unauthorized stop detection (>15 min), and interactive map playback.
4. **Luxury Industrial Enterprise UI/UX** (R4): 2026 Bento Grid architecture, Krone Emerald precision accents (`#059669`), Deep Obsidian substrate (`#0B121E`), and Level 3 Aura Glassmorphism.

---

## 1. Technical Stack Selection & Architectural Rationale

### 1.1 Architecture Blueprint: Decoupled Monorepo

We select a **Decoupled Client-Server Monorepo Architecture**:
- **Backend API Service**: Python FastAPI with Pydantic v2 & Uvicorn.
- **Frontend SPA**: React 18 with Vite, TypeScript, Tailwind CSS, Lucide Icons, React-Leaflet, and Recharts.
- **Telematics & Analytics Engine**: In-memory high-performance geospatial clustering and telemetry analyzer with caching.
- **Sync & Resilience Layer**: Dual-mode Fieldy FSM client with automated session fallback to an empirical Krone Agriculture India dataset generator.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               KRONE ENTERPRISE FRONTEND                                │
│                     (Vite + React 18 + TypeScript + Tailwind CSS)                      │
│  ┌────────────────────────┐  ┌────────────────────────┐  ┌──────────────────────────┐  │
│  │ Executive Bento Grid   │  │ Live Operational Pulse │  │ Route Inspector & Studio │  │
│  │ (KPI Cards & Telemetry)│  │ (Technicians & Assets) │  │ (Leaflet Map + Playback) │  │
│  └───────────┬────────────┘  └───────────┬────────────┘  └────────────┬─────────────┘  │
│              │                           │                            │                │
│              └───────────────────────────┼────────────────────────────┘                │
│                                          │ REST API Calls (Axios / Fetch)              │
└──────────────────────────────────────────┼─────────────────────────────────────────────┘
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              FASTAPI BACKEND API GATEWAY                               │
│                         (Python 3.10+ / Uvicorn / Starlette)                           │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │ Routers: /api/dashboard/*, /api/analytics/*, /api/telematics/*, /api/jobs, etc.  │  │
│  └───────────────────────────────────────┬──────────────────────────────────────────┘  │
│                                          │                                             │
│  ┌───────────────────────────────────────┴──────────────────────────────────────────┐  │
│  │ Core Service Engine:                                                             │  │
│  │  ├── 5 km Haversine Geofence Clusterer (Spatial-Temporal centroid merger)         │  │
│  │  ├── Route Corridor Inspector & Anomaly Detector (>15m unauthorized stop check)   │  │
│  │  ├── Productivity Aggregator (Working / Travel / Idle hours calculator)          │  │
│  │  └── Fieldy Sync Manager & Krone Mock Generator (Session tokens + Cache)         │  │
│  └───────────────────────────────────────┬──────────────────────────────────────────┘  │
└──────────────────────────────────────────┼─────────────────────────────────────────────┘
                                           ▼
                         ┌───────────────────────────────────┐
                         │   Fieldy Cloud / Local Storage    │
                         │    (https://api.getfieldy.com)    │
                         │   + Resilient Offline Generator   │
                         └───────────────────────────────────┘
```

### 1.2 Technology Stack Evaluation Matrix

| Component | Selected Technology | Alternative Evaluated | Why Selected | Why Alternative Rejected |
| :--- | :--- | :--- | :--- | :--- |
| **Backend API** | **FastAPI (Python 3.10+)** | Node.js / Express | Native mathematical precision for Haversine distance and geospatial clustering; Pydantic v2 strict type validation; auto-generated OpenAPI 3.1 Swagger docs; seamless programmatic testing via `pytest`. | Express requires extra libraries for mathematical and geospatial algorithms; lacks native type-safe serialization without complex TypeScript boilerplate. |
| **Frontend Framework** | **Vite + React 18 (TypeScript)** | Next.js 14 (App Router) | Sub-second HMR; lightweight bundle; instant standalone client-side execution without Node server runtime overhead; pure client SPA ideal for real-time dashboards. | Next.js adds unnecessary server-side rendering complexity, node runtime server maintenance, and hydration edge cases for Leaflet map canvas rendering (`window is not defined`). |
| **Styling & Design System** | **Tailwind CSS v3** | CSS Modules / Styled Components | Instant utility tokens, custom Krone color system (Emerald `#059669`, Obsidian `#0B121E`), responsive utility grid classes, zero runtime CSS-in-JS performance penalty. | CSS Modules require disjointed stylesheets and lack pre-configured design tokens for rapid bento grid layouts. |
| **Interactive Map** | **Leaflet + React-Leaflet** | MapLibre GL / Google Maps | 100% open-source, zero API keys required; native support for CartoDB Dark Matter tiles; clean SVG circle rendering for 5 km geofences; custom HTML DivIcons for stop badges. | Google Maps requires billing API keys and network credentials; MapLibre GL adds significant bundle weight for 2D route playback. |
| **Charts & Analytics** | **Recharts** | Chart.js / D3 | Native React declarative SVG architecture; smooth animated transitions; easily customizable tooltips matching dark-theme Aura Glassmorphism. | Chart.js relies on HTML5 Canvas which is harder to customize with React components; D3 has a steep learning curve and verbose boilerplate. |
| **Icons** | **Lucide React** | Heroicons / FontAwesome | Clean, minimalist SVG vector icons; tree-shakeable; comprehensive coverage of agricultural, telematics, and enterprise UI symbols. | FontAwesome has heavy bundle size and paid tier restrictions; Heroicons has limited agricultural and telematics glyphs. |

---

## 2. Directory Structure & File Inventory

The project is structured into a clean monorepo with clear separation between backend, frontend, scripts, and test suites:

```
fieldy-enterprise-dashboard/
├── .agents/                                  # Agent coordination, plans, and reports
│   ├── orchestrator/                         # Master planning and milestone tracking
│   ├── survey_spec_miner_1/                  # Fieldy schema & Krone domain reports
│   ├── survey_explorer_2/                    # Telematics math & clustering reports
│   └── survey_explorer_3/                    # Full-Stack Architecture & UI/UX reports
├── backend/                                  # Self-contained FastAPI backend server
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                           # FastAPI application factory, CORS & routers
│   │   ├── config.py                         # Settings, tenant IDs, defaults
│   │   ├── models/                           # Pydantic v2 domain schemas
│   │   │   ├── __init__.py
│   │   │   ├── pulse.py                      # Live pulse, KPI cards, machinery status
│   │   │   ├── productivity.py               # Hours analytics, daily/weekly/monthly metrics
│   │   │   ├── telematics.py                 # Breadcrumbs, 5km clusters, anomalies
│   │   │   ├── technician.py                 # Technician profiles, status, shift details
│   │   │   ├── job.py                        # Fieldy jobs (SR-26-XXXX)
│   │   │   └── sync.py                       # Sync trigger, status, and telemetry records
│   │   ├── services/                         # Business logic & algorithmic services
│   │   │   ├── __init__.py
│   │   │   ├── clustering.py                 # 5 km Haversine clustering & centroid engine
│   │   │   ├── route_inspector.py            # Journey analyzer & unauthorized stop detector
│   │   │   ├── analytics_engine.py           # Time aggregation (Working/Travel/Idle)
│   │   │   ├── fieldy_client.py              # Fieldy REST API client (live session integration)
│   │   │   └── mock_generator.py             # Realistic Krone India synthetic dataset generator
│   │   └── routers/                          # REST API route controllers
│   │       ├── __init__.py
│   │       ├── dashboard.py                  # /api/dashboard/pulse & /api/dashboard/sync
│   │       ├── analytics.py                  # /api/analytics/productivity
│   │       ├── telematics.py                 # /api/telematics/routes
│   │       ├── technicians.py                # /api/technicians
│   │       └── jobs.py                       # /api/jobs
│   ├── tests/                                # Automated pytest suite (Tiers 1-4)
│   │   ├── __init__.py
│   │   ├── test_clustering.py                # 5 km Haversine & centroid calculation tests
│   │   ├── test_route_inspector.py           # Transit vs unauthorized stop separation tests
│   │   ├── test_analytics_engine.py          # Daily/Weekly/Monthly hours aggregation tests
│   │   ├── test_api_endpoints.py             # FastAPI TestClient HTTP contract tests
│   │   └── test_fieldy_sync.py               # Sync trigger & cache fallback tests
│   ├── requirements.txt                      # Python dependencies
│   └── run.py                                # Standalone backend launcher
├── frontend/                                 # Vite + React 18 + TypeScript frontend
│   ├── public/
│   │   ├── favicon.ico
│   │   └── krone_logo.svg                    # Krone Agriculture branding
│   ├── src/
│   │   ├── assets/                           # Styles, imagery, icons
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.tsx               # Collapsible navigation drawer
│   │   │   │   ├── TopNav.tsx                # Header bar, sync indicator, user profile
│   │   │   │   └── StatusBeacon.tsx          # Real-time connection pulse indicator
│   │   │   ├── bento/
│   │   │   │   ├── ExecutiveBentoGrid.tsx    # 4-card master bento grid container
│   │   │   │   ├── KpiPulseCard.tsx          # Active technicians on paid jobs
│   │   │   │   ├── KpiMachineryCard.tsx      # Active machinery under service
│   │   │   │   ├── KpiHoursCard.tsx          # Today's hours distribution (Working/Travel/Idle)
│   │   │   │   └── KpiComplianceCard.tsx     # Route adherence & anomaly counter
│   │   │   ├── pulse/
│   │   │   │   ├── LivePulseBoard.tsx        # Technician shift status board
│   │   │   │   ├── MachineryTable.tsx        # High-density asset table with search/filters
│   │   │   │   └── JobPipelineBadge.tsx      # Color-coded job status chip
│   │   │   ├── analytics/
│   │   │   │   ├── ProductivityDashboard.tsx # Hours analytics container
│   │   │   │   ├── TimeframeSwitcher.tsx     # Daily / Weekly / Monthly toggle pills
│   │   │   │   ├── HoursBreakdownChart.tsx   # Recharts stacked area/bar chart
│   │   │   │   ├── TechnicianScorecard.tsx   # Individual technician scorecard table
│   │   │   │   └── CustomerShareChart.tsx    # Customer hours distribution pie chart
│   │   │   ├── telematics/
│   │   │   │   ├── RouteInspectorStudio.tsx  # Map + Playback master component
│   │   │   │   ├── LeafletRouteMap.tsx       # Leaflet interactive map with dark tiles
│   │   │   │   ├── GeofenceClusterLayer.tsx  # 5 km radius circles and cluster centroids
│   │   │   │   ├── PlaybackControls.tsx      # Play, pause, scrubber slider, speed selector
│   │   │   │   └── JourneyTimeline.tsx       # Step-by-step waypoint breakdown
│   │   │   ├── alerts/
│   │   │   │   ├── AnomalyAlertPanel.tsx     # Unauthorized stop drawer & alert banner
│   │   │   │   └── AnomalyCard.tsx           # Individual flagged stop details & badge
│   │   │   └── common/
│   │   │       ├── FilterBar.tsx             # Multi-dimensional filter toolbar
│   │   │       ├── SearchInput.tsx           # Debounced search box
│   │   │       ├── Modal.tsx                 # Accessible modal dialog
│   │   │       ├── Badge.tsx                 # Semantic status pills
│   │   │       └── Button.tsx                # Magnetic action button
│   │   ├── hooks/
│   │   │   ├── usePulseData.ts               # Hook for /api/dashboard/pulse polling
│   │   │   ├── useProductivity.ts            # Hook for /api/analytics/productivity
│   │   │   ├── useRoutePlayback.ts           # Hook for route interpolation and animation
│   │   │   └── useSyncTrigger.ts             # Hook for POST /api/dashboard/sync
│   │   ├── services/
│   │   │   ├── api.ts                        # Axios HTTP client configuration
│   │   │   └── endpoints.ts                  # API service functions
│   │   ├── types/
│   │   │   └── api.ts                        # Complete TypeScript interfaces for API contracts
│   │   ├── utils/
│   │   │   ├── formatters.ts                 # Time, date, currency (INR), distance formatters
│   │   │   └── geo.ts                        # Coordinates formatting and client-side calculations
│   │   ├── App.tsx                           # Master dashboard shell with tabbed navigation
│   │   ├── main.tsx                          # React DOM entry point
│   │   └── index.css                         # Tailwind directives & luxury dark theme variables
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── postcss.config.js
├── scripts/
│   ├── run_all.ps1                           # Concurrently launches backend & frontend
│   └── test_all.ps1                          # Runs backend pytest + frontend build checks
├── ORIGINAL_REQUEST.md                       # Canonical requirements
├── PROJECT.md                                # Master project documentation
├── TEST_INFRA.md                             # Test infrastructure & verification specification
└── README.md                                 # Quick start and architecture guide
```

---

## 3. Krone Agriculture India Real-World Domain Dataset Modeling

To satisfy R4 (Resilient Offline Fallback and Synthetic Mock Data Generator), the system incorporates a realistic domain dataset calibrated to **Krone Agriculture India Pvt Ltd** field operations.

### 3.1 Enterprise Tenant & Operating Context
- **Legal Entity**: Krone Agriculture India Pvt Ltd  
- **Corporate HQ**: 404, Qutub Plaza, DLF Phase 1, Gurugram, Haryana, 122002  
- **GSTIN**: `07AAKCK4471E1ZH` | **Service SAC**: `998719` (Agricultural Machinery Repair & Maintenance)  
- **Fieldy Tenant ID**: `4e51f497-b8dd-4036-8d78-60b12a7598b7`  
- **Workspace ID**: `87c32c6a-ec1f-49af-a925-8455d6933ed6` (`krone Gurugram Office`)

### 3.2 Operating Depots & Territory Anchors (GPS Centroids)
The synthetic generator features calibrated geographic territories across North, West, and South India:

| Region / Hub | Base Depot Name | Base Coordinates (Lat, Lng) | Primary Field Service Territories |
| :--- | :--- | :--- | :--- |
| **Punjab** | Ludhiana Central Ag Depot | `30.9010° N, 75.8573° E` | Hoshiarpur, Jalandhar, Bathinda, Sangrur, Patiala |
| **Haryana** | Hisar Regional Service Station | `29.1492° N, 75.7217° E` | Sirsa, Barwala, Fatehabad, Panipat, Karnal |
| **Western UP** | Muzaffarnagar Field Support Center | `29.4727° N, 77.7085° E` | Bareilly, Meerut, Saharanpur, Bijnor (Sugarcane & Forage) |
| **Maharashtra** | Baramati Agro-Service Hub | `18.1517° N, 74.5772° E` | Pune, Solapur, Kolhapur, Ahmednagar (Silage & Dairy) |
| **Madhya Pradesh**| Indore Bio-Power Depot | `22.7196° N, 75.8577° E` | Ujjain, Dewas, Dhar, Khargone (Soybean & Straw) |
| **Gujarat** | Jamnagar Bio-Energy Support Base | `22.4707° N, 70.0577° E` | Rajkot, Kutch, Bhavnagar (RIL Green Energy Complex) |
| **Andhra Pradesh**| Nellore Bio-Gas Service Depot | `14.4426° N, 79.9865° E` | Kakinada, Tirupati, Guntur (Paddy Straw Bio-Mass) |

### 3.3 Machinery Fleet Catalog (Krone Heavy Equipment)
Each machine model in the mock generator reflects real Krone commercial equipment:

1. **Krone BigPack 1290 HDP Large Square Baler**
   - High-density biomass baling (paddy straw, sugarcane bagasse).
   - Serial format: `BP-1290-XXXXXX` (e.g. `BP-1290-984210`, `BP-1290-984215`).
   - Typical customer: Reliance Bio-Energy Plants, Adani Agri Logistics.
2. **Krone Bellima F 130 Round Baler**
   - Fixed chamber round baler for medium farms and silage.
   - Serial format: `BL-130-XXXXXX` (e.g. `BL-130-449120`).
3. **Krone BiG X 700 / 1180 Forage Harvester**
   - Self-propelled forage harvester with high-capacity V-Max drum.
   - Serial format: `BX-700-XXXXXX` (e.g. `BX-700-112045`).
4. **Krone EasyCut F 320 Front Mower Conditioner**
   - Serial format: `EC-320-XXXXXX` (e.g. `EC-320-773190`).
5. **Krone Swadro TC 680 Twin-Rotor Rotary Rake**
   - Serial format: `SW-680-XXXXXX` (e.g. `SW-680-330182`).
6. **Krone Comprima F 155 XC Round Baler**
   - Variable-geometry round baler.
   - Serial format: `CP-155-XXXXXX` (e.g. `CP-155-882310`).

### 3.4 Key B2B Clients & Agricultural Sites
- **Reliance Industries Limited (RIL Bio-Energy Division)**:
  - Facilities: Hoshiarpur Bio-CNG Plant (Punjab), Barwala Bio-Gas Complex (Haryana), Jamnagar Clean Energy Hub (Gujarat), Nellore Bio-Energy Site (AP).
- **Adani Agri Logistics Ltd**:
  - Grain Silos & Biomass Centers at Panipat and Ludhiana.
- **Sugarfed Punjab (Cooperative Sugar Mills)**:
  - Morinda Sugar Mill, Budhewal Cooperative Mill.
- **Baramati Agro Industries Ltd**:
  - Baramati Silage Processing Station (Maharashtra).
- **Malwa Agro Biofuels Ltd**:
  - Bathinda Agricultural Pelletizing Plant (Punjab).

### 3.5 Field Technician Roster
A realistic roster of 12 certified service engineers and technicians:
1. **Gurpreet Singh** — Lead Baler Specialist (Punjab Hub) | ID: `TECH-01`
2. **Vikram Sharma** — Senior Field Service Engineer (Haryana Hub) | ID: `TECH-02`
3. **Rajesh Patel** — Harvester & Diagnostics Specialist (Gujarat Hub) | ID: `TECH-03`
4. **Amit Kumar** — Service Engineer (Western UP Hub) | ID: `TECH-04`
5. **Sachin Jadhav** — Hydraulics & Mechanical Engineer (Maharashtra Hub) | ID: `TECH-05`
6. **Manoj Verma** — Bio-Energy Field Engineer (MP Hub) | ID: `TECH-06`
7. **Suresh Naidu** — Senior Field Service Specialist (AP Hub) | ID: `TECH-07`
8. **Harpreet Brar** — Junior Field Technician (Punjab Hub) | ID: `TECH-08`
9. **Sandeep Yadav** — Electrical Diagnostics Technician (Gurugram HQ) | ID: `TECH-09`
10. **Dinesh Rathod** — Apprentice Service Trainee (Gujarat Hub) | ID: `TECH-10`
11. **Kuldeep Gill** — On Leave / Sick | ID: `TECH-11`
12. **Rohit Deshmukh** — Scheduled Off / Weekly Holiday | ID: `TECH-12`

### 3.6 Commercial Policy & Deputation Rules (RIL AMC Ground Truth)
All calculations in the analytics and invoicing engine align with the legal Krone AMC contract:
- **Technical Manpower Deputation**: Flat ₹5,000.00 / Man-Day (8-hour standard shift).
- **Outstation Boarding & Lodging (DA)**: Flat ₹2,000.00 / Day (for distances >50 km from home depot).
- **Travel Conveyance Rate**: Flat ₹5.00 / KM (when company transport is not provided).
- **GST Rate**: 18% IGST across SAC `998719`.

---

## 4. REST API Contract Definitions

All API endpoints follow strict REST conventions, use JSON for data exchange, and return standardized HTTP status codes (`200 OK`, `201 Created`, `400 Bad Request`, `404 Not Found`, `500 Internal Error`).

### 4.1 `GET /api/dashboard/pulse`

#### Purpose
Provides real-time operational metrics for today, satisfying Requirement R1:
- Technicians on paid jobs, total active, and on leave.
- Today's job pipeline (`SR-26-XXXX`).
- Active machinery under service with serial numbers and site contacts.
- Data synchronization metadata.

#### Query Parameters
- `region`: (Optional) string (e.g., `"Punjab"`, `"Haryana"`, `"All"`)
- `status`: (Optional) string (e.g., `"IN_PROGRESS"`, `"ALL"`)

#### Response Body (200 OK)
```json
{
  "status": "success",
  "data": {
    "summary": {
      "total_technicians": 12,
      "technicians_on_paid_jobs": 8,
      "technicians_available": 2,
      "technicians_on_leave": 2,
      "active_jobs_today": 9,
      "machines_under_service": 8,
      "critical_unresolved_breakdowns": 0,
      "overall_fleet_uptime_pct": 98.4
    },
    "technicians_on_jobs": [
      {
        "technician_id": "TECH-01",
        "name": "Gurpreet Singh",
        "phone": "+91 98140 88210",
        "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100",
        "region": "Punjab",
        "active_job_id": "SR-26-0412",
        "current_status": "IN_PROGRESS",
        "assigned_asset_name": "Krone BigPack 1290 HDP",
        "assigned_asset_serial": "BP-1290-984210",
        "client_company_name": "Reliance Industries Limited (Bio-Energy)",
        "site_location": "Hoshiarpur Bio-CNG Complex, Punjab",
        "started_at": "2026-09-22T08:30:00Z",
        "elapsed_minutes": 210,
        "is_paid_job": true,
        "hourly_billable_rate": 625.0
      },
      {
        "technician_id": "TECH-02",
        "name": "Vikram Sharma",
        "phone": "+91 98120 77412",
        "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100",
        "region": "Haryana",
        "active_job_id": "SR-26-0413",
        "current_status": "START_TRAVEL",
        "assigned_asset_name": "Krone Bellima F130 Baler",
        "assigned_asset_serial": "BL-130-449120",
        "client_company_name": "Reliance Industries Limited",
        "site_location": "Barwala Plant, Hisar, Haryana",
        "started_at": "2026-09-22T09:15:00Z",
        "elapsed_minutes": 165,
        "is_paid_job": true,
        "hourly_billable_rate": 625.0
      }
    ],
    "technicians_on_leave": [
      {
        "technician_id": "TECH-11",
        "name": "Kuldeep Gill",
        "region": "Punjab",
        "leave_type": "Sick Leave",
        "return_date": "2026-09-24"
      },
      {
        "technician_id": "TECH-12",
        "name": "Rohit Deshmukh",
        "region": "Maharashtra",
        "leave_type": "Weekly Off",
        "return_date": "2026-09-23"
      }
    ],
    "today_jobs": [
      {
        "job_id": "SR-26-0412",
        "title": "Baler Knotter & Hydraulic Overhaul",
        "status": "IN_PROGRESS",
        "priority": "HIGH",
        "service_category": "AMC Service",
        "client_company_name": "Reliance Industries Limited",
        "site_contact_person": "Er. Manpreet Dhillon (+91 98765 43210)",
        "assigned_technicians": ["Gurpreet Singh"],
        "scheduled_start": "2026-09-22T09:00:00Z",
        "scheduled_end": "2026-09-22T17:00:00Z"
      }
    ],
    "machines_under_service": [
      {
        "asset_id": "AST-001",
        "asset_name": "Krone BigPack 1290 HDP Large Square Baler",
        "serial_number": "BP-1290-984210",
        "client_company_name": "Reliance Industries Limited (Bio-Energy)",
        "site_contact_person": "Er. Manpreet Dhillon (Site Head, +91 98765 43210)",
        "site_address": "RIL Bio-CNG Facility, Mukerian Road, Hoshiarpur, Punjab 144205",
        "assigned_technician_name": "Gurpreet Singh",
        "service_issue": "500-Hour Scheduled Preventive Maintenance & Knotter Timing",
        "operating_hours": 1420.5,
        "health_status": "OPTIMAL",
        "last_serviced_date": "2026-08-15"
      },
      {
        "asset_id": "AST-002",
        "asset_name": "Krone Bellima F130 Round Baler",
        "serial_number": "BL-130-449120",
        "client_company_name": "Reliance Industries Limited",
        "site_contact_person": "Sunil Kumar (Plant Manager, +91 98123 99881)",
        "site_address": "RIL Bio-Gas Station, Agro Corridor, Barwala, Haryana 125121",
        "assigned_technician_name": "Vikram Sharma",
        "service_issue": "Bale Chamber Roller Bearing Replacement & Net Wrap Calibration",
        "operating_hours": 890.2,
        "health_status": "ATTENTION_REQUIRED",
        "last_serviced_date": "2026-07-28"
      }
    ],
    "sync_meta": {
      "last_synced_at": "2026-09-22T12:35:10Z",
      "sync_source": "fieldy_live",
      "is_fallback_mode": false,
      "tenant_id": "4e51f497-b8dd-4036-8d78-60b12a7598b7",
      "workspace_name": "krone Gurugram Office"
    }
  }
}
```

---

### 4.2 `POST /api/dashboard/sync`

#### Purpose
Triggers an immediate fresh synchronization with the Fieldy FSM cloud API (`https://api.getfieldy.com`), invalidating backend caches and returning updated records.

#### Request Body (Optional)
```json
{
  "force_refresh": true,
  "modules": ["jobs", "technicians", "assets", "telematics"]
}
```

#### Response Body (200 OK)
```json
{
  "status": "success",
  "sync_id": "SYNC-20260922-881920",
  "synced_at": "2026-09-22T12:45:00Z",
  "duration_ms": 342,
  "records_updated": {
    "jobs": 14,
    "technicians": 12,
    "assets": 18,
    "telematics_pings": 482
  },
  "source": "fieldy_live",
  "message": "Fieldy FSM synchronized successfully. Zero stale records."
}
```

---

### 4.3 `GET /api/analytics/productivity`

#### Purpose
Delivers multi-tier technician hours analytics (Working, Travelling, Idle) across Daily, Weekly, and Monthly frames with multi-dimensional filtering, fulfilling Requirement R2.

#### Query Parameters
- `timeframe`: `"daily"` | `"weekly"` | `"monthly"` (Default: `"weekly"`)
- `technician_id`: (Optional) string (e.g., `"TECH-01"`)
- `customer_name`: (Optional) string (e.g., `"Reliance Industries Limited"`)
- `job_status`: (Optional) string (e.g., `"COMPLETED"`, `"IN_PROGRESS"`)
- `job_type`: (Optional) string (e.g., `"AMC Service"`, `"Breakdown"`)
- `start_date`: (Optional) ISO date (`"2026-09-01"`)
- `end_date`: (Optional) ISO date (`"2026-09-22"`)

#### Response Body (200 OK)
```json
{
  "status": "success",
  "data": {
    "timeframe": "weekly",
    "date_range": {
      "start": "2026-09-15",
      "end": "2026-09-22"
    },
    "summary": {
      "total_working_hours": 328.5,
      "total_travelling_hours": 104.2,
      "total_idle_hours": 42.8,
      "total_logged_hours": 475.5,
      "average_utilization_rate_pct": 69.1,
      "total_distance_travelled_km": 4210.8,
      "jobs_completed_count": 38
    },
    "time_series": [
      {
        "date": "2026-09-15",
        "day_of_week": "Tue",
        "working_hours": 46.2,
        "travelling_hours": 14.8,
        "idle_hours": 6.5,
        "distance_km": 580.4
      },
      {
        "date": "2026-09-16",
        "day_of_week": "Wed",
        "working_hours": 48.0,
        "travelling_hours": 16.2,
        "idle_hours": 5.8,
        "distance_km": 640.2
      },
      {
        "date": "2026-09-17",
        "day_of_week": "Thu",
        "working_hours": 44.5,
        "travelling_hours": 15.0,
        "idle_hours": 7.2,
        "distance_km": 595.0
      },
      {
        "date": "2026-09-18",
        "day_of_week": "Fri",
        "working_hours": 50.1,
        "travelling_hours": 13.5,
        "idle_hours": 4.9,
        "distance_km": 540.6
      },
      {
        "date": "2026-09-19",
        "day_of_week": "Sat",
        "working_hours": 47.8,
        "travelling_hours": 15.4,
        "idle_hours": 6.1,
        "distance_km": 612.0
      },
      {
        "date": "2026-09-21",
        "day_of_week": "Mon",
        "working_hours": 49.5,
        "travelling_hours": 14.8,
        "idle_hours": 5.9,
        "distance_km": 625.5
      },
      {
        "date": "2026-09-22",
        "day_of_week": "Tue",
        "working_hours": 42.4,
        "travelling_hours": 14.5,
        "idle_hours": 6.4,
        "distance_km": 617.1
      }
    ],
    "technician_scorecards": [
      {
        "technician_id": "TECH-01",
        "technician_name": "Gurpreet Singh",
        "region": "Punjab",
        "working_hours": 36.5,
        "travelling_hours": 9.8,
        "idle_hours": 3.2,
        "total_hours": 49.5,
        "utilization_rate_pct": 73.7,
        "travel_distance_km": 412.0,
        "jobs_completed": 5,
        "deputation_revenue_inr": 25000.0,
        "status": "EXEMPLARY"
      },
      {
        "technician_id": "TECH-02",
        "technician_name": "Vikram Sharma",
        "region": "Haryana",
        "working_hours": 34.0,
        "travelling_hours": 11.2,
        "idle_hours": 4.5,
        "total_hours": 49.7,
        "utilization_rate_pct": 68.4,
        "travel_distance_km": 490.5,
        "jobs_completed": 4,
        "deputation_revenue_inr": 20000.0,
        "status": "NORMAL"
      }
    ],
    "customer_distribution": [
      {
        "client_company_name": "Reliance Industries Limited",
        "total_hours": 242.0,
        "percentage": 50.9,
        "jobs_count": 22
      },
      {
        "client_company_name": "Adani Agri Logistics Ltd",
        "total_hours": 112.5,
        "percentage": 23.7,
        "jobs_count": 8
      },
      {
        "client_company_name": "Sugarfed Punjab",
        "total_hours": 75.0,
        "percentage": 15.8,
        "jobs_count": 5
      },
      {
        "client_company_name": "Baramati Agro Industries",
        "total_hours": 46.0,
        "percentage": 9.6,
        "jobs_count": 3
      }
    ]
  }
}
```

---

### 4.4 `GET /api/telematics/routes`

#### Purpose
Delivers autonomous GPS journey inspection, 5 km Haversine geofence cluster zones, transit duration vs unauthorized stops, and route playback breadcrumbs, fulfilling Requirement R3.

#### Query Parameters
- `technician_id`: (Required) string (e.g. `"TECH-01"`)
- `date`: (Optional) ISO date string (default: `"2026-09-22"`)
- `trip_id`: (Optional) string (e.g. `"TRIP-20260922-01"`)

#### Response Body (200 OK)
```json
{
  "status": "success",
  "data": {
    "technician": {
      "technician_id": "TECH-01",
      "name": "Gurpreet Singh",
      "phone": "+91 98140 88210",
      "vehicle_number": "PB-10-CZ-4418",
      "vehicle_type": "Krone Mobile Field Support Van (Bolero Camper)"
    },
    "date": "2026-09-22",
    "trip_id": "TRIP-20260922-01",
    "journey_summary": {
      "start_location": {
        "name": "Krone Regional Depot Ludhiana",
        "lat": 30.9010,
        "lng": 75.8573,
        "departure_time": "2026-09-22T07:30:00Z"
      },
      "destination_location": {
        "name": "Reliance Bio-Energy Complex Hoshiarpur",
        "lat": 31.5273,
        "lng": 75.9142,
        "arrival_time": "2026-09-22T10:15:00Z"
      },
      "total_journey_duration_mins": 285,
      "designated_transit_duration_mins": 92,
      "on_site_working_duration_mins": 155,
      "unauthorized_stop_duration_mins": 38,
      "total_distance_km": 84.6,
      "average_speed_kmh": 55.2,
      "max_speed_kmh": 78.4,
      "anomaly_count": 1,
      "route_compliance_pct": 86.7
    },
    "clusters_5km": [
      {
        "cluster_id": "ZONE-01-DEPOT",
        "location_name": "Ludhiana Ag Hub Base (5 km Operations Zone)",
        "zone_type": "BASE_DEPOT",
        "centroid": {
          "lat": 30.9012,
          "lng": 75.8575
        },
        "radius_meters": 5000,
        "ping_count": 18,
        "dwell_time_mins": 35,
        "first_ping_at": "2026-09-22T06:55:00Z",
        "last_ping_at": "2026-09-22T07:30:00Z",
        "is_verified_geofence": true
      },
      {
        "cluster_id": "ZONE-02-UNAUTHORIZED",
        "location_name": "Phagwara Bypass Dhaba & Rest Area (5 km Zone)",
        "zone_type": "UNAUTHORIZED_3RD_PARTY",
        "centroid": {
          "lat": 31.2210,
          "lng": 75.7680
        },
        "radius_meters": 5000,
        "ping_count": 24,
        "dwell_time_mins": 38,
        "first_ping_at": "2026-09-22T08:45:00Z",
        "last_ping_at": "2026-09-22T09:23:00Z",
        "is_verified_geofence": false
      },
      {
        "cluster_id": "ZONE-03-SITE",
        "location_name": "RIL Bio-Energy Facility & Staging Yard (5 km Zone)",
        "zone_type": "CUSTOMER_SITE",
        "centroid": {
          "lat": 31.5268,
          "lng": 75.9140
        },
        "radius_meters": 5000,
        "ping_count": 68,
        "dwell_time_mins": 155,
        "first_ping_at": "2026-09-22T10:15:00Z",
        "last_ping_at": "2026-09-22T12:50:00Z",
        "is_verified_geofence": true
      }
    ],
    "anomalies": [
      {
        "anomaly_id": "ANOM-20260922-01",
        "type": "UNAUTHORIZED_STOP",
        "severity": "MEDIUM",
        "title": "Unscheduled 38-Minute Stop outside 5 km Corridor",
        "description": "Technician halted for 38 minutes at Phagwara Bypass without a scheduled job dispatch or breakdown ticket.",
        "location_name": "Phagwara Bypass Restaurant & Fuel Stop",
        "coordinates": {
          "lat": 31.2210,
          "lng": 75.7680
        },
        "distance_from_designated_route_km": 4.2,
        "duration_mins": 38,
        "started_at": "2026-09-22T08:45:00Z",
        "ended_at": "2026-09-22T09:23:00Z",
        "threshold_mins": 15,
        "action_required": "Dispatcher review or driver acknowledgment"
      }
    ],
    "designated_route_corridor": [
      {"lat": 30.9010, "lng": 75.8573},
      {"lat": 30.9500, "lng": 75.8450},
      {"lat": 31.0500, "lng": 75.8000},
      {"lat": 31.2200, "lng": 75.7700},
      {"lat": 31.3200, "lng": 75.7800},
      {"lat": 31.4500, "lng": 75.8800},
      {"lat": 31.5273, "lng": 75.9142}
    ],
    "gps_breadcrumbs": [
      {
        "index": 0,
        "lat": 30.9010,
        "lng": 75.8573,
        "speed_kmh": 0.0,
        "heading_deg": 0,
        "timestamp": "2026-09-22T07:30:00Z",
        "battery_pct": 98,
        "cluster_id": "ZONE-01-DEPOT",
        "status": "BASE_DEPARTURE"
      },
      {
        "index": 1,
        "lat": 30.9500,
        "lng": 75.8450,
        "speed_kmh": 62.0,
        "heading_deg": 350,
        "timestamp": "2026-09-22T07:45:00Z",
        "battery_pct": 97,
        "cluster_id": null,
        "status": "TRANSIT"
      },
      {
        "index": 2,
        "lat": 31.0500,
        "lng": 75.8000,
        "speed_kmh": 68.5,
        "heading_deg": 345,
        "timestamp": "2026-09-22T08:05:00Z",
        "battery_pct": 95,
        "cluster_id": null,
        "status": "TRANSIT"
      },
      {
        "index": 3,
        "lat": 31.2210,
        "lng": 75.7680,
        "speed_kmh": 0.0,
        "heading_deg": 20,
        "timestamp": "2026-09-22T08:45:00Z",
        "battery_pct": 92,
        "cluster_id": "ZONE-02-UNAUTHORIZED",
        "status": "UNAUTHORIZED_STOP"
      },
      {
        "index": 4,
        "lat": 31.2212,
        "lng": 75.7682,
        "speed_kmh": 0.0,
        "heading_deg": 20,
        "timestamp": "2026-09-22T09:23:00Z",
        "battery_pct": 90,
        "cluster_id": "ZONE-02-UNAUTHORIZED",
        "status": "STOP_END"
      },
      {
        "index": 5,
        "lat": 31.3200,
        "lng": 75.7800,
        "speed_kmh": 64.0,
        "heading_deg": 355,
        "timestamp": "2026-09-22T09:42:00Z",
        "battery_pct": 89,
        "cluster_id": null,
        "status": "TRANSIT"
      },
      {
        "index": 6,
        "lat": 31.4500,
        "lng": 75.8800,
        "speed_kmh": 58.0,
        "heading_deg": 40,
        "timestamp": "2026-09-22T10:02:00Z",
        "battery_pct": 87,
        "cluster_id": null,
        "status": "TRANSIT"
      },
      {
        "index": 7,
        "lat": 31.5273,
        "lng": 75.9142,
        "speed_kmh": 0.0,
        "heading_deg": 30,
        "timestamp": "2026-09-22T10:15:00Z",
        "battery_pct": 85,
        "cluster_id": "ZONE-03-SITE",
        "status": "CUSTOMER_SITE_ARRIVAL"
      }
    ]
  }
}
```

---

### 4.5 `GET /api/technicians`

#### Purpose
Lists all service technicians with current shift status, active job binding, and telemetry metrics.

#### Query Parameters
- `status`: (Optional) `"ALL"` | `"ON_JOB"` | `"AVAILABLE"` | `"LEAVE"`
- `region`: (Optional) `"Punjab"`, `"Haryana"`, `"Gujarat"`, `"Maharashtra"`, etc.
- `search`: (Optional) text query (e.g. `"Gurpreet"`)

#### Response Body (200 OK)
```json
{
  "status": "success",
  "count": 12,
  "data": [
    {
      "technician_id": "TECH-01",
      "name": "Gurpreet Singh",
      "role": "Lead Baler Specialist",
      "region": "Punjab",
      "phone": "+91 98140 88210",
      "email": "gurpreet.s@krone-india.com",
      "status": "ON_JOB",
      "active_job_id": "SR-26-0412",
      "active_job_title": "Baler Knotter & Hydraulic Overhaul",
      "vehicle_number": "PB-10-CZ-4418",
      "deputation_rate_per_day": 5000.0,
      "da_rate_per_day": 2000.0,
      "total_hours_today": 5.5,
      "last_ping_time": "2026-09-22T12:45:00Z",
      "last_coordinates": {"lat": 31.5273, "lng": 75.9142}
    }
  ]
}
```

---

### 4.6 `GET /api/jobs`

#### Purpose
Lists Fieldy jobs with job numbering (`SR-26-XXXX`), status pipeline, customer, asset, and assigned personnel.

#### Query Parameters
- `status`: (Optional) `"IN_PROGRESS"`, `"COMPLETED"`, `"START_TRAVEL"`, `"ASSIGNED"`
- `customer`: (Optional) string
- `technician_id`: (Optional) string
- `service_category`: (Optional) `"AMC Service"`, `"Breakdown Repair"`

#### Response Body (200 OK)
```json
{
  "status": "success",
  "count": 9,
  "data": [
    {
      "job_id": "SR-26-0412",
      "title": "Baler Knotter & Hydraulic Overhaul",
      "status": "IN_PROGRESS",
      "priority": "HIGH",
      "service_category": "AMC Service",
      "client_company_name": "Reliance Industries Limited",
      "asset_name": "Krone BigPack 1290 HDP",
      "asset_serial": "BP-1290-984210",
      "site_address": "RIL Bio-CNG Facility, Mukerian Road, Hoshiarpur, Punjab 144205",
      "site_contact_person": "Er. Manpreet Dhillon (+91 98765 43210)",
      "assigned_technicians": [
        {
          "technician_id": "TECH-01",
          "name": "Gurpreet Singh"
        }
      ],
      "scheduled_start": "2026-09-22T09:00:00Z",
      "scheduled_end": "2026-09-22T17:00:00Z",
      "actual_start": "2026-09-22T10:15:00Z",
      "created_at": "2026-09-21T14:30:00Z"
    }
  ]
}
```

---

## 5. UI/UX Component & Layout Architecture

The user interface follows the **Bento Motion Master** and **UI/UX Pro Max** guidelines:
- **Aesthetic Archetype**: Luxury Heavy-Industry & High-Velocity Sovereign Enterprise.
- **Palette**:
  - Substrate Obsidian: `#0B121E` (Background), `#0F172A` (Surface Cards).
  - Precision Emerald: `#059669` (Primary Brand), `#10B981` (Glow/Active), `#022C22` (Pill Container).
  - Harvest Amber: `#F59E0B` (Anomalies, Cautions, Trip Stops).
  - Slate Muted: `#94A3B8` (Labels, Subtitles, Grid Borders).
  - Pure White / Slate 50: `#F8FAFC` (High-contrast metrics & typography).
- **Typography**:
  - Headings: `Plus Jakarta Sans` or `Inter`, font-extrabold with negative tracking (`tracking-tight`).
  - Numbers & Metrics: `Plus Jakarta Sans` with monospace tabular numerals (`tabular-nums`).
  - Serial Codes & Coordinates: `JetBrains Mono` or `ui-monospace`.

### 5.1 Dashboard Shell Layout & Navigation

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ TOPNAV: [Krone Logo] Field Service & Telematics Hub  |  [Fresh Sync]  |  [Live Pulse]  │
├─────────────┬──────────────────────────────────────────────────────────────────────────┤
│ SIDEBAR     │ MAIN DASHBOARD CANVAS                                                    │
│ ─────────── │ ──────────────────────────────────────────────────────────────────────── │
│ ⚡ Live Pulse│ 1. EXECUTIVE BENTO GRID (4 KPI Cards)                                    │
│ 📊 Analytics│    ┌──────────────────┬──────────────────┬───────────────┬─────────────┐ │
│ 🗺️ Telematics│    │ Technicians Live │ Machinery Active │ Hours Today   │ Route Compr │ │
│ 📋 Jobs     │    │ 8 on Paid Jobs   │ 8 Under Service  │ 69% Work/31%Tr│ 1 Anomaly ⚠️ │ │
│ 🚜 Fleet    │    └──────────────────┴──────────────────┴───────────────┴─────────────┘ │
│ ⚙️ Settings │                                                                          │
│             │ 2. OPERATIONAL TABS & FILTER BAR                                         │
│             │    [ Daily | Weekly | Monthly ]  [ Tech Dropdown ] [ Customer ] [ Filter]│
│             │                                                                          │
│             │ 3. ACTIVE TAB VIEW:                                                      │
│             │    TAB A: Live Pulse & Active Machinery Table                            │
│             │    TAB B: Productivity Analytics Engine (Recharts Stacked Bar + Score)   │
│             │    TAB C: Autonomous Route Inspector (Leaflet Map + 5km Clusters + Scrub)│
│             │                                                                          │
│             │ 4. PERSISTENT ANOMALY DRAWER (Bottom Right Pill / Slide-out Panel)        │
└─────────────┴──────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Key UI Components & Interactions

#### Component 1: Executive KPI Bento Cards (`ExecutiveBentoGrid.tsx`)
- **Card 1: Technicians on Paid Jobs**
  - Live pulsing green beacon (`animate-ping`).
  - Metric: `8 / 12` active.
  - Micro-badge: `+2 available, 2 on leave`.
  - Sparkline of hourly workforce deployment.
- **Card 2: Machinery Under Service**
  - Icon: Heavy Baler / Gear (`Wrench` / `Cpu`).
  - Metric: `8 Units` under maintenance.
  - Sub-badges: `6 Large Square Balers (1290 HDP)`, `2 Round Balers`.
  - Zero critical breakdown alerts indicator.
- **Card 3: Today's Hours Split**
  - Horizontal stacked progress bar: Working (68% Emerald), Travelling (22% Cyan), Idle (10% Amber).
  - Metric: `42.4h Total Work` logged today across fleet.
- **Card 4: Fleet Telematics & Route Compliance**
  - Metric: `86.7% Compliance`.
  - Warning badge: `1 Unauthorized Stop Flagged (>15 min)`.
  - Direct quick-link to Route Inspector view.

#### Component 2: Live Operational Pulse Board & Machinery Table (`LivePulseBoard.tsx`)
- High-density table featuring:
  - **Asset Name & Model**: Krone baler badge with unique equipment glyph.
  - **Serial Number**: Monospace copyable pill (`BP-1290-984210`).
  - **Client Company & Site**: Company name + Plant location badge.
  - **Site Contact**: Person name with direct WhatsApp / Phone action button.
  - **Assigned Technician**: Avatar pill + status indicator (`IN_PROGRESS`).
  - **Service Issue**: Description of scheduled maintenance or repair.
  - **Actions**: "View Route Telematics" and "Fieldy Job Details".
- Header "Fresh Sync" control:
  - Button with rotating sync icon during fetch.
  - Relative timestamp text: `"Last synced 14 seconds ago"`.
  - Tooltip displaying Fieldy cloud tenant details.

#### Component 3: Multi-Dimensional Filter Bar (`FilterBar.tsx`)
- **Timeframe Switcher**: Segmented toggle pills for `[ Daily | Weekly | Monthly ]` with spring animation indicator.
- **Technician Search & Dropdown**: Fuzzy search across technician names and regional depots.
- **Customer Company Filter**: Multi-select dropdown (Reliance Industries, Adani, Sugarfed, Baramati Agro).
- **Job Status & Priority Filters**: Quick pills (`In Progress`, `Start Travel`, `Completed`).
- **Reactive state**: Updates all charts and tables in real-time with zero full-page reload.

#### Component 4: Technician Productivity Analytics Engine (`ProductivityDashboard.tsx`)
- **Master Recharts Stacked Area / Bar Chart**:
  - X-Axis: Days of week (Mon, Tue, Wed, Thu, Fri, Sat) or Months.
  - Y-Axis: Hours logged.
  - Stacks: Working Hours (`#059669`), Travelling Hours (`#0284C7`), Idle Hours (`#F59E0B`).
  - Interactive hover tooltip showing exact minutes, distance in KM, and daily utilization percentage.
- **Drill-Down Technician Scorecard Table**:
  - Detailed breakdown of each technician's hours, billable revenue generated (at ₹625/hr / ₹5,000/day), travel allowance, and performance rating badge.

#### Component 5: Route Inspector & 5 km Geofence Studio (`RouteInspectorStudio.tsx`)
- **Leaflet Interactive Map Canvas**:
  - Dark CartoDB tile layer (`https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png`).
  - **5 km Geofence Circles**: Semi-transparent green circles (`radius: 5000m`) around base depot and customer plant site, with dashed perimeter.
  - **Designated Route Polyline**: Solid emerald polyline along the verified transit corridor.
  - **Unauthorized Detour Polyline**: Dashed amber polyline indicating off-corridor travel.
  - **Stop Duration Badges**: Custom HTML DivIcons pinned at stop centroids showing dwell time (e.g. `[ ☕ 38 min ]`, `[ 🏭 155 min ]`).
  - **Moving Vehicle Marker**: Bolero camper icon rotating according to telemetry heading degree.
- **Playback Control Bar**:
  - Play / Pause toggle with spacebar keyboard shortcut.
  - Speed multiplier pills: `[ 1x | 2x | 5x | 10x ]`.
  - Scrubbing slider (0% to 100%) showing exact time of day (`08:45 AM`), current vehicle speed (`64 km/h`), and battery level (`92%`).
- **Journey Summary Breakdown Card**:
  - Side panel displaying total journey minutes, transit duration, on-site working duration, and unauthorized stop duration.

#### Component 6: Anomaly Alert Panel & Drawer (`AnomalyAlertPanel.tsx`)
- Slide-over alert drawer or collapsible bottom banner.
- Lists all detected anomalies:
  - Severity badge: `MEDIUM` or `HIGH`.
  - Details: Location name, coordinates, stop duration vs 15-minute threshold, and distance deviation from route corridor.
  - Action buttons: "Inspect on Map" (auto-pans and zooms to anomaly coordinates) and "Acknowledge Stop".

---

## 6. Build, Run, and Test Setup Requirements

To guarantee **100% clean automated execution**, both backend and frontend must follow standardized setup, execution, and verification procedures.

### 6.1 System Prerequisites
- **Python**: Version 3.10, 3.11, or 3.12 with `pip`.
- **Node.js**: Version 18.x or 20.x with `npm`.
- **PowerShell**: Windows PowerShell 5.1+ or PowerShell 7+.

### 6.2 Backend Setup & Dependencies
Create `backend/requirements.txt`:
```txt
fastapi>=0.110.0
uvicorn[standard]>=0.28.0
pydantic>=2.6.0
requests>=2.31.0
httpx>=0.27.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

Installation command:
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Launch backend server:
```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Swagger UI will be accessible at `http://127.0.0.1:8000/docs`.

### 6.3 Frontend Setup & Dependencies
Create `frontend/package.json` with dependencies:
```json
{
  "name": "krone-fieldy-enterprise-dashboard",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "lucide-react": "^0.359.0",
    "leaflet": "^1.9.4",
    "react-leaflet": "^4.2.1",
    "recharts": "^2.12.3",
    "axios": "^1.6.8",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.2"
  },
  "devDependencies": {
    "@types/react": "^18.2.66",
    "@types/react-dom": "^18.2.22",
    "@types/leaflet": "^1.9.8",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.2.2",
    "vite": "^5.1.6",
    "tailwindcss": "^3.4.1",
    "postcss": "^8.4.35",
    "autoprefixer": "^10.4.18"
  }
}
```

Installation command:
```powershell
cd frontend
npm install
```

Launch frontend dev server:
```powershell
npm run dev
```
Dashboard UI will be accessible at `http://localhost:5173`.

### 6.4 Automated Test Suite Setup (Pytest)

The automated test suite verifies all critical algorithms and API contracts:

1. **`test_clustering.py`**:
   - Haversine distance calculation correctness against known geographic points.
   - 5 km cluster merging: verifies that GPS pings within 4.9 km merge into a single centroid.
   - Verifies that a GPS ping 5.2 km away forms a distinct second cluster.
   - Jitter dampening: micro-moves < 50m with speed < 1.5 km/h do not displace the centroid.
2. **`test_route_inspector.py`**:
   - Identification of starting base depot and destination customer plant.
   - Accurate separation of designated route transit minutes vs unauthorized stop minutes.
   - Flagging of stops > 15 minutes outside the 5 km buffer of known waypoints.
3. **`test_analytics_engine.py`**:
   - Verification that `Working Hours + Travelling Hours + Idle Hours == Total Logged Hours`.
   - Aggregation across Daily, Weekly, and Monthly buckets.
   - Verification of utilization percentage formula: `(Working Hours / Total Hours) * 100`.
4. **`test_api_endpoints.py`**:
   - HTTP `GET /api/dashboard/pulse` returns 200 and passes all Pydantic schema assertions.
   - HTTP `POST /api/dashboard/sync` returns 200 and updates `last_synced_at`.
   - HTTP `GET /api/analytics/productivity?timeframe=daily` returns daily time series.
   - HTTP `GET /api/telematics/routes?technician_id=TECH-01` returns valid breadcrumbs and 5 km clusters.

Execution command:
```powershell
cd backend
pytest tests/ -v
```

### 6.5 Single-Command Launch & Verification Scripts

#### `scripts/run_all.ps1`:
```powershell
Write-Host "[KRONE FSM] Starting Backend API Server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\.venv\Scripts\Activate.ps1; python -m uvicorn app.main:app --port 8000 --reload"

Write-Host "[KRONE FSM] Starting Frontend Dev Server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host "[KRONE FSM] Both services running. Frontend: http://localhost:5173 | Backend: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
```

#### `scripts/test_all.ps1`:
```powershell
Write-Host "[KRONE FSM] Running Backend Pytest Suite..." -ForegroundColor Yellow
cd backend
python -m pytest tests/ -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Backend tests failed!" -ForegroundColor Red
    exit 1
}

Write-Host "[KRONE FSM] Running Frontend Typecheck & Build..." -ForegroundColor Yellow
cd ..\frontend
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Frontend build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "[SUCCESS] All tests and build checks passed with zero errors!" -ForegroundColor Green
```

---

## 7. Synthesis & Alignment with Peer Explorers

- **Alignment with `survey_spec_miner_1`**:
  - The API contract models directly adopt the Fieldy FSM schema extracted from `fieldy-management`: Tenant ID `4e51f497-b8dd-4036-8d78-60b12a7598b7`, workspace `87c32c6a-ec1f-49af-a925-8455d6933ed6`, job numbering `SR-26-XXXX`, and RIL commercial terms (₹5,000/day manpower, ₹2,000/day DA, ₹5/km travel, SAC `998719`).
- **Alignment with `survey_explorer_2`**:
  - The route telemetry and 5 km cluster structures in `/api/telematics/routes` exactly reflect Explorer 2's Haversine formulation, 5 km radius centroid merger, transit vs unauthorized stop separation, and 15-minute anomaly threshold.
- **Hand-off to Implementation Track (M1-M5)**:
  - This specification provides the complete blueprint for M1 (FastAPI backend + Mock generator), M2 (Pulse board), M3 (Productivity analytics), M4 (Route inspector & Leaflet map), and M5 (Enterprise UI/UX polish).

---

## 8. Conclusion

The architectural investigation confirms that a **FastAPI (Python) + Vite React (TypeScript) + Tailwind CSS + Leaflet + Recharts** stack delivers the optimal combination of mathematical robustness, rapid development velocity, lightweight local execution, and high-end visual fidelity. The calibrated Krone Agriculture India dataset grounds all screens and endpoints in authentic domain operations, enabling seamless end-to-end implementation and automated test verification.
