/**
 * frontend/src/App.tsx
 * Krone Agriculture India — Field Service & Telematics Operations Command Dashboard.
 * Unifies Executive Command, Attendance & Clock-In Roster, Fleet Radar & Route Inspector,
 * Machinery Under Service, Productivity Analytics, and Full-Page Technician Detailed Dossiers.
 * Supports Bright Mode (Default) and Dark Mode.
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { 
  Activity, 
  MapPin, 
  TrendingUp, 
  Tractor, 
  Layers, 
  ChevronRight,
  ChevronLeft,
  Sparkles,
  Users,
  Clock,
  Briefcase,
  ShieldCheck,
  CheckCircle2,
  CalendarOff,
  FileSearch,
  FileText,
  Zap,
  ShieldAlert
} from 'lucide-react';
import { 
  PulseResponse, 
  ProductivityResponse, 
  RouteResponse, 
  FilterState, 
  GeoPoint, 
  Cluster5km 
} from './types/dashboard';
import { api, getBackendLiveStatus } from './services/api';
import { Header } from './components/Header';
import { LivePulseBoard } from './components/LivePulseBoard';
import { FilterBar, DEFAULT_FILTER_STATE } from './components/FilterBar';
import { ProductivityCharts } from './components/ProductivityCharts';
import { RouteInspectorMap } from './components/RouteInspectorMap';
import { AnomalyAlerts } from './components/AnomalyAlerts';
import { AttendanceBoard } from './components/AttendanceBoard';
import { TechnicianDetailView, ExtendedTechnicianData } from './components/TechnicianDetailView';
import { FieldyApiModal } from './components/FieldyApiModal';
import { ForensicAuditView } from './components/ForensicAuditView';
import { AmcsContractsView } from './components/AmcsContractsView';
import { AutomationsView } from './components/AutomationsView';
import { SecurityModal } from './components/SecurityModal';
import { OverviewView } from './components/OverviewView';
import { KRONE_FLEET_MASTER } from './utils/kroneFleetData';

export const App: React.FC = () => {
  // Theme State: 'bright' (Default) | 'dark'
  const [theme, setTheme] = useState<'bright' | 'dark'>(() => {
    return (localStorage.getItem('krone_theme') as 'bright' | 'dark') || 'bright';
  });

  // Navigation View Tab: 'all' | 'audit' | 'amcs' | 'attendance' | 'telematics' | 'machines' | 'analytics' | 'automations'
  const [activeTab, setActiveTab] = useState<'all' | 'audit' | 'amcs' | 'attendance' | 'telematics' | 'machines' | 'analytics' | 'automations'>('all');
  const [isSecurityModalOpen, setIsSecurityModalOpen] = useState(false);


  // Selected Technician Detailed Page (If set, displays full-page dossier)
  const [selectedTechDetailId, setSelectedTechDetailId] = useState<string | null>(null);

  // Core Data States
  const [pulseData, setPulseData] = useState<PulseResponse | null>(null);
  const [productivityData, setProductivityData] = useState<ProductivityResponse | null>(null);
  const [routeData, setRouteData] = useState<RouteResponse | null>(null);

  // Loading States
  const [isLoadingPulse, setIsLoadingPulse] = useState(true);
  const [isLoadingProductivity, setIsLoadingProductivity] = useState(true);
  const [isLoadingRoute, setIsLoadingRoute] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [isLive, setIsLive] = useState(true);

  // Auto-Sync States
  const [isAutoSyncEnabled, setIsAutoSyncEnabled] = useState(true);
  const [autoSyncCountdown, setAutoSyncCountdown] = useState(15);
  const [isApiModalOpen, setIsApiModalOpen] = useState(false);

  // Filtering & Interaction States
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTER_STATE);
  const [selectedTechnicianId, setSelectedTechnicianId] = useState<string>('TECH-01');
  const [selectedAnomalyLocation, setSelectedAnomalyLocation] = useState<GeoPoint | null>(null);
  const [lastSyncedAt, setLastSyncedAt] = useState<string | null>(null);

  // Sync theme class to body
  useEffect(() => {
    if (theme === 'dark') {
      document.body.classList.add('dark');
    } else {
      document.body.classList.remove('dark');
    }
    localStorage.setItem('krone_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'bright' ? 'dark' : 'bright');
  };

  // 1. Fetch Pulse Data
  const loadPulse = useCallback(async () => {
    setIsLoadingPulse(true);
    try {
      const data = await api.getPulse();
      setPulseData(data);
      setLastSyncedAt(data.timestamp || new Date().toISOString());
      setIsLive(getBackendLiveStatus());
    } finally {
      setIsLoadingPulse(false);
    }
  }, []);

  // 2. Fetch Productivity Data based on Filters
  const loadProductivity = useCallback(async (currentFilters: FilterState) => {
    setIsLoadingProductivity(true);
    try {
      const data = await api.getProductivity({
        timeframe: currentFilters.timeframe,
        technician_id: currentFilters.technicianId !== 'ALL' ? currentFilters.technicianId : undefined,
        customer_company: currentFilters.customerCompany !== 'ALL' ? currentFilters.customerCompany : undefined,
        job_status: currentFilters.jobStatus !== 'ALL' ? currentFilters.jobStatus : undefined,
        job_type: currentFilters.jobType !== 'ALL' ? currentFilters.jobType : undefined,
        start_date: currentFilters.startDate || undefined,
        end_date: currentFilters.endDate || undefined,
      });
      setProductivityData(data);
    } finally {
      setIsLoadingProductivity(false);
    }
  }, []);

  // 3. Fetch Route Telematics Data
  const loadRoute = useCallback(async (technicianId: string) => {
    setIsLoadingRoute(true);
    try {
      const data = await api.getRoute(technicianId);
      setRouteData(data);
    } finally {
      setIsLoadingRoute(false);
    }
  }, []);

  // Initial Load
  useEffect(() => {
    loadPulse();
    loadProductivity(DEFAULT_FILTER_STATE);
    loadRoute(selectedTechnicianId);
  }, [loadPulse, loadProductivity, loadRoute, selectedTechnicianId]);

  // Automatic Background Polling Timer (15s interval)
  useEffect(() => {
    if (!isAutoSyncEnabled) return;

    const interval = setInterval(() => {
      setAutoSyncCountdown(prev => {
        if (prev <= 1) {
          // Trigger smooth background refresh
          loadPulse();
          loadProductivity(filters);
          loadRoute(selectedTechnicianId);
          return 15;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isAutoSyncEnabled, loadPulse, loadProductivity, loadRoute, filters, selectedTechnicianId]);

  // When filters update, reload productivity
  const handleFilterChange = (newFilters: FilterState) => {
    setFilters(newFilters);
    loadProductivity(newFilters);
    if (newFilters.technicianId !== 'ALL' && newFilters.technicianId !== selectedTechnicianId) {
      setSelectedTechnicianId(newFilters.technicianId);
      loadRoute(newFilters.technicianId);
    }
  };

  // Fresh Sync Trigger
  const handleFreshSync = async () => {
    setIsSyncing(true);
    try {
      const syncRes = await api.triggerSync(true);
      setLastSyncedAt(syncRes.last_synced_at || new Date().toISOString());
      await Promise.all([
        loadPulse(),
        loadProductivity(filters),
        loadRoute(selectedTechnicianId),
      ]);
      setAutoSyncCountdown(15);
    } finally {
      setIsSyncing(false);
    }
  };

  // Handler to open full-page detailed dossier for a technician
  const handleOpenTechnicianDetail = (techId: string) => {
    setSelectedTechDetailId(techId);
    setSelectedTechnicianId(techId);
    loadRoute(techId);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Find currently selected technician object for detailed page
  const selectedTechDetail = KRONE_FLEET_MASTER.find(t => t.id === selectedTechDetailId);

  const isDark = theme === 'dark';

  return (
    <div className={`min-h-screen flex flex-col transition-colors duration-200 ${
      isDark ? 'bg-[#060A11] text-slate-100' : 'bg-[#F8FAFC] text-slate-900'
    } selection:bg-emerald-500 selection:text-white`}>
      {/* 1. Executive Operations Header */}
      <Header
        lastSyncedAt={lastSyncedAt}
        isLive={isLive}
        onFreshSync={handleFreshSync}
        isSyncing={isSyncing}
        theme={theme}
        onToggleTheme={toggleTheme}
        autoSyncCountdown={autoSyncCountdown}
        isAutoSyncEnabled={isAutoSyncEnabled}
        onToggleAutoSync={() => setIsAutoSyncEnabled(!isAutoSyncEnabled)}
        onOpenApiModal={() => setIsApiModalOpen(true)}
        onOpenSecurityModal={() => setIsSecurityModalOpen(true)}
        dataSource={pulseData?.sync_meta?.source}
        totalJobsCount={pulseData?.kpis?.total_fieldy_jobs || 483}
      />

      {/* 2. Main Dashboard Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 space-y-6">
        
        {/* VIEW A: FULL-PAGE DETAILED DOSSIER VIEW (If technician clicked) */}
        {selectedTechDetail ? (
          <TechnicianDetailView
            technician={selectedTechDetail}
            allTechnicians={KRONE_FLEET_MASTER}
            onBack={() => setSelectedTechDetailId(null)}
            onSelectAnotherTech={(newId) => handleOpenTechnicianDetail(newId)}
            theme={theme}
          />
        ) : (
          /* VIEW B: STANDARD OPERATIONS COMMAND WITH TABS */
          <>
            {/* Navigation View Switcher & Title Ribbon */}
            <div className={`flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-3 border-b ${
              isDark ? 'border-slate-800' : 'border-slate-200'
            }`}>
              <div>
                <div className="flex items-center gap-1.5 text-xs font-mono font-bold text-emerald-600 dark:text-emerald-400">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>KRONE AGRICULTURE INDIA • FIELD SERVICE & TELEMATICS COMMAND</span>
                </div>
                <h2 className="text-xl sm:text-2xl font-black tracking-tight mt-0.5">
                  Krone Operations Command Center
                </h2>
              </div>

              {/* Module Navigation Tabs */}
              <div className={`inline-flex flex-wrap p-1 rounded-xl border ${
                isDark ? 'bg-[#0B121E] border-slate-800' : 'bg-white border-slate-300 shadow-sm'
              }`}>
                {[
                  { id: 'all', label: 'Overview', icon: Layers },
                  { id: 'machines', label: 'Field Operations', icon: Tractor },
                  { id: 'attendance', label: 'Roster & Manpower', icon: Clock },
                  { id: 'audit', label: 'Forensic Bill Audit', icon: FileSearch },
                  { id: 'amcs', label: 'AMCs & Retainers', icon: FileText },
                  { id: 'telematics', label: 'Fleet Map & Radar', icon: MapPin },
                  { id: 'analytics', label: 'Hours & Analytics', icon: TrendingUp },
                  { id: 'automations', label: 'Automations Hub', icon: Zap },
                ].map((tab) => {
                  const Icon = tab.icon;
                  const isActive = activeTab === tab.id;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id as any)}
                      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all duration-200 cursor-pointer ${
                        isActive
                          ? 'bg-emerald-600 text-white shadow-sm'
                          : isDark
                          ? 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                          : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                      }`}
                    >
                      <Icon className="w-3.5 h-3.5" />
                      <span>{tab.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* TAB 1: SIMPLE PLAIN OVERVIEW DASHBOARD */}
            {activeTab === 'all' && (
              <OverviewView
                kpis={pulseData?.kpis ?? null}
                todayJobs={pulseData?.today_jobs ?? []}
                technicians={KRONE_FLEET_MASTER}
                routeData={routeData}
                onSelectTechnician={handleOpenTechnicianDetail}
                onNavigateTab={(tab) => setActiveTab(tab)}
                theme={theme}
              />
            )}

            {/* TAB 2: ATTENDANCE & CLOCK-IN ROSTER */}
            {activeTab === 'attendance' && (
              <AttendanceBoard
                technicians={KRONE_FLEET_MASTER}
                onSelectTechnician={handleOpenTechnicianDetail}
                theme={theme}
              />
            )}

            {/* TAB 3: FLEET RADAR & ROUTE INSPECTOR */}
            {activeTab === 'telematics' && (
              <div className="space-y-6">
                {routeData && (
                  <RouteInspectorMap
                    routeData={routeData}
                    selectedAnomalyLocation={selectedAnomalyLocation}
                    onSelectCluster={(cluster) => {
                      setSelectedAnomalyLocation(cluster.centroid);
                    }}
                    onSelectTechnician={(id) => {
                      setSelectedTechnicianId(id);
                      loadRoute(id);
                    }}
                    theme={theme}
                  />
                )}

                {/* Anomaly Alerts */}
                {routeData?.anomalies && routeData.anomalies.length > 0 && (
                  <AnomalyAlerts
                    anomalies={routeData.anomalies}
                    onSelectAnomaly={(loc: GeoPoint) => setSelectedAnomalyLocation(loc)}
                  />
                )}
              </div>
            )}

            {/* TAB 4: MACHINES & WORK ORDERS */}
            {activeTab === 'machines' && (
              <div className="space-y-6">
                <LivePulseBoard
                  pulseData={pulseData}
                  isLoading={isLoadingPulse}
                  onSelectTechnician={handleOpenTechnicianDetail}
                  onInspectRoute={(id) => {
                    setSelectedTechnicianId(id);
                    setActiveTab('telematics');
                  }}
                  onSelectJob={(id) => console.log('Job:', id)}
                  theme={theme}
                />
              </div>
            )}

            {/* TAB 5: HOURS & PRODUCTIVITY ANALYTICS */}
            {activeTab === 'analytics' && (
              <div className="space-y-6">
                <FilterBar
                  filters={filters}
                  onFilterChange={handleFilterChange}
                  theme={theme}
                />

                <ProductivityCharts
                  data={productivityData}
                  isLoading={isLoadingProductivity}
                  onSelectTechnician={handleOpenTechnicianDetail}
                  theme={theme}
                />
              </div>
            )}

            {/* TAB 6: 12-PILLAR FORENSIC BILL & KM AUDIT */}
            {activeTab === 'audit' && (
              <ForensicAuditView theme={theme} />
            )}

            {/* TAB 7: AMCS & COMMERCIAL CONTRACTS */}
            {activeTab === 'amcs' && (
              <AmcsContractsView theme={theme} />
            )}

            {/* TAB 8: AUTOMATIONS & WHATSAPP / EMAIL HUB */}
            {activeTab === 'automations' && (
              <AutomationsView theme={theme} />
            )}
          </>
        )}
      </main>

      {/* 3. Fieldy Cloud API & Live Sync Settings Modal */}
      <FieldyApiModal
        isOpen={isApiModalOpen}
        onClose={() => setIsApiModalOpen(false)}
        onSyncComplete={handleFreshSync}
        theme={theme}
      />

      {/* 4. Enterprise Security & Compliance Audit Modal */}
      <SecurityModal
        isOpen={isSecurityModalOpen}
        onClose={() => setIsSecurityModalOpen(false)}
        theme={theme}
      />
    </div>
  );
};

export default App;
