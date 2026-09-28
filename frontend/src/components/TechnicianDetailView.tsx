/**
 * frontend/src/components/TechnicianDetailView.tsx
 * Dedicated Full-Page Detailed Dossier for Krone Field Engineers.
 * Displays exact clock-in timestamp, punch geofence location, attendance history,
 * active job order, machine serial, telematics travel hours, and route map.
 */

import React from 'react';
import {
  ArrowLeft,
  User,
  Clock,
  MapPin,
  Tractor,
  Phone,
  Mail,
  Truck,
  Battery,
  ShieldCheck,
  Calendar,
  Wrench,
  CheckCircle2,
  AlertTriangle,
  Navigation,
  Compass,
  Briefcase,
  Share2,
  Printer,
  ChevronRight,
  Gauge
} from 'lucide-react';
import { TechnicianLiveOnJob, JobItem, GeoPoint } from '../types/dashboard';

export interface ExtendedTechnicianData {
  id: string;
  name: string;
  role: string;
  region: string;
  phone: string;
  email: string;
  employeeCode: string;
  vehicleNumber: string;
  vehicleModel: string;
  status: 'On Paid Job' | 'Available' | 'On Holiday/Leave';
  leaveType?: string;
  isPresent: boolean;
  clockInTime: string;
  clockOutTime: string;
  punchLocationName: string;
  punchCoordinates: [number, number];
  batteryLevel: number;
  appVersion: string;
  todayJobId?: string;
  jobTitle?: string;
  customerCompany?: string;
  machineName?: string;
  machineSerial?: string;
  siteContact?: string;
  workingHours: number;
  travelHours: number;
  idleHours: number;
  totalKm: number;
  recentJobs: Array<{
    jobId: string;
    date: string;
    customer: string;
    machine: string;
    status: string;
    type: string;
  }>;
}

interface TechnicianDetailViewProps {
  technician: ExtendedTechnicianData;
  onBack: () => void;
  onSelectAnotherTech?: (techId: string) => void;
  allTechnicians?: ExtendedTechnicianData[];
  theme?: 'bright' | 'dark';
}

