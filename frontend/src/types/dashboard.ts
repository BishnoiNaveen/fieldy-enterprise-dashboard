/**
 * frontend/src/types/dashboard.ts
 * Authoritative TypeScript interfaces matching FastAPI backend Pydantic v2 schemas.
 */

// =====================================================================
// 1. DOMAIN ENUMS & LITERALS
// =====================================================================

export type JobStatus =
  | 'Draft'
  | 'Open'
  | 'Assigned'
  | 'Start Travel'
  | 'Reached'
  | 'In Progress'
  | 'Hold'
  | 'Completed'
  | 'Cancelled';

export type JobPriority = 'Low' | 'Medium' | 'High' | 'Emergency';

export type JobType = 'Paid' | 'Unpaid' | 'AMC' | 'Warranty' | 'Internal' | 'Training';

export type ServiceCategory = 'General Service' | 'Amc' | 'AMC Service' | 'Breakdown';

export type TechnicianOperationalStatus =
  | 'On Paid Job'
  | 'On Unpaid Job'
  | 'Travelling'
  | 'Available'
  | 'On Holiday/Leave';

export type LeaveType = 'Sick Leave' | 'Casual Leave' | 'Earned Leave' | 'Weekly Off';

export type MachineHealthStatus = 'Optimal' | 'Under Service' | 'Attention Required' | 'Critical Breakdown';

export type Timeframe = 'daily' | 'weekly' | 'monthly';

// =====================================================================
// 2. SHARED SUB-MODELS
// =====================================================================

export interface GeoPoint {
  lat: number;
  lng: number;
  address?: string;
  name?: string;
  departed_at?: string;
  arrived_at?: string;
}

export interface JourneyLocation {
  name: string;
  lat: number;
  lng: number;
  departed_at?: string;
  arrived_at?: string;
}

// =====================================================================
// 3. LIVE OPERATIONAL PULSE (R1)
// =====================================================================

export interface PulseKpis {
  technicians_on_paid_jobs: number;
  technicians_active_total: number;
  technicians_on_leave: number;
  total_jobs_today: number;
  jobs_completed_today: number;
  fleet_utilization_pct: number;
  machines_under_service?: number;
  total_fieldy_jobs?: number;
  total_fieldy_amcs?: number;
}

export interface TechnicianLiveOnJob {
  technician_id: string;
  name: string;
  status: string;
  live_job_id?: string;
  customer_company?: string;
  machine_asset?: string;
  current_location?: GeoPoint;
  elapsed_minutes?: number;
  is_paid_job: boolean;
  hourly_billable_rate?: number;
}

export interface TechnicianOnLeave {
  technician_id: string;
  name: string;
  region: string;
  leave_type: string;
  return_date?: string;
}

export interface JobItem {
  job_id: string; // e.g. "SR-26-0101"
  status: string;
  status_color?: string;
  customer_name: string;
  assigned_technicians: string[];
  machine_serial?: string;
  machine_name?: string;
  job_type: string;
  scheduled_start?: string;
  scheduled_end?: string;
  title?: string;
  priority?: string;
}

export interface MachineryUnderService {
  asset_name: string;
  serial_number: string;
  client_company_name: string;
  site_contact_person: string;
  location: string;
  active_job_id: string;
  service_type: string;
  operating_hours?: number;
  health_status?: string;
  last_serviced_date?: string;
}

export interface PulseResponse {
  timestamp: string;
  kpis: PulseKpis;
  technicians_on_jobs: TechnicianLiveOnJob[];
  today_jobs: JobItem[];
  machines_under_service: MachineryUnderService[];
  technicians_on_leave?: TechnicianOnLeave[];
  sync_meta?: {
    last_synced_at?: string;
    sync_source?: string;
    is_fallback_mode?: boolean;
    tenant_id?: string;
    workspace_name?: string;
    [key: string]: any;
  };
}

// =====================================================================
// 4. SYNCHRONIZATION SCHEMAS (R1 & R4)
// =====================================================================

export interface SyncRequest {
  force_refresh?: boolean;
  modules?: string[];
}

export interface SyncResponse {
  status: string;
  last_synced_at: string;
  records_synced: number;
  source: string;
  sync_id?: string;
  duration_ms?: number;
  records_updated?: Record<string, number>;
  message?: string;
}

