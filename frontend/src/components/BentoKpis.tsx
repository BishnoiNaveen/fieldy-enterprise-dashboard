/**
 * frontend/src/components/BentoKpis.tsx
 * Executive Command KPI Cards tailored to: Total Jobs, Working Technicians, Leave Technicians, and Machinery.
 * Supports both Bright (Default) and Dark modes with interactive click-to-filter.
 */

import React from 'react';
import {
  Wrench,
  Users,
  Briefcase,
  TrendingUp,
  Activity,
  CheckCircle2,
  CalendarOff,
  Tractor,
  ArrowRight,
  ShieldCheck,
  UserCheck
} from 'lucide-react';
import { PulseKpis } from '../types/dashboard';

interface BentoKpisProps {
  kpis: PulseKpis | null;
  isLoading?: boolean;
  onNavigateTab?: (tabId: 'all' | 'attendance' | 'jobs' | 'machines' | 'telematics' | 'analytics') => void;
  theme?: 'bright' | 'dark';
}

export const BentoKpis: React.FC<BentoKpisProps> = ({
  kpis,
  isLoading = false,
  onNavigateTab,
  theme = 'bright',
}) => {
  const isDark = theme === 'dark';

  // Skeleton Shimmer Loading State
  if (isLoading || !kpis) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className={`h-36 rounded-2xl border p-5 animate-pulse flex flex-col justify-between ${
              isDark ? 'bg-slate-900/60 border-slate-800' : 'bg-white border-slate-200'
            }`}
          >
            <div className="flex justify-between items-start">
              <div className="w-24 h-4 bg-slate-200 dark:bg-slate-800 rounded" />
              <div className="w-8 h-8 bg-slate-200 dark:bg-slate-800 rounded-lg" />
            </div>
            <div className="w-16 h-8 bg-slate-200 dark:bg-slate-800 rounded my-2" />
            <div className="w-32 h-3 bg-slate-200 dark:bg-slate-800 rounded" />
          </div>
        ))}
      </div>
    );
  }

  const {
    technicians_on_paid_jobs,
    technicians_active_total,
    technicians_on_leave,
    total_jobs_today,
    jobs_completed_today,
    machines_under_service = 8,
  } = kpis;

  const inProgressJobs = Math.max(0, total_jobs_today - jobs_completed_today);
  const cardBase = isDark
    ? 'bg-[#0B121E] border-slate-800 hover:border-emerald-500/50 text-white'
    : 'bg-white border-slate-200 hover:border-emerald-500 text-slate-900 shadow-sm hover:shadow-md';
  const textMuted = isDark ? 'text-slate-400' : 'text-slate-700 font-medium';
  const borderSub = isDark ? 'border-slate-800/80' : 'border-slate-200';

  return (
    <section className="mb-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* CARD 1: TOTAL JOBS TODAY */}
        <div
          onClick={() => onNavigateTab && onNavigateTab('jobs')}
          className={`group rounded-2xl p-5 border transition-all duration-300 flex flex-col justify-between cursor-pointer ${cardBase}`}
        >
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className={`text-[11px] font-bold uppercase tracking-wider font-mono ${isDark ? 'text-slate-400' : 'text-slate-700'}`}>
                Total Jobs Today
              </span>
              <div className="p-2 rounded-xl bg-blue-100 dark:bg-blue-950/80 text-blue-700 dark:text-blue-400 group-hover:scale-110 transition-transform">
                <Briefcase className="w-4 h-4" />
              </div>
            </div>

            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-black font-mono tracking-tight text-blue-700 dark:text-blue-400">
                {total_jobs_today}
              </span>
              <span className={`text-xs font-semibold ${textMuted}`}>
                dispatched work orders
              </span>
            </div>
          </div>

          <div className={`mt-4 pt-3 border-t ${borderSub} flex items-center justify-between text-xs`}>
            <div className="flex items-center gap-3">
              <span className="text-emerald-700 dark:text-emerald-400 font-bold flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" />
                {jobs_completed_today} Closed
              </span>
              <span className="text-amber-700 dark:text-amber-400 font-bold">
                {inProgressJobs} In Progress
              </span>
            </div>
            <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:translate-x-1 transition-transform" />
          </div>
        </div>

        {/* CARD 2: TECHNICIANS WORKING TODAY */}
        <div
          onClick={() => onNavigateTab && onNavigateTab('attendance')}
          className={`group rounded-2xl p-5 border transition-all duration-300 flex flex-col justify-between cursor-pointer ${cardBase}`}
        >
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-400 font-mono">
                Technicians Working
              </span>
              <div className="p-2 rounded-xl bg-emerald-100 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-400 group-hover:scale-110 transition-transform">
                <UserCheck className="w-4 h-4" />
              </div>
            </div>

            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-black font-mono tracking-tight text-emerald-700 dark:text-emerald-400">
                {technicians_on_paid_jobs}
              </span>
              <span className={`text-xs font-semibold ${textMuted}`}>
                on paid jobs ({technicians_active_total} active)
              </span>
            </div>
          </div>

          <div className={`mt-4 pt-3 border-t ${borderSub} flex items-center justify-between text-xs`}>
            <span className="text-emerald-700 dark:text-emerald-400 font-bold flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              Punched In & Active
            </span>
            <span className="font-mono text-slate-700 dark:text-slate-400 font-bold text-[11px]">₹625/hr Deputation</span>
          </div>
        </div>

        {/* CARD 3: TECHNICIANS ON LEAVE / HOLIDAY */}
        <div
          onClick={() => onNavigateTab && onNavigateTab('attendance')}
          className={`group rounded-2xl p-5 border transition-all duration-300 flex flex-col justify-between cursor-pointer ${cardBase}`}
        >
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-[11px] font-bold uppercase tracking-wider text-amber-700 dark:text-amber-400 font-mono">
                Technicians On Leave
              </span>
              <div className="p-2 rounded-xl bg-amber-100 dark:bg-amber-950/80 text-amber-700 dark:text-amber-400 group-hover:scale-110 transition-transform">
                <CalendarOff className="w-4 h-4" />
              </div>
            </div>

            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-black font-mono tracking-tight text-amber-700 dark:text-amber-400">
                {technicians_on_leave}
              </span>
              <span className={`text-xs font-semibold ${textMuted}`}>
                on scheduled off / leave
              </span>
            </div>
          </div>

          <div className={`mt-4 pt-3 border-t ${borderSub} flex items-center justify-between text-xs`}>
            <span className="text-amber-700 dark:text-amber-400 font-bold">
              Kuldeep Gill, Rohit Deshmukh
            </span>
            <span className="text-[11px] font-bold text-slate-600 dark:text-slate-400">View →</span>
          </div>
        </div>

        {/* CARD 4: ACTIVE MACHINES UNDER SERVICE */}
        <div
          onClick={() => onNavigateTab && onNavigateTab('machines')}
          className={`group rounded-2xl p-5 border transition-all duration-300 flex flex-col justify-between cursor-pointer ${cardBase}`}
        >
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className={`text-[11px] font-bold uppercase tracking-wider font-mono ${isDark ? 'text-slate-400' : 'text-slate-700'}`}>
                Machines Under Service
              </span>
              <div className="p-2 rounded-xl bg-purple-100 dark:bg-purple-950/80 text-purple-700 dark:text-purple-400 group-hover:scale-110 transition-transform">
                <Tractor className="w-4 h-4" />
              </div>
            </div>

            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-black font-mono tracking-tight text-purple-700 dark:text-purple-400">
                {machines_under_service}
              </span>
              <span className={`text-xs font-semibold ${textMuted}`}>
                balers & harvesters
              </span>
            </div>
          </div>

          <div className={`mt-4 pt-3 border-t ${borderSub} flex items-center justify-between text-xs`}>
            <span className="text-purple-700 dark:text-purple-400 font-bold">
              RIL, Adani, Punjab Farm
            </span>
            <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:translate-x-1 transition-transform" />
          </div>
        </div>

      </div>
    </section>
  );
};
