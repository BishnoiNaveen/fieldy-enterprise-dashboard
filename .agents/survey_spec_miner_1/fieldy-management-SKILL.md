---
name: fieldy-management
description: >-
  Definitive master operations, UI controls dictionary, API microservices catalog, and end-to-end automation engine for Fieldy FSM (Krone Agriculture India). ALWAYS USE when navigating Fieldy, krone.getfieldy.com, creating or linking jobs, managing AMCs, tracking technicians, dispatching schedules, generating proforma/tax invoices, or performing audits.
license: Apache-2.0
metadata:
  version: v4.0-master
  publisher: naveen-krone
  priority: maximum
  always_active: true
---

# Fieldy FSM Master Operations, Deep Architecture & Feature Encyclopedia (v4.0 Master)

This skill is the **definitive, empirical ground-truth reference and operating handbook** for the Fieldy Field Service Management (FSM) platform deployed at **Krone Agriculture India Pvt Ltd** (`krone.getfieldy.com`). It synthesizes all 28 system modules, 30 role-based permission clusters, 16 tutorial pillars, live microservices, PDF Report Builder mechanics, and enterprise agricultural service workflows.

---

> [!CAUTION]
> ### 🛑 MANDATORY PRE-FLIGHT MEMORY VERIFICATION (REQUIRED BEFORE ANY ACTION)
> Before running any tool, writing code, editing settings, or interacting with Fieldy or KIN OneHub, the AI agent MUST review these three canonical memory files:
> 1. **`FIELDY_AMC_INVOICING_MEMORY.md`**: Krone AMC contracts, 7 microservices, Add-On forms, dispatch configuration.
> 2. **`FIELDY_KIN_ONEHUB_INTEGRATION_MEMORY.md`**: KIN OneHub portal, Cloudflare Workers, Supabase PostgreSQL, RLS security audit, attendance bug fixes.
> 3. **`COMPLETE_FIELDY_MASTER_MEMORY.md`**: Master unified memory synthesizing both platforms, mistakes log, and self-learning anti-patterns.
>
> **File Locations:** Stored synchronously across `c:\Users\Naveen\Desktop\pi of amc\`, `C:\Users\Naveen\.gemini\antigravity\brain\4b00f5c5-2082-4b83-8c2a-a77bdb91df75\`, and `C:\Users\Naveen\.gemini\config\skills\fieldy-management\`.
> 
> **Auto-Update Directive:** Upon completion of any command or workflow, the AI agent MUST update these memory files to record new operations and lessons learned.

---

## 1. Enterprise Tenant Context & Architecture

* **Web Portal URL**: `https://krone.getfieldy.com`
* **API Gateway**: `https://api.getfieldy.com`
* **Tenant ID**: `4e51f497-b8dd-4036-8d78-60b12a7598b7`
* **Active Production Workspace**: `87c32c6a-ec1f-49af-a925-8455d6933ed6` (`krone Gurugram Office`)
* **Default Location ID**: `8176f98f-3d9f-4d70-ad2f-7c6a9c23d16c`
* **Admin / Authorized Signatory**: `Naveen Bishnoi` (`kin.it@krone-india.com`, `+91 9625957663`)
* **Legal Entity**: Krone Agriculture India Pvt Ltd (Corporate Office: 404, Qutub Plaza, Gurugram, Haryana, 122002; GSTIN: `07AAKCK4471E1ZH`, SAC: `998719`)
* **Session Storage Token**: `C:\Users\Naveen\.gemini\antigravity\brain\4b00f5c5-2082-4b83-8c2a-a77bdb91df75\scratch\fieldy_storage.json`

---

## 2. Global URL Routing & Plural Convention Encyclopedia

> **CRITICAL ROUTING RULE**: Fieldy uses strict plural naming for all core module URLs. Singular paths trigger the 404 "Oops! Page not found" modal.