// =====================================================================
// 5. PRODUCTIVITY ANALYTICS (R2)
// =====================================================================

export interface ProductivitySummary {
  total_working_hours: number;
  total_travelling_hours: number;
  total_idle_hours: number;
  total_shift_hours: number;
  average_utilization_pct: number;
  total_distance_km?: number;
  jobs_completed_count?: number;
}

export interface TechnicianProductivityRecord {
  technician_id: string;
  technician_name: string;
  working_hours: number;
  travelling_hours: number;
  idle_hours: number;
  shift_hours: number;
  utilization_pct: number;
  jobs_count: number;
  region?: string;
  distance_km?: number;
  travel_distance_km?: number;
  billable_revenue_inr?: number;
  deputation_revenue_inr?: number;
  man_days?: number;
  performance_badge?: string;
  status_rating?: string;
}

export interface TrendDataPoint {
  period: string;
  working: number;
  travelling: number;
  idle: number;
  day_of_week?: string;
  distance_km?: number;
}

export interface CustomerDistribution {
  customer_name?: string;
  client_company_name?: string;
  total_hours: number;
  percentage: number;
  jobs_count: number;
}

export interface ProductivityResponse {
  timeframe: Timeframe;
  summary: ProductivitySummary;
  technician_records: TechnicianProductivityRecord[];
  trend_data: TrendDataPoint[];
  date_range?: {
    start: string;
    end: string;
  };
  customer_distribution?: CustomerDistribution[];
}

export interface ProductivityFilterParams {
  timeframe?: Timeframe;
  technician_id?: string;
  customer_company?: string;
  job_status?: string;
  job_type?: string;
  start_date?: string;
  end_date?: string;
}

// =====================================================================
// 6. AUTONOMOUS ROUTE INSPECTOR & 5 KM CLUSTERING (R3)
// =====================================================================

export interface RawGpsPing {
  index?: number;
  lat: number;
  lng: number;
  speed_kmh: number;
  heading_deg?: number;
  timestamp?: string;
  battery_pct?: number;
  cluster_id?: string | null;
  status?: string;
  is_stationary?: boolean;
}

export interface Cluster5km {
  cluster_id: string;
  centroid: GeoPoint;
  radius_meters: number;
  location_name: string;
  pings_count: number;
  duration_minutes: number;
  is_job_site: boolean;
  is_base: boolean;
  zone_type?: string;
  first_ping_at?: string;
  last_ping_at?: string;
}

export interface RouteAnomaly {
  type: string;
  location: GeoPoint;
  duration_minutes: number;
  started_at?: string;
  ended_at?: string;
  description: string;
  anomaly_id?: string;
  severity?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' | string;
  title?: string;
  location_name?: string;
  distance_from_designated_route_km?: number;
  threshold_mins?: number;
  action_required?: string;
}

export interface JourneySummary {
  start_location: GeoPoint | JourneyLocation;
  destination: GeoPoint | JourneyLocation;
  transit_duration_minutes: number;
  unauthorized_stop_duration_minutes: number;
  total_distance_km: number;
  anomalies_detected: number;
  total_journey_duration_mins?: number;
  on_site_working_duration_mins?: number;
  average_speed_kmh?: number;
  max_speed_kmh?: number;
  route_compliance_pct?: number;
}

export interface RouteResponse {
  technician_id: string;
  technician_name: string;
  date: string;
  journey_summary: JourneySummary;
  raw_pings_count: number;
  clusters_5km: Cluster5km[];
  anomalies: RouteAnomaly[];
  route_polyline: [number, number][];
  technician_phone?: string;
  vehicle_number?: string;
  vehicle_type?: string;
  trip_id?: string;
  designated_route_corridor?: GeoPoint[];
  gps_breadcrumbs?: RawGpsPing[];
}

// =====================================================================
// 7. ENTITY CATALOG MODELS (Technicians & Jobs)
// =====================================================================

