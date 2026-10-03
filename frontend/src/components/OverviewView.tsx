/**
 * frontend/src/components/OverviewView.tsx
 * Ultra-Clean, Simple Plain Executive Dashboard for Krone Agriculture India.
 * Styled with Rich Industrial Colors (Krone Racing Forest Green, Royal Sapphire, Warm Harvest Amber, Deep Obsidian).
 * Eliminates visual clutter while presenting all mission-critical field operations at a glance.
 */

import React, { useState } from 'react';
import { 
  Briefcase, 
  UserCheck, 
  FileText, 
  Tractor, 
  ArrowRight, 
  CheckCircle2, 
  Clock, 
  MapPin, 
  ShieldAlert, 
  Zap, 
  ExternalLink,
  ChevronRight,
  Search
} from 'lucide-react';
import { PulseKpis, JobItem } from '../types/dashboard';
import { ExtendedTechnicianData } from './TechnicianDetailView';

interface OverviewViewProps {
  kpis: PulseKpis | null;
  todayJobs: JobItem[];
  technicians: ExtendedTechnicianData[];
  onSelectTechnician: (techId: string) => void;
  onNavigateTab: (tabId: 'all' | 'audit' | 'amcs' | 'attendance' | 'telematics' | 'machines' | 'analytics' | 'automations') => void;
  theme: 'bright' | 'dark';
}