| Module | Canonical URL | Gotcha / Behavior |
| :--- | :--- | :--- |
| **Jobs** | `https://krone.getfieldy.com/en/jobs` | Singular `/en/job` = 404. Detail: `/en/jobs/{id}`. |
| **AMCs** | `https://krone.getfieldy.com/en/amcs` | Singular `/en/amc` = 404. Detail: `/en/amcs/{id}`. |
| **Assets** | `https://krone.getfieldy.com/en/assets` | Singular `/en/asset` = 404. Detail: `/en/assets/{id}`. |
| **Forms / Checklists** | `https://krone.getfieldy.com/en/forms` | Singular `/en/form` = 404. Builder: `/en/forms/{id}`. |
| **Invoices** | `https://krone.getfieldy.com/en/invoices` | Singular `/en/invoice` = 404. Create: `/en/invoices/create`. |
| **Estimates** | `https://krone.getfieldy.com/en/estimate` | Singular `estimate`. |
| **Dispatch Board** | `https://krone.getfieldy.com/en/dispatch` | Matrix timeline, calendar, and map dispatch. |
| **Live Tracking** | `https://krone.getfieldy.com/en/tracking/live_tracking` | Telematics, speed, and GPS route playback. |
| **Parts & Services** | `https://krone.getfieldy.com/en/inventory` | Inventory, warehouses, van stocks, and POs. |
| **Features Settings** | `https://krone.getfieldy.com/en/settings/features` | Module-level custom forms, slugs, field ordering. |
| **Jobs Feature Settings** | `https://krone.getfieldy.com/en/settings/features/5926c3ba-6435-4f98-adfe-2ce5f84e37dc` | 18 sub-tabs: Customize Job Form, Customize Add-On Form, Job Management Settings, Job Report Settings, etc. |
| **Account Types (Roles)**| `https://krone.getfieldy.com/en/settings/account-types` | Role creation, Data Visibility, granular permissions. |
| **Tax Settings** | `https://krone.getfieldy.com/en/settings/tax-settings` | Tax names, rates (IGST 18%), HSN/SAC mappings. |
| **Integrations** | `https://krone.getfieldy.com/en/settings/integrations` | Connectors for Xero, Zoho Books, QuickBooks. |
| **Notifications** | `https://krone.getfieldy.com/en/settings/notifications` | Email templates, WhatsApp Business, In-App alerts. |
| **Report Builder** | `https://krone.getfieldy.com/en/report-builder/{id}`| WYSIWYG PDF report canvas and variable mapping. |

---

## 3. The 7 Cloud Microservices & API Gateway Matrix (2,345 Paths / 2,828 Endpoints)

Fieldy's backend runs on a high-throughput, decoupled **Enterprise Microservices Architecture** behind the API gateway `https://api.getfieldy.com`.

### Master Microservices Catalog:

| # | Microservice | Gateway / Docs URL | OpenAPI Spec | Paths | Operations | Core Domain & Responsibilities |
| :- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Fieldy Job Microservice** | `https://api.getfieldy.com/job/docs` | `/job/openapi.json` | **933** | **1,165** | Jobs, Add-On Forms, AMCs, Assets, Checklists, Leads, Deals, Tasks, Gemini AI |
| **2** | **Accounting Microservice** | `https://api.getfieldy.com/accounting/docs` | `/accounting/openapi.json` | **599** | **721** | Invoices, Estimates, Inventory, Van Stocks, GST/Taxes, PDF Templates, Stripe/Auth.net |
| **3** | **Fieldy User Microservice** | `https://api.getfieldy.com/docs` (Root) | `/openapi.json` | **460** | **535** | Users, Companies, Contacts, Roles (RBAC), Locations, Wallets, S3 Uploads, Tenant Auth |
| **4** | **Tracking Microservice** | `https://api.getfieldy.com/tracking/docs` | `/tracking/openapi.json` | **228** | **269** | Real-Time GPS Tracking, Trips (KM/Odometer), Attendance (Clock In/Out), Visits |
| **5** | **Fieldy Integration Microservice**| `https://api.getfieldy.com/integration/docs` | `/integration/openapi.json` | **52** | **53** | Zoho Books, QuickBooks, Xero, Salesforce (Assets, AMCs, CMCs, Contacts) |
| **6** | **Fieldy Notification Microservice**| `https://api.getfieldy.com/notification/docs`| `/notification/openapi.json` | **45** | **50** | WhatsApp Business API, SMTP/OAuth Email Templates, In-App WebSockets |
| **7** | **Fieldy Payment Microservice** | `https://api.getfieldy.com/payment/docs` | `/payment/openapi.json` | **28** | **35** | Subscription Plans, Feature Add-ons, Volume Add-ons, Billing History, In-App Cashout |
| **Σ** | **TOTAL ECOSYSTEM** | **https://api.getfieldy.com** | **7 Microservices** | **2,345** | **2,828** | **End-to-End Enterprise Field Service Automation** |

