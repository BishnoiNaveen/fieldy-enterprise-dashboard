# Architectural Blueprint & Implementation Specification: Pulse Board, Machinery Table, Filter Bar & Productivity Analytics

**Agent**: m2_explorer_2 (Exploration Specialist — Pulse Board & Productivity Analytics)  
**Target Milestone**: Milestone 2 (Enterprise Reactive Frontend)  
**System**: Krone Agriculture India — Field Service & Telematics Dashboard  
**Date**: 2026-09-23  
**Working Directory**: `C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m2_explorer_2`  
**Authoritative References**: `ORIGINAL_REQUEST.md`, `PROJECT.md`, `TEST_READY.md`, `fieldy-management` (v4.0 Master), `bento-motion-master`, `backend/app/models/schemas.py`

---

## Executive Summary

This report establishes the complete, production-grade architectural and component implementation blueprints for the core operational tracking and analytics modules of Milestone 2:
1. **`LivePulseBoard.tsx`**: Today's active technicians on paid jobs, technicians on holiday/leave, and the `SR-26-XXXX` work order pipeline with real-time status badges, customer names, assigned equipment, and telematics quick-links.
2. **`MachineryTable.tsx`**: High-density operational table displaying Krone agricultural machinery under service today (Asset Name, 7-digit Serial Number, Customer Company, Site Contact Person, location, active job ID, service type, and operating hours) with one-click copy and phone actions.
3. **`FilterBar.tsx`**: Centralized multi-dimensional filtering toolbar featuring a seamless Daily/Weekly/Monthly timeframe switcher, fuzzy technician and customer dropdowns, status pills, job type filters, date pickers, debounced search, and active filter pill tags—operating with zero full-page reload.
4. **`ProductivityCharts.tsx`**: Mathematical Recharts analytics engine strictly enforcing the Law of Hours Conservation ($H_{shift} = H_w + H_t + H_i$), composed stacked bar and trend charts, executive utilization summary cards, and drill-down technician scorecards with commercial deputation revenue calculations (₹5,000/day AMC tariff, SAC 998719).

All components adhere to the **2026 Bento Motion Master** and **UI/UX Pro Max** standards: Deep Obsidian substrate (`#060A11` / `#0B121E`), Krone Precision Emerald accents (`#059669` / `#10B981`), Harvest Amber alerts (`#F59E0B`), Level 3 Aura Glassmorphism, and strict TypeScript type-safety.

---

## 1. Domain Modeling & System Interoperability

### 1.1 Alignment with Backend REST API Contracts

The components interact directly with the FastAPI backend endpoints certified in Milestone 1:

| Component | Backend Endpoint | Query Parameters | Response Model |
| :--- | :--- | :--- | :--- |
| `LivePulseBoard.tsx` | `GET /api/dashboard/pulse` | `region`, `status` | `PulseResponse` (`kpis`, `technicians_on_jobs`, `today_jobs`, `technicians_on_leave`, `sync_meta`) |
| `MachineryTable.tsx` | `GET /api/dashboard/pulse` | (Extracted from `machines_under_service`) | `List[MachineryUnderService]` |
| `FilterBar.tsx` | Feeds state to all endpoints | N/A (State controller) | `FilterState` |
| `ProductivityCharts.tsx` | `GET /api/analytics/productivity` | `timeframe`, `technician_id`, `customer_company`, `job_status`, `job_type`, `start_date`, `end_date` | `ProductivityResponse` (`summary`, `technician_records`, `trend_data`, `customer_distribution`) |

### 1.2 Mathematical Conservation Invariant

Every component handling operational hours must strictly respect the invariant established in `backend/app/services/analytics_engine.py`:
$$H_{shift} = H_w + H_t + H_i$$
$$\text{Utilization \%} = \frac{H_w}{H_{shift}} \times 100 \quad \text{or} \quad \frac{H_w + H_t}{H_{shift}} \times 100$$
Where:
- $H_w$: Working Hours (Productive on-site repair, calibration, commissioning at customer facility).
- $H_t$: Travelling Hours (Verified transit between depot and customer site along designated corridors).
- $H_i$: Idle Hours (Stationary halts $> 15\text{ min}$ outside 5 km authorized zones, unauthorized roadside stops, or inactive depot periods).
- $H_{shift}$: Total logged shift duration (nominal 8.0 hours standard shift).

---

## 2. Component Blueprint 1: `LivePulseBoard.tsx`

### 2.1 Responsibilities & Features
1. **Workforce Split Overview**: Quick counter showing active technicians on paid jobs vs available vs on holiday/leave.
2. **Technicians Active on Paid Jobs**:
   - Visual cards showing technician avatar/initials, name, phone, regional depot (`Punjab`, `Haryana`, `AP`, `MP`, `UP`, `Maharashtra`).
   - Pulsing green beacon (`animate-ping`) indicating active in-progress job.
   - Bound Job ID badge (`SR-26-XXXX`).
   - Assigned Krone machine model (e.g. `Krone BigPack 1290 HDP`).
   - Client company name (e.g. `Reliance Industries Limited (Bio-Energy Division)`).
   - Time elapsed on job badge (e.g., `3h 30m on site`).
   - Direct button to inspect route telematics.
3. **Technicians on Holiday/Leave Panel**:
   - Collapsible panel showing technicians off-duty with leave classification (`Sick Leave`, `Casual Leave`, `Weekly Off`) and expected return date.
4. **Today's Jobs Table (`SR-26-XXXX` pipeline)**:
   - High-density table of all work orders scheduled for today.
   - Columns: Job ID, Priority, Task Title, Status Badge, Customer Company, Machine Serial & Model, Assigned Technicians, Scheduled Time.
   - Interactive local search and status quick-filter pills (`All`, `In Progress`, `Completed`, `Hold`).
   - Quick action to trigger technician selection or telematics inspection.

### 2.2 Complete Implementation Source Code

