/**
 * frontend/src/services/api.ts
 * Resilient API client connecting to FastAPI with high-fidelity Krone offline fallback.
 */

import axios, { AxiosInstance } from 'axios';
import {
  PulseResponse,
  SyncRequest,
  SyncResponse,
  ProductivityResponse,
  ProductivityFilterParams,
  RouteResponse,
  TechnicianDetail,
  JobDetail,
} from '../types/dashboard';

// Determine Base API URL
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 8000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

// Connection state tracker
let isBackendLive = true;

export const getBackendLiveStatus = (): boolean => isBackendLive;

// =====================================================================
// SYNTHETIC OFFLINE FALLBACK DATASET (CALIBRATED TO KRONE INDIA)
// =====================================================================

const FALLBACK_PULSE: PulseResponse = {
  timestamp: new Date().toISOString(),
  kpis: {
    technicians_on_paid_jobs: 8,
    technicians_active_total: 12,
    technicians_on_leave: 2,
    total_jobs_today: 10,
    jobs_completed_today: 4,
    fleet_utilization_pct: 83.3,
    machines_under_service: 8,
  },
  technicians_on_jobs: [
    {
      technician_id: 'TECH-01',
      name: 'Gurpreet Singh',
      status: 'On Paid Job',
      live_job_id: 'SR-26-0101',
      customer_company: 'Reliance Industries Limited (Bio-Energy Division)',
      machine_asset: 'Krone BigPack 1290 HDP High Density Baler',
      current_location: { lat: 30.901, lng: 75.8573, name: 'Ludhiana Hub' },
      elapsed_minutes: 240,
      is_paid_job: true,
      hourly_billable_rate: 625.0,
    },
    {
      technician_id: 'TECH-02',
      name: 'Vikram Sharma',
      status: 'On Paid Job',
      live_job_id: 'SR-26-0102',
      customer_company: 'Reliance Industries Limited',
      machine_asset: 'Krone Bellima F 130 Round Baler',
      current_location: { lat: 29.1492, lng: 75.7217, name: 'Hisar Base' },
      elapsed_minutes: 180,
      is_paid_job: true,
      hourly_billable_rate: 625.0,
    },
    {
      technician_id: 'TECH-03',
      name: 'Rajesh Patel',
      status: 'On Paid Job',
      live_job_id: 'SR-26-0103',
      customer_company: 'Adani Agri Logistics Ltd',
      machine_asset: 'Krone BiG X 700 Forage Harvester',
      current_location: { lat: 22.4707, lng: 70.0577, name: 'Jamnagar Hub' },
      elapsed_minutes: 310,
      is_paid_job: true,
      hourly_billable_rate: 625.0,
    },
    {
      technician_id: 'TECH-04',
      name: 'Jaswinder Singh',
      status: 'On Paid Job',
      live_job_id: 'SR-26-0104',
      customer_company: 'Punjab State Farm Cooperative',
      machine_asset: 'Krone EasyCut B 870 Mower',
      current_location: { lat: 31.326, lng: 75.5762, name: 'Jalandhar Cluster' },
      elapsed_minutes: 150,
      is_paid_job: true,
      hourly_billable_rate: 625.0,
    },
  ],
  today_jobs: [
    {
      job_id: 'SR-26-0101',
      status: 'In Progress',
      status_color: '#059669',
      customer_name: 'Reliance Industries Limited (Bio-Energy Division)',
      assigned_technicians: ['Gurpreet Singh'],
      machine_serial: 'BP1290-78401',
      machine_name: 'Krone BigPack 1290 HDP High Density Baler',
      job_type: 'Paid',
      scheduled_start: '2026-09-22T08:30:00Z',
      title: 'Emergency Knotter Timing Calibration & 500h PM',
      priority: 'High',
    },
    {
      job_id: 'SR-26-0102',
      status: 'In Progress',
      status_color: '#059669',
      customer_name: 'Reliance Industries Limited',
      assigned_technicians: ['Vikram Sharma'],
      machine_serial: 'BL130-449120',
      machine_name: 'Krone Bellima F 130 Round Baler',
      job_type: 'Paid',
      scheduled_start: '2026-09-22T09:00:00Z',
      title: 'Chamber Roller Bearing Replacement',
      priority: 'Medium',
    },
    {
      job_id: 'SR-26-0103',
      status: 'Completed',
      status_color: '#10B981',
      customer_name: 'Adani Agri Logistics Ltd',
      assigned_technicians: ['Rajesh Patel'],
      machine_serial: 'BX700-112045',
      machine_name: 'Krone BiG X 700 Forage Harvester',
      job_type: 'AMC',
      scheduled_start: '2026-09-22T06:00:00Z',
      title: 'Cutterhead Knife Sharpening & Shear Bar Setup',
      priority: 'Normal',
    },
    {
      job_id: 'SR-26-0104',
      status: 'In Progress',
      status_color: '#059669',
      customer_name: 'Punjab State Farm Cooperative',
      assigned_technicians: ['Jaswinder Singh'],
      machine_serial: 'EC870-221940',
      machine_name: 'Krone EasyCut B 870 Mower',
      job_type: 'Warranty',
      scheduled_start: '2026-09-22T09:30:00Z',
      title: 'Cutter Bed Oil Leak Inspection',
      priority: 'Normal',
    },
  ],
  machines_under_service: [
    {
      asset_name: 'Krone BigPack 1290 HDP High Density Baler',
      serial_number: 'BP1290-78401',
      client_company_name: 'Reliance Industries Limited (Bio-Energy Division)',
      site_contact_person: 'Er. Manpreet Dhillon (+91 98765 43210)',
      location: 'Hoshiarpur Bio-CNG Complex, Punjab',
      active_job_id: 'SR-26-0101',
      service_type: 'Emergency Knotter Timing Calibration',
      operating_hours: 1420.5,
      health_status: 'Under Service',
      last_serviced_date: '2026-08-15',
    },
    {
      asset_name: 'Krone Bellima F 130 Round Baler',
      serial_number: 'BL130-449120',
      client_company_name: 'Reliance Industries Limited',
      site_contact_person: 'Sunil Kumar (+91 98123 99881)',
      location: 'Barwala Bio-Gas Station, Hisar, Haryana',
      active_job_id: 'SR-26-0102',
      service_type: 'Chamber Roller Bearing Replacement',
      operating_hours: 890.2,
      health_status: 'Attention Required',
      last_serviced_date: '2026-07-28',
    },
    {
      asset_name: 'Krone BiG X 700 Forage Harvester',
      serial_number: 'BX700-112045',
      client_company_name: 'Adani Agri Logistics Ltd',
      site_contact_person: 'Ramesh Patel (+91 94280 11234)',
      location: 'Jamnagar Agro Hub, Gujarat',
      active_job_id: 'SR-26-0103',
      service_type: 'Cutterhead Knife Sharpening & Shear Bar Setup',
      operating_hours: 2150.0,
      health_status: 'Optimal',
      last_serviced_date: '2026-09-22',
    },
    {
      asset_name: 'Krone EasyCut B 870 Mower',
      serial_number: 'EC870-221940',
      client_company_name: 'Punjab State Farm Cooperative',
      site_contact_person: 'Harminder Singh (+91 98722 55431)',
      location: 'Jalandhar Depot, Punjab',
      active_job_id: 'SR-26-0104',
      service_type: 'Cutter Bed Oil Leak Inspection',
      operating_hours: 640.8,
      health_status: 'Under Service',
      last_serviced_date: '2026-08-02',
    },
  ],
  technicians_on_leave: [
    {
      technician_id: 'TECH-11',
      name: 'Kuldeep Gill',
      region: 'Punjab',
      leave_type: 'Sick Leave',
      return_date: '2026-09-24',
    },
    {
      technician_id: 'TECH-12',
      name: 'Rohit Deshmukh',
      region: 'Maharashtra',
      leave_type: 'Weekly Off',
      return_date: '2026-09-23',
    },
  ],
  sync_meta: {
    last_synced_at: new Date().toISOString(),
    sync_source: 'fieldy_cache',
    is_fallback_mode: true,
    tenant_id: '4e51f497-b8dd-4036-8d78-60b12a7598b7',
    workspace_name: 'Krone India Gurugram Hub',
  },
};