---

### Detailed Service-by-Service Functional Domains:

#### 1. Job Microservice (`/job/v1`) — 933 Paths / 1,165 Operations
* **Jobs Management**: 161 endpoints (`/v1/jobs`) — CRUD, assignment, status pipeline (`Draft` -> `Assigned` -> `Dispatched` -> `Start Travel` -> `Reached` -> `In Progress` -> `Hold` -> `Completed` -> `Cancelled`).
* **Jobs Add-On Custom Fields** (`/v1/job-add-on-custom-fields` & `/v1/jobs/add-on/{job_id}/update`): 23 endpoints — Programmatic field creation, mandatory enforcement, and job-level add-on data submission without editing the core job!
* **AMCs (Contracts)**: 108 endpoints (`/v1/amcs`) — Fixed Retainer, Service contract lifecycle, visit allowances, renewals, customer contract dashboards.
* **Assets (Equipment)**: 119 endpoints (`/v1/assets`) — Serialized agricultural machinery, QR code generation, AMC linking, service history logs.
* **Checklist System**: 63 endpoints (`/v1/job-settings-checklists`) — Multi-choice inspection forms, service-type binding, mandatory submission.
* **CRM Leads & Deals**: 157 endpoints (`/v1/leads`, `/v1/deals`) — Inbound lead capture forms, deal stages, lead-to-deal conversion mappings.
* **Tasks & Follow-ups**: 49 endpoints (`/v1/tasks`, `/v1/follow-ups`) — Recurring administrative tasks and technician follow-up reminders.
* **Gemini AI Operations**: Endpoints `/v1/dashboard/gemini`, `/v1/gemini-case` — Native Google Gemini AI case summarizing and dispatch support.

#### 2. Accounting Microservice (`/accounting/v1`) — 599 Paths / 721 Operations
* **Invoices**: 222 endpoints (`/v1/invoice`) — Tax Invoices, Proforma Invoices, SAC `998719` auto-coding, 18% IGST calculation, PDF download.
* **Estimates**: 223 endpoints (`/v1/estimate`) — Client quotations, digital approvals, auto-conversion to Invoices.
* **Inventory & Van Stock**: 110 endpoints (`/v1/inventory`) — Central Warehouse + Technician Mobile Truck inventories, serial/batch tracking, Stock Transfer Requests.
* **GST & Taxes**: Endpoints `/v1/tax` — Inter-state IGST, Intra-state CGST+SGST, tax group management.
* **PDF Report Templates**: Endpoints `/v1/template/report-template` — WYSIWYG HTML/PDF layout management, variable keys (`df-variable`).
* **Payment Gateways**: Stripe & Authorize.net customer card charge APIs.

#### 3. User Microservice (`/v1` Root) — 460 Paths / 535 Operations
* **Users & Staff**: 55 endpoints (`/v1/users`) — Technicians, Service Managers, Operators, reportee-manager hierarchy.
* **B2B Companies & Contacts**: 95 endpoints (`/v1/companies`, `/v1/contacts`) — Customer parent billing entities, GSTIN, site contacts.
* **Locations**: 34 endpoints (`/v1/locations`) — Branch offices, warehouse locations, geocoded boundaries.
* **RBAC & Security**: Endpoints `/v1/account-types` — Granular role permissions (30 permission clusters), data visibility tiers.
* **Technician Expense Wallets**: 19 endpoints (`/v1/wallet`) — Advance cash disbursement, daily DA/food sync.
* **File Storage**: Direct AWS S3 presigned URL generation and media uploads (`/v1/file-upload`).

