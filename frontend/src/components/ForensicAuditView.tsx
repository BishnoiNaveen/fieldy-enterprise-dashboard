/**
 * frontend/src/components/ForensicAuditView.tsx
 * 12-Pillar Forensic Bill & KM Claim Auditor for Krone Agriculture India.
 * Enforces statutory local conveyance (<50km) vs outstation (>50km), minimum 8-hour DA cutoff,
 * anti-double-claim client guest house rules, and calculates financial recovery.
 */

import React, { useState } from 'react';
import { 
  ShieldAlert, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  FileSearch, 
  DollarSign, 
  Clock, 
  Car, 
  Building2, 
  Receipt,
  Download,
  Check,
  RefreshCw
} from 'lucide-react';
import { BillAuditRequest, BillAuditResponse } from '../types/dashboard';
import { api } from '../services/api';
import { KRONE_FLEET_MASTER } from '../utils/kroneFleetData';

interface ForensicAuditViewProps {
  theme: 'bright' | 'dark';
}

export const ForensicAuditView: React.FC<ForensicAuditViewProps> = ({ theme }) => {
  const isDark = theme === 'dark';
  const cardBg = isDark ? 'bg-[#0D1520] border-slate-800 text-white' : 'bg-white border-slate-200 text-slate-900 shadow-sm';
  const textMuted = isDark ? 'text-slate-400' : 'text-slate-500';
  const inputBg = isDark ? 'bg-slate-900 border-slate-700 text-white' : 'bg-slate-50 border-slate-300 text-slate-900';

  // Form State
  const [techId, setTechId] = useState<string>('TECH-01');
  const [date, setDate] = useState<string>('2026-10-02');
  const [jobId, setJobId] = useState<string>('SR-26- 0148');
  const [vehicleType, setVehicleType] = useState<'bike' | 'car'>('bike');
  const [claimedKm, setClaimedKm] = useState<number>(35);
  const [dutyHours, setDutyHours] = useState<number>(8.5);
  const [claimedDa, setClaimedDa] = useState<number>(150);
  const [claimedHotel, setClaimedHotel] = useState<number>(0);
  const [stayProvided, setStayProvided] = useState<boolean>(false);
  const [tripPurpose, setTripPurpose] = useState<string>('Krone Baler Emergency Breakdown Service');

  // Audit Outcome State
  const [isAuditing, setIsAuditing] = useState(false);
  const [auditResult, setAuditResult] = useState<BillAuditResponse | null>(null);
  const [history, setHistory] = useState<BillAuditResponse[]>([]);

  const handleRunAudit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsAuditing(true);
    const tech = KRONE_FLEET_MASTER.find(t => t.id === techId) || KRONE_FLEET_MASTER[0];

    const req: BillAuditRequest = {
      technician_id: tech.id,
      technician_name: tech.name,
      date,
      claimed_km: Number(claimedKm),
      vehicle_type: vehicleType,
      claimed_da: Number(claimedDa),
      claimed_hotel: Number(claimedHotel),
      stay_provided_by_client: stayProvided,
      duty_hours: Number(dutyHours),
      job_id: jobId,
      trip_purpose: tripPurpose
    };

    try {
      const res = await api.performBillAudit(req);
      setAuditResult(res);
      setHistory(prev => [res, ...prev.slice(0, 9)]);
    } finally {
      setIsAuditing(false);
    }
  };

  const getVerdictBadge = (verdict: string) => {
    if (verdict === 'APPROVED') {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-400 border border-emerald-500/30">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
          Statutory Compliant — 100% Approved
        </span>
      );
    }
    if (verdict === 'FLAGGED_PARTIAL_APPROVAL') {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase bg-amber-100 text-amber-800 dark:bg-amber-950/80 dark:text-amber-400 border border-amber-500/30">
          <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400" />
          Flagged Overclaim — Partial Recovery
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase bg-rose-100 text-rose-800 dark:bg-rose-950/80 dark:text-rose-400 border border-rose-500/30">
        <XCircle className="w-4 h-4 text-rose-600 dark:text-rose-400" />
        Rejected — Zero Statutory Compliance
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className={`rounded-2xl border p-6 ${cardBg}`}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded text-[11px] font-mono font-bold uppercase tracking-wider bg-emerald-600/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                Statutory Control Layer
              </span>
              <span className="px-2.5 py-0.5 rounded text-[11px] font-mono font-bold uppercase tracking-wider bg-blue-600/10 text-blue-600 dark:text-blue-400 border border-blue-500/20">
                12-Pillar Forensic Engine
              </span>
            </div>
            <h2 className="text-xl font-black tracking-tight mt-1.5 flex items-center gap-2">
              <FileSearch className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
              Fieldy Bill, Conveyance & Travel Expense Forensic Auditor
            </h2>
            <p className={`text-xs mt-1 ${textMuted}`}>
              Automated anti-fraud verification enforcing 50 KM territory boundaries, 8-hour DA cutoff, client stay anti-double-claims, and GPS telematics parity.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => {
                // Preset: Fraud Sample
                setClaimedKm(110);
                setVehicleType('bike');
                setClaimedDa(300);
                setClaimedHotel(1600);
                setStayProvided(true);
                setDutyHours(5.0);
              }}
              className="px-3.5 py-2 rounded-xl text-xs font-bold bg-amber-500/10 text-amber-600 dark:text-amber-400 hover:bg-amber-500/20 transition border border-amber-500/30"
            >
              Load Overclaim Attack Test
            </button>
            <button
              onClick={() => {
                // Preset: Valid Local Sample
                setClaimedKm(32);
                setVehicleType('bike');
                setClaimedDa(150);
                setClaimedHotel(0);
                setStayProvided(false);
                setDutyHours(8.5);
              }}
              className="px-3.5 py-2 rounded-xl text-xs font-bold bg-emerald-600/10 text-emerald-600 dark:text-emerald-400 hover:bg-emerald-600/20 transition border border-emerald-500/30"
            >
              Load Valid Local Claim
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Form: Claim Inputs */}
        <div className={`lg:col-span-5 rounded-2xl border p-6 ${cardBg}`}>
          <h3 className="text-sm font-bold flex items-center gap-2 mb-4 pb-3 border-b border-slate-200 dark:border-slate-800">
            <Receipt className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            Technician Claim Details
          </h3>

          <form onSubmit={handleRunAudit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold font-mono text-slate-700 dark:text-slate-300 mb-1">
                Technician Name & Roster ID
              </label>
              <select
                value={techId}
                onChange={e => setTechId(e.target.value)}
                className={`w-full px-3 py-2 rounded-xl text-xs font-medium border ${inputBg} focus:outline-none focus:ring-2 focus:ring-emerald-500`}
              >
                {KRONE_FLEET_MASTER.map(t => (
                  <option key={t.id} value={t.id}>
                    {t.name} ({t.id} • {t.region})
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold font-mono text-slate-700 dark:text-slate-300 mb-1">
                  Service Date
                </label>
                <input
                  type="date"
                  value={date}
                  onChange={e => setDate(e.target.value)}
                  className={`w-full px-3 py-2 rounded-xl text-xs font-mono border ${inputBg} focus:outline-none focus:ring-2 focus:ring-emerald-500`}
                />
              </div>

              <div>
                <label className="block text-xs font-bold font-mono text-slate-700 dark:text-slate-300 mb-1">
                  Fieldy Job ID
                </label>
                <input
                  type="text"
                  value={jobId}
                  onChange={e => setJobId(e.target.value)}
                  placeholder="SR-26- 0148"
                  className={`w-full px-3 py-2 rounded-xl text-xs font-mono font-bold border ${inputBg} focus:outline-none focus:ring-2 focus:ring-emerald-500`}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold font-mono text-slate-700 dark:text-slate-300 mb-1">
                  Vehicle Running Mode
                </label>
                <select
                  value={vehicleType}
                  onChange={e => setVehicleType(e.target.value as 'bike' | 'car')}
                  className={`w-full px-3 py-2 rounded-xl text-xs border ${inputBg} focus:outline-none focus:ring-2 focus:ring-emerald-500`}
                >
                  <option value="bike">Personal Bike (₹5.00/KM)</option>
                  <option value="car">Four-Wheeler Car (₹15.00/KM)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold font-mono text-slate-700 dark:text-slate-300 mb-1">
                  Claimed Distance (KM)
                </label>
                <input
                  type="number"
                  step="0.5"
                  value={claimedKm}
                  onChange={e => setClaimedKm(parseFloat(e.target.value) || 0)}
                  className={`w-full px-3 py-2 rounded-xl text-xs font-mono font-bold border ${inputBg} focus:outline-none focus:ring-2 focus:ring-emerald-500`}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold font-mono text-slate-700 dark:text-slate-300 mb-1">
                  Total Duty Hours (Fieldy)
                </label>
                <input
                  type="number"
                  step="0.5"
                  value={dutyHours}
                  onChange={e => setDutyHours(parseFloat(e.target.value) || 0)}
                  className={`w-full px-3 py-2 rounded-xl text-xs font-mono border ${inputBg} focus:outline-none focus:ring-2 focus:ring-emerald-500`}
                />
                <span className={`text-[10px] ${dutyHours >= 8.0 ? 'text-emerald-600' : 'text-amber-600'} font-medium`}>
                  {dutyHours >= 8.0 ? '✓ Exceeds 8h cutoff' : '⚠ Below 8h DA cutoff'}
                </span>
              </div>

              <div>
                <label className="block text-xs font-bold font-mono text-slate-700 dark:text-slate-300 mb-1">
                  Claimed DA (₹)
                </label>
                <input
                  type="number"
                  value={claimedDa}
                  onChange={e => setClaimedDa(parseFloat(e.target.value) || 0)}
                  className={`w-full px-3 py-2 rounded-xl text-xs font-mono font-bold border ${inputBg} focus:outline-none focus:ring-2 focus:ring-emerald-500`}
                />
                <span className={`text-[10px] ${textMuted}`}>
                  Local: ₹150 / Outstation: ₹300
                </span>
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold font-mono text-slate-700 dark:text-slate-300 mb-1">
                Claimed Hotel Accommodation (₹)
              </label>
              <input
                type="number"
                value={claimedHotel}
                onChange={e => setClaimedHotel(parseFloat(e.target.value) || 0)}
                placeholder="0.00"
                className={`w-full px-3 py-2 rounded-xl text-xs font-mono border ${inputBg} focus:outline-none focus:ring-2 focus:ring-emerald-500`}
              />
            </div>

            <div className="flex items-center gap-2 p-3 rounded-xl bg-slate-100 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
              <input
                type="checkbox"
                id="stayProvided"
                checked={stayProvided}
                onChange={e => setStayProvided(e.target.checked)}
                className="w-4 h-4 rounded text-emerald-600 focus:ring-emerald-500 border-slate-300"
              />
              <label htmlFor="stayProvided" className="text-xs font-bold cursor-pointer">
                Client provided Guest House / Stay (e.g. Reliance / Adani Site)
              </label>
            </div>

            <button
              type="submit"
              disabled={isAuditing}
              className="w-full py-3 rounded-xl text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 shadow-lg shadow-emerald-600/20 transition flex items-center justify-center gap-2"
            >
              {isAuditing ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Running 12-Pillar Forensic Verification...
                </>
              ) : (
                <>
                  <ShieldAlert className="w-4 h-4" />
                  Execute 12-Pillar Forensic Audit
                </>
              )}
            </button>
          </form>
        </div>

        {/* Right Output: Audit Verdict & Recovery Table */}
        <div className="lg:col-span-7 space-y-4">
          {auditResult ? (
            <div className="space-y-4">
              {/* Verdict Header Card */}
              <div className={`rounded-2xl border p-5 ${cardBg}`}>
                <div className="flex items-center justify-between flex-wrap gap-2 mb-3">
                  <span className={`text-[11px] font-mono ${textMuted}`}>
                    Audit Reference: <strong className="text-slate-800 dark:text-slate-200">{auditResult.audit_id}</strong>
                  </span>
                  {getVerdictBadge(auditResult.verdict)}
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 my-4">
                  <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                    <span className={`text-[10px] font-mono font-bold uppercase ${textMuted}`}>Claimed Total</span>
                    <div className="text-xl font-black font-mono mt-1 text-slate-800 dark:text-slate-100">
                      ₹{auditResult.total_claimed_amount.toFixed(2)}
                    </div>
                  </div>

                  <div className="p-3.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-500/20">
                    <span className="text-[10px] font-mono font-bold uppercase text-emerald-600 dark:text-emerald-400">
                      Approved Admissible
                    </span>
                    <div className="text-xl font-black font-mono mt-1 text-emerald-600 dark:text-emerald-400">
                      ₹{auditResult.total_admissible_amount.toFixed(2)}
                    </div>
                  </div>

                  <div className="p-3.5 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-500/20">
                    <span className="text-[10px] font-mono font-bold uppercase text-rose-600 dark:text-rose-400">
                      Disallowed Recovery
                    </span>
                    <div className="text-xl font-black font-mono mt-1 text-rose-600 dark:text-rose-400">
                      ₹{auditResult.total_disallowed_recovery.toFixed(2)}
                    </div>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-slate-100 dark:bg-slate-800/80 text-xs font-medium">
                  <strong>Auditor Direct Action:</strong> {auditResult.action_required}
                </div>
              </div>

              {/* 12-Pillars Checklist Table */}
              <div className={`rounded-2xl border p-5 ${cardBg}`}>
                <h4 className="text-xs font-bold uppercase tracking-wider font-mono text-slate-500 mb-3">
                  12-Pillar Statutory Verification Breakdown
                </h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left">
                    <thead>
                      <tr className="border-b border-slate-200 dark:border-slate-800 text-[11px] font-mono uppercase text-slate-500">
                        <th className="py-2 px-3">Pillar</th>
                        <th className="py-2 px-3">Verification Rule</th>
                        <th className="py-2 px-3">Status</th>
                        <th className="py-2 px-3">Forensic Detail</th>
                        <th className="py-2 px-3 text-right">Recovery</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
                      {auditResult.forensic_checks.map((check, idx) => (
                        <tr key={idx} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30">
                          <td className="py-2.5 px-3 font-mono font-bold text-slate-600 dark:text-slate-400">
                            {check.pillar}
                          </td>
                          <td className="py-2.5 px-3 font-semibold">{check.name}</td>
                          <td className="py-2.5 px-3">
                            {check.passed ? (
                              <span className="inline-flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-bold">
                                <Check className="w-3.5 h-3.5" /> Pass
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1 text-rose-600 dark:text-rose-400 font-bold">
                                <XCircle className="w-3.5 h-3.5" /> Flagged
                              </span>
                            )}
                          </td>
                          <td className={`py-2.5 px-3 ${textMuted}`}>{check.details}</td>
                          <td className="py-2.5 px-3 text-right font-mono font-bold text-rose-600 dark:text-rose-400">
                            {check.disallowed_amount && check.disallowed_amount > 0 ? (
                              `₹${check.disallowed_amount.toFixed(2)}`
                            ) : (
                              '—'
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          ) : (
            <div className={`rounded-2xl border p-12 text-center flex flex-col items-center justify-center ${cardBg}`}>
              <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 flex items-center justify-center text-emerald-600 dark:text-emerald-400 mb-4">
                <FileSearch className="w-8 h-8" />
              </div>
              <h3 className="text-base font-bold">Awaiting Audit Execution</h3>
              <p className={`text-xs max-w-sm mt-1.5 ${textMuted}`}>
                Enter technician claim parameters or load a test case to execute the 12-pillar statutory audit engine.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