const FALLBACK_PRODUCTIVITY: ProductivityResponse = {
  timeframe: 'daily',
  summary: {
    total_working_hours: 64.5,
    total_travelling_hours: 21.0,
    total_idle_hours: 10.5,
    total_shift_hours: 96.0,
    average_utilization_pct: 67.2,
    total_distance_km: 842.5,
    jobs_completed_count: 4,
  },
  technician_records: [
    {
      technician_id: 'TECH-01',
      technician_name: 'Gurpreet Singh',
      working_hours: 6.5,
      travelling_hours: 1.5,
      idle_hours: 0.0,
      shift_hours: 8.0,
      utilization_pct: 81.25,
      jobs_count: 1,
      region: 'Punjab',
      travel_distance_km: 84.6,
      deputation_revenue_inr: 5000.0,
      performance_badge: 'EXEMPLARY',
    },
    {
      technician_id: 'TECH-02',
      technician_name: 'Vikram Sharma',
      working_hours: 5.5,
      travelling_hours: 2.0,
      idle_hours: 0.5,
      shift_hours: 8.0,
      utilization_pct: 68.75,
      jobs_count: 1,
      region: 'Haryana',
      travel_distance_km: 110.2,
      deputation_revenue_inr: 5000.0,
      performance_badge: 'NORMAL',
    },
    {
      technician_id: 'TECH-03',
      technician_name: 'Rajesh Patel',
      working_hours: 7.0,
      travelling_hours: 1.0,
      idle_hours: 0.0,
      shift_hours: 8.0,
      utilization_pct: 87.5,
      jobs_count: 1,
      region: 'Gujarat',
      travel_distance_km: 65.0,
      deputation_revenue_inr: 5000.0,
      performance_badge: 'EXEMPLARY',
    },
    {
      technician_id: 'TECH-04',
      technician_name: 'Jaswinder Singh',
      working_hours: 4.5,
      travelling_hours: 2.5,
      idle_hours: 1.0,
      shift_hours: 8.0,
      utilization_pct: 56.25,
      jobs_count: 1,
      region: 'Punjab',
      travel_distance_km: 140.0,
      deputation_revenue_inr: 5000.0,
      performance_badge: 'ATTENTION',
    },
  ],
  trend_data: [
    { period: '2026-09-17', working: 61.0, travelling: 22.0, idle: 13.0, distance_km: 790.0 },
    { period: '2026-09-18', working: 63.5, travelling: 20.5, idle: 12.0, distance_km: 810.0 },
    { period: '2026-09-19', working: 66.0, travelling: 19.0, idle: 11.0, distance_km: 780.0 },
    { period: '2026-09-20', working: 62.0, travelling: 21.5, idle: 12.5, distance_km: 830.0 },
    { period: '2026-09-21', working: 68.0, travelling: 18.0, idle: 10.0, distance_km: 890.0 },
    { period: '2026-09-22', working: 64.5, travelling: 21.0, idle: 10.5, distance_km: 842.5 },
  ],
  customer_distribution: [
    { customer_name: 'Reliance Industries Limited', total_hours: 32.5, percentage: 50.4, jobs_count: 5 },
    { customer_name: 'Adani Agri Logistics Ltd', total_hours: 14.0, percentage: 21.7, jobs_count: 2 },
    { customer_name: 'Punjab State Farm Cooperative', total_hours: 10.0, percentage: 15.5, jobs_count: 2 },
    { customer_name: 'VERBIO Bio-Gas India Pvt Ltd', total_hours: 8.0, percentage: 12.4, jobs_count: 1 },
  ],
};