#### 4. Tracking Microservice (`/tracking/v1`) — 228 Paths / 269 Operations
* **Real-time GPS Tracking**: Endpoints `/v1/tracking` — Continuous lat/long pings, technician speed, device battery status.
* **Trips & Distance Telematics**: 29 endpoints (`/v1/trips`) — Start/Stop travel odometer tracking, breadcrumb route history, total distance in KM.
* **Attendance**: 26 endpoints (`/v1/attendance`) — Geofenced Clock-In / Clock-Out, attendance status reports.
* **Scheduled Visits**: 40 endpoints (`/v1/scheduled-visits`, `/v1/visits`) — Site visit logs, arrival timestamps, technician notes.

#### 5. Integration Microservice (`/integration/v1`) — 52 Paths / 53 Operations
* **Accounting Connectors**: Zoho Books (Indian GST ledger sync), QuickBooks (Customers, Invoices, Webhooks), Xero.
* **Salesforce CRM Sync**: Endpoints `/v1/salesforce-*` — Bidirectional sync for Salesforce Assets, Contacts, Customers, AMCs, and CMCs.

#### 6. Notification Microservice (`/notification/v1`) — 45 Paths / 50 Operations
* **WhatsApp Business**: 24 endpoints (`/v1/whatsapp`) — Automated template messages, interactive button messages for customer dispatch alerts.
* **Email System**: 15 endpoints (`/v1/email-templates`, `/v1/mail-settings`) — SMTP and OAuth (Google Workspace / Microsoft 365) transactional mailers.
* **WebSockets**: Endpoints `/v1/websocket` — Live event streaming to Dispatch Boards and Mobile Apps.

#### 7. Payment Microservice (`/payment/v1`) — 28 Paths / 35 Operations
* **Tenant Billing**: Endpoints `/v1/subscription-plans`, `/v1/current-plan` — Fieldy SaaS subscription tiers, billing receipts, volume seats, feature add-ons.

---

### API Applicability Matrix: What is Programmatic vs UI-Only

| Capability / Workflow | API Applicable? | Endpoint / Mechanism | Limitations / Gotchas |
| :--- | :---: | :--- | :--- |
| **Job CRUD & Dispatch** | **100% API** | `POST /job/v1/jobs`, `PUT /job/v1/jobs/{id}` | Immediate execution without UI interaction. |
| **Add-On Form Submission**| **100% API** | `PUT /job/v1/jobs/add-on/{job_id}/update` | Submits technician DA, KM, Transport without editing job! |
| **Add-On Field Definition**| **100% API** | `POST /job/v1/job-add-on-custom-fields` | Programmatically creates mandatory radio/dropdown fields. |
| **AMC Contract Creation** | **100% API** | `POST /job/v1/amcs` | Sets Retainer fees, visit quotas, and customer binding. |
| **PDF Report Download** | **100% API** | `GET /job/v1/jobs/{id}/report-pdf` | Returns binary PDF or signed S3 download URL. |
| **Public Report Share URL**| **100% API** | `GET /job/v1/jobs/{id}/report-public` | Generates customer-facing verification link. |
| **Invoice Auto-Generation**| **100% API** | `POST /accounting/v1/invoice` | Generates 18% IGST Tax Invoice with Krone SAC `998719`. |
| **GPS Distance Extraction**| **100% API** | `GET /tracking/v1/trips/{trip_id}` | Returns verified KM for travel reimbursement billing. |
| **Attendance Clock In/Out**| **100% API** | `POST /tracking/v1/attendance/clock-in` | Requires device lat/long coordinates. |
| **Customer Glass Signature**| **Restricted** | Mobile Web / App Canvas | Captured as Base64 SVG on mobile glass; manual drawing. |
| **WYSIWYG Template Builder**| **UI-Only** | `/en/report-builder/{id}` | Drag-and-drop canvas is UI-only; raw HTML can be saved via API. |
| **Bulk Excel File Ingestion**| **UI Preferred**| `/job/v1/jobs/bulk-import` | Column headers must strictly match; UI provides error highlighting. |

