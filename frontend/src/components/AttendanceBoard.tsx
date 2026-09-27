/**
 * frontend/src/components/AttendanceBoard.tsx
 * Comprehensive Attendance, Clock-In & Manpower Roster for Krone Agriculture India.
 * Shows exact clock-in times, punch GPS locations, present vs leave breakdown,
 * and enables click-to-open full detailed dossier for every field technician.
 */

import React, { useState, useMemo } from 'react';
import {
  Users,
  Clock,
  CheckCircle2,
  CalendarOff,
  Search,
  MapPin,
  ArrowRight,
  ShieldCheck,
  Battery,
  Phone,
  Briefcase,
  Filter,
  UserCheck,
  UserX,
  ExternalLink
} from 'lucide-react';
import { ExtendedTechnicianData } from './TechnicianDetailView';

interface AttendanceBoardProps {
  technicians: ExtendedTechnicianData[];
  onSelectTechnician: (techId: string) => void;
  theme?: 'bright' | 'dark';
}

export const AttendanceBoard: React.FC<AttendanceBoardProps> = ({
  technicians,
  onSelectTechnician,
  theme = 'bright',
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'ALL' | 'PAID' | 'STANDBY' | 'LEAVE'>('ALL');

  const isDark = theme === 'dark';
  const cardBg = isDark ? 'bg-[#0B121E] border-slate-800 text-slate-100' : 'bg-white border-slate-200 text-slate-900 shadow-sm';
  const subBg = isDark ? 'bg-slate-900/60 border-slate-800' : 'bg-slate-50 border-slate-200';
  const textMuted = isDark ? 'text-slate-400' : 'text-slate-700 font-medium';
  const textHeader = isDark ? 'text-white' : 'text-slate-900';

  // Metrics
  const totalFleet = technicians.length;
  const onPaidJobsCount = technicians.filter(t => t.status === 'On Paid Job').length;
  const standbyCount = technicians.filter(t => t.status === 'Available').length;
  const onLeaveCount = technicians.filter(t => !t.isPresent).length;
  const dailyPaidRevenue = onPaidJobsCount * 5000; // Standard Krone Day Rate ₹5,000

  // Filtered List
  const filteredTechnicians = useMemo(() => {
    return technicians.filter(t => {
      const matchSearch =
        t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        t.role.toLowerCase().includes(searchQuery.toLowerCase()) ||
        t.region.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (t.todayJobId && t.todayJobId.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (t.customerCompany && t.customerCompany.toLowerCase().includes(searchQuery.toLowerCase()));

      if (!matchSearch) return false;
      if (statusFilter === 'PAID') return t.status === 'On Paid Job';
      if (statusFilter === 'STANDBY') return t.status === 'Available';
      if (statusFilter === 'LEAVE') return !t.isPresent;
      return true;
    });
  }, [technicians, searchQuery, statusFilter]);

  return (
    <div className="space-y-6">
      {/* 1. Top Attendance KPI Summary Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
        {/* Total Strength */}
        <div
          onClick={() => setStatusFilter('ALL')}
          className={`p-4 rounded-2xl border transition-all cursor-pointer ${
            statusFilter === 'ALL'
              ? 'ring-2 ring-emerald-500 bg-emerald-50/60 dark:bg-emerald-950/30 border-emerald-400'
              : `${cardBg} hover:border-slate-300`
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className={`text-[11px] font-bold uppercase tracking-wider ${isDark ? 'text-slate-400' : 'text-slate-700'}`}>
              Total Fleet
            </span>
            <Users className="w-4 h-4 text-slate-500" />
          </div>
          <span className={`text-2xl sm:text-3xl font-black font-mono ${textHeader}`}>
            {totalFleet}
          </span>
          <p className={`text-[11px] mt-1 font-semibold ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>Field Engineers</p>
        </div>

        {/* On Paid Jobs */}
        <div
          onClick={() => setStatusFilter('PAID')}
          className={`p-4 rounded-2xl border transition-all cursor-pointer ${
            statusFilter === 'PAID'
              ? 'ring-2 ring-emerald-500 bg-emerald-50/60 dark:bg-emerald-950/30 border-emerald-400'
              : `${cardBg} hover:border-emerald-400`
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-400">
              On Paid Jobs
            </span>
            <UserCheck className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl sm:text-3xl font-black font-mono text-emerald-700 dark:text-emerald-400">
              {onPaidJobsCount}
            </span>
            <span className="text-xs font-bold text-emerald-800 dark:text-emerald-300">
              (₹{dailyPaidRevenue.toLocaleString('en-IN')}/day)
            </span>
          </div>
          <p className="text-[11px] text-emerald-800 dark:text-emerald-400 mt-1 font-bold">
            Billable Deputation Active
          </p>
        </div>

        {/* Depot Standby / Unpaid */}
        <div
          onClick={() => setStatusFilter('STANDBY')}
          className={`p-4 rounded-2xl border transition-all cursor-pointer ${
            statusFilter === 'STANDBY'
              ? 'ring-2 ring-blue-500 bg-blue-50/60 dark:bg-blue-950/30 border-blue-400'
              : `${cardBg} hover:border-blue-300`
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-blue-700 dark:text-blue-400">
              Depot Standby (Unpaid)
            </span>
            <Clock className="w-4 h-4 text-blue-600" />
          </div>
          <span className="text-2xl sm:text-3xl font-black font-mono text-blue-700 dark:text-blue-400">
            {standbyCount}
          </span>
          <p className="text-[11px] text-blue-800 dark:text-blue-300 mt-1 font-semibold">
            Punched in, ready for dispatch
          </p>
        </div>

        {/* On Leave / Off */}
        <div
          onClick={() => setStatusFilter('LEAVE')}
          className={`p-4 rounded-2xl border transition-all cursor-pointer ${
            statusFilter === 'LEAVE'
              ? 'ring-2 ring-amber-500 bg-amber-50/60 dark:bg-amber-950/30 border-amber-400'
              : `${cardBg} hover:border-amber-300`
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-amber-700 dark:text-amber-400">
              On Holiday / Leave
            </span>
            <UserX className="w-4 h-4 text-amber-600" />
          </div>
          <span className="text-2xl sm:text-3xl font-black font-mono text-amber-700 dark:text-amber-400">
            {onLeaveCount}
          </span>
          <p className="text-[11px] text-amber-800 dark:text-amber-400 mt-1 font-semibold">
            Approved leaves / weekly off
          </p>
        </div>
      </div>

      {/* 2. Revenue & Deputation Strip */}
      <div className={`p-3.5 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
        isDark ? 'bg-emerald-950/30 border-emerald-800/50' : 'bg-emerald-50 border-emerald-300'
      }`}>
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-emerald-600 text-white flex items-center justify-center font-bold text-xs">
            ₹
          </div>
          <div>
            <span className="text-xs font-bold text-emerald-900 dark:text-emerald-300 block">
              Fieldy Daily Deputation Revenue: ₹{dailyPaidRevenue.toLocaleString('en-IN')} (10 Active Paid Technicians)
            </span>
            <span className="text-[11px] text-emerald-800 dark:text-emerald-400">
              Deputation billing rate ₹5,000 / day (₹625 / hr) • 2 standby non-billable • 2 scheduled leaves
            </span>
          </div>
        </div>
        <div className="text-xs font-mono font-bold text-emerald-800 dark:text-emerald-300">
          100% Geofence Punch Compliance
        </div>
      </div>

      {/* 3. Search & Filter Bar */}
      <div className={`p-4 rounded-2xl border ${cardBg} flex flex-col sm:flex-row items-center justify-between gap-3`}>
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            id="attendance-search"
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search technician, job, region..."
            className={`w-full text-xs rounded-xl pl-9 pr-4 py-2 border focus:outline-none focus:ring-2 focus:ring-emerald-500 ${
              isDark
                ? 'bg-slate-900 border-slate-700 text-white placeholder-slate-500'
                : 'bg-slate-50 border-slate-300 text-slate-900 placeholder-slate-400'
            }`}
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto justify-end flex-wrap">
          <span className={`text-xs font-bold ${isDark ? 'text-slate-400' : 'text-slate-700'}`}>Filter:</span>
          {(['ALL', 'PAID', 'STANDBY', 'LEAVE'] as const).map((filter) => (
            <button
              key={filter}
              onClick={() => setStatusFilter(filter)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                statusFilter === filter
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : isDark
                  ? 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  : 'bg-slate-100 text-slate-800 hover:bg-slate-200 border border-slate-200'
              }`}
            >
              {filter === 'ALL'
                ? `All (${totalFleet})`
                : filter === 'PAID'
                ? `Paid Jobs (${onPaidJobsCount})`
                : filter === 'STANDBY'
                ? `Standby (${standbyCount})`
                : `On Leave (${onLeaveCount})`}
            </button>
          ))}
        </div>
      </div>

      {/* 3. Detailed Attendance Roster Table */}
      <div className={`rounded-2xl border overflow-hidden ${cardBg}`}>
        <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <div>
            <h3 className={`text-sm font-bold ${textHeader} flex items-center gap-2`}>
              <Clock className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              Daily Manpower Clock-In & Verification Roster
            </h3>
            <p className={`text-xs ${textMuted}`}>
              Click on any engineer row to open their full detailed service & telematics dossier
            </p>
          </div>
          <span className="text-xs font-mono font-semibold px-2.5 py-1 rounded bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">
            {filteredTechnicians.length} Technicians Shown
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className={`border-b ${isDark ? 'border-slate-800 text-slate-400 bg-slate-900/80' : 'border-slate-200 text-slate-800 font-bold bg-slate-100/80'}`}>
              <tr>
                <th className="py-3 px-4">Technician Name & Code</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Clock-In Time</th>
                <th className="py-3 px-4">Clock-Out / Shift</th>
                <th className="py-3 px-4">Punch Location & Geofence</th>
                <th className="py-3 px-4">Active Work Order</th>
                <th className="py-3 px-4 text-right">Detailed Dossier</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
              {filteredTechnicians.map((tech) => (
                <tr
                  key={tech.id}
                  onClick={() => onSelectTechnician(tech.id)}
                  className="hover:bg-emerald-50/70 dark:hover:bg-slate-800/60 transition cursor-pointer group"
                >
                  {/* Name & Avatar */}
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2.5">
                      <div className="w-8 h-8 rounded-lg bg-emerald-600 text-white flex items-center justify-center font-black text-xs shadow-sm">
                        {tech.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                      </div>
                      <div>
                        <span className={`font-black block group-hover:text-emerald-700 dark:group-hover:text-emerald-400 transition ${textHeader}`}>
                          {tech.name}
                        </span>
                        <span className={`text-[11px] font-semibold ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
                          {tech.employeeCode} • {tech.region}
                        </span>
                      </div>
                    </div>
                  </td>

                  {/* Status Badge */}
                  <td className="py-3 px-4">
                    <span
                      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold ${
                        tech.status === 'On Paid Job'
                          ? 'bg-emerald-100 text-emerald-950 border border-emerald-400 dark:bg-emerald-950 dark:text-emerald-300'
                          : tech.status === 'Available'
                          ? 'bg-blue-100 text-blue-950 border border-blue-400 dark:bg-blue-950 dark:text-blue-300'
                          : 'bg-amber-100 text-amber-950 border border-amber-400 dark:bg-amber-950 dark:text-amber-300'
                      }`}
                    >
                      <span className={`w-1.5 h-1.5 rounded-full ${tech.isPresent ? 'bg-emerald-500' : 'bg-amber-500'}`} />
                      {tech.status}
                    </span>
                  </td>

                  {/* Clock In */}
                  <td className="py-3 px-4">
                    {tech.isPresent ? (
                      <div>
                        <span className="font-mono font-bold text-emerald-800 dark:text-emerald-400">
                          {tech.clockInTime}
                        </span>
                        <span className="block text-[10px] text-slate-500 font-semibold">Punched App</span>
                      </div>
                    ) : (
                      <span className="text-slate-500 font-mono italic font-medium">
                        Not Punched (Leave)
                      </span>
                    )}
                  </td>

                  {/* Clock Out / Shift Window */}
                  <td className="py-3 px-4">
                    {tech.isPresent ? (
                      <div>
                        <span className="font-mono font-bold text-slate-900 dark:text-slate-300">
                          {tech.clockOutTime}
                        </span>
                        <span className="block text-[10px] text-emerald-800 dark:text-emerald-400 font-bold">
                          Active ({tech.workingHours}h logged)
                        </span>
                      </div>
                    ) : (
                      <span className="text-amber-700 dark:text-amber-400 font-bold">
                        {tech.leaveType || 'Weekly Off'}
                      </span>
                    )}
                  </td>

                  {/* Punch Location */}
                  <td className="py-3 px-4">
                    {tech.isPresent ? (
                      <div className="max-w-xs">
                        <span className={`block font-bold truncate ${textHeader}`}>
                          {tech.punchLocationName}
                        </span>
                        <span className="text-[10px] text-slate-600 dark:text-slate-400 flex items-center gap-1 font-mono font-semibold">
                          <MapPin className="w-2.5 h-2.5 text-rose-500" />
                          {tech.punchCoordinates[0].toFixed(2)}°N, {tech.punchCoordinates[1].toFixed(2)}°E
                        </span>
                      </div>
                    ) : (
                      <span className="text-slate-400 font-bold">—</span>
                    )}
                  </td>

                  {/* Active Job */}
                  <td className="py-3 px-4">
                    {tech.todayJobId ? (
                      <div>
                        <span className="font-mono font-black text-emerald-800 dark:text-emerald-400">
                          {tech.todayJobId}
                        </span>
                        <span className={`block text-[11px] font-semibold truncate max-w-xs ${isDark ? 'text-slate-400' : 'text-slate-700'}`}>
                          {tech.customerCompany}
                        </span>
                      </div>
                    ) : (
                      <span className="text-slate-600 dark:text-slate-400 font-semibold">Depot Standby</span>
                    )}
                  </td>

                  {/* Action Link */}
                  <td className="py-3 px-4 text-right">
                    <span className="inline-flex items-center gap-1 text-xs font-bold text-emerald-600 dark:text-emerald-400 group-hover:translate-x-1 transition-transform">
                      View Dossier
                      <ArrowRight className="w-3.5 h-3.5" />
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
