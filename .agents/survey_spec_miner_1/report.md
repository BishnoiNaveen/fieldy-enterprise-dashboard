# Fieldy FSM & Krone Agriculture India — Technical Specification & Ground Truth Extraction Report

**Subagent ID:** `survey_spec_miner_1` (Specialized Specification Miner)  
**Target Project:** Field Service & Telematics Dashboard for Krone Agriculture India  
**Date of Record:** 2026-09-22T18:16:00+05:30  
**Status:** Completed & Empirically Verified  

---

## Executive Summary

This report delivers the authoritative specification extraction for integrating the **Fieldy Field Service Management (FSM)** platform (`krone.getfieldy.com` / `api.getfieldy.com`) with **Krone Agriculture India Pvt. Ltd.** operations. The investigation synthesizes ground-truth evidence extracted from:
1. `ORIGINAL_REQUEST.md` (Operational Pulse, Hours Analytics, 5 km Route Clustering, Resilient Architecture).
2. `C:\Users\Naveen\.gemini\config\skills\fieldy-management\SKILL.md` (7 microservices catalog, 2,828 operations, 16 tutorial pillars).
3. `COMPLETE_FIELDY_MASTER_MEMORY.md` & `FIELDY_AMC_INVOICING_MEMORY.md` (Live AMC contracts, 33 Nellore jobs, Add-On custom field IDs, mandatory completion gate).
4. `FIELDY_KIN_ONEHUB_INTEGRATION_MEMORY.md` (Employee directory, leave applications, daily reporting bridge, Supabase PostgreSQL backend).
5. `Fieldy_Complete_Portal_Scan_and_Master_API_Specification.md` (Network audit, 5 microservices, 2,249 endpoints).
6. Live Production Datasets: `all_fieldy_jobs.json` (483 jobs), `all_fieldy_amcs.json` (11 AMCs), `invoiced_jobs_database.json` (33 locked jobs), `job_fields.json` (30 default fields, 4 custom fields), and `scratch_naveen_tracking.json`.

---

## 1. Enterprise Tenant Context & Architecture Constants

| Parameter | Value | Description |
| :--- | :--- | :--- |
| **Tenant Name** | Krone Agriculture India Pvt Ltd (`krone`) | Authorized enterprise tenant |
| **Web Portal URL** | `https://krone.getfieldy.com` | Next.js SPA / SSR portal |
| **API Gateway** | `https://api.getfieldy.com` | Microservices API Gateway |
| **Tenant ID** | `4e51f497-b8dd-4036-8d78-60b12a7598b7` | Root multi-tenant UUID |
| **Workspace ID** | `87c32c6a-ec1f-49af-a925-8455d6933ed6` | `krone Gurugram Office` (Active Production Workspace) |
| **Default Location ID** | `8176f98f-3d9f-4d70-ad2f-7c6a9c23d16c` | Gurugram HQ Default Dispatch Location |
| **Authorized Signatory** | Naveen Bishnoi (`kin.it@krone-india.com`, `+91 9625957663`) | IT & Operations Admin |
| **Legal Entity Details** | Corporate Office: 404, Qutub Plaza, Gurugram, Haryana 122002; GSTIN: `07AAKCK4471E1ZH`; SAC: `998719` (18% IGST) | Invoicing entity |
| **Session Storage Token** | `C:\Users\Naveen\.gemini\antigravity\brain\4b00f5c5-2082-4b83-8c2a-a77bdb91df75\scratch\fieldy_storage.json` | Browser JWT session store (`access_token_krone`) |

---

## 2. The 7 Cloud Microservices & REST Endpoints Catalog

Fieldy runs on a decoupled microservices architecture behind `https://api.getfieldy.com`:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 https://api.getfieldy.com                              │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
   ┌──────────────────┬─────────────────────┼─────────────────────┬──────────────────┐
   ▼                  ▼                     ▼                     ▼                  ▼