---

## 4. The 16 Deep Tutorial Pillars (Complete Feature Mastery)

Fieldy's permission and capability engine is divided into 16 core training pillars:

### Pillar 1: Getting Started & Workspace Provisioning
* Organization structure setup, branch location geocoding, multi-currency formatting (INR ₹), and legal entity parameters.

### Pillar 2: Admin & Role-Based Access Control (RBAC)
* Located at `/en/settings/account-types`.
* **Data Visibility Scopes**:
  1. `permission own data`: User only sees their personally assigned jobs, leads, and customer interactions.
  2. `permission all users`: Unrestricted organization-wide transparency.
  3. `permission direct reportees`: Managerial scope covering immediate team members.
  4. `permission direct and indirect reportees`: Hierarchical branch/regional head visibility.
* **Predefined Roles**: Admin, Service Manager, Operator, Sales Manager, Sales Rep, Technician. Custom roles can be created via `+ Add role`.

### Pillar 3: CRM & Account Hierarchy
* Divided into **Companies** (`/en/customer/company`) and **Contacts** (`/en/customer/contacts`).
* Companies hold parent billing data (GSTIN, legal name, credit limits, geocoded site locations).
* Contacts represent site managers, operators, or supervisors with direct communication preferences.

### Pillar 4: Jobs & Smart Scheduling
* Work orders (`SR-...`) with scheduling windows, priority flags (`Cold`, `Warm`, `Hot`), estimated durations, and automated multi-visit support.
* Drag-and-drop dispatch board with timeline and calendar interfaces.

### Pillar 5: Quick Invoice & Cash Acceleration
* Auto-generation of Tax Invoices from completed jobs or AMC contracts.
* Line items pre-configured with Krone SAC code `998719` and 18% IGST.
* Public shareable invoice links allowing client accounting teams to verify and approve invoices without login credentials.

### Pillar 6: Sales & Lead Pipeline
* Full CRM funnel (`/en/leads` and `/en/deal`) tracking inbound machine inquiries, quote requests, and conversion to active service jobs.

### Pillar 7: Live Tracking & Telematics
* Real-time GPS pings capturing technician speed, route breadcrumbs, stopover durations, and battery status.
* Geofenced arrival detection when a technician enters a client's farm or plant perimeter.

### Pillar 8: Mobile App Field Operations (Fieldy Mobile)
* Technician smartphone flow:
  1. **Clock In**: Mandatory morning timestamp with GPS location and device battery level.
  2. **Accept & Travel**: Push notification -> `Accept` -> `Start Travel` -> `Reached`.
  3. **Evidence Capture**: Before/After photos and Audio Notes directly on the main job view.
  4. **Digital Sign-off**: Customer draws signature on glass.
  5. **Offline Mode**: Automatic local caching when cellular reception is lost in rural fields; auto-syncs upon reconnection.

### Pillar 9: Job Management & Mandatory Completion Gates
* State machine: `Draft` -> `Assigned` -> `In Progress` -> `Completed` / `Cancelled`.
* **Mobile App Mandatory Completion Gates** (`/en/settings/features/5926c3ba-6435-4f98-adfe-2ce5f84e37dc` -> `Job Management Settings`):
  1. **Add-On Form**: When enabled, technicians **MUST submit the Add-On form before completing the job**.
  2. **Upload 'Before' Images/Videos**: Requires mandatory media upload before starting the job.
  3. **Upload 'After' Images/Videos**: Requires mandatory media upload showing completed work before closing.
  4. **Technician Notes**: Mandatory notes/observations before closing.
  5. **Capture Customer Signature**: Mandatory glass digital signature to finalize.
  6. **Validate Asset & AMC**: Enforces asset and AMC verification at job close.
  7. **Save Time Spent**: Records total technician hours upon completion.
  8. **Restrict AMC Over-Visits**: Hard blocks job creation beyond contract visit quota.
  9. **Allow Only One Active Job**: Blocks starting a new job if any job is currently In-Progress/Dispatched.