export interface TechnicianDetail {
  technician_id: string;
  name: string;
  role: string;
  region: string;
  phone: string;
  status: string;
  email?: string;
  active_job_id?: string;
  active_job_title?: string;
  vehicle_number?: string;
  deputation_rate_per_day: number;
  da_rate_per_day: number;
  travel_rate_per_km?: number;
  total_hours_today?: number;
  last_ping_time?: string;
  current_location?: GeoPoint;
  last_coordinates?: GeoPoint;
}

export interface JobDetail {
  job_id: string;
  title: string;
  status: string;
  priority?: string;
  service_category?: string;
  customer_name?: string;
  client_company_name?: string;
  asset_name?: string;
  asset_serial?: string;
  machine_name?: string;
  machine_serial?: string;
  site_address?: string;
  location?: string;
  site_contact_person?: string;
  assigned_technicians: string[];
  assigned_technician_ids?: string[];
  job_type?: string;
  scheduled_date?: string;
  scheduled_start?: string;
  scheduled_end?: string;
  actual_start?: string;
  duration_hours?: number;
  created_at?: string;
}

// =====================================================================
// 8. UI STATE & FILTER INTERFACES
// =====================================================================

export interface FilterState {
  timeframe: Timeframe;
  technicianId: string;
  customerCompany: string;
  jobStatus: string;
  jobType: string;
  startDate: string;
  endDate: string;
  searchQuery: string;
}

// =====================================================================
// 9. AMC CONTRACT INTERFACE
// =====================================================================

export interface AMCDetail {
  amc_id: string;
  title: string;
  customer: string;
  customer_email?: string;
  customer_phone?: string;
  status: string;
  total_value: number;
  no_of_visits: number;
  start_date: string;
  expiry_date: string;
  monthly_retainer?: number;
  emergency_visit_rate?: number;
  pm_visit_rate?: number;
  assets: string[];
  description?: string;
}

export interface AMCsListResponse {
  count: number;
  amcs: AMCDetail[];
  total_contract_value: number;
  active_count: number;
}

// =====================================================================
// 10. FORENSIC BILL AUDIT INTERFACES
// =====================================================================

export interface ForensicCheckItem {
  pillar: string;
  name: string;
  passed: boolean;
  details: string;
  disallowed_amount?: number;
}

export interface BillAuditRequest {
  technician_id: string;
  technician_name: string;
  date: string;
  claimed_km: number;
  vehicle_type: 'bike' | 'car';
  claimed_da: number;
  claimed_hotel: number;
  stay_provided_by_client: boolean;
  duty_hours: number;
  job_id?: string;
  trip_purpose?: string;
}

export interface BillAuditResponse {
  audit_id: string;
  timestamp: string;
  technician_id: string;
  technician_name: string;
  date: string;
  classification: string;
  verified_gps_km: number;
  claimed_km: number;
  admissible_km: number;
  disallowed_km: number;
  rate_per_km: number;
  km_amount_admissible: number;
  claimed_da: number;
  admissible_da: number;
  disallowed_da: number;
  claimed_hotel: number;
  admissible_hotel: number;
  disallowed_hotel: number;
  total_claimed_amount: number;
  total_admissible_amount: number;
  total_disallowed_recovery: number;
  verdict: 'APPROVED' | 'FLAGGED_PARTIAL_APPROVAL' | 'REJECTED_OVERCLAIM';
  forensic_checks: ForensicCheckItem[];
  action_required: string;
}

// =====================================================================
// 11. AUTOMATIONS & SECURITY INTERFACES
// =====================================================================

export interface WhatsAppDispatchRequest {
  job_id: string;
  recipient_phone: string;
  recipient_name: string;
  recipient_role?: 'technician' | 'customer';
  custom_message?: string;
}

export interface WhatsAppDispatchResponse {
  status: string;
  message_id: string;
  recipient: string;
  formatted_body: string;
  dispatched_at: string;
}

export interface EmailReportRequest {
  recipient_email: string;
  report_type?: string;
  subject: string;
  job_id?: string;
}

export interface EmailReportResponse {
  status: string;
  email_id: string;
  recipient: string;
  subject: string;
  sent_at: string;
}

export interface SecurityAuditResponse {
  status: string;
  overall_rating: string;
  timestamp: string;
  checks: Record<string, { status: string; details: string }>;
  active_hardening: string[];
}