```tsx
/**
 * frontend/src/components/LivePulseBoard.tsx
 * Real-Time Operational Pulse Board for Krone Agriculture India Field Operations.
 * Displays technicians on paid jobs, technicians on holiday/leave, and today's jobs pipeline.
 */

import React, { useState, useMemo } from 'react';
import { 
  Users, 
  Wrench, 
  Clock, 
  CheckCircle2, 
  AlertCircle, 
  CalendarOff, 
  Navigation, 
  Search, 
  ExternalLink, 
  UserCheck, 
  Building2, 
  Tag, 
  PhoneCall,
  Activity,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { 
  PulseResponse, 
  TechnicianLiveOnJob, 
  JobItem, 
  TechnicianOnLeave 
} from '../types/dashboard';

interface LivePulseBoardProps {
  pulseData: PulseResponse | null;
  isLoading?: boolean;
  onSelectTechnician?: (technicianId: string) => void;
  onInspectRoute?: (technicianId: string) => void;
  onSelectJob?: (jobId: string) => void;
}

export const LivePulseBoard: React.FC<LivePulseBoardProps> = ({
  pulseData,
  isLoading = false,
  onSelectTechnician,
  onInspectRoute,
  onSelectJob,
}) => {
  const [jobSearchQuery, setJobSearchQuery] = useState('');
  const [selectedStatusFilter, setSelectedStatusFilter] = useState<string>('ALL');
  const [showLeaveDrawer, setShowLeaveDrawer] = useState(false);

  // Status badge styling helper
  const getStatusBadge = (status: string, statusColor?: string) => {
    const s = status.toLowerCase();
    if (s === 'in progress') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-950/80 text-emerald-400 border border-emerald-800/60 shadow-[0_0_12px_rgba(5,150,105,0.25)]">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          In Progress
        </span>
      );
    }
    if (s === 'completed') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-950/80 text-blue-400 border border-blue-800/60">
          <CheckCircle2 className="w-3 h-3" />
          Completed
        </span>
      );
    }
    if (s === 'start travel') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-sky-950/80 text-sky-400 border border-sky-800/60">
          <Navigation className="w-3 h-3" />
          Start Travel
        </span>
      );
    }
    if (s === 'hold') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-950/80 text-amber-400 border border-amber-800/60">
          <AlertCircle className="w-3 h-3" />
          On Hold
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700">
        {status}
      </span>
    );
  };

  // Priority badge styling helper
  const getPriorityBadge = (priority?: string) => {
    const p = (priority || 'NORMAL').toUpperCase();
    if (p === 'HIGH' || p === 'EMERGENCY') {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase bg-rose-950/80 text-rose-400 border border-rose-800/60">
          {p}
        </span>
      );
    }
    if (p === 'MEDIUM') {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase bg-amber-950/80 text-amber-400 border border-amber-800/60">
          MED
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 rounded text-[10px] font-medium tracking-wider uppercase bg-slate-800 text-slate-400">
        NORMAL
      </span>
    );
  };

  // Filtered jobs for today
  const filteredJobs = useMemo(() => {
    if (!pulseData?.today_jobs) return [];
    return pulseData.today_jobs.filter((job) => {
      const matchesSearch =
        job.job_id.toLowerCase().includes(jobSearchQuery.toLowerCase()) ||
        job.customer_name.toLowerCase().includes(jobSearchQuery.toLowerCase()) ||
        (job.title && job.title.toLowerCase().includes(jobSearchQuery.toLowerCase())) ||
        (job.machine_serial && job.machine_serial.toLowerCase().includes(jobSearchQuery.toLowerCase())) ||
        job.assigned_technicians.some((tech) => tech.toLowerCase().includes(jobSearchQuery.toLowerCase()));

      const matchesStatus =
        selectedStatusFilter === 'ALL' ||
        job.status.toLowerCase() === selectedStatusFilter.toLowerCase();

      return matchesSearch && matchesStatus;
    });
  }, [pulseData?.today_jobs, jobSearchQuery, selectedStatusFilter]);

  if (isLoading && !pulseData) {
    return (
      <div className="w-full bg-[#0B121E] border border-slate-800/80 rounded-2xl p-8 flex flex-col items-center justify-center min-h-[420px] animate-pulse">
        <Activity className="w-10 h-10 text-emerald-500 animate-spin mb-4" />
        <p className="text-slate-400 text-sm font-medium">Synchronizing Live Operational Pulse...</p>
      </div>
    );
  }

  const kpis = pulseData?.kpis;
  const activeTechs = pulseData?.technicians_on_jobs || [];
  const leaveTechs = pulseData?.technicians_on_leave || [];

  return (
    <div className="space-y-6">
      {/* 1. Header & Live Summary Status Ribbon */}
      <div className="bg-[#0B121E] border border-slate-800/80 rounded-2xl p-5 shadow-[0_10px_30px_rgba(0,0,0,0.5)]">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3.5">
            <div className="w-11 h-11 rounded-xl bg-emerald-950/70 border border-emerald-800/50 flex items-center justify-center text-emerald-400 shadow-[0_0_15px_rgba(5,150,105,0.25)]">
              <Activity className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-white tracking-tight">
                  Live Field Operational Pulse
                </h2>
                <span className="flex h-2.5 w-2.5 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500" />
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Real-time technician deployment, live work orders, and field availability
              </p>
            </div>
          </div>

          {/* Quick Counter Pills */}
          <div className="flex flex-wrap items-center gap-2.5">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#0F172A] border border-emerald-800/40 text-xs">
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
              <span className="text-slate-300 font-medium">Active on Paid Jobs:</span>
              <span className="font-bold text-emerald-400 font-mono text-sm">
                {kpis?.technicians_on_paid_jobs ?? activeTechs.length}
              </span>
            </div>

            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#0F172A] border border-slate-700/60 text-xs">
              <span className="w-2 h-2 rounded-full bg-blue-400" />
              <span className="text-slate-300 font-medium">Total Active Fleet:</span>
              <span className="font-bold text-blue-400 font-mono text-sm">
                {kpis?.technicians_active_total ?? 12}
              </span>
            </div>

            <button
              onClick={() => setShowLeaveDrawer(!showLeaveDrawer)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#0F172A] border border-amber-800/40 text-xs hover:border-amber-700 transition cursor-pointer"
            >
              <CalendarOff className="w-3.5 h-3.5 text-amber-400" />
              <span className="text-slate-300 font-medium">On Leave / Off:</span>
              <span className="font-bold text-amber-400 font-mono text-sm">
                {kpis?.technicians_on_leave ?? leaveTechs.length}
              </span>
              {showLeaveDrawer ? (
                <ChevronUp className="w-3.5 h-3.5 text-slate-400 ml-1" />
              ) : (
                <ChevronDown className="w-3.5 h-3.5 text-slate-400 ml-1" />
              )}
            </button>
          </div>
        </div>

        {/* Expandable Leave Drawer */}
        {showLeaveDrawer && (
          <div className="mt-4 pt-4 border-t border-slate-800/80">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-amber-400 flex items-center gap-2">
                <CalendarOff className="w-3.5 h-3.5" />
                Technicians on Approved Leave / Scheduled Off Today ({leaveTechs.length})
              </h3>
            </div>
            {leaveTechs.length === 0 ? (
              <p className="text-xs text-slate-400 italic">No technicians are currently on leave.</p>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {leaveTechs.map((tech) => (
                  <div
                    key={tech.technician_id}
                    className="p-3 rounded-xl bg-[#060A11]/60 border border-slate-800/80 flex items-center justify-between"
                  >
                    <div>
                      <div className="text-sm font-semibold text-slate-200">{tech.name}</div>
                      <div className="text-xs text-slate-400 flex items-center gap-2 mt-0.5">
                        <span className="text-slate-500 font-mono">{tech.technician_id}</span>
                        <span>•</span>
                        <span>{tech.region}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-amber-950/60 text-amber-300 border border-amber-800/50">
                        {tech.leave_type}
                      </span>
                      {tech.return_date && (
                        <div className="text-[10px] text-slate-400 mt-1 font-mono">
                          Returns: {tech.return_date}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* 2. Technicians Actively on Paid Jobs Cards Grid */}
      <div>
        <div className="flex items-center justify-between mb-3 px-1">
          <div className="flex items-center gap-2">
            <UserCheck className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Technicians on Paid Jobs ({activeTechs.length})
            </h3>
          </div>
          <span className="text-xs text-slate-400">
            Fieldy Live Assignment • Deputation Rate ₹5,000 / Day (₹625 / hr)
          </span>
        </div>

        {activeTechs.length === 0 ? (
          <div className="bg-[#0B121E] border border-slate-800/80 rounded-xl p-8 text-center text-slate-400 text-sm">
            No technicians currently assigned to active paid jobs.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {activeTechs.map((tech) => (
              <div
                key={tech.technician_id}
                className="bg-[#0F172A] border border-slate-800/80 hover:border-emerald-800/60 rounded-xl p-4 transition-all duration-200 flex flex-col justify-between shadow-[0_4px_20px_rgba(0,0,0,0.3)] group hover:-translate-y-0.5"
              >
                <div>
                  {/* Top: Avatar, Name & Live Badge */}
                  <div className="flex items-start justify-between gap-2 mb-2.5">
                    <div className="flex items-center gap-2.5">
                      <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-emerald-600 to-teal-800 flex items-center justify-center text-white font-bold text-xs shadow-md">
                        {tech.name.split(' ').map(n => n[0]).join('')}
                      </div>
                      <div>
                        <h4 className="text-sm font-semibold text-white group-hover:text-emerald-400 transition-colors leading-tight">
                          {tech.name}
                        </h4>
                        <div className="text-[11px] text-slate-400 font-mono">
                          {tech.technician_id}
                        </div>
                      </div>
                    </div>
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800/60">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                      LIVE
                    </span>
                  </div>

                  {/* Job ID & Machine Binding */}
                  <div className="space-y-1.5 text-xs mb-3">
                    <div className="flex items-center justify-between bg-[#060A11]/60 px-2.5 py-1.5 rounded-lg border border-slate-800/60">
                      <span className="text-slate-400 flex items-center gap-1">
                        <Tag className="w-3 h-3 text-slate-400" />
                        Job:
                      </span>
                      <button
                        onClick={() => tech.live_job_id && onSelectJob?.(tech.live_job_id)}
                        className="font-mono font-bold text-emerald-400 hover:underline cursor-pointer"
                      >
                        {tech.live_job_id || 'N/A'}
                      </button>
                    </div>

                    <div className="text-[11px] text-slate-300 truncate" title={tech.machine_asset}>
                      <span className="text-slate-500 mr-1 font-medium">Asset:</span>
                      {tech.machine_asset || 'Krone Heavy Equipment'}
                    </div>

                    <div className="text-[11px] text-slate-300 truncate" title={tech.customer_company}>
                      <span className="text-slate-500 mr-1 font-medium">Client:</span>
                      {tech.customer_company || 'Reliance Industries Limited'}
                    </div>
                  </div>
                </div>

                {/* Footer Actions */}
                <div className="pt-2.5 border-t border-slate-800/60 flex items-center justify-between text-xs">
                  <span className="text-slate-400 flex items-center gap-1 text-[11px]">
                    <Clock className="w-3 h-3 text-emerald-400" />
                    {tech.elapsed_minutes ? `${Math.floor(tech.elapsed_minutes / 60)}h ${tech.elapsed_minutes % 60}m` : 'Active'}
                  </span>

                  <button
                    onClick={() => onInspectRoute?.(tech.technician_id)}
                    className="flex items-center gap-1 text-[11px] font-semibold text-emerald-400 hover:text-emerald-300 transition cursor-pointer"
                  >
                    <Navigation className="w-3 h-3" />
                    Telematics
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 3. Today's Jobs Pipeline Table (SR-26-XXXX) */}
      <div className="bg-[#0B121E] border border-slate-800/80 rounded-2xl overflow-hidden shadow-[0_10px_30px_rgba(0,0,0,0.5)]">
        {/* Table Filter & Search Header */}
        <div className="p-4 border-b border-slate-800/80 flex flex-col md:flex-row md:items-center justify-between gap-3 bg-[#0F172A]/50">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-950/60 border border-emerald-800/40 flex items-center justify-center text-emerald-400">
              <Wrench className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white tracking-tight">
                Today's Work Orders ({filteredJobs.length} of {pulseData?.today_jobs?.length ?? 0})
              </h3>
              <p className="text-[11px] text-slate-400">Fieldy Job Pipeline (`SR-26-XXXX` Series)</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {/* Status Filter Chips */}
            <div className="flex items-center bg-[#060A11] rounded-lg p-0.5 border border-slate-800">
              {['ALL', 'In Progress', 'Completed', 'Hold'].map((status) => (
                <button
                  key={status}
                  onClick={() => setSelectedStatusFilter(status)}
                  className={`px-2.5 py-1 rounded-md text-xs font-medium transition cursor-pointer ${
                    selectedStatusFilter.toLowerCase() === status.toLowerCase()
                      ? 'bg-emerald-600 text-white font-semibold shadow-sm'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {status}
                </button>
              ))}
            </div>

            {/* Quick Search Input */}
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={jobSearchQuery}
                onChange={(e) => setJobSearchQuery(e.target.value)}
                placeholder="Search job ID, client, serial..."
                className="bg-[#060A11] border border-slate-800 rounded-lg pl-8 pr-3 py-1 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 w-44 md:w-56"
              />
            </div>
          </div>
        </div>

        {/* Table Content */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#060A11]/80 text-slate-400 font-semibold border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Job Order</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Customer Company</th>
                <th className="py-3 px-4">Machine & Serial</th>
                <th className="py-3 px-4">Assigned Field Engineers</th>
                <th className="py-3 px-4">Job Type</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filteredJobs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500 italic">
                    No work orders found matching the filter criteria.
                  </td>
                </tr>
              ) : (
                filteredJobs.map((job) => (
                  <tr
                    key={job.job_id}
                    className="hover:bg-slate-800/30 transition-colors group cursor-pointer"
                    onClick={() => onSelectJob?.(job.job_id)}
                  >
                    {/* Job ID & Priority */}
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-emerald-400 bg-emerald-950/40 border border-emerald-800/40 px-2 py-0.5 rounded text-xs">
                          {job.job_id}
                        </span>
                        {getPriorityBadge(job.priority)}
                      </div>
                      {job.title && (
                        <div className="text-[11px] text-slate-400 mt-1 max-w-xs truncate" title={job.title}>
                          {job.title}
                        </div>
                      )}
                    </td>

                    {/* Status */}
                    <td className="py-3 px-4 whitespace-nowrap">
                      {getStatusBadge(job.status, job.status_color)}
                    </td>

                    {/* Customer */}
                    <td className="py-3 px-4">
                      <div className="font-medium text-slate-200">{job.customer_name}</div>
                      {job.scheduled_start && (
                        <div className="text-[10px] text-slate-400 mt-0.5">
                          Sched: {new Date(job.scheduled_start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </div>
                      )}
                    </td>

                    {/* Machine & Serial */}
                    <td className="py-3 px-4">
                      <div className="font-medium text-slate-200">
                        {job.machine_name || 'Krone Baler'}
                      </div>
                      {job.machine_serial && (
                        <div className="font-mono text-[10px] text-slate-400 mt-0.5">
                          SN: {job.machine_serial}
                        </div>
                      )}
                    </td>

                    {/* Assigned Technicians */}
                    <td className="py-3 px-4">
                      {job.assigned_technicians.length === 0 ? (
                        <span className="text-slate-500 italic text-[11px]">Unassigned</span>
                      ) : (
                        <div className="flex flex-wrap gap-1">
                          {job.assigned_technicians.map((name, i) => (
                            <span
                              key={i}
                              className="px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-slate-300 text-[11px] font-medium"
                            >
                              {name}
                            </span>
                          ))}
                        </div>
                      )}
                    </td>

                    {/* Job Type */}
                    <td className="py-3 px-4 whitespace-nowrap">
                      <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-950/40 text-emerald-300 border border-emerald-800/40">
                        {job.job_type || 'Paid'}
                      </span>
                    </td>

                    {/* Actions */}
                    <td className="py-3 px-4 text-right whitespace-nowrap">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectJob?.(job.job_id);
                        }}
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-[#060A11] border border-slate-700 hover:border-emerald-500 text-slate-300 hover:text-emerald-400 transition text-[11px] font-medium cursor-pointer"
                      >
                        <ExternalLink className="w-3 h-3" />
                        Details
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
```

---

## 3. Component Blueprint 2: `MachineryTable.tsx`

### 3.1 Responsibilities & Features
1. **Equipment Catalog Realism**: Models authentic Krone commercial machinery:
   - `Krone BigPack 1290 HDP High Density Baler` (Square Baler)
   - `Krone Fortima V 1500 Round Baler` (Round Baler)
   - `Krone BiG X 680 Forage Harvester` (Forage Harvester)
   - `Krone EasyCut B 870 Mower Conditioner` (Mower)
   - `Krone Swadro TC 880 Rotary Rake` (Rotary Rake)
2. **7-Digit Serial Numbers with One-Click Copy**:
   - Monospace pill formatting (`BP1290-78401`, `FV1500-33901`, `BX6800-45912`, `EC8700-12845`, `SW8800-98321`).
   - Copy-to-clipboard action with visual confirmation toast/icon flip (`Check` icon).
3. **Site Contact Person & Direct Communication**:
   - Contact Person Name + Phone with international prefix (`+91 98765 43210`).
   - One-click `tel:` action and WhatsApp trigger button.
4. **Active Job Order Linkage**:
   - Monospace badge linking to the active `SR-26-XXXX` work order.
5. **Interactive Filtering & Sorting**:
   - Real-time search across Asset Name, Serial, Client Company, Contact Person, and Service Type.
   - Equipment Category quick pills: `All`, `Balers`, `Harvesters`, `Mowers & Rakes`.
   - Health status filter.
   - CSV Export trigger for field audit logs.

### 3.2 Complete Implementation Source Code

```tsx
/**
 * frontend/src/components/MachineryTable.tsx
 * High-Density Krone Machinery Under Service Table.
 * Asset Name, 7-digit Serial Number, Customer Company, Site Contact Person, and Active Work Order.
 */

import React, { useState, useMemo } from 'react';
import { 
  Tractor, 
  Copy, 
  Check, 
  Phone, 
  MapPin, 
  Wrench, 
  ExternalLink, 
  Search, 
  Filter, 
  Gauge, 
  AlertTriangle, 
  ShieldCheck, 
  Download,
  Clock
} from 'lucide-react';
import { MachineryUnderService } from '../types/dashboard';

interface MachineryTableProps {
  machinery: MachineryUnderService[];
  isLoading?: boolean;
  onSelectMachine?: (serialNumber: string) => void;
  onSelectJob?: (jobId: string) => void;
}

export const MachineryTable: React.FC<MachineryTableProps> = ({
  machinery,
  isLoading = false,
  onSelectMachine,
  onSelectJob,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [copiedSerial, setCopiedSerial] = useState<string | null>(null);

  // Copy Serial Number to Clipboard helper
  const handleCopySerial = (serial: string, e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(serial);
    setCopiedSerial(serial);
    setTimeout(() => setCopiedSerial(null), 2000);
  };

  // Health Status Badge helper
  const getHealthBadge = (status?: string) => {
    const s = (status || 'UNDER SERVICE').toUpperCase();
    if (s.includes('OPTIMAL')) {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-950/80 text-emerald-400 border border-emerald-800/60">
          <ShieldCheck className="w-3 h-3" />
          Optimal
        </span>
      );
    }
    if (s.includes('ATTENTION')) {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-950/80 text-amber-400 border border-amber-800/60">
          <AlertTriangle className="w-3 h-3" />
          Attention
        </span>
      );
    }
    if (s.includes('CRITICAL')) {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-950/80 text-rose-400 border border-rose-800/60">
          <AlertTriangle className="w-3 h-3" />
          Critical
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-950/60 text-amber-400 border border-amber-800/40">
        <Wrench className="w-3 h-3" />
        Under Service
      </span>
    );
  };

  // Filtered machinery list
  const filteredMachinery = useMemo(() => {
    return machinery.filter((m) => {
      const matchesSearch =
        m.asset_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        m.serial_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
        m.client_company_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        m.site_contact_person.toLowerCase().includes(searchQuery.toLowerCase()) ||
        m.location.toLowerCase().includes(searchQuery.toLowerCase()) ||
        m.active_job_id.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesCat =
        selectedCategory === 'ALL' ||
        (selectedCategory === 'BALER' && (m.asset_name.includes('Baler') || m.asset_name.includes('BigPack') || m.asset_name.includes('Fortima'))) ||
        (selectedCategory === 'HARVESTER' && (m.asset_name.includes('BiG X') || m.asset_name.includes('Harvester'))) ||
        (selectedCategory === 'MOWER_RAKE' && (m.asset_name.includes('EasyCut') || m.asset_name.includes('Swadro') || m.asset_name.includes('Mower') || m.asset_name.includes('Rake')));

      return matchesSearch && matchesCat;
    });
  }, [machinery, searchQuery, selectedCategory]);

  // CSV Export handler
  const handleExportCsv = () => {
    const headers = ['Asset Name', 'Serial Number', 'Customer Company', 'Site Contact', 'Location', 'Active Job ID', 'Service Type', 'Operating Hours', 'Status'];
    const rows = filteredMachinery.map(m => [
      `"${m.asset_name}"`,
      `"${m.serial_number}"`,
      `"${m.client_company_name}"`,
      `"${m.site_contact_person}"`,
      `"${m.location}"`,
      `"${m.active_job_id}"`,
      `"${m.service_type}"`,
      m.operating_hours ?? 'N/A',
      `"${m.health_status ?? 'Under Service'}"`
    ]);
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `krone_machinery_under_service_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="bg-[#0B121E] border border-slate-800/80 rounded-2xl overflow-hidden shadow-[0_10px_30px_rgba(0,0,0,0.5)]">
      {/* Table Header Bar */}
      <div className="p-5 border-b border-slate-800/80 bg-[#0F172A]/70 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-11 h-11 rounded-xl bg-emerald-950/70 border border-emerald-800/50 flex items-center justify-center text-emerald-400 shadow-[0_0_15px_rgba(5,150,105,0.25)]">
            <Tractor className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-bold text-white tracking-tight">
                Krone Machinery Under Service Today
              </h2>
              <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800/60 font-mono">
                {filteredMachinery.length} Units Active
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Heavy Equipment Fleet Roster • Large Square Balers, Round Balers, Harvesters & Mowers
            </p>
          </div>
        </div>

        {/* Toolbar Controls */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Category Filter Pills */}
          <div className="flex items-center bg-[#060A11] rounded-lg p-0.5 border border-slate-800">
            {[
              { id: 'ALL', label: 'All Fleet' },
              { id: 'BALER', label: 'Balers' },
              { id: 'HARVESTER', label: 'Harvesters' },
              { id: 'MOWER_RAKE', label: 'Mowers & Rakes' },
            ].map((cat) => (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition cursor-pointer ${
                  selectedCategory === cat.id
                    ? 'bg-emerald-600 text-white font-semibold shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>

          {/* Search Box */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search serial, asset, site..."
              className="bg-[#060A11] border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 w-48 md:w-56"
            />
          </div>

          {/* CSV Export Button */}
          <button
            onClick={handleExportCsv}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#060A11] border border-slate-800 hover:border-emerald-600 text-slate-300 hover:text-emerald-400 text-xs font-medium transition cursor-pointer"
            title="Export filtered records to CSV"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export</span>
          </button>
        </div>
      </div>

      {/* Table Content */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-[#060A11]/90 text-slate-400 font-semibold border-b border-slate-800">
            <tr>
              <th className="py-3.5 px-4">Asset Name & Model</th>
              <th className="py-3.5 px-4">Serial Number</th>
              <th className="py-3.5 px-4">Customer Company</th>
              <th className="py-3.5 px-4">Site Contact Person</th>
              <th className="py-3.5 px-4">Location / Facility</th>
              <th className="py-3.5 px-4">Active Work Order</th>
              <th className="py-3.5 px-4">Operating Hours</th>
              <th className="py-3.5 px-4">Health Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {isLoading ? (
              <tr>
                <td colSpan={8} className="py-12 text-center text-slate-400">
                  <div className="flex items-center justify-center gap-2">
                    <Wrench className="w-4 h-4 animate-spin text-emerald-500" />
                    <span>Loading machinery records...</span>
                  </div>
                </td>
              </tr>
            ) : filteredMachinery.length === 0 ? (
              <tr>
                <td colSpan={8} className="py-10 text-center text-slate-500 italic">
                  No machinery currently under service matches the search query.
                </td>
              </tr>
            ) : (
              filteredMachinery.map((machine) => (
                <tr
                  key={machine.serial_number}
                  className="hover:bg-slate-800/40 transition-colors group cursor-pointer"
                  onClick={() => onSelectMachine?.(machine.serial_number)}
                >
                  {/* 1. Asset Name & Service Description */}
                  <td className="py-3.5 px-4">
                    <div className="font-bold text-white group-hover:text-emerald-400 transition-colors text-sm">
                      {machine.asset_name}
                    </div>
                    <div className="text-[11px] text-slate-400 mt-0.5 flex items-center gap-1.5">
                      <span className="text-emerald-500 font-medium">Task:</span>
                      <span className="truncate max-w-xs">{machine.service_type}</span>
                    </div>
                  </td>

                  {/* 2. 7-Digit Serial Number with 1-Click Copy */}
                  <td className="py-3.5 px-4 whitespace-nowrap">
                    <div className="inline-flex items-center gap-1.5 bg-[#060A11] px-2.5 py-1 rounded-md border border-slate-800 group-hover:border-emerald-800/60 transition">
                      <span className="font-mono text-emerald-400 font-semibold text-xs">
                        {machine.serial_number}
                      </span>
                      <button
                        onClick={(e) => handleCopySerial(machine.serial_number, e)}
                        className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition cursor-pointer"
                        title="Copy Serial Number"
                      >
                        {copiedSerial === machine.serial_number ? (
                          <Check className="w-3 h-3 text-emerald-400" />
                        ) : (
                          <Copy className="w-3 h-3" />
                        )}
                      </button>
                    </div>
                  </td>

                  {/* 3. Customer Company */}
                  <td className="py-3.5 px-4">
                    <div className="font-semibold text-slate-200">
                      {machine.client_company_name}
                    </div>
                  </td>

                  {/* 4. Site Contact Person with Direct Call Action */}
                  <td className="py-3.5 px-4">
                    <div className="font-medium text-slate-300">
                      {machine.site_contact_person.split('(')[0].trim()}
                    </div>
                    {machine.site_contact_person.includes('+91') && (
                      <a
                        href={`tel:${machine.site_contact_person.match(/\+91[\s\d]+/)?.[0].replace(/\s+/g, '')}`}
                        onClick={(e) => e.stopPropagation()}
                        className="inline-flex items-center gap-1 text-[11px] font-mono text-emerald-400 hover:underline mt-0.5"
                      >
                        <Phone className="w-3 h-3 text-emerald-500" />
                        {machine.site_contact_person.match(/\+91[\s\d]+/)?.[0]}
                      </a>
                    )}
                  </td>

                  {/* 5. Location */}
                  <td className="py-3.5 px-4 text-slate-400">
                    <div className="flex items-center gap-1 truncate max-w-xs">
                      <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span>{machine.location}</span>
                    </div>
                  </td>

                  {/* 6. Active Work Order */}
                  <td className="py-3.5 px-4 whitespace-nowrap">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectJob?.(machine.active_job_id);
                      }}
                      className="inline-flex items-center gap-1.5 font-mono font-bold text-xs text-emerald-400 bg-emerald-950/60 border border-emerald-800/50 px-2.5 py-1 rounded-md hover:bg-emerald-900/60 transition cursor-pointer"
                    >
                      <span>{machine.active_job_id}</span>
                      <ExternalLink className="w-3 h-3" />
                    </button>
                  </td>

                  {/* 7. Operating Hours */}
                  <td className="py-3.5 px-4 whitespace-nowrap font-mono text-slate-300">
                    <div className="flex items-center gap-1.5">
                      <Gauge className="w-3.5 h-3.5 text-slate-400" />
                      <span>{machine.operating_hours ? `${machine.operating_hours.toLocaleString()} h` : 'N/A'}</span>
                    </div>
                  </td>

                  {/* 8. Health Status */}
                  <td className="py-3.5 px-4 whitespace-nowrap">
                    {getHealthBadge(machine.health_status)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
```

---

## 4. Component Blueprint 3: `FilterBar.tsx`

### 4.1 Responsibilities & Features
1. **Zero-Reload Reactive Filtering**:
   - Central state coordinator dispatching updates immediately to parent components via `onFilterChange(newFilters)`.
2. **Timeframe Switcher (Daily / Weekly / Monthly)**:
   - High-contrast segmented control.
   - Smooth pill transition with emerald background highlight (`#059669`).
3. **Multi-Dimensional Dropdowns**:
   - **Technician**: Populated from roster with exact IDs (`TECH-01: Gurpreet Singh`, `TECH-02: Vikram Sharma`, etc.).
   - **Customer Company**: `Reliance Industries Limited`, `Punjab State Farm Cooperative`, `VERBIO Bio-Gas`, `SAEL Punjab Biomass`, etc.
   - **Job Status**: `In Progress`, `Completed`, `Start Travel`, `Hold`.
   - **Job Type**: `Paid`, `AMC`, `Warranty`, `Emergency Repair`.
4. **Date Pickers**: Start Date and End Date calendar inputs.
5. **Instant Debounced Search Box**: With a single click clear button (`X`).
6. **Active Filter Tags Bar**: Shows all currently applied non-default filters with 1-click removal chips and a global "Reset All" action.

### 4.2 Complete Implementation Source Code

```tsx
/**
 * frontend/src/components/FilterBar.tsx
 * Multi-Dimensional Filter & Timeframe Switcher Bar.
 * Daily/Weekly/Monthly Switcher, Technician, Customer, Status, Job Type, and Date Range Filters.
 */

import React, { useState, useEffect } from 'react';
import { 
  Filter, 
  RotateCcw, 
  Search, 
  Calendar, 
  User, 
  Building2, 
  Activity, 
  Tag, 
  X,
  SlidersHorizontal
} from 'lucide-react';
import { Timeframe } from '../types/dashboard';

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

export const DEFAULT_FILTER_STATE: FilterState = {
  timeframe: 'daily',
  technicianId: 'ALL',
  customerCompany: 'ALL',
  jobStatus: 'ALL',
  jobType: 'ALL',
  startDate: '',
  endDate: '',
  searchQuery: '',
};

interface FilterBarProps {
  filters: FilterState;
  onFilterChange: (newFilters: FilterState) => void;
  technicianOptions?: Array<{ id: string; name: string }>;
  customerOptions?: string[];
  className?: string;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  filters,
  onFilterChange,
  technicianOptions = [
    { id: 'TECH-01', name: 'Gurpreet Singh' },
    { id: 'TECH-02', name: 'Vikram Sharma' },
    { id: 'TECH-03', name: 'Sunny Kumar' },
    { id: 'TECH-04', name: 'Jaswinder Singh' },
    { id: 'TECH-05', name: 'B. Vignesh' },
    { id: 'TECH-06', name: 'M. Naveen Kumar' },
    { id: 'TECH-07', name: 'Palthiya Kishore' },
    { id: 'TECH-08', name: 'Nitin Gour' },
  ],
  customerOptions = [
    'Reliance Industries Limited',
    'Punjab State Farm Cooperative',
    'VERBIO Bio-Gas India Pvt Ltd',
    'SAEL Punjab Biomass Energy Project',
    'Hoshiarpur Bio-Fuels Farm Cluster',
    'Adani Agri Logistics Ltd',
    'Baramati Agro Industries',
    'Sugarfed Punjab',
  ],
  className = '',
}) => {
  const [localSearch, setLocalSearch] = useState(filters.searchQuery);

  // Debounced search query
  useEffect(() => {
    const handler = setTimeout(() => {
      if (localSearch !== filters.searchQuery) {
        onFilterChange({ ...filters, searchQuery: localSearch });
      }
    }, 300);
    return () => clearTimeout(handler);
  }, [localSearch, filters, onFilterChange]);

  const handleUpdate = (patch: Partial<FilterState>) => {
    onFilterChange({ ...filters, ...patch });
  };

  const handleReset = () => {
    setLocalSearch('');
    onFilterChange(DEFAULT_FILTER_STATE);
  };

  // Determine active non-default filters for chip bar
  const activeFilters = [
    filters.technicianId !== 'ALL' && {
      key: 'technicianId',
      label: `Tech: ${technicianOptions.find(t => t.id === filters.technicianId)?.name || filters.technicianId}`,
      reset: () => handleUpdate({ technicianId: 'ALL' }),
    },
    filters.customerCompany !== 'ALL' && {
      key: 'customerCompany',
      label: `Client: ${filters.customerCompany}`,
      reset: () => handleUpdate({ customerCompany: 'ALL' }),
    },
    filters.jobStatus !== 'ALL' && {
      key: 'jobStatus',
      label: `Status: ${filters.jobStatus}`,
      reset: () => handleUpdate({ jobStatus: 'ALL' }),
    },
    filters.jobType !== 'ALL' && {
      key: 'jobType',
      label: `Type: ${filters.jobType}`,
      reset: () => handleUpdate({ jobType: 'ALL' }),
    },
    filters.startDate && {
      key: 'startDate',
      label: `From: ${filters.startDate}`,
      reset: () => handleUpdate({ startDate: '' }),
    },
    filters.endDate && {
      key: 'endDate',
      label: `To: ${filters.endDate}`,
      reset: () => handleUpdate({ endDate: '' }),
    },
    filters.searchQuery && {
      key: 'searchQuery',
      label: `Search: "${filters.searchQuery}"`,
      reset: () => {
        setLocalSearch('');
        handleUpdate({ searchQuery: '' });
      },
    },
  ].filter(Boolean) as Array<{ key: string; label: string; reset: () => void }>;

  return (
    <div className={`bg-[#0B121E] border border-slate-800/80 rounded-2xl p-4 shadow-[0_10px_30px_rgba(0,0,0,0.5)] space-y-3.5 ${className}`}>
      {/* Top Row: Timeframe Switcher + Search + Reset */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
        {/* Timeframe Segmented Control (Daily / Weekly / Monthly) */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider mr-1 hidden sm:inline">
            Horizon:
          </span>
          <div className="inline-flex bg-[#060A11] p-1 rounded-xl border border-slate-800/90 shadow-inner">
            {(['daily', 'weekly', 'monthly'] as Timeframe[]).map((tf) => (
              <button
                key={tf}
                onClick={() => handleUpdate({ timeframe: tf })}
                className={`px-4 py-1.5 rounded-lg text-xs font-bold capitalize transition-all duration-200 cursor-pointer ${
                  filters.timeframe === tf
                    ? 'bg-emerald-600 text-white shadow-[0_0_15px_rgba(5,150,105,0.4)]'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>

        {/* Global Search Bar */}
        <div className="flex items-center gap-2.5 flex-1 max-w-md">
          <div className="relative w-full">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={localSearch}
              onChange={(e) => setLocalSearch(e.target.value)}
              placeholder="Search technician, machine, client..."
              className="w-full bg-[#060A11] border border-slate-800 rounded-xl pl-9 pr-8 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition"
            />
            {localSearch && (
              <button
                onClick={() => setLocalSearch('')}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {activeFilters.length > 0 && (
            <button
              onClick={handleReset}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white text-xs font-semibold transition shrink-0 cursor-pointer"
              title="Reset all filters"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>
          )}
        </div>
      </div>

      {/* Bottom Row: Multi-Dimensional Dropdowns */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 pt-2 border-t border-slate-800/60 text-xs">
        {/* 1. Technician Dropdown */}
        <div>
          <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1 flex items-center gap-1">
            <User className="w-3 h-3 text-emerald-400" />
            Technician
          </label>
          <select
            value={filters.technicianId}
            onChange={(e) => handleUpdate({ technicianId: e.target.value })}
            className="w-full bg-[#060A11] border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-emerald-500"
          >
            <option value="ALL">All Technicians</option>
            {technicianOptions.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name} ({t.id})
              </option>
            ))}
          </select>
        </div>

        {/* 2. Customer Company Dropdown */}
        <div>
          <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1 flex items-center gap-1">
            <Building2 className="w-3 h-3 text-blue-400" />
            Client Company
          </label>
          <select
            value={filters.customerCompany}
            onChange={(e) => handleUpdate({ customerCompany: e.target.value })}
            className="w-full bg-[#060A11] border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-emerald-500 truncate"
          >
            <option value="ALL">All Clients</option>
            {customerOptions.map((c, i) => (
              <option key={i} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>

        {/* 3. Job Status Dropdown */}
        <div>
          <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1 flex items-center gap-1">
            <Activity className="w-3 h-3 text-emerald-400" />
            Job Status
          </label>
          <select
            value={filters.jobStatus}
            onChange={(e) => handleUpdate({ jobStatus: e.target.value })}
            className="w-full bg-[#060A11] border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-emerald-500"
          >
            <option value="ALL">All Statuses</option>
            <option value="In Progress">In Progress</option>
            <option value="Completed">Completed</option>
            <option value="Start Travel">Start Travel</option>
            <option value="Hold">On Hold</option>
          </select>
        </div>

        {/* 4. Job Type Dropdown */}
        <div>
          <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1 flex items-center gap-1">
            <Tag className="w-3 h-3 text-amber-400" />
            Job Type
          </label>
          <select
            value={filters.jobType}
            onChange={(e) => handleUpdate({ jobType: e.target.value })}
            className="w-full bg-[#060A11] border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-emerald-500"
          >
            <option value="ALL">All Types</option>
            <option value="Paid">Paid</option>
            <option value="AMC">AMC</option>
            <option value="Warranty">Warranty</option>
            <option value="Emergency Repair">Emergency Repair</option>
          </select>
        </div>

        {/* 5. Start Date */}
        <div>
          <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1 flex items-center gap-1">
            <Calendar className="w-3 h-3 text-slate-400" />
            Start Date
          </label>
          <input
            type="date"
            value={filters.startDate}
            onChange={(e) => handleUpdate({ startDate: e.target.value })}
            className="w-full bg-[#060A11] border border-slate-800 rounded-lg px-2 py-1.5 text-slate-200 focus:outline-none focus:border-emerald-500 font-mono text-[11px]"
          />
        </div>

        {/* 6. End Date */}
        <div>
          <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1 flex items-center gap-1">
            <Calendar className="w-3 h-3 text-slate-400" />
            End Date
          </label>
          <input
            type="date"
            value={filters.endDate}
            onChange={(e) => handleUpdate({ endDate: e.target.value })}
            className="w-full bg-[#060A11] border border-slate-800 rounded-lg px-2 py-1.5 text-slate-200 focus:outline-none focus:border-emerald-500 font-mono text-[11px]"
          />
        </div>
      </div>

      {/* Active Filter Chips */}
      {activeFilters.length > 0 && (
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-800/40">
          <span className="text-[11px] font-medium text-slate-400 flex items-center gap-1">
            <SlidersHorizontal className="w-3 h-3 text-emerald-400" />
            Active Filters ({activeFilters.length}):
          </span>
          {activeFilters.map((chip, idx) => (
            <span
              key={idx}
              className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-emerald-950/80 text-emerald-300 border border-emerald-800/60"
            >
              <span>{chip.label}</span>
              <button
                onClick={chip.reset}
                className="hover:text-white transition ml-0.5"
                title="Remove filter"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}
          <button
            onClick={handleReset}
            className="text-[11px] text-slate-400 hover:text-rose-400 font-semibold underline ml-1 cursor-pointer"
          >
            Clear All
          </button>
        </div>
      )}
    </div>
  );
};
```

---

## 5. Component Blueprint 4: `ProductivityCharts.tsx`

### 5.1 Responsibilities & Features
1. **Executive Hours Conservation KPI Cards**:
   - Total Working Hours ($H_w$): Productive on-job time, billable under RIL AMC tariff (₹625/hr).
   - Total Travelling Hours ($H_t$): Verified highway corridor transit.
   - Total Idle Hours ($H_i$): Unauthorized stops $> 15\text{ min}$, rest breaks, inactive buffer.
   - Total Shift Hours ($H_{shift}$): Validating $H_w + H_t + H_i == H_{shift}$.
   - Overall Fleet Utilization Rate: $\frac{H_w}{H_{shift}} \times 100$.
2. **Recharts Stacked Visualizations**:
   - Stacked Bar Chart with custom emerald (`#059669`), sky (`#0284C7`), and amber (`#F59E0B`) bars.
   - Composed secondary Y-Axis rendering utilization percentage curve.
   - Bespoke Level 3 Aura Glassmorphism Tooltip showing exact hours, minutes, and conservation checkmark.
3. **Drill-Down Technician Scorecard Table**:
   - Lists each technician with Working, Travelling, Idle, Shift Hours, Utilization %, Distance (km), and Jobs Closed.
   - Commercial Deputation Revenue column calculated as $H_w \times ₹625$ or ₹5,000/day.
   - Performance Badge: `EXEMPLARY` (crown), `NORMAL`, `ATTENTION REQUIRED`.
4. **Customer Hours Distribution Mini-Widget**:
   - Visual share of total working hours allocated across major clients (Reliance Bio-Energy, Adani, Sugarfed, etc.).

### 5.2 Complete Implementation Source Code

```tsx
/**
 * frontend/src/components/ProductivityCharts.tsx
 * Recharts Stacked Bar & Trend Analytics Engine for Working, Travelling, and Idle Hours.
 * Adheres strictly to the Conservation Law of Hours: H_shift = H_w + H_t + H_i.
 */

import React, { useState } from 'react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  Line, 
  ComposedChart, 
  AreaChart, 
  Area, 
  PieChart, 
  Pie, 
  Cell 
} from 'recharts';
import { 
  Briefcase, 
  Navigation, 
  Clock, 
  TrendingUp, 
  CheckCircle, 
  AlertTriangle, 
  Building2, 
  IndianRupee, 
  Award, 
  ArrowUpDown, 
  BarChart3, 
  LineChart as LineChartIcon,
  PieChart as PieChartIcon
} from 'lucide-react';
import { 
  ProductivityResponse, 
  TechnicianProductivityRecord, 
  TrendDataPoint 
} from '../types/dashboard';

interface ProductivityChartsProps {
  data: ProductivityResponse | null;
  isLoading?: boolean;
  onSelectTechnician?: (technicianId: string) => void;
}

// Custom Glassmorphic Dark Tooltip for Recharts
const CustomRechartsTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const working = payload.find((p: any) => p.dataKey === 'working')?.value || 0;
    const travelling = payload.find((p: any) => p.dataKey === 'travelling')?.value || 0;
    const idle = payload.find((p: any) => p.dataKey === 'idle')?.value || 0;
    const total = working + travelling + idle;
    const utilPct = total > 0 ? Math.round((working / total) * 100) : 0;

    return (
      <div className="bg-[#0B121E]/95 border border-slate-700/80 rounded-xl p-3.5 shadow-2xl backdrop-blur-md text-xs space-y-2 min-w-[200px]">
        <div className="font-bold text-white border-b border-slate-800 pb-1 flex items-center justify-between">
          <span>{label}</span>
          <span className="font-mono text-emerald-400 font-semibold">{utilPct}% Util</span>
        </div>

        <div className="space-y-1 text-slate-300 font-mono text-[11px]">
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-1.5 text-emerald-400">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              Working (H_w):
            </span>
            <span className="font-bold">{working.toFixed(1)} hrs</span>
          </div>

          <div className="flex items-center justify-between">
            <span className="flex items-center gap-1.5 text-sky-400">
              <span className="w-2 h-2 rounded-full bg-sky-500" />
              Travelling (H_t):
            </span>
            <span className="font-bold">{travelling.toFixed(1)} hrs</span>
          </div>

          <div className="flex items-center justify-between">
            <span className="flex items-center gap-1.5 text-amber-400">
              <span className="w-2 h-2 rounded-full bg-amber-500" />
              Idle (H_i):
            </span>
            <span className="font-bold">{idle.toFixed(1)} hrs</span>
          </div>
        </div>

        <div className="pt-1.5 border-t border-slate-800/80 flex items-center justify-between font-mono text-[11px] font-bold text-slate-200">
          <span>Total Shift:</span>
          <span>{total.toFixed(1)} hrs</span>
        </div>
      </div>
    );
  }
  return null;
};

export const ProductivityCharts: React.FC<ProductivityChartsProps> = ({
  data,
  isLoading = false,
  onSelectTechnician,
}) => {
  const [activeVisualMode, setActiveVisualMode] = useState<'stacked-bar' | 'trend-area'>('stacked-bar');
  const [sortField, setSortField] = useState<'utilization_pct' | 'working_hours' | 'revenue'>('utilization_pct');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  if (isLoading && !data) {
    return (
      <div className="w-full bg-[#0B121E] border border-slate-800/80 rounded-2xl p-8 flex flex-col items-center justify-center min-h-[400px] animate-pulse">
        <TrendingUp className="w-10 h-10 text-emerald-500 animate-spin mb-4" />
        <p className="text-slate-400 text-sm font-medium">Computing Multi-Tier Hours Analytics...</p>
      </div>
    );
  }

  const summary = data?.summary;
  const records = data?.technician_records || [];
  const trendData = data?.trend_data || [];
  const customerDistribution = data?.customer_distribution || [];

  // Sort technician scorecards
  const sortedRecords = [...records].sort((a, b) => {
    let valA = a[sortField as keyof TechnicianProductivityRecord] as number;
    let valB = b[sortField as keyof TechnicianProductivityRecord] as number;
    if (sortField === 'revenue') {
      valA = a.deputation_revenue_inr ?? (a.working_hours * 625);
      valB = b.deputation_revenue_inr ?? (b.working_hours * 625);
    }
    return sortDirection === 'desc' ? valB - valA : valA - valB;
  });

  const handleSortToggle = (field: 'utilization_pct' | 'working_hours' | 'revenue') => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'desc' ? 'asc' : 'desc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. Executive Hours Conservation KPI Cards (H_shift = H_w + H_t + H_i) */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3.5">
        {/* Working Hours */}
        <div className="bg-[#0B121E] border border-slate-800/80 rounded-2xl p-4 shadow-[0_4px_20px_rgba(0,0,0,0.3)]">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Working (H_w)</span>
            <div className="w-7 h-7 rounded-lg bg-emerald-950/80 text-emerald-400 flex items-center justify-center">
              <Briefcase className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-white font-mono tracking-tight">
            {summary?.total_working_hours ? `${summary.total_working_hours.toFixed(1)}h` : '0.0h'}
          </div>
          <div className="text-[11px] text-emerald-400 font-medium mt-1 flex items-center gap-1">
            <span>Productive on-site repair</span>
          </div>
        </div>

        {/* Travelling Hours */}
        <div className="bg-[#0B121E] border border-slate-800/80 rounded-2xl p-4 shadow-[0_4px_20px_rgba(0,0,0,0.3)]">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Travelling (H_t)</span>
            <div className="w-7 h-7 rounded-lg bg-sky-950/80 text-sky-400 flex items-center justify-center">
              <Navigation className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-white font-mono tracking-tight">
            {summary?.total_travelling_hours ? `${summary.total_travelling_hours.toFixed(1)}h` : '0.0h'}
          </div>
          <div className="text-[11px] text-sky-400 font-medium mt-1">
            <span>Verified transit corridor</span>
          </div>
        </div>

        {/* Idle Hours */}
        <div className="bg-[#0B121E] border border-slate-800/80 rounded-2xl p-4 shadow-[0_4px_20px_rgba(0,0,0,0.3)]">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Idle Hours (H_i)</span>
            <div className="w-7 h-7 rounded-lg bg-amber-950/80 text-amber-400 flex items-center justify-center">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-white font-mono tracking-tight">
            {summary?.total_idle_hours ? `${summary.total_idle_hours.toFixed(1)}h` : '0.0h'}
          </div>
          <div className="text-[11px] text-amber-400 font-medium mt-1">
            <span>Inactive / halt buffer</span>
          </div>
        </div>

        {/* Total Shift Hours */}
        <div className="bg-[#0B121E] border border-slate-800/80 rounded-2xl p-4 shadow-[0_4px_20px_rgba(0,0,0,0.3)]">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Shift</span>
            <div className="w-7 h-7 rounded-lg bg-slate-800 text-slate-300 flex items-center justify-center">
              <CheckCircle className="w-4 h-4 text-emerald-400" />
            </div>
          </div>
          <div className="text-2xl font-black text-white font-mono tracking-tight">
            {summary?.total_shift_hours ? `${summary.total_shift_hours.toFixed(1)}h` : '0.0h'}
          </div>
          <div className="text-[11px] text-slate-400 font-medium mt-1">
            <span>H_shift = H_w + H_t + H_i</span>
          </div>
        </div>

        {/* Fleet Utilization Rate */}
        <div className="bg-[#0B121E] border border-emerald-800/50 rounded-2xl p-4 shadow-[0_0_20px_rgba(5,150,105,0.15)] col-span-2 lg:col-span-1">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
              Fleet Utilization
            </span>
            <div className="w-7 h-7 rounded-lg bg-emerald-950/90 text-emerald-300 flex items-center justify-center">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-emerald-400 font-mono tracking-tight">
            {summary?.average_utilization_pct ? `${summary.average_utilization_pct.toFixed(1)}%` : '0.0%'}
          </div>
          <div className="text-[11px] text-slate-300 font-medium mt-1">
            <span>{summary?.jobs_completed_count ?? 0} jobs closed</span>
          </div>
        </div>
      </div>

      {/* 2. Recharts Master Visualizations Container */}
      <div className="bg-[#0B121E] border border-slate-800/80 rounded-2xl p-5 shadow-[0_10px_30px_rgba(0,0,0,0.5)]">
        {/* Chart Header Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
          <div>
            <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-emerald-400" />
              Hours Distribution & Productivity Trajectory ({data?.timeframe ? data.timeframe.toUpperCase() : 'DAILY'})
            </h3>
            <p className="text-xs text-slate-400">
              Multi-tier stacked breakdown: Productive Working vs Highway Transit vs Inactive Halts
            </p>
          </div>

          {/* Visualization Mode Toggle */}
          <div className="inline-flex bg-[#060A11] p-1 rounded-xl border border-slate-800 self-start sm:self-auto">
            <button
              onClick={() => setActiveVisualMode('stacked-bar')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
                activeVisualMode === 'stacked-bar'
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <BarChart3 className="w-3.5 h-3.5" />
              Stacked Bar
            </button>
            <button
              onClick={() => setActiveVisualMode('trend-area')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
                activeVisualMode === 'trend-area'
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <LineChartIcon className="w-3.5 h-3.5" />
              Trend Area
            </button>
          </div>
        </div>

        {/* Chart Canvas */}
        <div className="w-full h-80">
          <ResponsiveContainer width="100%" height="100%">
            {activeVisualMode === 'stacked-bar' ? (
              <BarChart data={trendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
                <XAxis 
                  dataKey="period" 
                  stroke="#64748B" 
                  fontSize={11} 
                  tickLine={false} 
                  axisLine={{ stroke: '#334155' }} 
                />
                <YAxis 
                  stroke="#64748B" 
                  fontSize={11} 
                  tickLine={false} 
                  axisLine={{ stroke: '#334155' }} 
                  unit="h" 
                />
                <Tooltip content={<CustomRechartsTooltip />} />
                <Legend 
                  wrapperStyle={{ paddingTop: '12px', fontSize: '12px' }} 
                  iconType="circle"
                />
                <Bar dataKey="working" name="Working Hours" stackId="a" fill="#059669" radius={[0, 0, 0, 0]} />
                <Bar dataKey="travelling" name="Travelling Hours" stackId="a" fill="#0284C7" radius={[0, 0, 0, 0]} />
                <Bar dataKey="idle" name="Idle Hours" stackId="a" fill="#F59E0B" radius={[4, 4, 0, 0]} />
              </BarChart>
            ) : (
              <AreaChart data={trendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="workingGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#059669" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#059669" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="travelGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0284C7" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#0284C7" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
                <XAxis dataKey="period" stroke="#64748B" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={11} tickLine={false} unit="h" />
                <Tooltip content={<CustomRechartsTooltip />} />
                <Legend wrapperStyle={{ paddingTop: '12px', fontSize: '12px' }} iconType="circle" />
                <Area type="monotone" dataKey="working" name="Working Hours" stroke="#059669" fillOpacity={1} fill="url(#workingGrad)" strokeWidth={2} />
                <Area type="monotone" dataKey="travelling" name="Travelling Hours" stroke="#0284C7" fillOpacity={1} fill="url(#travelGrad)" strokeWidth={2} />
                <Area type="monotone" dataKey="idle" name="Idle Hours" stroke="#F59E0B" fill="#F59E0B" fillOpacity={0.2} strokeWidth={2} />
              </AreaChart>
            )}
          </ResponsiveContainer>
        </div>
      </div>

      {/* 3. Drill-Down Technician Scorecard Table */}
      <div className="bg-[#0B121E] border border-slate-800/80 rounded-2xl overflow-hidden shadow-[0_10px_30px_rgba(0,0,0,0.5)]">
        <div className="p-4 border-b border-slate-800/80 bg-[#0F172A]/70 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-950/70 border border-emerald-800/50 flex items-center justify-center text-emerald-400">
              <Award className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white tracking-tight">
                Field Technician Productivity Scorecards ({sortedRecords.length})
              </h3>
              <p className="text-[11px] text-slate-400">
                Performance Rating, Working/Travel/Idle Split, and Deputation Revenue (₹5,000 / Man-Day)
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-400">Sort By:</span>
            <button
              onClick={() => handleSortToggle('utilization_pct')}
              className={`px-2.5 py-1 rounded-md border text-xs font-semibold cursor-pointer ${
                sortField === 'utilization_pct'
                  ? 'bg-emerald-950 text-emerald-400 border-emerald-800'
                  : 'bg-[#060A11] text-slate-400 border-slate-800'
              }`}
            >
              Utilization {sortField === 'utilization_pct' && (sortDirection === 'desc' ? '↓' : '↑')}
            </button>
            <button
              onClick={() => handleSortToggle('working_hours')}
              className={`px-2.5 py-1 rounded-md border text-xs font-semibold cursor-pointer ${
                sortField === 'working_hours'
                  ? 'bg-emerald-950 text-emerald-400 border-emerald-800'
                  : 'bg-[#060A11] text-slate-400 border-slate-800'
              }`}
            >
              Working Hours {sortField === 'working_hours' && (sortDirection === 'desc' ? '↓' : '↑')}
            </button>
            <button
              onClick={() => handleSortToggle('revenue')}
              className={`px-2.5 py-1 rounded-md border text-xs font-semibold cursor-pointer ${
                sortField === 'revenue'
                  ? 'bg-emerald-950 text-emerald-400 border-emerald-800'
                  : 'bg-[#060A11] text-slate-400 border-slate-800'
              }`}
            >
              Revenue {sortField === 'revenue' && (sortDirection === 'desc' ? '↓' : '↑')}
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#060A11]/90 text-slate-400 font-semibold border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Technician Name & ID</th>
                <th className="py-3 px-4">Working (H_w)</th>
                <th className="py-3 px-4">Travelling (H_t)</th>
                <th className="py-3 px-4">Idle (H_i)</th>
                <th className="py-3 px-4">Total Shift</th>
                <th className="py-3 px-4">Utilization</th>
                <th className="py-3 px-4">Distance</th>
                <th className="py-3 px-4">Jobs</th>
                <th className="py-3 px-4">Deputation Revenue</th>
                <th className="py-3 px-4 text-center">Status Badge</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300 font-mono">
              {sortedRecords.length === 0 ? (
                <tr>
                  <td colSpan={10} className="py-8 text-center text-slate-500 font-sans italic">
                    No technician records match current timeframe or filter criteria.
                  </td>
                </tr>
              ) : (
                sortedRecords.map((tech) => {
                  const revenue = tech.deputation_revenue_inr ?? (tech.working_hours * 625);
                  return (
                    <tr
                      key={tech.technician_id}
                      className="hover:bg-slate-800/40 transition-colors cursor-pointer group"
                      onClick={() => onSelectTechnician?.(tech.technician_id)}
                    >
                      {/* Name & ID */}
                      <td className="py-3 px-4 font-sans">
                        <div className="font-semibold text-white group-hover:text-emerald-400 transition-colors">
                          {tech.technician_name}
                        </div>
                        <div className="text-[10px] text-slate-400 font-mono">
                          {tech.technician_id} {tech.region ? `• ${tech.region}` : ''}
                        </div>
                      </td>

                      {/* Working Hours */}
                      <td className="py-3 px-4 text-emerald-400 font-bold">
                        {tech.working_hours.toFixed(1)}h
                      </td>

                      {/* Travelling Hours */}
                      <td className="py-3 px-4 text-sky-400">
                        {tech.travelling_hours.toFixed(1)}h
                      </td>

                      {/* Idle Hours */}
                      <td className="py-3 px-4 text-amber-400">
                        {tech.idle_hours.toFixed(1)}h
                      </td>

                      {/* Total Shift */}
                      <td className="py-3 px-4 font-bold text-slate-200">
                        {tech.shift_hours.toFixed(1)}h
                      </td>

                      {/* Utilization */}
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <span
                            className={`font-bold ${
                              tech.utilization_pct >= 75
                                ? 'text-emerald-400'
                                : tech.utilization_pct >= 60
                                ? 'text-blue-400'
                                : 'text-amber-400'
                            }`}
                          >
                            {tech.utilization_pct.toFixed(1)}%
                          </span>
                        </div>
                      </td>

                      {/* Distance */}
                      <td className="py-3 px-4 text-slate-300">
                        {tech.travel_distance_km ? `${tech.travel_distance_km.toFixed(1)} km` : tech.distance_km ? `${tech.distance_km.toFixed(1)} km` : '—'}
                      </td>

                      {/* Jobs */}
                      <td className="py-3 px-4 text-slate-200">
                        {tech.jobs_count}
                      </td>

                      {/* Revenue */}
                      <td className="py-3 px-4 font-semibold text-emerald-300">
                        ₹{revenue.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                      </td>

                      {/* Status Rating Badge */}
                      <td className="py-3 px-4 text-center font-sans">
                        {tech.utilization_pct >= 75 ? (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-emerald-950/80 text-emerald-300 border border-emerald-800/60">
                            EXEMPLARY
                          </span>
                        ) : tech.utilization_pct >= 60 ? (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-blue-950/80 text-blue-300 border border-blue-800/60">
                            NORMAL
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-amber-950/80 text-amber-300 border border-amber-800/60">
                            ATTENTION
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 4. Customer Hours Share Distribution Mini-Widget */}
      {customerDistribution.length > 0 && (
        <div className="bg-[#0B121E] border border-slate-800/80 rounded-2xl p-5 shadow-[0_10px_30px_rgba(0,0,0,0.5)]">
          <div className="flex items-center gap-2 mb-4">
            <Building2 className="w-4 h-4 text-blue-400" />
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Customer Field Service Hours Share
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {customerDistribution.map((cust, i) => (
              <div
                key={i}
                className="bg-[#0F172A] border border-slate-800/70 rounded-xl p-3.5 flex flex-col justify-between"
              >
                <div>
                  <div className="text-xs font-semibold text-slate-200 truncate" title={cust.client_company_name || cust.customer_name}>
                    {cust.client_company_name || cust.customer_name}
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1">
                    {cust.jobs_count} service work orders
                  </div>
                </div>

                <div className="mt-3 pt-2.5 border-t border-slate-800/60 flex items-center justify-between font-mono">
                  <span className="text-emerald-400 font-bold text-sm">
                    {cust.total_hours.toFixed(1)} hrs
                  </span>
                  <span className="text-slate-400 text-xs font-semibold">
                    {cust.percentage.toFixed(1)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
```

---

## 6. Shared Formatters Utility (`frontend/src/utils/formatters.ts`)

To ensure consistent numeric, temporal, and monetary representations across all components, the implementer should establish `frontend/src/utils/formatters.ts`:

```typescript
/**
 * frontend/src/utils/formatters.ts
 * Enterprise formatting utilities for Krone Agriculture India FSM.
 */

export function formatHours(hours: number | undefined | null): string {
  if (hours == null) return '0.0h';
  return `${hours.toFixed(1)}h`;
}

export function formatCurrencyINR(amount: number | undefined | null): string {
  if (amount == null) return '₹0';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatDistanceKm(km: number | undefined | null): string {
  if (km == null) return '0.0 km';
  return `${km.toFixed(1)} km`;
}

export function formatDateTime(isoString: string | undefined | null): string {
  if (!isoString) return '—';
  try {
    const d = new Date(isoString);
    return d.toLocaleString('en-IN', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return isoString;
  }
}
```

---

## 7. Verification & Implementation Strategy

### 7.1 Cross-Cutting Verification Rules
1. **Zero Full-Page Reload**: All interactions in `FilterBar.tsx` (switching between Daily, Weekly, Monthly; picking a technician or customer; or clearing filters) must trigger state changes and API fetches asynchronously without causing browser window reload.
2. **Serial Number Copying**: Clicking the copy button next to the 7-digit serial number (`BP1290-78401`, `FV1500-33901`, etc.) must copy the exact string to `navigator.clipboard` and toggle the icon to a green checkmark for 2 seconds.
3. **Hours Conservation Invariant**: In `ProductivityCharts.tsx`, the tooltips and table must satisfy $|H_{shift} - (H_w + H_t + H_i)| \le 0.05\text{ h}$.
4. **Authentic Equipment Family Names**: Must feature authentic Krone heavy machinery (`BigPack 1290 HDP`, `Fortima V 1500`, `BiG X 680`, `EasyCut B 870`, `Swadro TC 880`).
5. **No Broken References or Missing Handlers**: All callback props (`onSelectTechnician`, `onSelectJob`, `onInspectRoute`, `onFilterChange`) have clean fallbacks and optional bindings.

---

## 8. Worker Handoff Checklist

- [ ] Ensure `frontend/src/components/LivePulseBoard.tsx` is written with exact code from Section 2.2.
- [ ] Ensure `frontend/src/components/MachineryTable.tsx` is written with exact code from Section 3.2.
- [ ] Ensure `frontend/src/components/FilterBar.tsx` is written with exact code from Section 4.2.
- [ ] Ensure `frontend/src/components/ProductivityCharts.tsx` is written with exact code from Section 5.2.
- [ ] Ensure `frontend/src/utils/formatters.ts` is available as outlined in Section 6.
- [ ] Verify TypeScript compiles cleanly (`tsc --noEmit` or `npm run build`).
- [ ] Verify test suite `pytest tests/ -v` remains 100% passing.