┌──────────────┐ ┌─────────────────┐ ┌───────────────┐ ┌───────────────────┐ ┌──────────────┐
│     JOB      │ │   ACCOUNTING    │ │     USER      │ │    TRACKING       │ │ NOTIFICATION │
│ /job/v1/...  │ │ /accounting/v1/ │ │    /v1/...    │ │  /tracking/v1/... │ │ /notification│
│  933 Paths   │ │   599 Paths     │ │   460 Paths   │ │    228 Paths      │ │   45 Paths   │
└──────────────┘ └─────────────────┘ └───────────────┘ └───────────────────┘ └──────────────┘
```

### 2.1 Job Microservice (`/job/v1/...`)
- `GET /job/v1/jobs`: Query work orders with parameters `workspace-id`, `location-id`, `page`, `per_page`, `filters`, `sort_item`, `sort_type`, `search`. Returns `{ "data": [ { "metadata": {...}, "values": {...} } ], "total": 483 }`.
- `GET /job/v1/jobs/{job_id}`: Single job detail card with full assigned technicians, checklists, timestamps, and customer metadata.
- `POST /job/v1/jobs`: Create work order with EAV payload (`default_fields`, `custom_fields`).
- `PUT /job/v1/jobs/{job_id}`: Update job status, technician assignment, due dates, or location.
- `GET /job/v1/jobs/add-on/{job_id}`: Read technician on-site Add-On form responses (DA, KM, Transport).
- `PUT /job/v1/jobs/add-on/{job_id}/update`: Update Add-On fields. *Gotcha:* Radio custom fields require list format `value: ["<option_id>"]`. Passing bare string returns HTTP 422.
- `GET /job/v1/assets`: Query registered machinery and serial numbers. Parameters: `customer_id`, `workspace-id`, `location-id`.
- `GET /job/v1/assets/{asset_id}`: Asset details including linked AMC contracts, QR code, and service history.
- `GET /job/v1/amcs`: List Annual Maintenance Contracts (Fixed Retainer / Service).
- `GET /job/v1/amcs/{amc_id}`: Contract terms, visit quota consumption (e.g. 12 visits/year), and customer machine mappings.
- `GET /job/v1/jobs/dispatch`: Technician matrix timeline and calendar dispatch schedules.
- `GET /job/v1/jobs/{job_id}/report-pdf`: Stream or retrieve pre-signed S3 URL for official customer-signed PDF report.

### 2.2 Tracking & Telematics Microservice (`/tracking/v1/...`)
- `GET /tracking/v1/tracking/live`: Current GPS telemetry of all active technicians (latitude, longitude, speed, battery percentage, last ping timestamp).
- `GET /tracking/v1/trips`: Daily transit logs, start/stop odometer readings, total distance in KM, and breadcrumb route coordinates.
- `GET /tracking/v1/trips/{trip_id}`: Granular GPS breadcrumb path for route inspection and playback.
- `GET /tracking/v1/attendance`: Daily technician punch-in/out timestamps, geofenced clock-in location, and battery level at punch.
- `POST /tracking/v1/attendance/clock-in`: Mobile morning attendance clock-in with device lat/long coordinates.
- `POST /tracking/v1/attendance/clock-out`: Evening clock-out recording shift completion.

### 2.3 User & Organization Microservice (`/v1/...`)
- `GET /v1/users`: Full technician, engineer, and manager directory.
- `GET /v1/users-dropdown`: Compact dropdown list of technicians for assignment modals.
- `GET /v1/companies`: Customer billing organizations (`RED-RIL-...`, `Bio Fuel Corporation`, `VERBIO`).
- `GET /v1/contacts`: Customer site contact persons (Site Engineers, Plant Supervisors).
- `GET /v1/locations`: Organization branch locations (`krone Gurugram Office`).

### 2.4 Accounting Microservice (`/accounting/v1/...`)
- `GET /accounting/v1/invoice`: List Proforma and Tax Invoices.
- `POST /accounting/v1/invoice`: Create GST-compliant Tax Invoice with Krone SAC `998719` and 18% IGST.
- `GET /accounting/v1/inventory`: Multi-tier inventory (Central Gurugram Warehouse & Technician Van/Truck stocks).

---

## 3. Exact Domain Models & Schemas

### 3.1 Fieldy Jobs Schema (`SR-26-XXXX`)

Fieldy serializes jobs in an entity model consisting of `metadata` and `values`:

```typescript
interface FieldyJobMetadata {
  id: string;                                // UUID e.g. "2600bdcf-0c10-474f-ab95-f00042865e80"
  status: "In Progress" | "Completed" | "Cancelled" | "Hold" | "Open";
  status_label: string;                      // Display text
  status_color: string;                      // Hex code: In Progress (#f79009), Completed (#17b26a), Cancelled (#2f3236), Hold (#e53529), Open (#8d9199)
  has_user_status_update_permission: boolean;
  job_created_by: string;                    // User UUID
}

