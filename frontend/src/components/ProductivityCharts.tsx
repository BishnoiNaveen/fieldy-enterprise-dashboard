/**
 * frontend/src/components/ProductivityCharts.tsx
 * Recharts Stacked Bar & Trend Analytics Engine for Working, Travelling, and Idle Hours.
 * Adheres strictly to the Conservation Law of Hours: H_shift = H_w + H_t + H_i.
 * Supports both Bright (Default) and Dark modes.
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
  AreaChart, 
  Area, 
} from 'recharts';
import { 
  Briefcase, 
  Navigation, 
  Clock, 
  TrendingUp, 
  CheckCircle, 
  Award, 
  BarChart3, 
  LineChart as LineChartIcon,
} from 'lucide-react';
import { 
  ProductivityResponse, 
  TechnicianProductivityRecord, 
} from '../types/dashboard';

interface ProductivityChartsProps {
  data: ProductivityResponse | null;
  isLoading?: boolean;
  onSelectTechnician?: (technicianId: string) => void;
  theme?: 'bright' | 'dark';
}

export const ProductivityCharts: React.FC<ProductivityChartsProps> = ({
  data,
  isLoading = false,
  onSelectTechnician,
  theme = 'bright',
}) => {
  const [activeVisualMode, setActiveVisualMode] = useState<'stacked-bar' | 'trend-area'>('stacked-bar');

  const isDark = theme === 'dark';
  const cardBg = isDark ? 'bg-[#0B121E] border-slate-800 text-white' : 'bg-white border-slate-200 text-slate-900 shadow-sm';
  const textMuted = isDark ? 'text-slate-400' : 'text-slate-500';
  const gridStroke = isDark ? '#1E293B' : '#E2E8F0';

  // Custom Tooltip for Recharts
  const CustomRechartsTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const working = payload.find((p: any) => p.dataKey === 'working')?.value || 0;
      const travelling = payload.find((p: any) => p.dataKey === 'travelling')?.value || 0;
      const idle = payload.find((p: any) => p.dataKey === 'idle')?.value || 0;
      const total = working + travelling + idle;
      const utilPct = total > 0 ? Math.round((working / total) * 100) : 0;

      return (
        <div className={`rounded-xl p-3.5 shadow-xl text-xs space-y-2 min-w-[200px] border ${
          isDark ? 'bg-[#0B121E]/95 border-slate-700/80 text-white' : 'bg-white/95 border-slate-200 text-slate-900'
        }`}>
          <div className="font-bold border-b border-slate-200 dark:border-slate-800 pb-1 flex items-center justify-between">
            <span>{label}</span>
            <span className="font-mono text-emerald-600 dark:text-emerald-400 font-semibold">{utilPct}% Util</span>
          </div>

          <div className="space-y-1 font-mono text-[11px]">
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400">
                <span className="w-2 h-2 rounded-full bg-emerald-500" />
                Working (H_w):
              </span>
              <span className="font-bold">{working.toFixed(1)}h</span>
            </div>

            <div className="flex items-center justify-between">
              <span className="flex items-center gap-1.5 text-blue-600 dark:text-blue-400">
                <span className="w-2 h-2 rounded-full bg-blue-500" />
                Travelling (H_t):
              </span>
              <span className="font-bold">{travelling.toFixed(1)}h</span>
            </div>

            <div className="flex items-center justify-between">
              <span className="flex items-center gap-1.5 text-amber-600 dark:text-amber-400">
                <span className="w-2 h-2 rounded-full bg-amber-500" />
                Idle (H_i):
              </span>
              <span className="font-bold">{idle.toFixed(1)}h</span>
            </div>

            <div className="flex items-center justify-between pt-1 border-t border-slate-200 dark:border-slate-800 font-bold">
              <span>Total Shift:</span>
              <span>{total.toFixed(1)}h</span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  if (isLoading || !data) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className={`h-28 rounded-2xl border p-4 animate-pulse ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-slate-200'}`} />
          ))}
        </div>
        <div className={`h-96 rounded-2xl border p-6 animate-pulse ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-slate-200'}`} />
      </div>
    );
  }

  const rawAggregates = (data as any).aggregates || (data as any).summary || {};
  const totalWorking = Number(rawAggregates.total_working_hours ?? rawAggregates.working_hours ?? 0);
  const totalTravelling = Number(rawAggregates.total_travelling_hours ?? rawAggregates.travelling_hours ?? 0);
  const totalIdle = Number(rawAggregates.total_idle_hours ?? rawAggregates.idle_hours ?? 0);
  const totalShift = Number(rawAggregates.total_shift_hours ?? (totalWorking + totalTravelling + totalIdle));
  const utilization = Number(rawAggregates.fleet_utilization_rate_pct ?? rawAggregates.average_utilization_pct ?? (totalShift > 0 ? (totalWorking / totalShift) * 100 : 0));
  const jobsCompleted = rawAggregates.jobs_completed_count ?? rawAggregates.jobs_closed_count ?? 0;

  const records = (data as any).records || (data as any).technician_records || [];
  const trend_data = (data as any).trend_data || [];
  const timeframe = data.timeframe;

  const trendData = (trend_data || []).map((t: any) => ({
    period: t.period,
    working: Number(((t.working_hours ?? t.working) || 0).toFixed(1)),
    travelling: Number(((t.travelling_hours ?? t.travelling) || 0).toFixed(1)),
    idle: Number(((t.idle_hours ?? t.idle) || 0).toFixed(1)),
    utilization: Number(((t.utilization_rate_pct ?? t.utilization_pct) || 0).toFixed(1)),
  }));

  const sortedRecords = [...records].sort((a: any, b: any) => (Number(b.working_hours || 0)) - (Number(a.working_hours || 0)));

  return (
    <div className="space-y-6">
      {/* 1. Aggregates KPI Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5">
        {/* Working Hours */}
        <div className={`rounded-2xl p-4 border flex flex-col justify-between ${cardBg}`}>
          <div className="flex items-center justify-between mb-2">
            <span className={`text-[11px] font-bold uppercase tracking-wider font-mono ${textMuted}`}>
              Working (H_w)
            </span>
            <div className="p-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/80 text-emerald-600 dark:text-emerald-400">
              <Briefcase className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-1.5">
            <span className="text-2xl font-black font-mono tracking-tight text-emerald-600 dark:text-emerald-400">
              {totalWorking.toFixed(1)}h
            </span>
          </div>
          <span className="text-[11px] text-emerald-600 dark:text-emerald-400 mt-2 font-medium">
            Productive on-site repair
          </span>
        </div>

        {/* Travelling Hours */}
        <div className={`rounded-2xl p-4 border flex flex-col justify-between ${cardBg}`}>
          <div className="flex items-center justify-between mb-2">
            <span className={`text-[11px] font-bold uppercase tracking-wider font-mono ${textMuted}`}>
              Travelling (H_t)
            </span>
            <div className="p-1.5 rounded-lg bg-blue-50 dark:bg-blue-950/80 text-blue-600 dark:text-blue-400">
              <Navigation className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-1.5">
            <span className="text-2xl font-black font-mono tracking-tight text-blue-600 dark:text-blue-400">
              {totalTravelling.toFixed(1)}h
            </span>
          </div>
          <span className="text-[11px] text-blue-600 dark:text-blue-400 mt-2 font-medium">
            Verified transit corridor
          </span>
        </div>

        {/* Idle Hours */}
        <div className={`rounded-2xl p-4 border flex flex-col justify-between ${cardBg}`}>
          <div className="flex items-center justify-between mb-2">
            <span className={`text-[11px] font-bold uppercase tracking-wider font-mono ${textMuted}`}>
              Idle Hours (H_i)
            </span>
            <div className="p-1.5 rounded-lg bg-amber-50 dark:bg-amber-950/80 text-amber-600 dark:text-amber-400">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-1.5">
            <span className="text-2xl font-black font-mono tracking-tight text-amber-600 dark:text-amber-400">
              {totalIdle.toFixed(1)}h
            </span>
          </div>
          <span className="text-[11px] text-amber-600 dark:text-amber-400 mt-2 font-medium">
            Inactive / halt buffer
          </span>
        </div>

        {/* Total Shift Hours */}
        <div className={`rounded-2xl p-4 border flex flex-col justify-between ${cardBg}`}>
          <div className="flex items-center justify-between mb-2">
            <span className={`text-[11px] font-bold uppercase tracking-wider font-mono ${textMuted}`}>
              Total Shift
            </span>
            <div className="p-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
              <CheckCircle className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-1.5">
            <span className="text-2xl font-black font-mono tracking-tight">
              {totalShift.toFixed(1)}h
            </span>
          </div>
          <span className={`text-[11px] mt-2 font-mono ${textMuted}`}>
            H_shift = H_w + H_t + H_i
          </span>
        </div>

        {/* Fleet Utilization */}
        <div className={`rounded-2xl p-4 border flex flex-col justify-between ${cardBg}`}>
          <div className="flex items-center justify-between mb-2">
            <span className={`text-[11px] font-bold uppercase tracking-wider font-mono ${textMuted}`}>
              Fleet Utilization
            </span>
            <div className="p-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/80 text-emerald-600 dark:text-emerald-400">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-1.5">
            <span className="text-2xl font-black font-mono tracking-tight text-emerald-600 dark:text-emerald-400">
              {utilization.toFixed(1)}%
            </span>
          </div>
          <span className={`text-[11px] mt-2 font-medium ${textMuted}`}>
            {jobsCompleted} jobs closed
          </span>
        </div>
      </div>

      {/* 2. Visual Chart Canvas */}
      <div className={`rounded-2xl border p-5 ${cardBg}`}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
          <div>
            <h3 className="text-sm font-bold flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              Hours Distribution & Productivity Trajectory ({timeframe.toUpperCase()})
            </h3>
            <p className={`text-xs ${textMuted}`}>
              Multi-tier stacked breakdown: Productive Working vs Highway Transit vs Inactive Halts
            </p>
          </div>

          <div className={`flex items-center rounded-xl p-0.5 border ${isDark ? 'bg-[#060A11] border-slate-800' : 'bg-slate-100 border-slate-200'}`}>
            <button
              onClick={() => setActiveVisualMode('stacked-bar')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
                activeVisualMode === 'stacked-bar'
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : textMuted
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
                  : textMuted
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
                <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} vertical={false} />
                <XAxis 
                  dataKey="period" 
                  stroke="#94A3B8" 
                  fontSize={11} 
                  tickLine={false} 
                />
                <YAxis 
                  stroke="#94A3B8" 
                  fontSize={11} 
                  tickLine={false} 
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
                  <linearGradient id="idleGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#F59E0B" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} vertical={false} />
                <XAxis 
                  dataKey="period" 
                  stroke="#94A3B8" 
                  fontSize={11} 
                  tickLine={false} 
                />
                <YAxis 
                  stroke="#94A3B8" 
                  fontSize={11} 
                  tickLine={false} 
                  unit="h" 
                />
                <Tooltip content={<CustomRechartsTooltip />} />
                <Legend 
                  wrapperStyle={{ paddingTop: '12px', fontSize: '12px' }} 
                  iconType="circle"
                />
                <Area type="monotone" dataKey="working" name="Working Hours" stroke="#059669" fillOpacity={1} fill="url(#workingGrad)" />
                <Area type="monotone" dataKey="travelling" name="Travelling Hours" stroke="#0284C7" fillOpacity={1} fill="url(#travelGrad)" />
                <Area type="monotone" dataKey="idle" name="Idle Hours" stroke="#F59E0B" fillOpacity={1} fill="url(#idleGrad)" />
              </AreaChart>
            )}
          </ResponsiveContainer>
        </div>
      </div>

      {/* 3. Detailed Per-Technician Scorecard Table */}
      <div className={`rounded-2xl border overflow-hidden ${cardBg}`}>
        <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold flex items-center gap-2">
              <Award className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              Technician Productivity Scorecard
            </h3>
            <p className={`text-xs ${textMuted}`}>
              Verified shift breakdown adhering to Krone Clause 4.7 commercial standards
            </p>
          </div>
          <span className="text-xs font-mono font-semibold px-2 py-1 rounded bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">
            {records.length} Technicians Logged
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className={`border-b ${isDark ? 'bg-[#060A11]/80 text-slate-400 border-slate-800' : 'bg-slate-50 text-slate-600 border-slate-200'}`}>
              <tr>
                <th className="py-3 px-4">Technician Name</th>
                <th className="py-3 px-4">Region</th>
                <th className="py-3 px-4">Working (H_w)</th>
                <th className="py-3 px-4">Travelling (H_t)</th>
                <th className="py-3 px-4">Idle (H_i)</th>
                <th className="py-3 px-4">Total Shift</th>
                <th className="py-3 px-4">Utilization Rate</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
              {sortedRecords.map((r) => (
                <tr
                  key={r.technician_id}
                  onClick={() => onSelectTechnician?.(r.technician_id)}
                  className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition group cursor-pointer"
                >
                  <td className="py-3 px-4">
                    <div className="font-bold">{r.technician_name}</div>
                    <div className={`text-[11px] font-mono ${textMuted}`}>{r.technician_id}</div>
                  </td>
                  <td className="py-3 px-4 font-medium">{r.region}</td>
                  <td className="py-3 px-4 font-mono font-bold text-emerald-600 dark:text-emerald-400">
                    {Number(r.working_hours ?? 0).toFixed(1)}h
                  </td>
                  <td className="py-3 px-4 font-mono font-semibold text-blue-600 dark:text-blue-400">
                    {Number(r.travelling_hours ?? 0).toFixed(1)}h
                  </td>
                  <td className="py-3 px-4 font-mono text-amber-600 dark:text-amber-400">
                    {Number(r.idle_hours ?? 0).toFixed(1)}h
                  </td>
                  <td className="py-3 px-4 font-mono font-bold">
                    {Number(r.shift_hours ?? ((r.working_hours ?? 0) + (r.travelling_hours ?? 0) + (r.idle_hours ?? 0))).toFixed(1)}h
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-2 rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden">
                        <div
                          className="h-full bg-emerald-500 rounded-full"
                          style={{ width: `${Math.min(100, Number(r.utilization_rate_pct ?? r.utilization_pct ?? 0))}%` }}
                        />
                      </div>
                      <span className="font-mono text-xs font-bold text-emerald-600 dark:text-emerald-400">
                        {Number(r.utilization_rate_pct ?? r.utilization_pct ?? 0).toFixed(1)}%
                      </span>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <span className="text-emerald-600 dark:text-emerald-400 font-semibold text-xs group-hover:underline">
                      View Details →
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
