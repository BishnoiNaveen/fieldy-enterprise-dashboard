"""
backend/app/routers/telematics.py
Endpoints for Autonomous Route Inspector, 5km Geofences & Anomalies.
Dynamically wired to telematics_engine.analyze_route_journey and Krone field telemetry.
"""
from fastapi import APIRouter, Depends, Query, HTTPException, Request
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone, timedelta

from app.models.telematics import RouteResponse
from app.services.sync_service import SyncService
from app.services.telematics_engine import analyze_route_journey
from app.services.mock_generator import KroneMockGenerator

router = APIRouter()


def get_sync_service(request: Request) -> SyncService:
    return request.app.state.sync_service


# ---------------------------------------------------------------------------
# Authoritative Krone Job Site Directory (Geodetic Coordinates & En-Route Halts)
# ---------------------------------------------------------------------------
JOB_SITE_DIRECTORY: Dict[str, Dict[str, Any]] = {
    "SR-26-0101": {
        "name": "RIL Bio-Energy Facility Barwala",
        "lat": 30.3800,
        "lng": 76.8405,
        "customer": "Reliance Industries Limited (Bio-Energy Division)",
        "has_unauthorized_stop": True,
        "halt_coords": (30.6450, 76.3200),
        "halt_mins": 25,
        "halt_name": "Rajpura Highway Dhaba Halt"
    },
    "SR-26-0102": {
        "name": "Barwala Plant Hisar",
        "lat": 29.3582,
        "lng": 75.9085,
        "customer": "Reliance Industries Limited",
        "has_unauthorized_stop": True,
        "halt_coords": (29.2500, 75.8100),
        "halt_mins": 20,
        "halt_name": "Agroha Roadside Dhaba Halt"
    },
    "SR-26-0103": {
        "name": "Panipat Grain Silos",
        "lat": 29.3909,
        "lng": 76.9635,
        "customer": "Adani Agri Logistics Ltd",
        "has_unauthorized_stop": False,
        "halt_coords": (29.2700, 76.8400),
        "halt_mins": 6,
        "halt_name": "Gohana Toll Plaza"
    },
    "SR-26-0104": {
        "name": "Barnala Bio-Mass Site",
        "lat": 30.3819,
        "lng": 75.5469,
        "customer": "SAEL Punjab Biomass Energy Project",
        "has_unauthorized_stop": False,
        "halt_coords": (30.6400, 75.7000),
        "halt_mins": 8,
        "halt_name": "Raikot Fuel Station"
    },
    "SR-26-0105": {
        "name": "Dagadarthi Bio-Mass Plant Nellore",
        "lat": 14.5855,
        "lng": 79.9405,
        "customer": "Reliance Industries Limited (RIL-Nellore)",
        "has_unauthorized_stop": False,
        "halt_coords": (14.5140, 79.9635),
        "halt_mins": 5,
        "halt_name": "Allur Highway Junction"
    },
    "SR-26-0106": {
        "name": "Kovur Bio-Mass Yard Nellore",
        "lat": 14.4983,
        "lng": 79.9922,
        "customer": "RIL Nellore Bio-Mass Facility",
        "has_unauthorized_stop": False,
        "halt_coords": (14.4700, 79.9900),
        "halt_mins": 4,
        "halt_name": "Pennar Bridge Toll"
    },
    "SR-26-0107": {
        "name": "Kakinada Port Agro Yard",
        "lat": 16.9891,
        "lng": 82.2475,
        "customer": "Kakinada Agro Energy Terminal",
        "has_unauthorized_stop": False,
        "halt_coords": (16.7000, 81.8000),
        "halt_mins": 7,
        "halt_name": "Rajahmundry Bypass Toll"
    },
    "SR-26-0108": {
        "name": "Pithampur Bio-Mass Hub Indore",
        "lat": 22.6139,
        "lng": 75.6823,
        "customer": "Bathinda Bio-Power Co. (MP Facility)",
        "has_unauthorized_stop": False,
        "halt_coords": (22.6650, 75.7700),
        "halt_mins": 6,
        "halt_name": "Rau Bypass Toll"
    },
    "SR-26-0109": {
        "name": "Sangrur Bio-Energy Site",
        "lat": 30.2458,
        "lng": 75.8421,
        "customer": "Sangrur Green Agro",
        "has_unauthorized_stop": False,
        "halt_coords": (30.5700, 75.8500),
        "halt_mins": 5,
        "halt_name": "Ahmedgarh Toll Plaza"
    },
    "SR-26-0110": {
        "name": "Ludhiana Bio-Energy Hub",
        "lat": 30.8200,
        "lng": 75.9800,
        "customer": "Ludhiana Bio-Energy Hub",
        "has_unauthorized_stop": False,
        "halt_coords": (30.8600, 75.9100),
        "halt_mins": 4,
        "halt_name": "Sahnewal Junction"
    }
}


