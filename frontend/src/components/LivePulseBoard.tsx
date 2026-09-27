/**
 * frontend/src/components/LivePulseBoard.tsx
 * Real-Time Operational Pulse Board for Krone Agriculture India Field Operations.
 * Displays technicians on paid jobs, technicians on holiday/leave, and today's jobs pipeline.
 * Supports both Bright (Default) and Dark modes.
 */

import React, { useState, useMemo } from 'react';
import { 
  Wrench, 
  Clock, 
  CheckCircle2, 
  AlertCircle, 
  CalendarOff, 
  Navigation, 
  Search, 
  ExternalLink, 
  UserCheck, 
  Tag, 
  Activity,
  ChevronDown,
  ChevronUp,
  MapPin,
  Tractor,
  ArrowRight
} from 'lucide-react';
import { 
  PulseResponse, 
  JobItem, 
} from '../types/dashboard';

interface LivePulseBoardProps {
  pulseData: PulseResponse | null;
  isLoading?: boolean;
  onSelectTechnician?: (technicianId: string) => void;
  onInspectRoute?: (technicianId: string) => void;
  onSelectJob?: (jobId: string) => void;
  theme?: 'bright' | 'dark';
}

export const LivePulseBoard: React.FC<LivePulseBoardProps> = ({
  pulseData,
  isLoading = false,
  onSelectTechnician,
  onInspectRoute,
  onSelectJob,
  theme = 'bright',
}) => {
  const [jobSearchQuery, setJobSearchQuery] = useState('');
  const [selectedStatusFilter, setSelectedStatusFilter] = useState<string>('ALL');
  const [showLeaveDrawer, setShowLeaveDrawer] = useState(false);

  const isDark = theme === 'dark';
  const cardBg = isDark ? 'bg-[#0B121E] border-slate-800 text-white' : 'bg-white border-slate-200 text-slate-900 shadow-sm';
  const subBg = isDark ? 'bg-[#0F172A] border-slate-800' : 'bg-slate-50 border-slate-200';
  const textMuted = isDark ? 'text-slate-400' : 'text-slate-500';
  const textHeader = isDark ? 'text-white' : 'text-slate-900';

  // Status badge styling helper
  const getStatusBadge = (status: string) => {
    const s = status.toLowerCase();
    if (s === 'in progress') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300 dark:bg-emerald-950 dark:text-emerald-300 dark:border-emerald-800">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          In Progress
        </span>
      );
    }
    if (s === 'completed') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-300 dark:bg-blue-950 dark:text-blue-300 dark:border-blue-800">
          <CheckCircle2 className="w-3 h-3 text-blue-600" />
          Completed
        </span>
      );
    }
    if (s === 'start travel') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-sky-100 text-sky-800 border border-sky-300 dark:bg-sky-950 dark:text-sky-300 dark:border-sky-800">
          <Navigation className="w-3 h-3 text-sky-600" />
          Start Travel
        </span>
      );
    }
    if (s === 'hold') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-300 dark:bg-amber-950 dark:text-amber-300 dark:border-amber-800">
          <AlertCircle className="w-3 h-3 text-amber-600" />
          On Hold
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-300 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700">
        {status}
      </span>
    );
  };

  const getPriorityBadge = (priority?: string) => {
    const p = (priority || 'NORMAL').toUpperCase();
    if (p === 'HIGH' || p === 'EMERGENCY') {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase bg-rose-100 text-rose-800 border border-rose-300 dark:bg-rose-950 dark:text-rose-300 dark:border-rose-800">
          {p}
        </span>
      );
    }
    if (p === 'MEDIUM') {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase bg-amber-100 text-amber-800 border border-amber-300 dark:bg-amber-950 dark:text-amber-300 dark:border-amber-800">
          MED
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase bg-slate-100 text-slate-600 border border-slate-300 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700">
        NORMAL
      </span>
    );
  };

  const filteredJobs = useMemo(() => {
    if (!pulseData?.today_jobs) return [];
    return pulseData.today_jobs.filter((job) => {
      const matchesSearch =
        job.job_id.toLowerCase().includes(jobSearchQuery.toLowerCase()) ||
        job.customer_name.toLowerCase().includes(jobSearchQuery.toLowerCase()) ||
        (job.machine_serial && job.machine_serial.toLowerCase().includes(jobSearchQuery.toLowerCase())) ||
        (job.title && job.title.toLowerCase().includes(jobSearchQuery.toLowerCase()));

      const matchesStatus =
        selectedStatusFilter === 'ALL' ||
        job.status.toLowerCase() === selectedStatusFilter.toLowerCase();

      return matchesSearch && matchesStatus;
    });
  }, [pulseData?.today_jobs, jobSearchQuery, selectedStatusFilter]);

  if (isLoading && !pulseData) {
    return (
      <div className={`w-full rounded-2xl p-8 border flex flex-col items-center justify-center min-h-[380px] animate-pulse ${cardBg}`}>
        <Activity className="w-10 h-10 text-emerald-500 animate-spin mb-4" />
        <p className={`text-sm font-medium ${textMuted}`}>Synchronizing Live Field Operations Pulse...</p>
      </div>
    );
  }

  const kpis = pulseData?.kpis;
  const activeTechs = pulseData?.technicians_on_jobs || [];
  const leaveTechs = pulseData?.technicians_on_leave || [];

  return (
    <div className="space-y-6">
      {/* 1. Header & Live Summary Status Ribbon */}
      <div className={`rounded-2xl border p-5 ${cardBg}`}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3.5">
            <div className="w-11 h-11 rounded-xl bg-emerald-50 dark:bg-emerald-950/70 border border-emerald-200 dark:border-emerald-800/50 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
              <Activity className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className={`text-lg font-bold tracking-tight ${textHeader}`}>
                  Live Field Operational Pulse
                </h2>
                <span className="flex h-2.5 w-2.5 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500" />
                </span>
              </div>
              <p className={`text-xs ${textMuted}`}>
                Real-time technician deployment, live work orders, and field availability
              </p>
            </div>
          </div>

          {/* Quick Counter Pills */}
          <div className="flex flex-wrap items-center gap-2.5">
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs ${
              isDark ? 'bg-[#0F172A] border-emerald-800/40' : 'bg-emerald-50 border-emerald-200'
            }`}>
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              <span className="font-medium text-emerald-800 dark:text-slate-300">Active on Paid Jobs:</span>
              <span className="font-bold text-emerald-700 dark:text-emerald-400 font-mono text-sm">
                {kpis?.technicians_on_paid_jobs ?? activeTechs.length}
              </span>
            </div>

            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs ${
              isDark ? 'bg-[#0F172A] border-slate-700/60' : 'bg-blue-50 border-blue-200'
            }`}>
              <span className="w-2 h-2 rounded-full bg-blue-500" />
              <span className="font-medium text-blue-800 dark:text-slate-300">Total Active Fleet:</span>
              <span className="font-bold text-blue-700 dark:text-blue-400 font-mono text-sm">
                {kpis?.technicians_active_total ?? 12}
              </span>
            </div>

            <button
              onClick={() => setShowLeaveDrawer(!showLeaveDrawer)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs transition cursor-pointer ${
                isDark ? 'bg-[#0F172A] border-amber-800/40 text-amber-300' : 'bg-amber-50 border-amber-200 text-amber-800'
              }`}
            >
              <CalendarOff className="w-3.5 h-3.5 text-amber-500" />
              <span className="font-medium">On Leave / Off:</span>
              <span className="font-bold font-mono text-sm">
                {kpis?.technicians_on_leave ?? leaveTechs.length}
              </span>
              {showLeaveDrawer ? (
                <ChevronUp className="w-3.5 h-3.5 ml-1" />
              ) : (
                <ChevronDown className="w-3.5 h-3.5 ml-1" />
              )}
            </button>
          </div>
        </div>

        {/* Expandable Leave Drawer */}
        {showLeaveDrawer && (
          <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-800">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-amber-600 dark:text-amber-400 flex items-center gap-2 mb-3">
              <CalendarOff className="w-3.5 h-3.5" />
              Technicians on Approved Leave / Scheduled Off Today ({leaveTechs.length})
            </h3>
            {leaveTechs.length === 0 ? (
              <p className={`text-xs italic ${textMuted}`}>No technicians are currently on leave.</p>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {leaveTechs.map((tech) => (
                  <div
                    key={tech.technician_id}
                    onClick={() => onSelectTechnician?.(tech.technician_id)}
                    className={`p-3 rounded-xl border flex items-center justify-between cursor-pointer hover:border-amber-400 transition ${subBg}`}
                  >
                    <div>
                      <div className={`text-sm font-bold ${textHeader}`}>{tech.name}</div>
                      <div className={`text-xs ${textMuted} flex items-center gap-2 mt-0.5`}>
                        <span className="font-mono">{tech.technician_id}</span>
                        <span>•</span>
                        <span>{tech.region}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-100 text-amber-800 border border-amber-300 dark:bg-amber-950 dark:text-amber-300">
                        {tech.leave_type}
                      </span>
                      {tech.return_date && (
                        <div className="text-[10px] text-slate-500 mt-1 font-mono">
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
            <UserCheck className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            <h3 className={`text-sm font-bold uppercase tracking-wider ${textHeader}`}>
              Technicians on Paid Jobs ({activeTechs.length})
            </h3>
          </div>
          <span className={`text-xs ${textMuted}`}>
            Fieldy Live Assignment • Deputation Rate ₹5,000 / Day (₹625 / hr)
          </span>
        </div>

        {activeTechs.length === 0 ? (
          <div className={`rounded-xl p-8 text-center text-sm border ${cardBg}`}>
            No technicians currently assigned to active paid jobs.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {activeTechs.map((tech) => (
              <div
                key={tech.technician_id}
                onClick={() => onSelectTechnician?.(tech.technician_id)}
                className={`rounded-2xl p-4 border transition-all duration-200 flex flex-col justify-between group hover:-translate-y-0.5 cursor-pointer ${
                  isDark
                    ? 'bg-[#0F172A] border-slate-800 hover:border-emerald-600'
                    : 'bg-white border-slate-200 hover:border-emerald-400 shadow-sm hover:shadow-md'
                }`}
              >
                <div>
                  {/* Top: Avatar, Name & Live Badge */}
                  <div className="flex items-start justify-between gap-2 mb-2.5">
                    <div className="flex items-center gap-2.5">
                      <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-600 to-teal-700 flex items-center justify-center text-white font-extrabold text-xs shadow-md">
                        {tech.name.split(' ').map((n) => n[0]).join('').slice(0, 2)}
                      </div>
                      <div>
                        <h4 className={`text-sm font-bold group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors leading-tight ${textHeader}`}>
                          {tech.name}
                        </h4>
                        <div className="text-[11px] text-slate-500 font-mono">
                          {tech.technician_id}
                        </div>
                      </div>
                    </div>
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300 dark:bg-emerald-950 dark:text-emerald-300">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping" />
                      LIVE
                    </span>
                  </div>

                  {/* Job ID & Machine Binding */}
                  <div className={`p-2.5 rounded-xl border text-xs space-y-1.5 ${subBg}`}>
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-mono font-bold text-emerald-700 dark:text-emerald-400">
                        Job: {tech.live_job_id || 'Active'}
                      </span>
                      <span className="text-[10px] font-semibold px-1.5 py-0.2 rounded bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
                        Paid Service
                      </span>
                    </div>

                    <div className={`font-semibold text-xs line-clamp-1 ${textHeader}`}>
                      {tech.machine_asset || 'Krone Heavy Asset'}
                    </div>

                    <div className={`text-[11px] line-clamp-1 ${textMuted}`}>
                      {tech.customer_company || 'Reliance Industries Ltd'}
                    </div>
                  </div>
                </div>

                {/* Bottom: Elapsed Time & Action Links */}
                <div className="mt-3 pt-2.5 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-1 text-slate-500 text-[11px]">
                    <Clock className="w-3.5 h-3.5 text-emerald-500" />
                    <span>{Math.floor((tech.elapsed_minutes || 210) / 60)}h {(tech.elapsed_minutes || 210) % 60}m</span>
                  </div>

                  <span className="text-emerald-600 dark:text-emerald-400 font-bold text-[11px] flex items-center gap-1 group-hover:translate-x-0.5 transition-transform">
                    View Dossier
                    <ArrowRight className="w-3 h-3" />
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 3. Today's Work Orders Pipeline Table */}
      <div className={`rounded-2xl border overflow-hidden ${cardBg}`}>
        {/* Table Filter & Search Header */}
        <div className={`p-4 border-b flex flex-col md:flex-row md:items-center justify-between gap-3 ${
          isDark ? 'border-slate-800 bg-[#0F172A]/50' : 'border-slate-200 bg-slate-50/80'
        }`}>
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-emerald-100 dark:bg-emerald-950/60 border border-emerald-300 dark:border-emerald-800/40 flex items-center justify-center text-emerald-700 dark:text-emerald-400">
              <Wrench className="w-4 h-4" />
            </div>
            <div>
              <h3 className={`text-sm font-bold tracking-tight ${textHeader}`}>
                Today's Work Orders ({filteredJobs.length} of {pulseData?.today_jobs?.length ?? 0})
              </h3>
              <p className={`text-[11px] ${textMuted}`}>Fieldy Job Pipeline (`SR-26-XXXX` Series)</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {/* Status Filter Chips */}
            <div className={`flex items-center rounded-lg p-0.5 border ${isDark ? 'bg-[#060A11] border-slate-800' : 'bg-white border-slate-300'}`}>
              {['ALL', 'In Progress', 'Completed', 'Hold'].map((status) => (
                <button
                  key={status}
                  onClick={() => setSelectedStatusFilter(status)}
                  className={`px-2.5 py-1 rounded-md text-xs font-semibold transition cursor-pointer ${
                    selectedStatusFilter.toLowerCase() === status.toLowerCase()
                      ? 'bg-emerald-600 text-white shadow-sm'
                      : textMuted
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
                id="pulse-search"
                type="text"
                value={jobSearchQuery}
                onChange={(e) => setJobSearchQuery(e.target.value)}
                placeholder="Search job ID, client, serial..."
                className={`rounded-lg pl-8 pr-3 py-1.5 text-xs border focus:outline-none focus:ring-2 focus:ring-emerald-500 w-44 md:w-56 ${
                  isDark
                    ? 'bg-[#060A11] border-slate-800 text-white placeholder-slate-500'
                    : 'bg-white border-slate-300 text-slate-900 placeholder-slate-400'
                }`}
              />
            </div>
          </div>
        </div>

        {/* Table Content */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className={`border-b ${isDark ? 'bg-[#060A11]/80 text-slate-400 border-slate-800' : 'bg-slate-50 text-slate-600 border-slate-200'}`}>
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
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
              {filteredJobs.length === 0 ? (
                <tr>
                  <td colSpan={7} className={`py-8 text-center italic ${textMuted}`}>
                    No work orders found matching the filter criteria.
                  </td>
                </tr>
              ) : (
                filteredJobs.map((job) => (
                  <tr
                    key={job.job_id}
                    className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition group cursor-pointer"
                    onClick={() => onSelectJob?.(job.job_id)}
                  >
                    {/* Job ID & Priority */}
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/40 px-2 py-0.5 rounded text-xs">
                          {job.job_id}
                        </span>
                        {getPriorityBadge(job.priority)}
                      </div>
                      {job.title && (
                        <div className={`text-[11px] mt-1 max-w-xs truncate ${textMuted}`} title={job.title}>
                          {job.title}
                        </div>
                      )}
                    </td>

                    {/* Status */}
                    <td className="py-3 px-4 whitespace-nowrap">
                      {getStatusBadge(job.status)}
                    </td>

                    {/* Customer */}
                    <td className="py-3 px-4">
                      <div className={`font-semibold ${textHeader}`}>{job.customer_name}</div>
                      {job.scheduled_start && (
                        <div className="text-[10px] text-slate-500 mt-0.5">
                          Sched: {new Date(job.scheduled_start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </div>
                      )}
                    </td>

                    {/* Machine & Serial */}
                    <td className="py-3 px-4">
                      <div className={`font-medium ${textHeader}`}>{job.machine_name}</div>
                      <div className="text-[10px] font-mono text-emerald-700 dark:text-emerald-400 mt-0.5">
                        SN: {job.machine_serial}
                      </div>
                    </td>

                    {/* Assigned Technicians */}
                    <td className="py-3 px-4">
                      <div className="flex flex-wrap gap-1">
                        {job.assigned_technicians.map((techName, idx) => (
                          <span
                            key={idx}
                            className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-slate-100 text-slate-800 border border-slate-300 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700"
                          >
                            {techName}
                          </span>
                        ))}
                      </div>
                    </td>

                    {/* Job Type */}
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950 dark:text-emerald-300 dark:border-emerald-800">
                        {job.job_type}
                      </span>
                    </td>

                    {/* Action */}
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectJob?.(job.job_id);
                        }}
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg border border-slate-200 dark:border-slate-700 hover:border-emerald-500 text-xs font-semibold transition"
                      >
                        <span>Details</span>
                        <ExternalLink className="w-3 h-3 text-slate-400" />
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
