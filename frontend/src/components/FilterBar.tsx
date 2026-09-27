/**
 * frontend/src/components/FilterBar.tsx
 * Multi-Dimensional Filter & Timeframe Switcher Bar.
 * Daily/Weekly/Monthly Switcher, Technician, Customer, Status, Job Type, and Date Range Filters.
 * Supports both Bright (Default) and Dark modes.
 */

import React, { useState, useEffect } from 'react';
import { 
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
import { Timeframe, FilterState } from '../types/dashboard';

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
  theme?: 'bright' | 'dark';
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
    { id: 'TECH-09', name: 'Sunil Kumar' },
    { id: 'TECH-10', name: 'Sachin Jadhav' },
  ],
  customerOptions = [
    'Reliance Industries Limited (Bio-Energy Division)',
    'Reliance Industries Limited',
    'Punjab State Farm Cooperative',
    'VERBIO Bio-Gas India Pvt Ltd',
    'SAEL Punjab Biomass Energy Project',
    'Adani Agri Logistics Ltd',
    'Godrej Agrovet Ltd',
  ],
  theme = 'bright',
  className = '',
}) => {
  const [localSearch, setLocalSearch] = useState(filters.searchQuery || '');

  const isDark = theme === 'dark';
  const cardBg = isDark ? 'bg-[#0B121E] border-slate-800 text-white' : 'bg-white border-slate-200 text-slate-900 shadow-sm';
  const inputBg = isDark ? 'bg-[#060A11] border-slate-800 text-white' : 'bg-slate-50 border-slate-300 text-slate-900';
  const textMuted = isDark ? 'text-slate-400' : 'text-slate-500';

  useEffect(() => {
    setLocalSearch(filters.searchQuery || '');
  }, [filters.searchQuery]);

  const handleUpdate = (partial: Partial<FilterState>) => {
    onFilterChange({ ...filters, ...partial });
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      if (localSearch !== filters.searchQuery) {
        handleUpdate({ searchQuery: localSearch });
      }
    }, 350);
    return () => clearTimeout(timer);
  }, [localSearch]);

  const handleReset = () => {
    setLocalSearch('');
    onFilterChange(DEFAULT_FILTER_STATE);
  };

  const activeFilters = [
    filters.technicianId !== 'ALL' && `Tech: ${filters.technicianId}`,
    filters.customerCompany !== 'ALL' && `Client: ${filters.customerCompany}`,
    filters.jobStatus !== 'ALL' && `Status: ${filters.jobStatus}`,
    filters.jobType !== 'ALL' && `Type: ${filters.jobType}`,
    filters.startDate && `From: ${filters.startDate}`,
    filters.endDate && `To: ${filters.endDate}`,
  ].filter(Boolean) as string[];

  return (
    <div className={`rounded-2xl border p-4 sm:p-5 space-y-4 ${cardBg} ${className}`}>
      {/* Top Row: Timeframe Switcher & Global Search */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        
        {/* Timeframe Radio Pills */}
        <div className="flex items-center gap-2">
          <span className={`text-xs font-bold uppercase tracking-wider font-mono ${textMuted}`}>
            Horizon:
          </span>
          <div className={`flex items-center rounded-xl p-1 border ${isDark ? 'bg-[#060A11] border-slate-800' : 'bg-slate-100 border-slate-200'}`}>
            {(['daily', 'weekly', 'monthly'] as Timeframe[]).map((tf) => (
              <button
                key={tf}
                onClick={() => handleUpdate({ timeframe: tf })}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-bold capitalize transition-all duration-200 cursor-pointer ${
                  filters.timeframe === tf
                    ? 'bg-emerald-600 text-white shadow-sm'
                    : `${textMuted} hover:text-slate-900`
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
              id="filterbar-search"
              type="text"
              value={localSearch}
              onChange={(e) => setLocalSearch(e.target.value)}
              placeholder="Search technician, machine, client..."
              className={`w-full rounded-xl pl-9 pr-8 py-2 text-xs border focus:outline-none focus:ring-2 focus:ring-emerald-500 transition ${inputBg}`}
            />
            {localSearch && (
              <button
                onClick={() => setLocalSearch('')}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 cursor-pointer"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {activeFilters.length > 0 && (
            <button
              onClick={handleReset}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold transition shrink-0 cursor-pointer ${
                isDark ? 'bg-slate-800 hover:bg-slate-700 text-white' : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
              }`}
              title="Reset all filters"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>
          )}
        </div>
      </div>

      {/* Bottom Row: Multi-Dimensional Dropdowns */}
      <div className={`grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 pt-2 border-t text-xs ${
        isDark ? 'border-slate-800' : 'border-slate-100'
      }`}>
        {/* 1. Technician Dropdown */}
        <div>
          <label htmlFor="filter-technician" className={`text-[10px] font-semibold uppercase tracking-wider mb-1 flex items-center gap-1 ${textMuted}`}>
            <User className="w-3 h-3 text-emerald-500" />
            Technician
          </label>
          <select
            id="filter-technician"
            value={filters.technicianId}
            onChange={(e) => handleUpdate({ technicianId: e.target.value })}
            className={`w-full rounded-lg px-2.5 py-1.5 border focus:outline-none focus:ring-2 focus:ring-emerald-500 ${inputBg}`}
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
          <label htmlFor="filter-client" className={`text-[10px] font-semibold uppercase tracking-wider mb-1 flex items-center gap-1 ${textMuted}`}>
            <Building2 className="w-3 h-3 text-blue-500" />
            Client Company
          </label>
          <select
            id="filter-client"
            value={filters.customerCompany}
            onChange={(e) => handleUpdate({ customerCompany: e.target.value })}
            className={`w-full rounded-lg px-2.5 py-1.5 border focus:outline-none focus:ring-2 focus:ring-emerald-500 truncate ${inputBg}`}
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
          <label htmlFor="filter-status" className={`text-[10px] font-semibold uppercase tracking-wider mb-1 flex items-center gap-1 ${textMuted}`}>
            <Activity className="w-3 h-3 text-emerald-500" />
            Job Status
          </label>
          <select
            id="filter-status"
            value={filters.jobStatus}
            onChange={(e) => handleUpdate({ jobStatus: e.target.value })}
            className={`w-full rounded-lg px-2.5 py-1.5 border focus:outline-none focus:ring-2 focus:ring-emerald-500 ${inputBg}`}
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
          <label htmlFor="filter-type" className={`text-[10px] font-semibold uppercase tracking-wider mb-1 flex items-center gap-1 ${textMuted}`}>
            <Tag className="w-3 h-3 text-amber-500" />
            Job Type
          </label>
          <select
            id="filter-type"
            value={filters.jobType}
            onChange={(e) => handleUpdate({ jobType: e.target.value })}
            className={`w-full rounded-lg px-2.5 py-1.5 border focus:outline-none focus:ring-2 focus:ring-emerald-500 ${inputBg}`}
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
          <label htmlFor="filter-start-date" className={`text-[10px] font-semibold uppercase tracking-wider mb-1 flex items-center gap-1 ${textMuted}`}>
            <Calendar className="w-3 h-3 text-slate-400" />
            Start Date
          </label>
          <input
            id="filter-start-date"
            type="date"
            value={filters.startDate}
            onChange={(e) => handleUpdate({ startDate: e.target.value })}
            className={`w-full rounded-lg px-2 py-1.5 border focus:outline-none focus:ring-2 focus:ring-emerald-500 font-mono text-[11px] ${inputBg}`}
          />
        </div>

        {/* 6. End Date */}
        <div>
          <label htmlFor="filter-end-date" className={`text-[10px] font-semibold uppercase tracking-wider mb-1 flex items-center gap-1 ${textMuted}`}>
            <Calendar className="w-3 h-3 text-slate-400" />
            End Date
          </label>
          <input
            id="filter-end-date"
            type="date"
            value={filters.endDate}
            onChange={(e) => handleUpdate({ endDate: e.target.value })}
            className={`w-full rounded-lg px-2 py-1.5 border focus:outline-none focus:ring-2 focus:ring-emerald-500 font-mono text-[11px] ${inputBg}`}
          />
        </div>
      </div>

      {/* Active Filter Chips */}
      {activeFilters.length > 0 && (
        <div className={`flex flex-wrap items-center gap-2 pt-2 border-t ${isDark ? 'border-slate-800' : 'border-slate-100'}`}>
          <span className={`text-[11px] font-medium flex items-center gap-1 ${textMuted}`}>
            <SlidersHorizontal className="w-3 h-3 text-emerald-500" />
            Active Filters:
          </span>
          {activeFilters.map((tag, i) => (
            <span
              key={i}
              className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200 dark:bg-emerald-950 dark:text-emerald-300 dark:border-emerald-800"
            >
              {tag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};