### Pillar 10: Asset Lifecycle & Equipment Database
* Located at `/en/assets`.
* Tracks physical machines (e.g. `Krone BigPack 1290 HDP`, `Bellima F130 Baler`) by unique serial numbers.
* **QR Code Generation**: Generates printable QR codes. Scanning via Fieldy Mobile instantly displays the full chronological service history of the machine.

### Pillar 11: Multi-Tier Inventory & Truck Stocks
* Located at `/en/inventory`.
* Manages multi-location stock: Central Warehouse (Gurugram HQ) and Van/Truck Inventory (allocated to individual technician vehicles).
* Parts added to a job under `Parts Used` are automatically deducted from that technician's truck inventory.
* Supports Stock Transfer Requests, Restock Approvals, and Purchase Orders.

### Pillar 12: AMC Management (Annual Maintenance Contracts)
* Located at `/en/amcs`.
* Supports `Fixed Retainer` (periodic fee with visit quota) and `Service` (pay-per-visit).
* Tracks contract start/expiry dates, visit consumption ratios, and real-time revenue margin profitability.

### Pillar 13: Asset-to-AMC Linking (The Golden Rule)
* **The `Service Category` Switch**:
  - When creating a job from `/en/jobs`, default category is `General Service`.
  - In `General Service`, AMC and Asset fields are hidden.
  - Selecting radio button **`Amc`** immediately reveals:
    1. **`AMC`**: Contract selection dropdown.
    2. **`Asset/Service`**: Auto-populated dropdown containing *only* the machines attached to that AMC!
* **Best-Practice Shortcut**: Navigate to `/en/amcs` -> Open the contract (e.g. `RIL-Kakinada`) -> Open **`Jobs` tab** -> Click **`+ Add job`**. Fieldy auto-links the AMC and pre-populates all customer machines.

### Pillar 14: GPS & Time Tracking
* Automatic calculation of `actual_time_spent` from status transitions.
* Multiplies technician working hours by deputation hourly rates to feed job cost accounting.

### Pillar 15: Customization & Form Architecture (Custom Fields vs Add-On Form)
Fieldy has two distinct form customization architectures with strictly differentiated operational roles:

1. **Job Custom Fields** (`Customize Job Form` tab):
   - **Visible on**: Job Creation and Edit modal in Web Portal & Mobile.
   - **Target User**: Office Dispatcher / Service Coordinator.
   - **Behavior**: Used for static parameters known *before* dispatching.
   - **Gotcha**: If marked "Mandatory", office cannot dispatch a job without filling it. Does NOT force field-level post-service completion prompts.

2. **Job Add-On Form** (`Customize Add-On Form` tab):
   - **Visible on**: Inside the **Job Detail View** in web and mobile app (`Add-on Fields` tab). **NEVER on the create/edit form**.
   - **Target User**: Field Technician at customer site.
   - **Completion Lock**: Controlled by `Job Management Settings` -> **`Add-On Form`** toggle. When ON, technician **CANNOT complete the job** without filling all mandatory Add-On fields.
   - **PDF Reporting**: Add-on field variables are mapped into the official PDF Job Report template (`/accounting/v1/template/report-template`).

3. **Checklist Forms** (`/job/v1/forms` / `Checklist Settings` tab):
   - Dynamic multi-question inspection forms (`for_job: true`, `default_on_all_job: true`).

### Pillar 16: Cost & Profitability Accounting
* Aggregates Technician Labor Cost + Spare Parts Used vs Contract Billing to compute net project margin.

---

