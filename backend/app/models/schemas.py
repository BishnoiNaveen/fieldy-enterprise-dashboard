"""
backend/app/models/schemas.py
Pydantic v2 Domain Schemas for Jobs, Technicians, Machinery, Pulse, Sync, and Analytics
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator


# =====================================================================
# 1. DOMAIN ENUMS
# =====================================================================

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
    AMC = "AMC"
    WARRANTY = "Warranty"
    INTERNAL = "Internal"
    TRAINING = "Training"


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


class LeaveType(str, Enum):
    SICK = "Sick Leave"
    CASUAL = "Casual Leave"
    EARNED = "Earned Leave"
    WEEKLY_OFF = "Weekly Off"


class MachineHealthStatus(str, Enum):
    OPTIMAL = "Optimal"
    UNDER_SERVICE = "Under Service"
    ATTENTION_REQUIRED = "Attention Required"
    CRITICAL = "Critical Breakdown"


class TimeframeEnum(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


# =====================================================================
# 2. SHARED SUB-MODELS
# =====================================================================

class GeoPoint(BaseModel):
    """Geographic coordinate representation."""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    lat: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees")
    lng: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees")
    address: Optional[str] = Field(None, description="Human readable site address")
    name: Optional[str] = Field(None, description="Location name")
    departed_at: Optional[str] = None
    arrived_at: Optional[str] = None


# =====================================================================
# 3. LIVE OPERATIONAL PULSE MODELS (R1)
# =====================================================================

class TechnicianLiveOnJob(BaseModel):
    """Technician currently active on an in-progress job."""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    technician_id: str = Field(..., description="Technician identifier e.g. TECH-01")
    name: str = Field(..., description="Technician full name")
    status: str = Field(..., description="e.g. On Paid Job")
    live_job_id: Optional[str] = Field(None, description="Work order number e.g. SR-26-0101")
    customer_company: Optional[str] = Field(None, description="Client company name e.g. Reliance Industries Limited")
    machine_asset: Optional[str] = Field(None, description="Equipment name e.g. Krone BigPack 1290 HDP")
    current_location: Optional[GeoPoint] = Field(None, description="Live coordinates")
    elapsed_minutes: Optional[int] = Field(0, description="Minutes elapsed on job")
    is_paid_job: bool = Field(True, description="True if paid job")
    hourly_billable_rate: Optional[float] = Field(625.0, description="Derived hourly billing rate")


class TechnicianOnLeave(BaseModel):
    """Technician currently on approved leave or scheduled off."""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    technician_id: str
    name: str
    region: str
    leave_type: str
    return_date: Optional[str] = None


class JobItem(BaseModel):
    """Job record displayed in today's work order table."""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    job_id: str = Field(..., description="Work order number e.g. SR-26-0149 or JOBZ 314")
    status: str = Field(..., description="In Progress, Completed, etc.")
    status_color: Optional[str] = Field("#059669", description="Hex status badge color")
    customer_name: str = Field(..., description="Client company or contact")
    assigned_technicians: List[str] = Field(default_factory=list, description="Names of assigned personnel")
    machine_serial: Optional[str] = Field(None, description="Equipment serial number")
    machine_name: Optional[str] = Field(None, description="Equipment model name")
    job_type: str = Field("Paid", description="Paid, AMC, Warranty, etc.")
    scheduled_start: Optional[str] = Field(None, description="Scheduled start timestamp")
    scheduled_end: Optional[str] = None
    title: Optional[str] = Field(None, description="Service task summary")
    priority: Optional[str] = Field("Normal", description="Priority level")


class MachineryUnderService(BaseModel):
    """Machine asset currently undergoing maintenance or breakdown repair."""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    asset_name: str = Field(..., description="Krone machine model name")
    serial_number: str = Field(..., description="Unique serial number e.g. BP1290-78401")
    client_company_name: str = Field(..., description="Owner organization")
    site_contact_person: str = Field(..., description="Contact name and phone")
    location: str = Field(..., description="Facility or farm location")
    active_job_id: str = Field(..., description="Associated SR-26-XXXX job")
    service_type: str = Field(..., description="Nature of service e.g. Calibration, 500h PM")
    operating_hours: Optional[float] = Field(None, description="Lifetime machine engine/baler hours")
    health_status: Optional[str] = Field("Under Service", description="Operational health condition")
    last_serviced_date: Optional[str] = Field(None, description="Last maintenance date")


class PulseKpis(BaseModel):
    """Executive KPI summary block."""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    technicians_on_paid_jobs: int = Field(..., ge=0)
    technicians_active_total: int = Field(..., ge=0)
    technicians_on_leave: int = Field(..., ge=0)
    total_jobs_today: int = Field(..., ge=0)
    jobs_completed_today: int = Field(..., ge=0)
    fleet_utilization_pct: float = Field(..., ge=0.0, le=100.0)
    machines_under_service: Optional[int] = None


class PulseResponse(BaseModel):
    """Response contract for GET /api/dashboard/pulse."""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    timestamp: str
    kpis: PulseKpis
    technicians_on_jobs: List[TechnicianLiveOnJob]
    today_jobs: List[JobItem]
    machines_under_service: List[MachineryUnderService]
    technicians_on_leave: Optional[List[TechnicianOnLeave]] = Field(default_factory=list)
    sync_meta: Optional[Dict[str, Any]] = None


# =====================================================================
# 4. SYNCHRONIZATION SCHEMAS (R1 & R4)
# =====================================================================