export const TechnicianDetailView: React.FC<TechnicianDetailViewProps> = ({
  technician: tech,
  onBack,
  onSelectAnotherTech,
  allTechnicians = [],
  theme = 'bright',
}) => {
  const isDark = theme === 'dark';

  const cardBg = isDark ? 'bg-[#0B121E] border-slate-800 text-slate-100' : 'bg-white border-slate-200 text-slate-900 shadow-sm';
  const subBg = isDark ? 'bg-slate-900/60 border-slate-800' : 'bg-slate-50 border-slate-200';
  const textMuted = isDark ? 'text-slate-400' : 'text-slate-500';
  const textHeader = isDark ? 'text-white' : 'text-slate-900';

  return (
    <div className="space-y-6 animate-fadeIn pb-12">
      {/* 1. Top Action Ribbon: Back Button & Tech Switcher */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-200 dark:border-slate-800">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              isDark
                ? 'bg-slate-800 hover:bg-slate-700 text-white'
                : 'bg-slate-100 hover:bg-slate-200 text-slate-700 hover:text-slate-900 border border-slate-300'
            }`}
          >
            <ArrowLeft className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            <span>← Back to Operations Command</span>
          </button>

          <span className="text-xs font-mono px-2.5 py-1 rounded-md bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/80 dark:text-emerald-300 dark:border-emerald-800">
            EMPLOYEE DOSSIER • {tech.employeeCode}
          </span>
        </div>

        {/* Quick Tech Switcher */}
        {allTechnicians.length > 0 && onSelectAnotherTech && (
          <div className="flex items-center gap-2">
            <span className={`text-xs font-medium ${textMuted}`}>Switch Technician:</span>
            <select
              value={tech.id}
              onChange={(e) => onSelectAnotherTech(e.target.value)}
              className={`text-xs font-semibold px-2.5 py-1.5 rounded-lg border focus:outline-none focus:ring-2 focus:ring-emerald-500 ${
                isDark
                  ? 'bg-slate-900 border-slate-700 text-white'
                  : 'bg-white border-slate-300 text-slate-800'
              }`}
            >
              {allTechnicians.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name} ({t.status === 'On Holiday/Leave' ? 'On Leave' : t.role})
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* 2. Hero Profile Banner */}
      <div className={`rounded-2xl border p-6 ${cardBg}`}>
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          {/* Avatar and Primary Identity */}
          <div className="flex items-start sm:items-center gap-4">
            <div className="relative">
              <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center text-white font-extrabold text-2xl shadow-lg border-2 border-white dark:border-slate-800">
                {tech.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
              </div>
              <div
                className={`absolute -bottom-1 -right-1 w-5 h-5 rounded-full border-2 border-white dark:border-slate-900 ${
                  tech.isPresent ? 'bg-emerald-500' : 'bg-amber-500'
                }`}
                title={tech.isPresent ? 'Present Today' : 'On Leave'}
              />
            </div>

            <div>
              <div className="flex flex-wrap items-center gap-2 mb-1">
                <h2 className={`text-xl sm:text-2xl font-black ${textHeader}`}>
                  {tech.name}
                </h2>
                <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                  {tech.employeeCode}
                </span>
                <span
                  className={`text-xs font-bold px-2.5 py-0.5 rounded-full ${
                    tech.status === 'On Paid Job'
                      ? 'bg-emerald-100 text-emerald-800 border border-emerald-300 dark:bg-emerald-950 dark:text-emerald-300 dark:border-emerald-700'
                      : tech.status === 'Available'
                      ? 'bg-blue-100 text-blue-800 border border-blue-300 dark:bg-blue-950 dark:text-blue-300 dark:border-blue-700'
                      : 'bg-amber-100 text-amber-800 border border-amber-300 dark:bg-amber-950 dark:text-amber-300 dark:border-amber-700'
                  }`}
                >
                  {tech.status}
                </span>
              </div>

              <p className={`text-xs sm:text-sm font-semibold text-emerald-600 dark:text-emerald-400 mb-2`}>
                {tech.role} • Krone Agriculture India ({tech.region} Region)
              </p>

              <div className="flex flex-wrap items-center gap-4 text-xs font-medium text-slate-600 dark:text-slate-300">
                <span className="flex items-center gap-1">
                  <Phone className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
                  {tech.phone}
                </span>
                <span className="flex items-center gap-1">
                  <Mail className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
                  {tech.email}
                </span>
                <span className="flex items-center gap-1">
                  <Truck className="w-3.5 h-3.5 text-purple-600 dark:text-purple-400" />
                  {tech.vehicleNumber} ({tech.vehicleModel})
                </span>
              </div>
            </div>
          </div>

          {/* Quick Metrics Bar */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-50 dark:bg-slate-900/80 p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 text-center">
            <div>
              <span className={`block text-[10px] uppercase font-bold tracking-wider ${textMuted}`}>Today's Clock In</span>
              <span className="text-sm font-mono font-bold text-emerald-600 dark:text-emerald-400">
                {tech.clockInTime}
              </span>
            </div>
            <div>
              <span className={`block text-[10px] uppercase font-bold tracking-wider ${textMuted}`}>Shift Status</span>
              <span className={`text-xs font-bold ${tech.isPresent ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600'}`}>
                {tech.isPresent ? 'Present (In Shift)' : tech.leaveType || 'On Leave'}
              </span>
            </div>
            <div>
              <span className={`block text-[10px] uppercase font-bold tracking-wider ${textMuted}`}>Logged Work</span>
              <span className={`text-sm font-mono font-bold ${textHeader}`}>
                {tech.workingHours}h
              </span>
            </div>
            <div>
              <span className={`block text-[10px] uppercase font-bold tracking-wider ${textMuted}`}>Transit KM</span>
              <span className={`text-sm font-mono font-bold text-blue-600 dark:text-blue-400`}>
                {tech.totalKm} km
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Main Grid: Attendance Dossier (Left) + Current Job & Machine (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* A. ATTENDANCE & PUNCH DOSSIER */}
        <div className={`rounded-2xl border p-5 ${cardBg} space-y-4`}>
          <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-emerald-100 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-400">
                <Clock className="w-4 h-4" />
              </div>
              <div>
                <h3 className={`text-sm font-bold ${textHeader}`}>Field Attendance & Punch Verification</h3>
                <p className={`text-[11px] ${textMuted}`}>Fieldy FSM Biometric GPS Punch Log</p>
              </div>
            </div>
            <span className="flex items-center gap-1 text-[11px] font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-200 dark:border-emerald-800">
              <ShieldCheck className="w-3.5 h-3.5" />
              Geofence Verified
            </span>
          </div>

          {/* Punch Times Grid */}
          <div className="grid grid-cols-2 gap-3">
            <div className={`p-3.5 rounded-xl border ${subBg}`}>
              <span className={`text-[11px] font-semibold ${textMuted} flex items-center gap-1`}>
                <Clock className="w-3 h-3 text-emerald-500" />
                Clock-In Time
              </span>
              <span className={`text-lg font-mono font-black mt-1 block ${textHeader}`}>
                {tech.clockInTime}
              </span>
              <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium">
                Punched via Mobile App
              </span>
            </div>

            <div className={`p-3.5 rounded-xl border ${subBg}`}>
              <span className={`text-[11px] font-semibold ${textMuted} flex items-center gap-1`}>
                <Calendar className="w-3 h-3 text-blue-500" />
                Clock-Out / Expected
              </span>
              <span className={`text-lg font-mono font-black mt-1 block ${textHeader}`}>
                {tech.clockOutTime}
              </span>
              <span className={`text-[10px] ${textMuted} font-medium`}>
                Standard 8h Shift Window
              </span>
            </div>
          </div>

          {/* Punch Location Details */}
          <div className={`p-3.5 rounded-xl border ${subBg} space-y-2`}>
            <span className={`text-[11px] font-semibold ${textMuted} flex items-center gap-1`}>
              <MapPin className="w-3.5 h-3.5 text-rose-500" />
              Punch Geofence Location
            </span>
            <p className={`text-xs font-bold ${textHeader}`}>
              {tech.punchLocationName}
            </p>
            <div className="flex items-center justify-between text-[11px] font-mono text-slate-500 dark:text-slate-400 pt-1 border-t border-slate-200 dark:border-slate-800">
              <span>GPS: {tech.punchCoordinates[0].toFixed(4)}°N, {tech.punchCoordinates[1].toFixed(4)}°E</span>
              <span className="text-emerald-600 dark:text-emerald-400 font-semibold">Hub Distance: 12 meters</span>
            </div>
          </div>

          {/* Device & Field Health */}
          <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 text-xs">
            <span className="flex items-center gap-1.5 text-slate-600 dark:text-slate-300">
              <Battery className="w-4 h-4 text-emerald-500" />
              Phone Battery: <strong className={textHeader}>{tech.batteryLevel}%</strong>
            </span>
            <span className="text-slate-500 text-[11px]">
              Fieldy App: <strong className={textHeader}>{tech.appVersion}</strong>
            </span>
            <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-semibold text-[11px]">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              GPS Live
            </span>
          </div>
        </div>

        {/* B. TODAY'S ASSIGNED JOB & MACHINE ASSET */}
        <div className={`rounded-2xl border p-5 ${cardBg} space-y-4`}>
          <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-950/80 text-blue-700 dark:text-blue-400">
                <Briefcase className="w-4 h-4" />
              </div>
              <div>
                <h3 className={`text-sm font-bold ${textHeader}`}>Active Service Job & Asset</h3>
                <p className={`text-[11px] ${textMuted}`}>Fieldy Work Order Assignment</p>
              </div>
            </div>
            {tech.todayJobId && (
              <span className="text-xs font-mono font-bold px-2.5 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-300 dark:bg-emerald-950 dark:text-emerald-300 dark:border-emerald-800">
                {tech.todayJobId}
              </span>
            )}
          </div>

          {tech.todayJobId ? (
            <>
              {/* Job Title and Customer */}
              <div className={`p-3.5 rounded-xl border ${subBg} space-y-1.5`}>
                <span className={`text-[10px] font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400 font-mono`}>
                  Work Order Scope
                </span>
                <h4 className={`text-sm font-bold ${textHeader}`}>
                  {tech.jobTitle}
                </h4>
                <p className="text-xs font-semibold text-slate-700 dark:text-slate-300 flex items-center gap-1.5 pt-1">
                  <span className="text-slate-400">Client:</span> {tech.customerCompany}
                </p>
              </div>

              {/* Machine Asset & Serial Number */}
              <div className={`p-3.5 rounded-xl border ${subBg} space-y-2`}>
                <div className="flex items-center justify-between">
                  <span className={`text-[10px] font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400 font-mono flex items-center gap-1`}>
                    <Tractor className="w-3.5 h-3.5" />
                    Machine Under Service
                  </span>
                  <span className="text-xs font-mono font-black px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200 dark:bg-blue-950 dark:text-blue-300 dark:border-blue-800">
                    SN: {tech.machineSerial}
                  </span>
                </div>
                <p className={`text-xs font-bold ${textHeader}`}>
                  {tech.machineName}
                </p>
                <div className="flex items-center justify-between text-[11px] pt-1 border-t border-slate-200 dark:border-slate-800">
                  <span className={textMuted}>Site Contact:</span>
                  <span className={`font-semibold ${textHeader}`}>{tech.siteContact}</span>
                </div>
              </div>

              {/* Commercials Note */}
              <div className="flex items-center justify-between text-xs px-3 py-2 rounded-xl bg-emerald-50/80 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800">
                <span className="text-emerald-800 dark:text-emerald-300 font-medium">
                  Billing Category: <strong>Billable Deputation (₹5,000 / Shift)</strong>
                </span>
                <span className="text-emerald-700 dark:text-emerald-400 font-mono font-bold">
                  Rate: ₹625/hr
                </span>
              </div>
            </>
          ) : (
            <div className="py-8 text-center space-y-2">
              <Calendar className="w-8 h-8 text-amber-500 mx-auto" />
              <h4 className={`text-sm font-bold ${textHeader}`}>No Active Job Assignment</h4>
              <p className={`text-xs ${textMuted} max-w-xs mx-auto`}>
                {tech.status === 'On Holiday/Leave'
                  ? `Technician is currently on approved leave (${tech.leaveType || 'Leave'}). Expected return tomorrow.`
                  : 'Technician is currently on standby at the regional hub ready for dispatch.'}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* 4. Hours & Productivity Telemetry Breakdown */}
      <div className={`rounded-2xl border p-5 ${cardBg}`}>
        <h3 className={`text-sm font-bold ${textHeader} mb-4 flex items-center gap-2`}>
          <Gauge className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
          Today's Hours & Telematics Distribution
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl border border-emerald-300 dark:border-emerald-800 bg-emerald-50 dark:bg-emerald-950/40 shadow-sm">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-950 dark:text-emerald-300 font-mono">
              Productive Working Hours (H_w)
            </span>
            <div className="flex items-baseline gap-2 mt-1.5">
              <span className="text-3xl font-black font-mono text-emerald-950 dark:text-emerald-200">
                {tech.workingHours}h
              </span>
              <span className="text-xs text-emerald-800 dark:text-emerald-400 font-bold">On-site servicing</span>
            </div>
            <p className="text-xs text-emerald-900 dark:text-emerald-300 mt-2 font-medium">
              Direct machine repair & knotter alignment
            </p>
          </div>

          <div className="p-4 rounded-xl border border-blue-300 dark:border-blue-800 bg-blue-50 dark:bg-blue-950/40 shadow-sm">
            <span className="text-xs font-bold uppercase tracking-wider text-blue-950 dark:text-blue-300 font-mono">
              Transit & Highway Travel (H_t)
            </span>
            <div className="flex items-baseline gap-2 mt-1.5">
              <span className="text-3xl font-black font-mono text-blue-950 dark:text-blue-200">
                {tech.travelHours}h
              </span>
              <span className="text-xs text-blue-800 dark:text-blue-400 font-bold">Bolero transit</span>
            </div>
            <p className="text-xs text-blue-900 dark:text-blue-300 mt-2 font-medium">
              Verified route distance: {tech.totalKm} KM logged
            </p>
          </div>

          <div className="p-4 rounded-xl border border-slate-300 dark:border-slate-800 bg-slate-100 dark:bg-slate-900/60 shadow-sm">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-slate-300 font-mono">
              Idle & Buffer Hours (H_i)
            </span>
            <div className="flex items-baseline gap-2 mt-1.5">
              <span className="text-3xl font-black font-mono text-slate-950 dark:text-white">
                {tech.idleHours}h
              </span>
              <span className="text-xs text-slate-700 dark:text-slate-400 font-bold">Halts & breaks</span>
            </div>
            <p className="text-xs text-slate-800 dark:text-slate-300 mt-2 font-medium">
              Compliant within standard shift allowances
            </p>
          </div>
        </div>
      </div>

      {/* 5. Recent Job Execution History Table */}
      <div className={`rounded-2xl border p-5 ${cardBg}`}>
        <h3 className={`text-sm font-bold ${textHeader} mb-3 flex items-center gap-2`}>
          <Wrench className="w-4 h-4 text-purple-600 dark:text-purple-400" />
          Recent Service Job Assignments
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className={`border-b ${isDark ? 'border-slate-800 text-slate-400' : 'border-slate-200 text-slate-500'}`}>
              <tr>
                <th className="py-2.5 px-3">Job Order</th>
                <th className="py-2.5 px-3">Service Date</th>
                <th className="py-2.5 px-3">Client Company</th>
                <th className="py-2.5 px-3">Machine Asset</th>
                <th className="py-2.5 px-3">Job Type</th>
                <th className="py-2.5 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
              {tech.recentJobs.map((j, idx) => (
                <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition">
                  <td className="py-2.5 px-3 font-mono font-bold text-emerald-700 dark:text-emerald-400">
                    {j.jobId}
                  </td>
                  <td className="py-2.5 px-3 text-slate-700 dark:text-slate-400 font-mono font-medium">
                    {j.date}
                  </td>
                  <td className={`py-2.5 px-3 font-bold ${textHeader}`}>
                    {j.customer}
                  </td>
                  <td className="py-2.5 px-3 font-semibold text-slate-900 dark:text-slate-200">
                    {j.machine}
                  </td>
                  <td className="py-2.5 px-3">
                    <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300">
                      {j.type}
                    </span>
                  </td>
                  <td className="py-2.5 px-3">
                    <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      {j.status}
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