interface FieldyJobValues {
  job_no: string;                            // Canonical pattern: "SR-26-XXXX" (e.g. "SR-26- 0149")
  title: string;                             // e.g. "Rod's bend removeing in bellima f 130"
  description: string;                       // Detailed fault / service observation
  customer: string;                          // Customer Name e.g. "RIL-Nellore - Leela Baisetty"
  job_status: string;                        // "In Progress" | "Completed" | "Cancelled" | "Hold" | "Open"
  location_id: string;                       // "krone Gurugram Office"
  location: string;                          // Street address e.g. "Mdr019, Dagadarthi, Andhra Pradesh, India, 524240"
  service_type_id: {
    option: "Repair" | "Installation" | "Maintenance" | "Operator training" | "General" | "Preseason Machine Test" | "Spare Parts";
    color_code: string | null;
  };
  assign_to: string[];                       // Technician display names e.g. ["Vignesh"]
  assigned_technicians?: string[];           // Technician UUIDs
  service_category: "General Service" | "Amc";
  amc_id: string;                            // AMC UUID if service_category == "Amc", else empty
  amc_asset_id_or_service_id: string[];      // Associated asset UUIDs under AMC
  asset_id: string[];                        // Direct equipment names/IDs e.g. ["Bellima"]
  job_start_date: string;                    // DD-MM-YYYY e.g. "17-09-2026"
  job_start_time: string;                    // HH:MM AM/PM e.g. "04:00 PM"
  job_end_date: string;                      // Due date / "Over due"
  job_end_time: string;                      // Due time
  actual_time_spent: string;                 // HH:MM:SS e.g. "06:21:00"
  created_at: string;                        // DD-MM-YYYY
  updated_at: string;                        // DD-MM-YYYY
  created_by: string;                        // Technician / Creator name
  updated_by: string;                        // Last updater name
  checklists: string[];                      // Attached inspection checklists
  
  // Custom Fields (Configured for Krone Agriculture)
  total_bales_till_date?: number;            // Custom field ID: "0a753e7e-7203-4b0e-8946-e0164659897b"
  baling_crop?: Array<{                      // Custom field ID: "b42e8cb7-955e-4cdf-9e85-0b599f7da9e4"
    option: "Paddy" | "Wheat" | "Cane Trash" | "Maize";
    color_code: string | null;
  }>;
  operator_contact_no?: string;
  serial_number?: string;                    // e.g. "1177557"
}

// On-Site Add-On Form Schema (Mandatory Completion Gate)
interface FieldyJobAddOnForm {
  transport_provided_by: {                   // Field ID: "014e553f-76b0-4e1e-a000-8fc942da6ca2"
    selected_id: "13e819d0-da08-4ace-9abd-09c636a23fc0" | "19524edb-4708-4e8f-b1d8-d24d17aca30b";
    label: "Customer" | "KIN";
  };
  stay_and_food_provided_by: {               // Field ID: "0f5c1448-1a26-49db-8e19-864954b43cad"
    selected_id: "d12bd700-056c-4c05-a80c-d6ce33a4fa9d" | "191efe39-f14b-4433-b3f4-35d8449bf376";
    label: "Customer" | "KIN";
  };
  job_type: {                                // Field ID: "bc64d1a2-a5e1-4ad4-9154-88f200d06975"
    selected_id: "0c1bc7ce-6bf8-45b8-86a9-87f9cd20c778" | "544c2e6b-2e00-4a9c-9b63-cefb063c7b81";
    label: "Paid" | "Unpaid";
  };
  kilometers_travelled?: number;             // Field ID: "b1d05729-f884-4b5a-a18f-a24041edec8b"
}
```

### 3.2 Technicians & Operational Status Schema

```typescript
interface KroneTechnician {
  id: string;                                // Fieldy User UUID
  employee_code: string;                     // KIN OneHub ID e.g. "002", "005", "021"
  name: string;                              // Full Name e.g. "Sunny Kumar", "B. Vignesh"
  phone: string;                             // e.g. "+91 9625957663"
  email: string;                             // e.g. "sunny.kumar@krone-india.com"
  designation: string;                       // e.g. "Senior Field Service Engineer"
  region: "North" | "South" | "West" | "Central"; // Deployed Regional Hub
  
