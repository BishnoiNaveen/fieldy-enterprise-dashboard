"""
Verification script for M1 Pydantic v2 domain schemas and telematics models.
Tests parsing of exact sample payloads from PROJECT.md Interface Contracts 1-4.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import json
from pydantic import BaseModel, Field, ConfigDict, field_validator


# ==========================================
# 1. ENUMS
# ==========================================

class JobStatus(str, Enum):
    DRAFT = "Draft"
    OPEN = "Open"
    ASSIGNED = "Assigned"
    START_TRAVEL = "Start Travel"
    REACHED = "Reached"
    IN_PROGRESS = "In Progress"
    HOLD = "Hold"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class JobPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    EMERGENCY = "Emergency"


class JobType(str, Enum):
    PAID = "Paid"
    UNPAID = "Unpaid"


class ServiceCategory(str, Enum):
    GENERAL = "General Service"
    AMC = "Amc"
    AMC_SERVICE = "AMC Service"
    BREAKDOWN = "Breakdown"


class TechnicianOperationalStatus(str, Enum):
    ON_PAID_JOB = "On Paid Job"
    ON_UNPAID_JOB = "On Unpaid Job"
    TRAVELLING = "Travelling"
    AVAILABLE = "Available"
    ON_HOLIDAY = "On Holiday/Leave"


class TimeframeEnum(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


# ==========================================
# 2. SUB-MODELS
# ==========================================

class GeoPoint(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    lat: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees")
    lng: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees")
    address: Optional[str] = Field(None, description="Optional geocoded address")


class TechnicianLiveOnJob(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    technician_id: str
    name: str
    status: str
    live_job_id: str
    customer_company: str
    machine_asset: str
    current_location: GeoPoint
    elapsed_minutes: Optional[int] = 0
    is_paid_job: bool = True
    hourly_billable_rate: Optional[float] = 625.0


class TechnicianOnLeave(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    technician_id: str
    name: str
    region: str
    leave_type: str
    return_date: str


class JobItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    job_id: str = Field(..., pattern=r"^SR-26-\s*[A-Za-z0-9]+$")
    status: str
    status_color: Optional[str] = "#059669"
    customer_name: str
    assigned_technicians: List[str]
    machine_serial: Optional[str] = None
    machine_name: Optional[str] = None
    job_type: str = "Paid"
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    title: Optional[str] = None
    priority: Optional[str] = "Normal"


class MachineryUnderService(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    asset_name: str
    serial_number: str
    client_company_name: str
    site_contact_person: str
    location: str
    active_job_id: str
    service_type: str
    operating_hours: Optional[float] = None
    health_status: Optional[str] = "Optimal"
    last_serviced_date: Optional[str] = None


class PulseKpis(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    technicians_on_paid_jobs: int
    technicians_active_total: int
    technicians_on_leave: int
    total_jobs_today: int
    jobs_completed_today: int
    fleet_utilization_pct: float
    machines_under_service: Optional[int] = None


class PulseResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    timestamp: datetime
    kpis: PulseKpis
    technicians_on_jobs: List[TechnicianLiveOnJob]
    today_jobs: List[JobItem]
    machines_under_service: List[MachineryUnderService]
    technicians_on_leave: Optional[List[TechnicianOnLeave]] = []
    sync_meta: Optional[Dict[str, Any]] = None


# ==========================================
# 3. SYNC SCHEMAS
# ==========================================

class SyncRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    force_refresh: bool = True
    modules: Optional[List[str]] = None


class SyncResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    status: str
    last_synced_at: datetime
    records_synced: int
    source: str
    sync_id: Optional[str] = None
    duration_ms: Optional[int] = None
    records_updated: Optional[Dict[str, int]] = None
    message: Optional[str] = "Sync completed successfully."


# ==========================================
# 4. PRODUCTIVITY SCHEMAS
# ==========================================

class ProductivitySummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    total_working_hours: float
    total_travelling_hours: float
    total_idle_hours: float
    total_shift_hours: float
    average_utilization_pct: float
    total_distance_km: Optional[float] = None
    jobs_completed_count: Optional[int] = None


class TechnicianProductivityRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    technician_id: str
    technician_name: str
    working_hours: float
    travelling_hours: float
    idle_hours: float
    shift_hours: float
    utilization_pct: float
    jobs_count: int
    region: Optional[str] = None
    travel_distance_km: Optional[float] = None
    deputation_revenue_inr: Optional[float] = None


class TrendDataPoint(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    period: str
    working: float
    travelling: float
    idle: float
    day_of_week: Optional[str] = None
    distance_km: Optional[float] = None


class CustomerDistribution(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    client_company_name: str
    total_hours: float
    percentage: float
    jobs_count: int


class ProductivityResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    timeframe: str
    summary: ProductivitySummary
    technician_records: List[TechnicianProductivityRecord]
    trend_data: List[TrendDataPoint]
    date_range: Optional[Dict[str, str]] = None
    customer_distribution: Optional[List[CustomerDistribution]] = None


# ==========================================
# 5. TELEMATICS SCHEMAS
# ==========================================

class JourneyLocation(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    name: str
    lat: float
    lng: float
    departed_at: Optional[datetime] = None
    arrived_at: Optional[datetime] = None


class JourneySummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    start_location: JourneyLocation
    destination: JourneyLocation
    transit_duration_minutes: float
    unauthorized_stop_duration_minutes: float
    total_distance_km: float
    anomalies_detected: int
    total_journey_duration_mins: Optional[float] = None
    on_site_working_duration_mins: Optional[float] = None
    average_speed_kmh: Optional[float] = None
    max_speed_kmh: Optional[float] = None
    route_compliance_pct: Optional[float] = None


class Cluster5km(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    cluster_id: str
    centroid: GeoPoint
    radius_meters: float
    location_name: str
    pings_count: int
    duration_minutes: float
    is_job_site: bool
    is_base: bool
    zone_type: Optional[str] = None
    first_ping_at: Optional[datetime] = None
    last_ping_at: Optional[datetime] = None


class RouteAnomaly(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    type: str
    location: GeoPoint
    duration_minutes: float
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    description: str
    anomaly_id: Optional[str] = None
    severity: Optional[str] = "MEDIUM"
    title: Optional[str] = None
    location_name: Optional[str] = None
    distance_from_designated_route_km: Optional[float] = None


class RawGpsPing(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    index: int
    lat: float
    lng: float
    speed_kmh: float
    heading_deg: Optional[float] = 0.0
    timestamp: datetime
    battery_pct: Optional[int] = None
    cluster_id: Optional[str] = None
    status: Optional[str] = None


class RouteResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    technician_id: str
    technician_name: str
    date: str
    journey_summary: JourneySummary
    raw_pings_count: int
    clusters_5km: List[Cluster5km]
    anomalies: List[RouteAnomaly]
    route_polyline: List[List[float]]
    designated_route_corridor: Optional[List[GeoPoint]] = None
    gps_breadcrumbs: Optional[List[RawGpsPing]] = None


# ==========================================
# 6. VERIFICATION AGAINST PROJECT.MD CONTRACTS
# ==========================================

def test_pulse_contract():
    raw_pulse = {
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
    obj = PulseResponse.model_validate(raw_pulse)
    assert obj.kpis.technicians_on_paid_jobs == 8
    assert obj.today_jobs[0].job_id == "SR-26-0101"
    print("[PASS] Contract 1: PulseResponse parsed successfully")


def test_sync_contract():
    raw_sync_req = { "force_refresh": True }
    req = SyncRequest.model_validate(raw_sync_req)
    assert req.force_refresh is True

    raw_sync_resp = {
        "status": "success",
        "last_synced_at": "2026-09-22T12:00:00Z",
        "records_synced": 42,
        "source": "fieldy_cache"
    }
    resp = SyncResponse.model_validate(raw_sync_resp)
    assert resp.records_synced == 42
    print("[PASS] Contract 2: SyncRequest & SyncResponse parsed successfully")


def test_productivity_contract():
    raw_prod = {
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
    resp = ProductivityResponse.model_validate(raw_prod)
    assert resp.summary.total_shift_hours == 96.0
    assert len(resp.technician_records) == 1
    print("[PASS] Contract 3: ProductivityResponse parsed successfully")


def test_telematics_contract():
    raw_routes = {
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
          "is_job_site": False,
          "is_base": True
        },
        {
          "cluster_id": "CLUST-02",
          "centroid": { "lat": 30.3800, "lng": 76.8405 },
          "radius_meters": 820,
          "location_name": "RIL Barwala Bio-Mass Job Site",
          "pings_count": 110,
          "duration_minutes": 390,
          "is_job_site": True,
          "is_base": False
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
    resp = RouteResponse.model_validate(raw_routes)
    assert resp.raw_pings_count == 180
    assert len(resp.clusters_5km) == 2
    assert len(resp.anomalies) == 1
    assert len(resp.route_polyline) == 4
    print("[PASS] Contract 4: RouteResponse parsed successfully")


if __name__ == "__main__":
    test_pulse_contract()
    test_sync_contract()
    test_productivity_contract()
    test_telematics_contract()
    print("\nALL CONTRACTS VERIFIED SUCCESSFULLY WITH 100% PYDANTIC V2 COMPLIANCE!")