## 5. Deep Hidden Features & Integrations Catalog

### A. Accounting System Connectors (`/en/settings/integrations`):
* **Xero**: 1-click sync for customers, invoices, and payments.
* **Zoho Books**: Direct API ledger sync for Indian GST compliance.
* **QuickBooks**: Automatic financial ledger mapping.

### B. Omnichannel Communication Hub (`/en/settings/notifications`):
* **WhatsApp Business Integration**: Direct integration to dispatch job confirmations, technician arrival alerts, and PDF invoices via WhatsApp.
* **Customer Notification Triggers**: Can be set to `All Customers`, `Specific Customers`, or `No Customers`.
* **In-App Messaging**: Real-time dispatcher-to-technician chat thread within each job.

### C. PDF Report Builder Mechanics (`/accounting/v1/template/report-template`):
* Template ID: `d038dbcf-632d-4548-84f3-5f819ec95d54` ("Job Report").
* Variable syntax: `<span class="df-variable" data-key="{customfield_id}">Label</span>`.
* **Verified Live Mapped Variables**:
  - `Transport Provided By`: `4e59e7ae-f068-4002-9351-bdbe63aea4cf`
  - `Kilometers Travelled (KM)`: `b1d05729-f884-4b5a-a18f-a24041edec8b`
  - `Stay & Food Provided By`: `6a906ae5-c38e-4533-9498-0554a01189e5`
  - `Job Type (Paid / Unpaid)`: `c5752659-fe83-4227-b4c6-aa13dc6d9a77`
* Enqueue PDF generation endpoint: `POST https://krone.getfieldy.com/report-builder/api/generate-pdf/enqueue` (Payload: `tenant_id`, `workspace_id`, `user_id`, `time_zone`, `job_id`, `template_id`).

---

## 6. Reliance Commercial Policy & Billing Matrix (Ground Truth)

All 11 Reliance Industries AMC contracts follow the legal agreement `RIL_AMC_Krone_Final_Clean.pdf`:

| Parameter | Contract Clause | Rate (excl. GST) | Billing Basis |
| :--- | :--- | :--- | :--- |
| **Annual Retainer Fee** | Annexure II (A) | ₹24,00,000 / Site / Year | Fixed Retainer across 12 scheduled visits (₹2,00,000/mo) |
| **Additional Deputation Rate** | Clause C.2 / Sched. IV | **₹5,000.00 / Man-Day** | 1 Man-Day = 8 working hours. |
| **Outstation Boarding & Lodging (DA)** | Clause 4.8 & C.3 | **₹2,000.00 / Person / Day** | Fixed allowance. Billed when stay/food NOT provided by RIL. |
| **Travel Conveyance Reimbursement** | Clause 4.8 & C.3 | **₹5.00 / KM** | Flat rate for technician's own travel. Billed when RIL does NOT provide transport. |
| **Payment Terms** | Clause C.5 | 14 Days Net | Released within 14 days of invoice submission |
| **SAC / Tax Classification** | GST Regime | SAC: `998719` / 18% IGST | Interstate technical repair & maintenance service |

---

## 7. Playwright Automation Protocol (System Standard)

Execute browser interactions using `wait_until='domcontentloaded'` to bypass persistent websockets:

```python
from playwright.sync_api import sync_playwright

storage_file = r"C:\Users\Naveen\.gemini\antigravity\brain\4b00f5c5-2082-4b83-8c2a-a77bdb91df75\scratch\fieldy_storage.json"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(storage_state=storage_file, viewport={'width': 1400, 'height': 1000})
    page = ctx.new_page()
    page.goto("https://krone.getfieldy.com/en/jobs", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    # Perform verified automation
    browser.close()
```

---

## 8. Dual Execution Framework: Headless Browser UI vs Direct REST API Automation

To ensure maximum operational stability, reliability, and proof verification, Fieldy tasks are governed by a **Dual Execution Protocol**:

### Decision Matrix: When to Use Browser UI vs REST API