export const OverviewView: React.FC<OverviewViewProps> = ({
  kpis,
  todayJobs,
  technicians,
  onSelectTechnician,
  onNavigateTab,
  theme,
}) => {
  const isDark = theme === 'dark';
  const [jobSearch, setJobSearch] = useState('');

  // Rich Color Themes & Tokens
  const cardBg = isDark ? 'bg-[#0E1524] border-slate-800 text-white' : 'bg-white border-slate-200/90 text-slate-900 shadow-sm';
  const tableHeaderBg = isDark ? 'bg-slate-900/90 text-slate-400' : 'bg-slate-50 text-slate-600';
  const rowHover = isDark ? 'hover:bg-slate-800/50' : 'hover:bg-slate-50/80';
  const textMuted = isDark ? 'text-slate-400' : 'text-slate-600 font-medium';
  const borderSub = isDark ? 'border-slate-800' : 'border-slate-200';

  const filteredJobs = todayJobs.filter(j => 
    j.customer_name.toLowerCase().includes(jobSearch.toLowerCase()) ||
    j.job_id.toLowerCase().includes(jobSearch.toLowerCase()) ||
    ((j.machine_name || j.title || '').toLowerCase().includes(jobSearch.toLowerCase())) ||
    j.assigned_technicians.some(t => t.toLowerCase().includes(jobSearch.toLowerCase()))
  );

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      
      {/* ===================================================================== */}
      {/* 1. TOP 4 RICH BENTO KPI METRIC CARDS                                 */}
      {/* ===================================================================== */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* KPI 1: Active Work Orders (Royal Sapphire Blue) */}
        <div 
          onClick={() => onNavigateTab('machines')}
          className={`p-5 rounded-2xl border transition-all duration-200 cursor-pointer group hover:-translate-y-0.5 ${cardBg} hover:border-blue-500`}
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold font-mono tracking-wider uppercase text-blue-600 dark:text-blue-400">
              Work Orders Today
            </span>
            <div className="p-2 rounded-xl bg-blue-100 dark:bg-blue-950/80 text-blue-600 dark:text-blue-400 group-hover:scale-110 transition-transform">
              <Briefcase className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black font-mono tracking-tight text-blue-600 dark:text-blue-400">
              {kpis?.total_jobs_today ?? todayJobs.length}
            </span>
            <span className={`text-xs ${textMuted}`}>Dispatched Orders</span>
          </div>
          <div className={`mt-4 pt-3 border-t ${borderSub} flex items-center justify-between text-xs`}>
            <span className="text-emerald-600 dark:text-emerald-400 font-bold flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              {kpis?.jobs_completed_today ?? 2} Completed
            </span>
            <span className="text-blue-600 dark:text-blue-400 font-bold">
              {Math.max(0, (kpis?.total_jobs_today ?? todayJobs.length) - (kpis?.jobs_completed_today ?? 2))} In Progress →
            </span>
          </div>
        </div>

        {/* KPI 2: Field Technicians Working (Krone Racing Forest Emerald) */}
        <div 
          onClick={() => onNavigateTab('attendance')}
          className={`p-5 rounded-2xl border transition-all duration-200 cursor-pointer group hover:-translate-y-0.5 ${cardBg} hover:border-emerald-500`}
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold font-mono tracking-wider uppercase text-emerald-600 dark:text-emerald-400">
              Field Technicians
            </span>
            <div className="p-2 rounded-xl bg-emerald-100 dark:bg-emerald-950/80 text-emerald-600 dark:text-emerald-400 group-hover:scale-110 transition-transform">
              <UserCheck className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black font-mono tracking-tight text-emerald-600 dark:text-emerald-400">
              {kpis?.technicians_on_paid_jobs ?? 8}
            </span>
            <span className={`text-xs ${textMuted}`}>On Paid Jobs (12 Active)</span>
          </div>
          <div className={`mt-4 pt-3 border-t ${borderSub} flex items-center justify-between text-xs`}>
            <span className="text-emerald-600 dark:text-emerald-400 font-bold flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              Punched In & Deployed
            </span>
            <span className="text-emerald-600 dark:text-emerald-400 font-bold">Roster →</span>
          </div>
        </div>

        {/* KPI 3: Commercial AMCs & Retainers (Warm Agri Harvest Amber) */}
        <div 
          onClick={() => onNavigateTab('amcs')}
          className={`p-5 rounded-2xl border transition-all duration-200 cursor-pointer group hover:-translate-y-0.5 ${cardBg} hover:border-amber-500`}
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold font-mono tracking-wider uppercase text-amber-600 dark:text-amber-400">
              Active AMCs & Retainers
            </span>
            <div className="p-2 rounded-xl bg-amber-100 dark:bg-amber-950/80 text-amber-600 dark:text-amber-400 group-hover:scale-110 transition-transform">
              <FileText className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black font-mono tracking-tight text-amber-600 dark:text-amber-400">
              11
            </span>
            <span className={`text-xs ${textMuted}`}>Contracts (₹264 Lakhs)</span>
          </div>
          <div className={`mt-4 pt-3 border-t ${borderSub} flex items-center justify-between text-xs`}>
            <span className="text-amber-600 dark:text-amber-400 font-bold">
              RIL (4 sites) & Adani Agri
            </span>
            <span className="text-amber-600 dark:text-amber-400 font-bold">Ledger →</span>
          </div>
        </div>

        {/* KPI 4: Machinery Health Under Service (Rich Imperial Violet) */}
        <div 
          onClick={() => onNavigateTab('machines')}
          className={`p-5 rounded-2xl border transition-all duration-200 cursor-pointer group hover:-translate-y-0.5 ${cardBg} hover:border-violet-500`}
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold font-mono tracking-wider uppercase text-violet-600 dark:text-violet-400">
              Machinery Under Service
            </span>
            <div className="p-2 rounded-xl bg-violet-100 dark:bg-violet-950/80 text-violet-600 dark:text-violet-400 group-hover:scale-110 transition-transform">
              <Tractor className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black font-mono tracking-tight text-violet-600 dark:text-violet-400">
              5
            </span>
            <span className={`text-xs ${textMuted}`}>Commercial Units</span>
          </div>
          <div className={`mt-4 pt-3 border-t ${borderSub} flex items-center justify-between text-xs`}>
            <span className="text-violet-600 dark:text-violet-400 font-bold">
              Swadro, Fortima, BiG X
            </span>
            <span className="text-violet-600 dark:text-violet-400 font-bold">Fleet →</span>
          </div>
        </div>

      </div>

      {/* ===================================================================== */}
      {/* 2. MAIN OPERATIONS SPLIT: WORK ORDERS (65%) & MANPOWER ROSTER (35%)   */}
      {/* ===================================================================== */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        {/* LEFT COLUMN: LIVE FIELD WORK ORDERS (7 Cols) */}
        <div className={`lg:col-span-7 rounded-2xl border p-5 ${cardBg}`}>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
            <div>
              <h3 className="text-base font-bold flex items-center gap-2 text-slate-900 dark:text-white">
                <Briefcase className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                Live Field Work Orders
              </h3>
              <p className={`text-xs ${textMuted}`}>
                Dispatched service jobs currently active across client sites
              </p>
            </div>
            
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search jobs, customers..."
                  value={jobSearch}
                  onChange={(e) => setJobSearch(e.target.value)}
                  className={`pl-8 pr-3 py-1.5 rounded-xl text-xs border ${
                    isDark ? 'bg-slate-900 border-slate-700 text-white' : 'bg-slate-50 border-slate-300 text-slate-900'
                  } focus:outline-none focus:ring-2 focus:ring-emerald-500`}
                />
              </div>
              <button
                onClick={() => onNavigateTab('machines')}
                className="text-xs font-bold text-emerald-600 dark:text-emerald-400 hover:underline flex items-center gap-0.5"
              >
                <span>All ({todayJobs.length})</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Clean Work Orders Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className={`border-b ${borderSub} ${tableHeaderBg} text-[11px] font-mono uppercase tracking-wider`}>
                  <th className="py-2.5 px-3 font-bold">Job ID</th>
                  <th className="py-2.5 px-3 font-bold">Customer & Location</th>
                  <th className="py-2.5 px-3 font-bold">Machinery Asset</th>
                  <th className="py-2.5 px-3 font-bold">Specialist</th>
                  <th className="py-2.5 px-3 font-bold">Status</th>
                  <th className="py-2.5 px-3 font-bold text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {filteredJobs.slice(0, 6).map((job) => (
                  <tr key={job.job_id} className={`transition ${rowHover}`}>
                    <td className="py-3 px-3 font-mono font-bold text-emerald-700 dark:text-emerald-400 whitespace-nowrap">
                      {job.job_id}
                    </td>
                    <td className="py-3 px-3">
                      <div className="font-bold text-slate-900 dark:text-white truncate max-w-[150px]">
                        {job.customer_name}
                      </div>
                      <div className="text-[10px] text-slate-500 truncate max-w-[150px]">
                        {job.scheduled_start ? `Scheduled: ${job.scheduled_start}` : 'Field Worksite'}
                      </div>
                    </td>
                    <td className="py-3 px-3 font-medium text-slate-700 dark:text-slate-300">
                      <span className="truncate block max-w-[160px]" title={job.machine_name || job.title || 'Krone Machinery'}>
                        {job.machine_name || job.title || 'Krone Machinery'}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      <span className="font-semibold text-slate-900 dark:text-slate-100">
                        {job.assigned_technicians.join(', ')}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        job.status.toLowerCase() === 'in progress'
                          ? 'bg-emerald-100 text-emerald-900 border border-emerald-300 dark:bg-emerald-950 dark:text-emerald-300'
                          : 'bg-blue-100 text-blue-900 border border-blue-300 dark:bg-blue-950 dark:text-blue-300'
                      }`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${
                          job.status.toLowerCase() === 'in progress' ? 'bg-emerald-500 animate-pulse' : 'bg-blue-500'
                        }`} />
                        {job.status}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-right">
                      <button
                        onClick={() => onNavigateTab('telematics')}
                        className="px-2 py-1 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 hover:bg-emerald-100 border border-emerald-200 dark:border-emerald-800 text-[11px] font-semibold transition"
                      >
                        Map
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* RIGHT COLUMN: ACTIVE FIELD MANPOWER ROSTER (5 Cols) */}
        <div className={`lg:col-span-5 rounded-2xl border p-5 ${cardBg}`}>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold flex items-center gap-2 text-slate-900 dark:text-white">
                <UserCheck className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                Technician Roster & Clock-In
              </h3>
              <p className={`text-xs ${textMuted}`}>
                Click on any engineer to view full service dossier
              </p>
            </div>
            <button
              onClick={() => onNavigateTab('attendance')}
              className="text-xs font-bold text-emerald-600 dark:text-emerald-400 hover:underline flex items-center gap-0.5"
            >
              <span>Full ({technicians.length})</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Clean Technicians List */}
          <div className="space-y-2.5 max-h-[380px] overflow-y-auto pr-1">
            {technicians.slice(0, 7).map((tech) => (
              <div
                key={tech.id}
                onClick={() => onSelectTechnician(tech.id)}
                className={`p-3 rounded-xl border transition flex items-center justify-between cursor-pointer group ${
                  isDark ? 'bg-slate-900/60 border-slate-800 hover:bg-slate-800' : 'bg-slate-50/70 border-slate-200/80 hover:bg-emerald-50/50'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-9 h-9 rounded-full flex items-center justify-center font-bold text-xs border ${
                    tech.status === 'On Paid Job'
                      ? 'bg-emerald-100 text-emerald-900 border-emerald-300 dark:bg-emerald-950 dark:text-emerald-300'
                      : tech.status === 'Available'
                      ? 'bg-blue-100 text-blue-900 border-blue-300 dark:bg-blue-950 dark:text-blue-300'
                      : 'bg-amber-100 text-amber-900 border-amber-300 dark:bg-amber-950 dark:text-amber-300'
                  }`}>
                    {tech.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-slate-900 dark:text-white group-hover:text-emerald-600 transition">
                      {tech.name}
                    </h4>
                    <span className="text-[11px] font-mono text-slate-500 block">
                      Clock: {tech.clockInTime} • {tech.region.split('/')[0]}
                    </span>
                  </div>
                </div>

                <div className="text-right">
                  <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold ${
                    tech.status === 'On Paid Job'
                      ? 'bg-emerald-100 text-emerald-900 dark:bg-emerald-950 dark:text-emerald-300'
                      : tech.status === 'Available'
                      ? 'bg-blue-100 text-blue-900 dark:bg-blue-950 dark:text-blue-300'
                      : 'bg-slate-200 text-slate-800 dark:bg-slate-800 dark:text-slate-300'
                  }`}>
                    {tech.status}
                  </span>
                  <span className="block text-[10px] text-slate-400 font-mono mt-0.5">
                    {tech.todayJobId || 'Standby'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* ===================================================================== */}
      {/* 3. OPERATIONS FAST-LAUNCH ACTION CARDS                                */}
      {/* ===================================================================== */}
      <div>
        <h3 className="text-xs font-bold font-mono uppercase tracking-wider text-slate-500 mb-3">
          Specialist Command Engines
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          
          <div 
            onClick={() => onNavigateTab('audit')}
            className={`p-4 rounded-2xl border transition cursor-pointer group hover:border-emerald-500 ${cardBg}`}
          >
            <div className="p-2.5 rounded-xl bg-emerald-100 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400 w-fit mb-2.5">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-slate-900 dark:text-white group-hover:text-emerald-600 transition">
              12-Pillar Forensic Auditor
            </h4>
            <p className="text-xs text-slate-500 mt-1">
              Verify local conveyance vs outstation, 8h DA cutoff, and guest house stay rules.
            </p>
          </div>

          <div 
            onClick={() => onNavigateTab('amcs')}
            className={`p-4 rounded-2xl border transition cursor-pointer group hover:border-amber-500 ${cardBg}`}
          >
            <div className="p-2.5 rounded-xl bg-amber-100 dark:bg-amber-950 text-amber-600 dark:text-amber-400 w-fit mb-2.5">
              <FileText className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-slate-900 dark:text-white group-hover:text-amber-600 transition">
              Commercial AMCs & Retainers
            </h4>
            <p className="text-xs text-slate-500 mt-1">
              Track 11 commercial contracts (Reliance & Adani) and monthly service visit quotas.
            </p>
          </div>

          <div 
            onClick={() => onNavigateTab('telematics')}
            className={`p-4 rounded-2xl border transition cursor-pointer group hover:border-blue-500 ${cardBg}`}
          >
            <div className="p-2.5 rounded-xl bg-blue-100 dark:bg-blue-950 text-blue-600 dark:text-blue-400 w-fit mb-2.5">
              <MapPin className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-slate-900 dark:text-white group-hover:text-blue-600 transition">
              Fleet Map & 5km Radar
            </h4>
            <p className="text-xs text-slate-500 mt-1">
              Live GPS route tracing with 5km Haversine stationary clustering and anomaly alerts.
            </p>
          </div>

          <div 
            onClick={() => onNavigateTab('automations')}
            className={`p-4 rounded-2xl border transition cursor-pointer group hover:border-violet-500 ${cardBg}`}
          >
            <div className="p-2.5 rounded-xl bg-violet-100 dark:bg-violet-950 text-violet-600 dark:text-violet-400 w-fit mb-2.5">
              <Zap className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-slate-900 dark:text-white group-hover:text-violet-600 transition">
              WhatsApp & Email Hub
            </h4>
            <p className="text-xs text-slate-500 mt-1">
              Dispatch work order templates via WhatsApp Business API and automated PDF audit digests.
            </p>
          </div>

        </div>
      </div>

    </div>
  );
};
