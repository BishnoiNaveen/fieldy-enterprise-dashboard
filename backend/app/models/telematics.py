"""
backend/app/models/telematics.py
Pydantic v2 Models for Autonomous Route Inspection, 5 km Clustering, and Telemetry
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict
from app.models.schemas import GeoPoint


class RawGpsPing(BaseModel):
    """Granular GPS breadcrumb ping from mobile or OBD tracker."""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    index: Optional[int] = Field(None, description="Chronological sequence index")
    lat: float = Field(..., ge=-90.0, le=90.0)
    lng: float = Field(..., ge=-180.0, le=180.0)
    speed_kmh: float = Field(0.0, ge=0.0, description="Vehicle ground speed in km/h")
    heading_deg: Optional[float] = Field(0.0, ge=0.0, le=360.0, description="Direction azimuth")
    timestamp: Optional[str] = Field(None, description="UTC ISO ping timestamp")
    battery_pct: Optional[int] = Field(None, ge=0, le=100, description="Device battery percentage")
    cluster_id: Optional[str] = Field(None, description="Assigned 5km operational zone ID")
    status: Optional[str] = Field(None, description="TRANSIT, STATIONARY, BASE_DEPARTURE, etc.")
    is_stationary: Optional[bool] = Field(False, description="True if speed < 1.5 km/h")


class RawStop(BaseModel):
    """Contiguous stationary sequence exceeding 5 minutes."""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    stop_id: Optional[str] = None
    lat: float
    lng: float
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_seconds: float
    location_name: Optional[str] = None


class Cluster5km(BaseModel):
    """
    Operational Zone formed by merging stops within a 5 km radius.
    Centroid is computed using duration-weighted 3D Cartesian spherical projection.
    """
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    cluster_id: str = Field(..., description="e.g. CLUST-01 or ZONE-01")
    centroid: GeoPoint = Field(..., description="Weighted 3D Cartesian centroid")
    radius_meters: float = Field(..., le=5000.0, description="Cluster spatial spread <= 5000m")
    location_name: str = Field(..., description="Identified operational area label")
    pings_count: int = Field(..., description="Count of aggregated telemetry pings")
    duration_minutes: float = Field(..., description="Total dwell time in minutes")
    is_job_site: bool = Field(..., description="True if within 5 km of customer job ticket")
    is_base: bool = Field(..., description="True if within 5 km of depot/hotel")
    zone_type: Optional[str] = Field(None, description="BASE_DEPOT, CUSTOMER_SITE, UNAUTHORIZED_STOP")
    first_ping_at: Optional[str] = None
    last_ping_at: Optional[str] = None


class RouteAnomaly(BaseModel):
    """Operational route anomaly flagged by route inspector."""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    type: str = Field(..., description="unauthorized_stop, route_deviation, signal_dropout, overspeed")
    location: GeoPoint = Field(..., description="Anomaly coordinates")
    duration_minutes: float = Field(..., description="Duration of anomaly condition")
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    description: str = Field(..., description="Detailed diagnostic description")
    anomaly_id: Optional[str] = None
    severity: Optional[str] = Field("MEDIUM", description="LOW, MEDIUM, HIGH, CRITICAL")
    title: Optional[str] = None
    location_name: Optional[str] = None
    distance_from_designated_route_km: Optional[float] = None
    threshold_mins: Optional[float] = 15.0
    action_required: Optional[str] = None


class JourneyLocation(BaseModel):
    """Journey endpoint (Origin Base or Customer Destination)."""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    name: str = Field(..., description="Facility or site name")
    lat: float
    lng: float
    departed_at: Optional[str] = None
    arrived_at: Optional[str] = None


class JourneySummary(BaseModel):
    """High-level summary of technician journey."""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    start_location: Union[JourneyLocation, GeoPoint]
    destination: Union[JourneyLocation, GeoPoint]
    transit_duration_minutes: float = Field(..., description="Active corridor transit time")
    unauthorized_stop_duration_minutes: float = Field(..., description="Unscheduled stop time >15m")
    total_distance_km: float = Field(..., description="Total kilometers traveled")
    anomalies_detected: int = Field(..., description="Count of detected anomalies")
    total_journey_duration_mins: Optional[float] = None
    on_site_working_duration_mins: Optional[float] = None
    average_speed_kmh: Optional[float] = None
    max_speed_kmh: Optional[float] = None
    route_compliance_pct: Optional[float] = None


class RouteResponse(BaseModel):
    """Response contract for GET /api/telematics/routes."""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    technician_id: str
    technician_name: str
    date: str = Field(..., description="ISO Date string YYYY-MM-DD")
    journey_summary: JourneySummary
    raw_pings_count: int
    clusters_5km: List[Cluster5km]
    anomalies: List[RouteAnomaly]
    route_polyline: List[List[float]] = Field(..., description="Array of [lat, lng] pairs for Leaflet")
    technician_phone: Optional[str] = None
    vehicle_number: Optional[str] = None
    vehicle_type: Optional[str] = None
    trip_id: Optional[str] = None
    designated_route_corridor: Optional[List[GeoPoint]] = None
    gps_breadcrumbs: Optional[List[RawGpsPing]] = None


# Alias for compatibility
RouteInspectorResponse = RouteResponse