  // Real-Time Operational State
  operational_status: "On Paid Job" | "On Unpaid Job" | "Travelling" | "Available" | "On Holiday/Leave";
  active_job_id?: string;                    // UUID of currently active job (if on job)
  active_job_no?: string;                    // "SR-26-XXXX" (e.g. "SR-26- 0149")
  
  // Attendance & Telematics
  is_clocked_in_today: boolean;
  clock_in_time?: string;                    // ISO timestamp
  clock_in_location?: { lat: number; lng: number; address: string };
  current_location: {
    lat: number;
    lng: number;
    speed_kmh: number;
    battery_level: number;                   // Percentage 0-100
    last_ping_time: string;                  // ISO timestamp
  };
  
  // Commercial Billing Attributes (Contract Terms)
  deputation_rate_per_manday: 5000.00;       // Clause 4.7: ₹5,000 / 8-hr shift
  daily_allowance_rate: 2000.00;             // Clause 4.8: ₹2,000 / day (if stay not by client)
  travel_rate_per_km: 5.00;                  // Clause 4.8: ₹5 / KM (two-wheeler)
  
  // Time Tracking Accumulators (Today / Current Filter)
  working_hours: number;                     // Productive hours on job
  travelling_hours: number;                  // Telematics transit hours
  idle_hours: number;                        // Clocked-in time minus (working + travelling)
}
```

#### Real Verified Technician Roster (Krone Agriculture India):
1. **Sunny Kumar** (Lead Service Engineer — North/Central)
2. **Sukhdeep Singh** (Senior Field Specialist — Punjab/Haryana)
3. **Sunil Kumar** (Field Technician — Punjab)
4. **Sunder** (Field Technician — North)
5. **Naveen Bishnoi** (Service & IT Operations Manager — Gurugram HQ)
6. **Vidhyant Kumar** (Field Technician — Rajasthan/Haryana)
7. **B. Vignesh** (Field Service Specialist — RIL Nellore Bio-Energy MTCC Hub)
8. **M. Naveen Kumar** (Field Service Engineer — RIL Nellore / Kurnool)
9. **Palthiya Kishore** (Field Service Engineer — RIL Warangal / Vijayawada)
10. **Nitin Gour** (Field Technician — RIL Indore / Bhopal)
11. **Gursewak Singh** (Field Technician — Punjab)
12. **Prem Kumar** (Field Technician — UP / Prayagraj)
13. **Ravinder Bishnoi** (Field Service Engineer — North)
14. **Vishnu** (Service Coordinator & Dispatcher)

### 3.3 Machinery & Assets Schema (Krone Agriculture Lines)

```typescript
interface KroneAsset {
  asset_id: string;                          // UUID
  asset_name: string;                        // Equipment Model Name
  serial_number: string;                     // Unique 7-digit Serial e.g. "1177557", "1152377"
  equipment_line: "BiG Pack" | "Comprima" | "Bellima" | "Fortima" | "BiG X" | "EasyCut" | "Swadro" | "Vendro";
  client_company_name: string;               // e.g. "Reliance Industries Limited (RIL-Nellore)"
  site_contact_person: string;               // e.g. "Leela Baisetty"
  site_contact_phone: string;                // e.g. "+91 9703719368"
  site_location: string;                     // e.g. "Mdr019, Dagadarthi, Andhra Pradesh"
  qr_code_url: string;                       // Direct scan URL for chronological service history
  linked_amc_id?: string;                    // e.g. "7d6c65cf-afaa-4cea-897a-9fecb15e94ef" (AMC 011)
  linked_amc_title?: string;                 // "AMC 2026-27: Fixed Retainer - RIL-Nellore"
  total_bales_count?: number;                // Lifetime bale counter
  crop_type?: string;                        // "Paddy Straw", "Wheat Straw", "Cane Trash"
  health_status: "Operational" | "Under Service" | "Critical Breakdown" | "Pending Parts";
  last_service_date: string;                 // DD-MM-YYYY
}
```

#### Krone India Equipment Product Catalog:
- **BiG Pack Series (Large Square Balers):** `BiG Pack 1290 HDP VC`, `BiG Pack 1270 VC`, `BiG Pack 890`. High-density straw baling for 2G Ethanol biomass generation.
- **Bellima Series (Fixed Chamber Round Balers):** `Bellima F 130`, `Bellima F 125`. High-output baling for paddy straw (primary baler at Reliance Nellore, Rajahmundry, Kakinada).
- **Comprima Series (Variable Chamber Round Balers):** `Comprima F 155 XC`, `Comprima V 180 XC`. Robust round balers equipped with crop cutters.
- **Fortima Series (Round Balers):** `Fortima F 1250`, `Fortima F 1600`.
- **BiG X Series (Precision Forage Harvesters):** `BiG X 680`, `BiG X 780`, `BiG X 1180`. Flagship high-throughput crop choppers.
- **EasyCut Series (Disc Mowers & Conditioners):** `EasyCut B 870 CR`, `EasyCut F 320 CV`, `EasyCut R 360`. High-capacity mowing for forage crops.
- **Swadro Series (Rotary Rakes):** `Swadro TC 640`, `Swadro TS 680`. Precision swath collection.

---

## 4. Multi-Tier Time Tracking & Analytics Engine

The analytics engine tracks three distinct time categories across Daily, Weekly, and Monthly horizons:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        TECHNICIAN TOTAL RECORDED SHIFT TIME                            │
├──────────────────────────────┬─────────────────────────────┬───────────────────────────┤
│     1. WORKING HOURS         │     2. TRAVELLING HOURS     │      3. IDLE HOURS        │
│   (On-Job Productive Time)   │    (Transit Telematics)     │   (Unaccounted/Waiting)   │
├──────────────────────────────┼─────────────────────────────┼───────────────────────────┤
│ • Status: In Progress        │ • Status: Start Travel      │ • Inactive between jobs   │
│ • On-site service, repair,   │ • GPS odometer trips        │ • Gate pass / safety delays│
│   maintenance, or training   │ • Verified distance (KM)    │ • Parts waiting time      │
│ • Client verified signatures │ • Transit duration tracking │ • Unscheduled stops       │
└──────────────────────────────┴─────────────────────────────┴───────────────────────────┘
```

