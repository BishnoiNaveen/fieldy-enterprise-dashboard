/**
 * frontend/src/components/AnomalyAlerts.tsx
 * Anomaly Alert Drawer for unauthorized stops (>15 min outside 5km zone), route deviations, and pan-to-map.
 */

import React, { useState } from 'react';
import {
  AlertTriangle,
  Clock,
  MapPin,
  Compass,
  CheckCircle2,
  ChevronRight,
  ShieldCheck,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { RouteAnomaly, GeoPoint } from '../types/dashboard';

export interface AnomalyAlertsProps {
  anomalies: RouteAnomaly[];
  onSelectAnomaly?: (location: GeoPoint) => void;
  className?: string;
}

export const AnomalyAlerts: React.FC<AnomalyAlertsProps> = ({
  anomalies,
  onSelectAnomaly,
  className = '',
}) => {
  const [acknowledgedIds, setAcknowledgedIds] = useState<Set<string>>(new Set());
  const [isCollapsed, setIsCollapsed] = useState(false);

  const handleAcknowledge = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setAcknowledgedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const activeAnomaliesCount = anomalies.filter(
    (a, idx) => !acknowledgedIds.has(a.anomaly_id || `anom-${idx}`)
  ).length;

  return (
    <div className={`rounded-2xl border border-slate-800 bg-[#0B121E] shadow-2xl flex flex-col overflow-hidden ${className}`}>
      {/* Drawer Header */}
      <div
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="flex items-center justify-between px-5 py-4 border-b border-slate-800/80 bg-slate-900/60 cursor-pointer select-none hover:bg-slate-900/90 transition-all"
      >
        <div className="flex items-center gap-3">
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
            activeAnomaliesCount > 0
              ? 'bg-rose-500/10 border border-rose-500/30 text-rose-400'
              : 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-400'
          }`}>
            {activeAnomaliesCount > 0 ? <AlertTriangle className="w-4 h-4" /> : <ShieldCheck className="w-4 h-4" />}
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              Route Telematics Anomalies
              <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border ${
                activeAnomaliesCount > 0
                  ? 'bg-rose-950/80 text-rose-300 border-rose-800 animate-pulse'
                  : 'bg-emerald-950/80 text-emerald-300 border-emerald-800'
              }`}>
                {activeAnomaliesCount > 0 ? `${activeAnomaliesCount} Flagged` : 'All Clear'}
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              5 km corridor compliance & unauthorized halts (&gt;15m)
            </p>
          </div>
        </div>

        <button className="text-slate-400 hover:text-slate-200 p-1 cursor-pointer">
          {isCollapsed ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
        </button>
      </div>

      {/* Anomaly Card List */}
      {!isCollapsed && (
        <div className="p-4 space-y-3 overflow-y-auto max-h-[460px]">
          {anomalies.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-8 text-center space-y-2">
              <div className="w-12 h-12 rounded-full bg-emerald-950/50 border border-emerald-700/50 flex items-center justify-center text-emerald-400">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <h4 className="text-sm font-semibold text-slate-200">Zero Route Anomalies</h4>
              <p className="text-xs text-slate-500 max-w-[240px]">
                Technician maintained strict transit corridor compliance within the 5 km authorized operational zones.
              </p>
            </div>
          ) : (
            anomalies.map((anomaly, idx) => {
              const id = anomaly.anomaly_id || `anom-${idx}`;
              const isAcknowledged = acknowledgedIds.has(id);
              const isCritical = anomaly.duration_minutes > 30 || anomaly.severity === 'CRITICAL';

              return (
                <div
                  key={id}
                  onClick={() => onSelectAnomaly && onSelectAnomaly(anomaly.location)}
                  className={`group relative rounded-xl border p-3.5 transition-all cursor-pointer ${
                    isAcknowledged
                      ? 'border-slate-800 bg-slate-900/40 opacity-60'
                      : isCritical
                      ? 'border-rose-800/80 bg-rose-950/20 hover:border-rose-600 hover:bg-rose-950/30'
                      : 'border-amber-800/80 bg-amber-950/20 hover:border-amber-600 hover:bg-amber-950/30'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2">
                      <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-md uppercase border ${
                        isAcknowledged
                          ? 'bg-slate-800 text-slate-400 border-slate-700'
                          : isCritical
                          ? 'bg-rose-900/60 text-rose-200 border-rose-700'
                          : 'bg-amber-900/60 text-amber-200 border-amber-700'
                      }`}>
                        {isAcknowledged ? 'ACKNOWLEDGED' : isCritical ? 'CRITICAL STOP' : 'UNAUTHORIZED HALT'}
                      </span>
                      {anomaly.started_at && (
                        <span className="text-[11px] font-mono text-slate-400">
                          {new Date(anomaly.started_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      )}
                    </div>

                    <button
                      onClick={(e) => handleAcknowledge(id, e)}
                      className={`text-[10px] font-semibold px-2 py-0.5 rounded-md border transition-all cursor-pointer ${
                        isAcknowledged
                          ? 'bg-emerald-950 text-emerald-400 border-emerald-800'
                          : 'bg-slate-800 hover:bg-slate-700 text-slate-300 border-slate-700'
                      }`}
                      title={isAcknowledged ? 'Re-open alert' : 'Acknowledge alert'}
                    >
                      {isAcknowledged ? 'Resolved ✓' : 'Acknowledge'}
                    </button>
                  </div>

                  {/* Description */}
                  <p className="text-xs font-semibold text-slate-200 mt-2">
                    {anomaly.description}
                  </p>

                  {/* Key Telematics Indicators */}
                  <div className="grid grid-cols-2 gap-2 mt-2.5 pt-2 border-t border-slate-800/60 text-[11px] font-mono">
                    <div className="flex items-center gap-1.5 text-slate-400">
                      <Clock className="w-3.5 h-3.5 text-amber-400" />
                      <span>Duration: <strong className="text-slate-100">{anomaly.duration_minutes}m</strong></span>
                    </div>
                    <div className="flex items-center gap-1.5 text-slate-400">
                      <MapPin className="w-3.5 h-3.5 text-rose-400" />
                      <span>Limit: <strong className="text-slate-100">15m Max</strong></span>
                    </div>
                    {anomaly.distance_from_designated_route_km !== undefined && (
                      <div className="flex items-center gap-1.5 text-slate-400 col-span-2">
                        <Compass className="w-3.5 h-3.5 text-cyan-400" />
                        <span>Route Detour: <strong className="text-slate-100">{anomaly.distance_from_designated_route_km} km</strong> off corridor</span>
                      </div>
                    )}
                  </div>

                  {/* Coordinates & Quick Pan CTA */}
                  <div className="flex items-center justify-between mt-3 pt-2 border-t border-slate-800/60 text-[10px] text-slate-400">
                    <span className="font-mono">
                      Coord: [{anomaly.location.lat.toFixed(4)}, {anomaly.location.lng.toFixed(4)}]
                    </span>
                    <span className="text-emerald-400 group-hover:translate-x-1 transition-transform flex items-center gap-0.5 font-bold">
                      Inspect on Map <ChevronRight className="w-3 h-3" />
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
};
