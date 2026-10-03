/**
 * frontend/src/components/AmcsContractsView.tsx
 * Authentic Annual Maintenance Contracts (AMCs) browser for Krone Agriculture India.
 * Displays all 11 authentic Fieldy contracts with visit allocations, monthly retainers, and emergency rates.
 */

import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Search, 
  Building2, 
  Calendar, 
  ShieldCheck, 
  Wrench, 
  Phone, 
  Mail, 
  DollarSign, 
  Layers,
  ChevronRight
} from 'lucide-react';
import { AMCDetail } from '../types/dashboard';
import { api } from '../services/api';

interface AmcsContractsViewProps {
  theme: 'bright' | 'dark';
}

export const AmcsContractsView: React.FC<AmcsContractsViewProps> = ({ theme }) => {
  const isDark = theme === 'dark';
  const cardBg = isDark ? 'bg-[#0D1520] border-slate-800 text-white' : 'bg-white border-slate-200 text-slate-900 shadow-sm';
  const textMuted = isDark ? 'text-slate-400' : 'text-slate-500';
  const inputBg = isDark ? 'bg-slate-900 border-slate-700 text-white' : 'bg-slate-50 border-slate-300 text-slate-900';

  const [amcs, setAmcs] = useState<AMCDetail[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedAmc, setSelectedAmc] = useState<AMCDetail | null>(null);

  useEffect(() => {
    const fetchAmcs = async () => {
      setIsLoading(true);
      try {
        const data = await api.getAmcs();
        setAmcs(data);
        if (data.length > 0) setSelectedAmc(data[0]);
      } finally {
        setIsLoading(false);
      }
    };
    fetchAmcs();
  }, []);

  const filtered = amcs.filter(a => 
    a.customer.toLowerCase().includes(search.toLowerCase()) ||
    a.title.toLowerCase().includes(search.toLowerCase()) ||
    a.amc_id.toLowerCase().includes(search.toLowerCase())
  );

  const totalContractValue = amcs.reduce((acc, curr) => acc + (curr.total_value || 0), 0);

  return (
    <div className="space-y-6">
      {/* Top Banner KPI */}
      <div className={`rounded-2xl border p-6 ${cardBg}`}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded text-[11px] font-mono font-bold uppercase tracking-wider bg-emerald-600/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                Commercial Contracts
              </span>
              <span className="px-2.5 py-0.5 rounded text-[11px] font-mono font-bold uppercase tracking-wider bg-purple-600/10 text-purple-600 dark:text-purple-400 border border-purple-500/20">
                Fixed Retainer
              </span>
            </div>
            <h2 className="text-xl font-black tracking-tight mt-1.5 flex items-center gap-2">
              <FileText className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
              Krone Annual Maintenance Contracts & Service Retainers
            </h2>
            <p className={`text-xs mt-1 ${textMuted}`}>
              Authentic Fieldy AMC master ledger for Reliance Industries (Kakinada, Rajahmundry, Shahjahanpur, Hoshiarpur), Adani Agri Logistics, and agricultural enterprises.
            </p>
          </div>

          <div className="flex items-center gap-4">
            <div className="px-4 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
              <span className={`text-[10px] font-mono font-bold uppercase ${textMuted}`}>Active AMCs</span>
              <div className="text-lg font-black font-mono text-emerald-600 dark:text-emerald-400">
                {amcs.length} Contracts
              </div>
            </div>
            <div className="px-4 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
              <span className={`text-[10px] font-mono font-bold uppercase ${textMuted}`}>Total Portfolio Value</span>
              <div className="text-lg font-black font-mono text-slate-800 dark:text-slate-100">
                ₹{(totalContractValue / 100000).toFixed(1)} Lakhs
              </div>
            </div>
          </div>
        </div>

        {/* Search Input */}
        <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-800">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search by customer name, AMC number (e.g. AMC 013), or machinery..."
              className={`w-full pl-10 pr-4 py-2 rounded-xl text-xs border ${inputBg} focus:outline-none focus:ring-2 focus:ring-emerald-500`}
            />
          </div>
        </div>
      </div>

      {/* Grid of Contracts */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map(amc => (
          <div
            key={amc.amc_id}
            onClick={() => setSelectedAmc(amc)}
            className={`rounded-2xl border p-5 transition cursor-pointer hover:border-emerald-500/60 ${cardBg} ${
              selectedAmc?.amc_id === amc.amc_id ? 'ring-2 ring-emerald-500' : ''
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                {amc.amc_id}
              </span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-400">
                {amc.status}
              </span>
            </div>

            <h3 className="text-sm font-bold tracking-tight line-clamp-1">{amc.title}</h3>
            <div className={`text-xs font-medium flex items-center gap-1.5 mt-1 ${textMuted}`}>
              <Building2 className="w-3.5 h-3.5 text-slate-400" />
              {amc.customer}
            </div>

            <div className="grid grid-cols-2 gap-2 mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 text-xs">
              <div>
                <span className={`text-[10px] font-mono uppercase ${textMuted}`}>Total Value</span>
                <div className="font-mono font-black text-slate-800 dark:text-slate-200">
                  ₹{(amc.total_value || 0).toLocaleString('en-IN')}
                </div>
              </div>
              <div>
                <span className={`text-[10px] font-mono uppercase ${textMuted}`}>Monthly Retainer</span>
                <div className="font-mono font-black text-emerald-600 dark:text-emerald-400">
                  ₹{(amc.monthly_retainer || 0).toLocaleString('en-IN')}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 mt-2 text-xs">
              <div>
                <span className={`text-[10px] font-mono uppercase ${textMuted}`}>Visits Quota</span>
                <div className="font-mono font-semibold">{amc.no_of_visits} Visits</div>
              </div>
              <div>
                <span className={`text-[10px] font-mono uppercase ${textMuted}`}>Contract Expiry</span>
                <div className="font-mono text-slate-600 dark:text-slate-400">{amc.expiry_date}</div>
              </div>
            </div>

            {amc.assets && amc.assets.length > 0 && (
              <div className="mt-3 pt-2 border-t border-slate-100 dark:border-slate-800">
                <span className={`text-[10px] font-mono uppercase block mb-1 ${textMuted}`}>Covered Assets</span>
                <div className="flex flex-wrap gap-1">
                  {amc.assets.slice(0, 2).map((a, i) => (
                    <span key={i} className="text-[10px] px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 font-medium">
                      {a}
                    </span>
                  ))}
                  {amc.assets.length > 2 && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 font-mono">
                      +{amc.assets.length - 2} more
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