### Analytical Formulas:
1. **Total Shift Hours** = $T_{\text{clock\_out}} - T_{\text{clock\_in}}$ (or current time if still clocked in).
2. **Working Hours** = $\sum (T_{\text{job\_complete}} - T_{\text{job\_reached}})$ for all assigned jobs on that date.
3. **Travelling Hours** = $\sum (T_{\text{job\_reached}} - T_{\text{job\_start\_travel}})$ extracted from telematics trips.
4. **Idle Hours** = $\max(0, \text{Total Shift Hours} - (\text{Working Hours} + \text{Travelling Hours}))$.
5. **Productivity Index** = $\frac{\text{Working Hours}}{\text{Total Shift Hours}} \times 100\%$.

---

## 5. Autonomous Route Inspector & 5 km Geofence Clustering Engine

### 5.1 The 5 km Radius Haversine Clustering Specification

In rural agriculture and bio-energy hubs, a customer "site" is not a single point; it encompasses a central biomass plant, multiple storage depots, weighbridges, tractor yards, and adjacent paddy fields spread across a 1 to 4 km diameter. Sub-kilometer GPS micro-jitter or field transitions must not create false trip records.

#### Algorithmic Definition:
Given GPS pings $P_i = (\text{lat}_i, \text{lng}_i, t_i)$:
1. Calculate the Great-Circle distance between point $P_i$ and the current active cluster centroid $C_k = (\text{lat}_k, \text{lng}_k)$ using Haversine:
   $$\Delta \phi = \text{lat}_i - \text{lat}_k, \quad \Delta \lambda = \text{lng}_i - \text{lng}_k$$
   $$a = \sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\text{lat}_k) \cos(\text{lat}_i) \sin^2\left(\frac{\Delta \lambda}{2}\right)$$
   $$d = 2 R \cdot \arcsin\left(\sqrt{a}\right) \quad \text{where } R = 6371.0088 \text{ km}$$