def normalize_tech_id(tech_id: str) -> str:
    """Normalizes technician IDs (e.g. TECH-001 -> TECH-01) for robust matching."""
    tid = tech_id.strip().upper()
    return tid.replace("TECH-00", "TECH-").replace("TECH-0", "TECH-")


def generate_corridor_pings(
    start_lat: float,
    start_lng: float,
    end_lat: float,
    end_lng: float,
    date_str: str,
    start_time_iso: Optional[str] = None,
    has_unauth_stop: bool = False,
    halt_coords: Optional[Tuple[float, float]] = None,
    halt_mins: int = 25
) -> List[Dict[str, Any]]:
    """
    Generates high-fidelity chronological GPS breadcrumbs adhering to 
    Krone operational patterns (Depot dwell -> Transit -> Halt -> Transit -> Site dwell).
    Total count strictly targets 180 pings.
    """
    if start_time_iso:
        try:
            t0 = datetime.fromisoformat(start_time_iso.replace("Z", "+00:00"))
        except Exception:
            t0 = datetime.fromisoformat(f"{date_str}T08:00:00+00:00")
    else:
        t0 = datetime.fromisoformat(f"{date_str}T08:00:00+00:00")

    pings: List[Dict[str, Any]] = []

    # If stationary at base (available / on leave)
    if abs(start_lat - end_lat) < 1e-5 and abs(start_lng - end_lng) < 1e-5:
        for i in range(180):
            pings.append({
                "lat": round(start_lat + (i % 3 - 1) * 0.00001, 6),
                "lon": round(start_lng + (i % 2) * 0.00001, 6),
                "speed_kmh": 0.0,
                "timestamp": (t0 + timedelta(minutes=i)).isoformat(),
                "timestamp_s": i * 60.0,
                "is_stationary": True
            })
        return pings

    # 1. Base Depot dwell: 25 pings (stationary speed 0.0, <20m jitter)
    for i in range(25):
        pings.append({
            "lat": round(start_lat + (i % 3 - 1) * 0.00002, 6),
            "lon": round(start_lng + (i % 2) * 0.00002, 6),
            "speed_kmh": 0.0,
            "timestamp": (t0 + timedelta(minutes=i)).isoformat(),
            "timestamp_s": i * 60.0,
            "is_stationary": True
        })

    # Resolve en-route halt coordinates
    if halt_coords:
        h_lat, h_lng = halt_coords
    else:
        h_lat = (start_lat + end_lat) / 2.0
        h_lng = (start_lng + end_lng) / 2.0

    # 2. Highway transit leg 1: 40 pings moving along corridor
    t_offset = 25
    for i in range(40):
        frac = (i + 1) / 40.0
        lat = start_lat + frac * (h_lat - start_lat)
        lon = start_lng + frac * (h_lng - start_lng)
        pings.append({
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "speed_kmh": 62.5,
            "timestamp": (t0 + timedelta(minutes=t_offset + i)).isoformat(),
            "timestamp_s": (t_offset + i) * 60.0,
            "is_stationary": False
        })
    t_offset += 40

    # 3. En-route stop: stationary dwell
    actual_halt_mins = halt_mins if has_unauth_stop else 5
    for i in range(actual_halt_mins):
        pings.append({
            "lat": round(h_lat, 6),
            "lon": round(h_lng, 6),
            "speed_kmh": 0.0,
            "timestamp": (t0 + timedelta(minutes=t_offset + i)).isoformat(),
            "timestamp_s": (t_offset + i) * 60.0,
            "is_stationary": True
        })
    t_offset += actual_halt_mins

    # 4. Highway transit leg 2: 35 pings moving to destination site
    for i in range(35):
        frac = (i + 1) / 35.0
        lat = h_lat + frac * (end_lat - h_lat)
        lon = h_lng + frac * (end_lng - h_lng)
        pings.append({
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "speed_kmh": 58.0,
            "timestamp": (t0 + timedelta(minutes=t_offset + i)).isoformat(),
            "timestamp_s": (t_offset + i) * 60.0,
            "is_stationary": False
        })
    t_offset += 35

    # 5. Customer Job Site dwell: stationary pings to complete 180 pings
    remaining_pings = max(10, 180 - len(pings))
    for i in range(remaining_pings):
        pings.append({
            "lat": round(end_lat + (i % 4 - 1) * 0.00002, 6),
            "lon": round(end_lng + (i % 3) * 0.00002, 6),
            "speed_kmh": 0.0,
            "timestamp": (t0 + timedelta(minutes=t_offset + i)).isoformat(),
            "timestamp_s": (t_offset + i) * 60.0,
            "is_stationary": True
        })

    return pings