| Operational Need | Execution Mode | Rationale & Tool |
| :--- | :---: | :--- |
| **System Settings & Toggles** | **Browser UI (Playwright)** | Settings toggles (`Job Management Settings` -> `Add-On Form`) require Next.js frontend cache invalidation. Screenshots provide unambiguous audit proof. |
| **Form Customization (Add-On / Custom Fields)** | **Browser UI (Playwright)** | Guarantees exact UI drag-and-drop alignment, label matching, and visual confirmation for admins. |
| **Visual Proof & Client Audit** | **Browser UI (Playwright)** | Delivers high-resolution screenshots (`.png`) for admin sign-off. |
| **Bulk Data Fetching & Sync** | **Direct REST API** | 100x faster than UI rendering; reads jobs, customers, and AMCs cleanly as JSON. |
| **Technician Add-On Data Submission** | **Direct REST API** | Endpoint `PUT /job/v1/jobs/add-on/{job_id}/update` injects DA/KM data cleanly without opening web forms. |
| **PDF Job Report Download** | **Direct REST API** | Endpoint `GET /job/v1/jobs/{job_id}/report-pdf` streams raw PDF binary directly to disk. |
| **Proforma & Tax Invoicing** | **Python Engine / API** | Computes contract logic, DA clauses, ₹5/KM travel rates, and 18% IGST with zero arithmetic error. |

### Authorized Direct API Python Client Standard

All direct API requests to `https://api.getfieldy.com` automatically derive authentication from the active session storage:

```python
import json, requests

storage_file = r"C:\Users\Naveen\.gemini\antigravity\brain\4b00f5c5-2082-4b83-8c2a-a77bdb91df75\scratch\fieldy_storage.json"

with open(storage_file, "r", encoding="utf-8") as f:
    storage = json.load(f)

# Extract active auth token from cookies / localStorage
token = ""
for cookie in storage.get("cookies", []):
    if "token" in cookie.get("name", "").lower() or "auth" in cookie.get("name", "").lower():
        token = cookie.get("value")
        break

api_headers = {
    "Authorization": f"Bearer {token}",
    "x-tenant-id": "4e51f497-b8dd-4036-8d78-60b12a7598b7",
    "workspace-id": "87c32c6a-ec1f-49af-a925-8455d6933ed6",
    "location-id": "8176f98f-3d9f-4d70-ad2f-7c6a9c23d16c",
    "Content-Type": "application/json"
}
```



## [17-Sep-2026] UPDATE: CRITICAL INVOICING POLICY CORRECTION
- **Problem Identified:** Technician Excel logs contained internal petty reimbursement amounts (food Rs 280, hotel Rs 1260, local travel Rs 60-150). Invoicing the client for internal expenses was rejected as an operational violation.
- **Official Policy Rule Enforced:** Invoices to client (RIL) must STRICTLY adhere to the RIL AMC Master Contract Terms (Clause 4.7 & 4.8 / Table 4):
  1. **Technical Manpower Deputation:** Flat **INR 5,000.00 / Man-Day** (8-hour shift).
  2. **Fixed Outstation Lodging & Boarding Allowance (DA):** Flat **INR 2,000.00 / Day** (>50 km from base).
  3. **GST:** 18% IGST on all service codes (SAC 998719 / 998519).
  4. **Retainer Benchmark Reference:** Monthly Fixed Retainer Milestone (AMC 011 Primary) is Rs 2,00,000.00 + 18% IGST = Rs 2,36,000.00.
- **Updated Output Deliverables:**
  - Proforma_Invoice_PI_KIN_RIL_2026_003_Nellore_AMC.pdf (2 Pages: Page 1 Commercial PI @ Rs 1,89,980.00, Page 2 Verified 33-Job Fieldy Annexure).
  - Proforma_Invoice_PI_KIN_RIL_2026_003_Nellore_AMC.xlsx (Excel workbook with dynamic formulas).
  - Proforma_Invoice_PI_KIN_RIL_2026_003_Nellore_AMC.html (Pixel-perfect printable template).