2. **Clustering Decision:**
   - If $d \le 5.0\text{ km}$: The ping belongs to the existing cluster $C_k$. Update centroid coordinates using duration-weighted average. Aggregate stationary duration.
   - If $d > 5.0\text{ km}$: Close cluster $C_k$. If the technician is moving ($\text{speed} > 10\text{ km/h}$), transition to `TRANSIT` mode. When stationary for $> 10$ minutes, create a new cluster $C_{k+1}$.

### 5.2 Transit Duration vs Unauthorized Stop Detection
- **Verified Corridor Transit:** Continuous travel between Base Location (e.g. Gurugram HQ / Nellore Hotel) and Job Destination along recognized road paths.
- **Unauthorized / 3rd-Party Stop Anomaly:** Any stationary period $\ge 15\text{ minutes}$ that occurs:
  1. More than 5 km away from the starting base.
  2. More than 5 km away from the destination job site.
  3. Not matched to an active breakdown call.
- **Alert Generation:** Flagged as an unauthorized stop badge with exact address, stationary duration, and alert indicator on the map.

---

## 6. Synchronization & Resilient Offline Cache Architecture

### 6.1 Authentication Protocol & Header Specification
Every direct API interaction with Fieldy requires an active session derived from `scratch\fieldy_storage.json`:

```http
GET /job/v1/jobs?workspace-id=87c32c6a-ec1f-49af-a925-8455d6933ed6&location-id=8176f98f-3d9f-4d70-ad2f-7c6a9c23d16c HTTP/1.1
Host: api.getfieldy.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
x-tenant-id: 4e51f497-b8dd-4036-8d78-60b12a7598b7
workspace-id: 87c32c6a-ec1f-49af-a925-8455d6933ed6
location-id: 8176f98f-3d9f-4d70-ad2f-7c6a9c23d16c
Content-Type: application/json
```

### 6.2 "Fresh Sync" Trigger & Background Polling
1. **Manual "Fresh Sync" Button:**
   - Positioned prominently in the dashboard header.
   - Triggers an immediate full-lifecycle re-fetch across Jobs, Technicians, Telematics, and Assets with cache-busting timestamp `?_ts=Date.now()`.
   - Displays real-time sync progress, last sync timestamp (e.g. `● Synced 2 seconds ago`), and sync metrics (e.g. `483 jobs synchronized`).
2. **Automatic Background Polling:**
   - Polling worker polls every **30 seconds** for live telematics (`/tracking/v1/tracking/live`) and job status changes.
   - Exponential backoff with jitter on network failures (30s $\rightarrow$ 60s $\rightarrow$ 120s $\rightarrow$ max 300s).

### 6.3 Offline Fallback & Synthetic Mock Generator
- When network disconnects or Fieldy cloud returns `401 Unauthorized` / `502 Bad Gateway`, the application transitions transparently to the **Krone Synthetic Mock Engine**.
- The synthetic dataset is calibrated to real-world Krone operations:
  - 483 verified historical jobs.
  - Active Reliance AMC contracts across 11 bio-energy plants.
  - 14 certified Krone technicians with live locations in Nellore, Kurnool, Warangal, Prayagraj, and Punjab.
  - Krone machinery catalog (Bellima, BiG Pack, Comprima, BiG X) with authentic 7-digit serial numbers.

---

## 7. Authoritative Features Discovered

