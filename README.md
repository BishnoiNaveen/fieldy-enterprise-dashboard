# Krone Agriculture India — Field Service & Telematics Operations Command

Enterprise Field Operations, Attendance & Telematics Platform integrated with Fieldy FSM cloud API and vehicle GPS tracking. Designed for Krone Agriculture India's heavy agricultural machinery operations (Large Square Balers, BiG X Harvesters, Fortima Round Balers, and EasyCut Mowers).

---

## 🌟 Key Features

### 1. Executive Operations Command Center
- **Total Jobs Pipeline**: Real-time tracking of work orders (`SR-26-XXXX` series), completed vs in-progress dispatch statuses.
- **Field Manpower Status**: Live count of active technicians on paid jobs, depot standby, and scheduled leaves.
- **Machinery Under Service**: Real-time tracking of heavy agricultural machinery assets with serial numbers, customer accounts (Reliance Industries, Adani Agri Logistics, Punjab State Farms), and contact persons.
- **Theme Support**: Seamless toggle between **Bright High-Contrast Mode** (default) and **Deep Dark Mode**.

### 2. Live Manpower Attendance & Clock-In Roster
- **Multi-Page Roster Pagination**: Interactive quick switcher between Page 1 (Tech 1–7), Page 2 (Tech 8–14), and All (1–14).
- **Biometric & GPS Geofence Verification**: Exact punch-in time, punch location, coordinates, and compliance audit.
- **Revenue Tracking**: Live tracking of billable deputation (₹5,000/day standard day rate, ₹625/hr standard billing) vs unpaid depot standby.
- **Full Dossier View**: Click-to-open full-page technician service dossier with historical work orders, telematics metrics, and active scope of work.

### 3. Autonomous Route Inspector & 5 km Geofence Clustering Engine
- **5 km Radius Haversine Clustering**: Merges sub-kilometer GPS jitter into unified operational zones.
- **Route Playback & Speed Scrubber**: Interactive scrubber with speed tracking (km/h), vehicle heading, and distance elapsed.
- **Unscheduled Stop Anomaly Detection**: Flags unauthorized 3rd-party stops (>15 min) separately from customer job sites.
- **All-India Fleet Radar**: Interactive OpenStreetMap visualization locating all 14 Krone field engineers across Punjab, Haryana, Uttar Pradesh, Madhya Pradesh, Maharashtra, and Andhra Pradesh.

### 4. Fieldy Cloud API & Database Sync Engine
- **Real-Time Polling**: Automatic background synchronization every 15s with manual "Fresh Sync" trigger.
- **Fieldy Cloud API v1/v4.2 Support**: Native integration with `https://api.getfieldy.com/job/v1/jobs` using session bearer token and workspace authentication headers.
- **Authentic Fallback Database**: Instant failover to authentic 483-job Krone Fieldy dataset if cloud session refreshes.

---

## 🏗️ Architecture & Technology Stack

- **Frontend**:
  - React 18, TypeScript, Vite
  - Tailwind CSS (Tailored high-contrast color palette)
  - Leaflet & React-Leaflet (Hardware-accelerated SVG markers, 5 km geofence circles, OSM tiles)
  - Lucide React Icons
- **Backend**:
  - FastAPI (Python 3.10+ / 3.11+)
  - Async HTTP Client (`httpx`)
  - Pydantic v2 data models & validation
  - Uvicorn ASGI server
- **Mathematical & Telematics Engine**:
  - Haversine Distance Calculation & DBSCAN-style 5 km spatial clustering
  - Temporal duration and dwell calculation

---

## 🚀 Quick Start Guide

### Prerequisites
- Node.js 18+ & npm
- Python 3.10+

### 1. Setup Backend
```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Setup Frontend
```bash
cd frontend
npm install
npm run dev
# Or build for production preview:
npm run build
npm run preview
```

### 3. Access Dashboard
- **Web UI**: `http://localhost:4173/` or `http://localhost:5173/`
- **FastAPI OpenAPI Docs**: `http://127.0.0.1:8000/docs`

---

## 🔒 Security & Data Integrity
- Zero-Guessing Policy: All job numbers, machine serials, and technician rosters match authentic Fieldy schemas.
- Credentials and authentication tokens are kept strictly isolated in `.env` and never committed to source control.