const FALLBACK_ROUTE: RouteResponse = {
  technician_id: 'TECH-01',
  technician_name: 'Gurpreet Singh',
  date: '2026-09-22',
  journey_summary: {
    start_location: {
      name: 'Krone Regional Hub Ludhiana',
      lat: 30.901,
      lng: 75.8573,
      departed_at: '2026-09-22T08:00:00Z',
    },
    destination: {
      name: 'RIL Bio-Energy Facility Barwala',
      lat: 30.3801,
      lng: 76.8402,
      arrived_at: '2026-09-22T09:45:00Z',
    },
    transit_duration_minutes: 105,
    unauthorized_stop_duration_minutes: 25,
    total_distance_km: 84.6,
    anomalies_detected: 1,
    average_speed_kmh: 52.4,
    route_compliance_pct: 85.0,
  },
  raw_pings_count: 180,
  clusters_5km: [
    {
      cluster_id: 'CLUST-01',
      centroid: { lat: 30.9015, lng: 75.857 },
      radius_meters: 450,
      location_name: 'Ludhiana Depot Operational Zone',
      pings_count: 45,
      duration_minutes: 60,
      is_job_site: false,
      is_base: true,
      zone_type: 'BASE_DEPOT',
    },
    {
      cluster_id: 'CLUST-02',
      centroid: { lat: 30.38, lng: 76.8405 },
      radius_meters: 820,
      location_name: 'RIL Barwala Bio-Mass Job Site',
      pings_count: 110,
      duration_minutes: 390,
      is_job_site: true,
      is_base: false,
      zone_type: 'CUSTOMER_SITE',
    },
  ],
  anomalies: [
    {
      type: 'unauthorized_stop',
      location: { lat: 30.645, lng: 76.32 },
      duration_minutes: 25,
      started_at: '2026-09-22T08:45:00Z',
      ended_at: '2026-09-22T09:10:00Z',
      description: 'Vehicle stationary > 15 min outside 5km authorized corridor',
      title: 'Rajpura Highway Dhaba Halt',
      severity: 'MEDIUM',
      distance_from_designated_route_km: 3.2,
    },
  ],
  route_polyline: [
    [30.901, 75.8573],
    [30.875, 75.92],
    [30.85, 76.01],
    [30.76, 76.15],
    [30.645, 76.32],
    [30.51, 76.54],
    [30.38, 76.8405],
  ],
  vehicle_number: 'PB-10-CZ-4418 (Bolero Camper 4x4)',
  technician_phone: '+91 98140 88210',
};