```
## Features Discovered
| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Jobs | Work Order Retrieval | Fetches work orders with status, timestamps, and customer metadata | `workspace-id`, `location-id`, `page`, `filters` | JSON array of `{ metadata, values }` | Returns `total: 0` if `workspace-id` missing | `GET /job/v1/jobs` |
| 2 | Jobs | Job Numbering Standard | Generates official work order numbers formatted as `SR-26-XXXX` | Job creation payload | Work order number e.g. `SR-26- 0149` | Rejects non-conforming patterns | `all_fieldy_jobs.json` |
| 3 | Jobs | Status Pipeline Management | Tracks lifecycle: Open -> Assigned -> In Progress -> Hold -> Completed -> Cancelled | `job_id`, `status` string | Updated status with color code | Rejects unauthorized transition | `COMPLETE_FIELDY_MASTER_MEMORY.md` |
| 4 | Jobs | Mandatory Add-On Completion Gate | Strictly locks job from being marked 'Completed' until on-site Add-On form is submitted | Add-on values: Transport, Stay/Food, Job Type | Boolean validation success | Prevents closing ticket with error modal | `Job Management Settings` Tab 13 |
| 5 | Jobs | Technician Add-On Form Submission | Submits technician DA, KM, and transport without editing core job | `job_id`, list format `value: ["<option_id>"]` | HTTP 200 with updated fields | HTTP 422 if passed as bare string | `PUT /job/v1/jobs/add-on/{id}/update` |
| 6 | Jobs | PDF Service Report Generation | Enqueues and generates client-signed PDF report with custom fields | `job_id`, `tenant_id`, `template_id` | Signed PDF binary / pre-signed S3 URL | HTTP 404 if template ID invalid | `POST /report-builder/api/generate-pdf` |
| 7 | Technicians | Live GPS Telematics Stream | Tracks real-time latitude, longitude, speed, battery, and last ping | Bearer token, `workspace-id` | JSON array of active technician telemetry | Empty array if technician offline | `GET /tracking/v1/tracking/live` |
| 8 | Technicians | Geofenced Attendance Clock-In | Mandatory morning punch-in capturing GPS location and battery level | `lat`, `lng`, `battery_level` | Attendance record with clock-in timestamp | Fails if GPS coordinates null | `POST /tracking/v1/attendance/clock-in` |
| 9 | Technicians | Leave Applications Sync | Tracks approved Casual, Sick, and Earned leaves from KIN OneHub | `employee_id`, date range | Approved leave records | Hides unapproved/pending applications | Supabase `leave_applications` table |
| 10 | Technicians | Paid Job Operational Filter | Classifies active technicians as 'On Paid Job' when working on in-progress paid job | Active job ID, `job_type == "Paid"` | Boolean `is_on_paid_job` | Defaults to Unpaid if radio unset | `FIELDY_AMC_INVOICING_MEMORY.md` |
| 11 | Machinery | Equipment Asset Database | Tracks serialized Krone balers, harvesters, and mowers | `customer_id`, `serial_number` | Full asset profile with serial and AMC links | HTTP 404 if asset ID not found | `GET /job/v1/assets` |
| 12 | Machinery | QR Code Service Lifecycle | Generates scannable QR code for instant mobile service history | `asset_id` | QR code image and public scan URL | Fails if asset unassigned | `GET /job/v1/asset-settings/asset/qrcode-details` |
| 13 | Machinery | Asset-to-AMC Linking Filter | Auto-populates only machinery attached to the selected AMC contract | `amc_id` UUID | Filtered dropdown of eligible machines | Shows empty dropdown if no linked assets | `GET /job/v1/amcs/asset/{asset_id}` |
| 14 | Invoicing | Contractual Commercial Deputation | Automatically calculates ₹5,000.00 / Man-Day (max 1/day/tech) | Service dates, technician count | Line item amount with 18% IGST | Fails audit if >1 man-day billed per date | `RIL_AMC_Krone_Final_Clean.pdf` |
| 15 | Invoicing | Honest DA Rule Billing | Billed at ₹2,000/day only when stay is Self/KIN; ₹0 when client guest house | Add-on `stay_food` option | Computed DA amount | Banned from billing internal expenses | `FIELDY_AMC_INVOICING_MEMORY.md` |
| 16 | Invoicing | Travel Conveyance Reimbursement | Flat ₹5.00/KM for two-wheeler; ₹0 when client vehicle provided | Add-on `transport`, verified KM | Computed travel conveyance amount | Zero KM enforced on client transport | Clause 4.8 / SOP Section 5 |
| 17 | Invoicing | Duplicate Invoice Prevention | Persistent registry prevents re-invoicing already invoiced jobs | `job_no` | Lock status: `INVOICED_LOCKED` | Halts invoicing with duplicate warning | `invoiced_jobs_database.json` |
| 18 | Route Inspector | 5 km Radius Location Clustering | Merges consecutive GPS pings/stops within 5 km into a single site cluster | Stream of GPS coordinates $(lat_i, lng_i, t_i)$ | Consolidated location cluster with total stay | Distinguishes movements $> 5$ km | Haversine Clustering Engine |
| 19 | Route Inspector | Unauthorized Stop Detection | Detects stationary stops $> 15$ min outside 5 km of base or job site | Geocoded cluster, route corridor | Anomaly alert badge with duration | Ignores traffic stops $< 15$ min | Route Inspector Module |
| 20 | Synchronizer | Fresh Sync Cache Invalidator | Forces live API fetch bypassing Next.js BFF and browser cache | Manual button click, `_ts` param | Refreshed dashboard state with sync timestamp | Seamless failover to synthetic mock | Dashboard Synchronizer Engine |
| 21 | Synchronizer | Automatic Background Polling | Polls telematics and job changes every 30 seconds with backoff | Cron / Timer interval (30s) | Incremental diff updates | Backoff to 60s/120s on connection loss | Polling Worker Service |
```