@router.get("/routes", response_model=RouteResponse)
async def get_technician_routes(
    technician_id: str = Query(..., description="Technician ID e.g. TECH-01 or TECH-001"),
    date: Optional[str] = Query(None, description="ISO Date e.g. 2026-09-22"),
    sync_service: SyncService = Depends(get_sync_service)
) -> Dict[str, Any]:
    """
    Returns dynamically computed route inspection telemetry for a technician.
    Executes telematics_engine.analyze_route_journey with genuine 5 km Haversine clustering,
    duration-weighted 3D Cartesian centroids, jitter suppression, and anomaly detection.
    """
    target_date = date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    norm_id = normalize_tech_id(technician_id)

    # 1. Resolve technician from synchronized roster
    technicians = sync_service.get_all_technicians()
    matched_tech: Optional[Dict[str, Any]] = None
    for t in technicians:
        curr_id = t.get("technician_id") or t.get("id") or ""
        if normalize_tech_id(curr_id) == norm_id:
            matched_tech = t
            break

    if not matched_tech:
        raise HTTPException(
            status_code=404,
            detail=f"No telematics route found for technician {technician_id} on {target_date}"
        )

    # 2. Resolve origin base coordinates from technician's regional hub
    region = matched_tech.get("region", "Punjab")
    hub = KroneMockGenerator.HUBS.get(region, KroneMockGenerator.HUBS["Punjab"])
    base_coords = {
        "name": hub["name"],
        "lat": float(hub["lat"]),
        "lng": float(hub["lng"]),
        "lon": float(hub["lng"])
    }

    # 3. Resolve destination job site coordinates
    active_job_id = matched_tech.get("active_job_id")
    job_spec = JOB_SITE_DIRECTORY.get(active_job_id) if active_job_id else None

    if job_spec:
        dest_coords = {
            "name": job_spec["name"],
            "lat": float(job_spec["lat"]),
            "lng": float(job_spec["lng"]),
            "lon": float(job_spec["lng"])
        }
        has_unauth_stop = job_spec.get("has_unauthorized_stop", False)
        halt_coords = job_spec.get("halt_coords")
        halt_mins = job_spec.get("halt_mins", 25)
    else:
        # Stationary dwell at base if on leave or available without active ticket
        dest_coords = dict(base_coords)
        has_unauth_stop = False
        halt_coords = None
        halt_mins = 0

    # 4. Generate or retrieve chronological GPS breadcrumb pings
    scheduled_start = f"{target_date}T08:00:00Z"
    pings = generate_corridor_pings(
        start_lat=base_coords["lat"],
        start_lng=base_coords["lng"],
        end_lat=dest_coords["lat"],
        end_lng=dest_coords["lng"],
        date_str=target_date,
        start_time_iso=scheduled_start,
        has_unauth_stop=has_unauth_stop,
        halt_coords=halt_coords,
        halt_mins=halt_mins
    )

    # 5. Dynamically execute telematics engine route inspection
    canonical_id = matched_tech.get("technician_id", technician_id)
    tech_name = matched_tech.get("name", "Krone Field Specialist")

    analysis_result = analyze_route_journey(
        pings=pings,
        base_coords=base_coords,
        job_site_coords=dest_coords,
        technician_id=canonical_id,
        technician_name=tech_name
    )

    # 6. Format and enrich metadata
    clean_date = target_date.replace("-", "")
    analysis_result["date"] = target_date
    analysis_result["technician_phone"] = matched_tech.get("phone", "+91 98140 88210")
    analysis_result["vehicle_number"] = matched_tech.get("vehicle_number", f"PB-10-KR-0101")
    analysis_result["vehicle_type"] = "Service Van Mahindra Bolero Maxi"
    analysis_result["trip_id"] = f"TRIP-{canonical_id}-{clean_date}"

    return analysis_result