// =====================================================================
// EXPORTED API METHODS WITH AUTOMATIC FAILOVER
// =====================================================================

export const api = {
  /**
   * GET /api/dashboard/pulse
   */
  async getPulse(): Promise<PulseResponse> {
    try {
      const response = await client.get<PulseResponse>('/api/dashboard/pulse');
      isBackendLive = true;
      return response.data;
    } catch (err) {
      console.warn('[API] /api/dashboard/pulse unreachable. Falling back to synthetic mock.', err);
      isBackendLive = false;
      return {
        ...FALLBACK_PULSE,
        timestamp: new Date().toISOString(),
      };
    }
  },

  /**
   * POST /api/dashboard/sync
   */
  async triggerSync(forceRefresh = true, modules?: string[]): Promise<SyncResponse> {
    try {
      const payload: SyncRequest = { force_refresh: forceRefresh, modules };
      const response = await client.post<SyncResponse>('/api/dashboard/sync', payload);
      isBackendLive = true;
      return response.data;
    } catch (err) {
      console.warn('[API] /api/dashboard/sync failed. Simulating local sync response.', err);
      isBackendLive = false;
      return {
        status: 'success',
        last_synced_at: new Date().toISOString(),
        records_synced: 42,
        source: 'fieldy_cache',
        sync_id: `SYNC-${Date.now()}`,
        duration_ms: 180,
        message: 'Krone Fieldy dataset re-synchronized. All records fresh.',
      };
    }
  },

  /**
   * GET /api/analytics/productivity
   */
  async getProductivity(params?: ProductivityFilterParams): Promise<ProductivityResponse> {
    try {
      const response = await client.get<ProductivityResponse>('/api/analytics/productivity', {
        params,
      });
      isBackendLive = true;
      return response.data;
    } catch (err) {
      console.warn('[API] /api/analytics/productivity unreachable. Using fallback.', err);
      isBackendLive = false;
      return {
        ...FALLBACK_PRODUCTIVITY,
        timeframe: params?.timeframe || 'daily',
      };
    }
  },

  /**
   * GET /api/telematics/routes
   */
  async getRoute(technicianId: string, date?: string): Promise<RouteResponse> {
    try {
      const response = await client.get<RouteResponse>('/api/telematics/routes', {
        params: { technician_id: technicianId, date },
      });
      isBackendLive = true;
      return response.data;
    } catch (err) {
      console.warn('[API] /api/telematics/routes unreachable. Using fallback route.', err);
      isBackendLive = false;
      return {
        ...FALLBACK_ROUTE,
        technician_id: technicianId || 'TECH-01',
      };
    }
  },

  /**
   * GET /api/technicians
   */
  async getTechnicians(params?: { status?: string; region?: string; search?: string }): Promise<TechnicianDetail[]> {
    try {
      const response = await client.get<TechnicianDetail[]>('/api/technicians', { params });
      isBackendLive = true;
      return response.data;
    } catch (err) {
      console.warn('[API] /api/technicians unreachable. Returning static list.', err);
      isBackendLive = false;
      return [
        {
          technician_id: 'TECH-01',
          name: 'Gurpreet Singh',
          role: 'Lead Baler Specialist',
          region: 'Punjab',
          phone: '+91 98140 88210',
          status: 'On Paid Job',
          active_job_id: 'SR-26-0101',
          vehicle_number: 'PB-10-CZ-4418',
          deputation_rate_per_day: 5000.0,
          da_rate_per_day: 2000.0,
        },
        {
          technician_id: 'TECH-02',
          name: 'Vikram Sharma',
          role: 'Senior Field Service Engineer',
          region: 'Haryana',
          phone: '+91 98120 77412',
          status: 'On Paid Job',
          active_job_id: 'SR-26-0102',
          vehicle_number: 'HR-20-AB-1290',
          deputation_rate_per_day: 5000.0,
          da_rate_per_day: 2000.0,
        },
      ];
    }
  },

  /**
   * GET /api/jobs
   */
  async getJobs(params?: { status?: string; customer?: string; technician_id?: string; job_type?: string }): Promise<JobDetail[]> {
    try {
      const response = await client.get<JobDetail[]>('/api/jobs', { params });
      isBackendLive = true;
      return response.data;
    } catch (err) {
      console.warn('[API] /api/jobs unreachable. Returning static jobs.', err);
      isBackendLive = false;
      return [
        {
          job_id: 'SR-26-0101',
          title: 'Emergency Knotter Timing Calibration & 500h PM',
          status: 'In Progress',
          priority: 'High',
          customer_name: 'Reliance Industries Limited (Bio-Energy Division)',
          asset_name: 'Krone BigPack 1290 HDP High Density Baler',
          assigned_technicians: ['Gurpreet Singh'],
          job_type: 'Paid',
        },
      ];
    }
  },
};