class SyncRequest(BaseModel):
    """Request body for POST /api/dashboard/sync."""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    force_refresh: bool = Field(False, description="Force fresh fetch bypassing cache")
    modules: Optional[List[str]] = Field(None, description="Target modules to sync")


class SyncResponse(BaseModel):
    """Response contract for POST /api/dashboard/sync."""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    status: str = Field("success", description="Sync status")
    last_synced_at: str = Field(..., description="Timestamp of completed sync")
    records_synced: int = Field(..., description="Total count of updated records")
    source: str = Field(..., description="fieldy_live, fieldy_cache, or synthetic_fallback")
    sync_id: Optional[str] = Field(None, description="Unique sync transaction ID")
    duration_ms: Optional[float] = Field(None, description="Sync duration in milliseconds")
    records_updated: Optional[Dict[str, int]] = Field(None, description="Breakdown by entity")
    message: Optional[str] = Field("Synchronization completed successfully", description="Status message")


# =====================================================================
# 5. PRODUCTIVITY ANALYTICS SCHEMAS (R2)
# =====================================================================

class ProductivitySummary(BaseModel):
    """Aggregated hours summary adhering to conservation math."""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    total_working_hours: float = Field(..., description="Productive on-job hours")
    total_travelling_hours: float = Field(..., description="Telematics transit hours")
    total_idle_hours: float = Field(..., description="Inactive or unauthorized hours")
    total_shift_hours: float = Field(..., description="Total shift duration")
    average_utilization_pct: float = Field(..., description="Working / Shift * 100")
    total_distance_km: Optional[float] = Field(None, description="Total verified transit distance")
    jobs_completed_count: Optional[int] = Field(None, description="Count of closed tickets")

    @field_validator("total_shift_hours")
    @classmethod
    def validate_conservation(cls, v: float, info: Any) -> float:
        values = info.data
        if "total_working_hours" in values and "total_travelling_hours" in values and "total_idle_hours" in values:
            expected_sum = values["total_working_hours"] + values["total_travelling_hours"] + values["total_idle_hours"]
            if abs(v - expected_sum) > 0.05:
                raise ValueError(f"Shift hours conservation violated: {v} != {expected_sum}")
        return v


class TechnicianProductivityRecord(BaseModel):
    """Individual technician productivity scorecard entry."""
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
    distance_km: Optional[float] = None
    travel_distance_km: Optional[float] = None
    billable_revenue_inr: Optional[float] = None
    deputation_revenue_inr: Optional[float] = None
    man_days: Optional[float] = None
    performance_badge: Optional[str] = None
    status_rating: Optional[str] = None


class TrendDataPoint(BaseModel):
    """Time series point for stacked bar / area charts."""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    period: str = Field(..., description="Date YYYY-MM-DD or Month name")
    working: float
    travelling: float
    idle: float
    day_of_week: Optional[str] = None
    distance_km: Optional[float] = None


class CustomerDistribution(BaseModel):
    """Distribution of service hours across customer organizations."""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    customer_name: Optional[str] = None
    client_company_name: Optional[str] = None
    total_hours: float
    percentage: float
    jobs_count: int


class ProductivityResponse(BaseModel):
    """Response contract for GET /api/analytics/productivity."""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    timeframe: str = Field(..., description="daily, weekly, or monthly")
    summary: ProductivitySummary
    technician_records: List[TechnicianProductivityRecord]
    trend_data: List[TrendDataPoint]
    date_range: Optional[Dict[str, str]] = None
    customer_distribution: Optional[List[CustomerDistribution]] = None


# =====================================================================
# 6. ENTITY CATALOG SCHEMAS (Technicians & Jobs API)
# =====================================================================

class TechnicianDetail(BaseModel):
    """Full profile for GET /api/technicians."""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    technician_id: str
    name: str
    role: str
    region: str
    phone: str
    status: str
    email: Optional[str] = None
    active_job_id: Optional[str] = None
    active_job_title: Optional[str] = None
    vehicle_number: Optional[str] = None
    deputation_rate_per_day: float = 5000.0
    da_rate_per_day: float = 2000.0
    travel_rate_per_km: Optional[float] = 5.0
    total_hours_today: Optional[float] = 0.0
    last_ping_time: Optional[str] = None
    current_location: Optional[GeoPoint] = None
    last_coordinates: Optional[GeoPoint] = None


class TechniciansListResponse(BaseModel):
    """Response for GET /api/technicians."""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    status: str = "success"
    count: int
    data: List[TechnicianDetail]


class JobDetail(BaseModel):
    """Full detail for GET /api/jobs."""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    job_id: str
    title: str
    status: str
    priority: Optional[str] = "Normal"
    service_category: Optional[str] = None
    customer_name: Optional[str] = None
    client_company_name: Optional[str] = None
    asset_name: Optional[str] = None
    asset_serial: Optional[str] = None
    machine_name: Optional[str] = None
    machine_serial: Optional[str] = None
    site_address: Optional[str] = None
    location: Optional[str] = None
    site_contact_person: Optional[str] = None
    assigned_technicians: List[str] = Field(default_factory=list)
    assigned_technician_ids: Optional[List[str]] = Field(default_factory=list)
    job_type: Optional[str] = "Paid"
    scheduled_date: Optional[str] = None
    scheduled_start: Optional[str] = None
    scheduled_end: Optional[str] = None
    actual_start: Optional[str] = None
    duration_hours: Optional[float] = 4.0
    created_at: Optional[str] = None


class JobsListResponse(BaseModel):
    """Response for GET /api/jobs."""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    status: str = "success"
    count: int
    data: List[JobDetail]