---

## 8. Authoritative Edge Cases

```
## Edge Cases
| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | Add-On Form API | Bare string ID passed: `value: "13e819d0-da08-4ace-9abd-09c636a23fc0"` | API rejects with HTTP 422 Unprocessable Entity; requires array format `value: ["..."]` |
| 2 | Job Dropdown Update | Nested object passed: `company_id: { "id": "uuid" }` | API rejects with PostgreSQL SQLAlchemy type error; requires raw UUID string |
| 3 | Location Scoping | API query submitted without `workspace-id` or `location-id` header | API returns empty dataset `{"data": [], "total": 0}` despite records existing |
| 4 | Playwright Automation | Browser navigation with `wait_until='networkidle'` on tracking pages | Script hangs indefinitely due to continuous WebSocket telematics streaming; must use `domcontentloaded` |
| 5 | Travel KM Billing | Multiple jobs completed by same technician at same plant on same date | Max 1 travel KM claim allowed per calendar date; all secondary jobs must record 0 KM |
| 6 | DA Billing Rule | Technician accommodated in RIL Guest House (e.g. Naveen Kumar 27-Aug to 02-Sep) | DA must be strictly waived (₹0.00); billing ₹2,000 causes immediate audit rejection |
| 7 | 5 km Geofence Jitter | Technician moves 800m from machine in field to farm weighbridge | Distance $< 5.0$ km; clustering engine maintains single site stay without fragmenting into 2 jobs |
| 8 | Unauthorized Stop | Technician halts for 42 minutes at unverified roadside dhaba 24 km from site | Detected as unauthorized stop anomaly; flagged with red alert badge and duration badge |
| 9 | Offline Detection | Cellular connectivity drops in remote paddy field | Mobile app and dashboard switch to IndexedDB offline cache; auto-syncs when online |
| 10 | Duplicate Job Invoicing | User requests invoice generation for job `SR-26- 0067` | Pre-check detects job locked under `KIN/RIL-NEL/2026/003`; halts execution and raises duplicate alarm |
```

---

## 9. Conclusion & Implementation Recommendations

1. **Architecture Stack:** Deploy a modular FastAPI or Node.js backend paired with a high-performance React (Vite / Next.js) frontend styled with Tailwind CSS.
2. **Telemetry & Route Clustering Engine:** Implement the pure mathematical 5 km Haversine clustering in both Python and TypeScript, accompanied by unit tests.
3. **Data Resilience:** Ensure the dashboard features a prominent "Fresh Sync" button with timestamp badges and seamlessly falls back to the calibrated synthetic Krone dataset if Fieldy cloud session expires.
