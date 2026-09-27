/**
 * frontend/src/components/MachineryTable.tsx
 * High-Density Krone Machinery Under Service Table.
 * Asset Name, Serial Number, Customer Company, Site Contact Person, and Active Work Order.
 * Supports both Bright (Default) and Dark modes.
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
  Gauge, 
  AlertTriangle, 
  ShieldCheck, 
  Download,
} from 'lucide-react';
import { MachineryUnderService } from '../types/dashboard';

interface MachineryTableProps {
  machinery: MachineryUnderService[];
  isLoading?: boolean;
  onSelectMachine?: (serialNumber: string) => void;
  onSelectJob?: (jobId: string) => void;
  theme?: 'bright' | 'dark';
}

export const MachineryTable: React.FC<MachineryTableProps> = ({
  machinery,
  isLoading = false,
  onSelectMachine,
  onSelectJob,
  theme = 'bright',
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [copiedSerial, setCopiedSerial] = useState<string | null>(null);

  const isDark = theme === 'dark';
  const cardBg = isDark ? 'bg-[#0B121E] border-slate-800 text-white' : 'bg-white border-slate-200 text-slate-900 shadow-sm';
  const subBg = isDark ? 'bg-[#0F172A]/70 border-slate-800' : 'bg-slate-50 border-slate-200';
  const textMuted = isDark ? 'text-slate-400' : 'text-slate-500';
  const textHeader = isDark ? 'text-white' : 'text-slate-900';

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
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300 dark:bg-emerald-950/80 dark:text-emerald-400 dark:border-emerald-800/60">
          <ShieldCheck className="w-3 h-3" />
          Optimal
        </span>
      );
    }
    if (s.includes('ATTENTION')) {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-300 dark:bg-amber-950/80 dark:text-amber-400 dark:border-amber-800/60">
          <AlertTriangle className="w-3 h-3" />
          Attention
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-300 dark:bg-blue-950/80 dark:text-blue-400 dark:border-blue-800/60">
        <Wrench className="w-3 h-3" />
        Under Service
      </span>
    );
  };

  // Filter Logic
  const filteredMachinery = useMemo(() => {
    return machinery.filter((item) => {
      const q = searchQuery.toLowerCase();
      const matchesSearch =
        item.asset_name.toLowerCase().includes(q) ||
        item.serial_number.toLowerCase().includes(q) ||
        item.client_company_name.toLowerCase().includes(q) ||
        item.site_contact_person.toLowerCase().includes(q) ||
        item.location.toLowerCase().includes(q) ||
        (item.active_job_id && item.active_job_id.toLowerCase().includes(q));

      const matchesCat =
        selectedCategory === 'ALL' ||
        (selectedCategory === 'BALER' && (item.asset_name.includes('Baler') || item.asset_name.includes('BigPack') || item.asset_name.includes('Bellima') || item.asset_name.includes('Fortima'))) ||
        (selectedCategory === 'HARVESTER' && (item.asset_name.includes('Harvester') || item.asset_name.includes('BiG X'))) ||
        (selectedCategory === 'MOWER_RAKE' && (item.asset_name.includes('Mower') || item.asset_name.includes('EasyCut') || item.asset_name.includes('Swadro')));

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
    <div className={`rounded-2xl border overflow-hidden ${cardBg}`}>
      {/* Table Header Bar */}
      <div className={`p-5 border-b flex flex-col lg:flex-row lg:items-center justify-between gap-4 ${subBg}`}>
        <div className="flex items-center gap-3.5">
          <div className="w-11 h-11 rounded-xl bg-purple-100 dark:bg-purple-950/70 border border-purple-200 dark:border-purple-800/50 flex items-center justify-center text-purple-700 dark:text-purple-400">
            <Tractor className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className={`text-lg font-bold tracking-tight ${textHeader}`}>
                Krone Machinery Under Service Today
              </h2>
              <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300 dark:bg-emerald-950 dark:text-emerald-400 font-mono">
                {filteredMachinery.length} Units Active
              </span>
            </div>
            <p className={`text-xs ${textMuted}`}>
              Heavy Equipment Fleet Roster • Large Square Balers, Round Balers, Harvesters & Mowers
            </p>
          </div>
        </div>

        {/* Toolbar Controls */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Category Filter Pills */}
          <div className={`flex items-center rounded-lg p-0.5 border ${isDark ? 'bg-[#060A11] border-slate-800' : 'bg-white border-slate-300'}`}>
            {[
              { id: 'ALL', label: 'All Fleet' },
              { id: 'BALER', label: 'Balers' },
              { id: 'HARVESTER', label: 'Harvesters' },
              { id: 'MOWER_RAKE', label: 'Mowers & Rakes' },
            ].map((cat) => (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`px-3 py-1 rounded-md text-xs font-semibold transition cursor-pointer ${
                  selectedCategory === cat.id
                    ? 'bg-emerald-600 text-white shadow-sm'
                    : textMuted
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>

          {/* Quick Search Input */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              id="machinery-search"
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search serial, asset, site..."
              className={`rounded-lg pl-8 pr-3 py-1.5 text-xs border focus:outline-none focus:ring-2 focus:ring-emerald-500 w-48 md:w-56 ${
                isDark
                  ? 'bg-[#060A11] border-slate-800 text-white placeholder-slate-500'
                  : 'bg-white border-slate-300 text-slate-900 placeholder-slate-400'
              }`}
            />
          </div>

          {/* CSV Export Button */}
          <button
            onClick={handleExportCsv}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border font-semibold text-xs transition cursor-pointer ${
              isDark
                ? 'bg-[#060A11] border-slate-800 hover:border-emerald-600 text-slate-300 hover:text-emerald-400'
                : 'bg-white border-slate-300 hover:border-emerald-600 text-slate-700 hover:text-emerald-700'
            }`}
            title="Export filtered records to CSV"
          >
            <Download className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Table Content */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className={`border-b ${isDark ? 'bg-[#060A11]/90 text-slate-400 border-slate-800' : 'bg-slate-50 text-slate-600 border-slate-200'}`}>
            <tr>
              <th className="py-3.5 px-4">Asset Name & Model</th>
              <th className="py-3.5 px-4">Serial Number</th>
              <th className="py-3.5 px-4">Customer Company</th>
              <th className="py-3.5 px-4">Site Contact Person</th>
              <th className="py-3.5 px-4">Location / Facility</th>
              <th className="py-3.5 px-4">Active Work Order</th>
              <th className="py-3.5 px-4">Operating Hours</th>
              <th className="py-3.5 px-4 text-right">Equipment Health</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
            {filteredMachinery.length === 0 ? (
              <tr>
                <td colSpan={8} className={`py-12 text-center italic ${textMuted}`}>
                  No Krone machinery assets found matching your criteria.
                </td>
              </tr>
            ) : (
              filteredMachinery.map((item) => (
                <tr
                  key={item.serial_number}
                  className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition group cursor-pointer"
                  onClick={() => onSelectMachine?.(item.serial_number)}
                >
                  {/* Asset Name */}
                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-2.5">
                      <div className="p-2 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/40 shrink-0">
                        <Tractor className="w-4 h-4" />
                      </div>
                      <div>
                        <div className={`font-bold ${textHeader}`}>
                          {item.asset_name}
                        </div>
                        <div className={`text-[11px] ${textMuted} flex items-center gap-2 mt-0.5`}>
                          <span>{item.service_type || 'Scheduled Service'}</span>
                        </div>
                      </div>
                    </div>
                  </td>

                  {/* Serial Number with Copy Action */}
                  <td className="py-3.5 px-4">
                    <div className="inline-flex items-center gap-1.5 font-mono text-xs font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-800 border border-slate-300 dark:bg-slate-900 dark:text-slate-300 dark:border-slate-800">
                      <span>{item.serial_number}</span>
                      <button
                        onClick={(e) => handleCopySerial(item.serial_number, e)}
                        className="text-slate-400 hover:text-emerald-600 transition cursor-pointer p-0.5"
                        title="Copy Serial Number"
                      >
                        {copiedSerial === item.serial_number ? (
                          <Check className="w-3 h-3 text-emerald-500" />
                        ) : (
                          <Copy className="w-3 h-3" />
                        )}
                      </button>
                    </div>
                  </td>

                  {/* Customer Company */}
                  <td className="py-3.5 px-4">
                    <div className={`font-semibold line-clamp-1 ${textHeader}`}>
                      {item.client_company_name}
                    </div>
                  </td>

                  {/* Site Contact Person */}
                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-1.5 text-slate-700 dark:text-slate-300">
                      <Phone className="w-3 h-3 text-emerald-500 shrink-0" />
                      <span className="truncate">{item.site_contact_person}</span>
                    </div>
                  </td>

                  {/* Location */}
                  <td className="py-3.5 px-4">
                    <div className={`flex items-center gap-1.5 ${textMuted}`}>
                      <MapPin className="w-3 h-3 text-rose-500 shrink-0" />
                      <span className="truncate">{item.location}</span>
                    </div>
                  </td>

                  {/* Active Work Order Link */}
                  <td className="py-3.5 px-4">
                    {item.active_job_id ? (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectJob?.(item.active_job_id!);
                        }}
                        className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded font-mono text-xs font-bold text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800/60 hover:bg-emerald-100 transition cursor-pointer"
                      >
                        <span>{item.active_job_id}</span>
                        <ExternalLink className="w-3 h-3" />
                      </button>
                    ) : (
                      <span className={`text-[11px] italic ${textMuted}`}>Unscheduled</span>
                    )}
                  </td>

                  {/* Operating Hours */}
                  <td className="py-3.5 px-4 font-mono font-medium text-slate-700 dark:text-slate-300">
                    <div className="flex items-center gap-1">
                      <Gauge className="w-3.5 h-3.5 text-slate-400" />
                      <span>{item.operating_hours ? `${item.operating_hours} hrs` : '1,420 hrs'}</span>
                    </div>
                  </td>

                  {/* Health Status */}
                  <td className="py-3.5 px-4 text-right">
                    {getHealthBadge(item.health_status)}
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
