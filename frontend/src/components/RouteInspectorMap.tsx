/**
 * frontend/src/components/RouteInspectorMap.tsx
 * Autonomous Route Inspector with 5 km Geofence Circles, Route Playback Scrubber,
 * OpenStreetMap Bright Tiles, and Fleet Radar (All Technicians across India).
 */

import React, { useState, useEffect, useMemo } from 'react';
import {
  MapContainer,
  TileLayer,
  Polyline,
  Circle,
  Marker,
  Popup,
  Tooltip,
  useMap,
} from 'react-leaflet';
import L, { LatLngBoundsExpression } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import {
  Play,
  Pause,
  RotateCcw,
  Navigation,
  Clock,
  Gauge,
  ShieldAlert,
  Maximize2,
  Users,
  Compass,
  MapPin,
  Tractor,
  Layers,
  ArrowRight
} from 'lucide-react';
import { RouteResponse, GeoPoint, Cluster5km } from '../types/dashboard';
import { KRONE_FLEET_MASTER } from '../utils/kroneFleetData';
import { ExtendedTechnicianData } from './TechnicianDetailView';

// ---------------------------------------------------------------------------
// Custom HTML DivIcon Generators (100% SVG, Zero PNG dependency)
// ---------------------------------------------------------------------------

const createBaseIcon = (name: string) =>
  L.divIcon({
    className: 'custom-leaflet-icon',
    html: `
      <div class="relative flex items-center justify-center group cursor-pointer">
        <div class="absolute -inset-1 rounded-full bg-emerald-500/40 animate-ping"></div>
        <div class="w-10 h-10 rounded-xl bg-slate-900 border-2 border-emerald-500 shadow-lg shadow-emerald-500/30 flex items-center justify-center text-emerald-400">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
          </svg>
        </div>
        <div class="absolute -bottom-7 whitespace-nowrap bg-slate-900/90 border border-emerald-500/40 text-emerald-300 text-[10px] font-semibold px-2 py-0.5 rounded-md shadow-md backdrop-blur-sm pointer-events-none">
          Origin: ${name}
        </div>
      </div>
    `,
    iconSize: [40, 40],
    iconAnchor: [20, 20],
  });

const createDestIcon = (name: string) =>
  L.divIcon({
    className: 'custom-leaflet-icon',
    html: `
      <div class="relative flex items-center justify-center group cursor-pointer">
        <div class="absolute -inset-1.5 rounded-full bg-indigo-500/40 animate-pulse"></div>
        <div class="w-10 h-10 rounded-xl bg-slate-900 border-2 border-indigo-500 shadow-lg shadow-indigo-500/30 flex items-center justify-center text-indigo-400">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
          </svg>
        </div>
        <div class="absolute -bottom-7 whitespace-nowrap bg-slate-900/90 border border-indigo-500/40 text-indigo-300 text-[10px] font-semibold px-2 py-0.5 rounded-md shadow-md backdrop-blur-sm pointer-events-none">
          Job Site: ${name}
        </div>
      </div>
    `,
    iconSize: [40, 40],
    iconAnchor: [20, 20],
  });

const createVehicleIcon = (heading: number, speed: number) =>
  L.divIcon({
    className: 'custom-leaflet-icon',
    html: `
      <div class="relative flex items-center justify-center">
        <div class="absolute -inset-2 rounded-full bg-emerald-400/30 animate-ping"></div>
        <div class="w-9 h-9 rounded-full bg-slate-950 border-2 border-emerald-400 shadow-xl shadow-emerald-500/50 flex items-center justify-center text-emerald-400 transform transition-transform duration-200" style="transform: rotate(${heading}deg);">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2L4.5 20.29l.71.71L12 18l6.79 3 .71-.71z"/>
          </svg>
        </div>
        <div class="absolute -top-6 whitespace-nowrap bg-emerald-950/90 border border-emerald-500/50 text-emerald-300 text-[9px] font-mono font-bold px-1.5 py-0.5 rounded shadow">
          ${Math.round(speed)} km/h
        </div>
      </div>
    `,
    iconSize: [36, 36],
    iconAnchor: [18, 18],
  });

const createFleetTechIcon = (tech: ExtendedTechnicianData) => {
  const isPaid = tech.status === 'On Paid Job';
  const isLeave = tech.status === 'On Holiday/Leave';
  const color = isPaid ? 'bg-emerald-600 border-emerald-400 text-white' : isLeave ? 'bg-amber-600 border-amber-300 text-white' : 'bg-blue-600 border-blue-300 text-white';

  return L.divIcon({
    className: 'custom-leaflet-icon',
    html: `
      <div class="relative flex items-center justify-center group cursor-pointer">
        <div class="w-8 h-8 rounded-full ${color} border-2 shadow-lg flex items-center justify-center font-bold text-[11px] font-mono">
          ${tech.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
        </div>
        <div class="absolute -bottom-6 whitespace-nowrap bg-slate-900/90 text-white border border-slate-700 text-[10px] font-bold px-1.5 py-0.5 rounded shadow pointer-events-none">
          ${tech.name}
        </div>
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });
};

const createStopBadgeIcon = (label: string, durationMin: number, isAnomaly: boolean) => {
  const borderClass = isAnomaly ? 'border-rose-500/70 text-rose-300 bg-rose-950/90' : 'border-slate-700/80 text-slate-300 bg-slate-900/90';
  const pulseDot = isAnomaly ? '<span class="w-2 h-2 rounded-full bg-rose-400 animate-ping mr-1"></span>' : '<span class="w-2 h-2 rounded-full bg-emerald-400 mr-1"></span>';
  return L.divIcon({
    className: 'custom-leaflet-icon',
    html: `
      <div class="flex items-center ${borderClass} border px-2 py-0.5 rounded-full shadow-lg backdrop-blur-md text-[11px] font-medium whitespace-nowrap">
        ${pulseDot}
        <span>${label} (${Math.round(durationMin)}m)</span>
      </div>
    `,
    iconSize: [120, 24],
    iconAnchor: [60, 12],
  });
};

const createAnomalyIcon = (_type: string, durationMin: number) =>
  L.divIcon({
    className: 'custom-leaflet-icon',
    html: `
      <div class="relative flex items-center justify-center group cursor-pointer">
        <div class="absolute -inset-2 rounded-full bg-rose-500/40 animate-ping"></div>
        <div class="w-8 h-8 rounded-full bg-rose-950 border-2 border-rose-500 shadow-lg shadow-rose-500/40 flex items-center justify-center text-rose-300">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
          </svg>
        </div>
        <div class="absolute -bottom-6 whitespace-nowrap bg-rose-950/90 border border-rose-500/50 text-rose-200 text-[10px] font-bold px-2 py-0.5 rounded shadow">
          ⚠️ ${Math.round(durationMin)}m Unauth Stop
        </div>
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });

// ---------------------------------------------------------------------------
// MapController Component (Bounds Fitting, Pan/Zoom & Invalidation)
// ---------------------------------------------------------------------------

interface MapControllerProps {
  bounds: LatLngBoundsExpression | null;
  targetFocus: GeoPoint | null;
}

const MapController: React.FC<MapControllerProps> = ({ bounds, targetFocus }) => {
  const map = useMap();

  useEffect(() => {
    const timer = setTimeout(() => {
      map.invalidateSize();
    }, 250);
    return () => clearTimeout(timer);
  }, [map]);

  useEffect(() => {
    if (bounds) {
      map.fitBounds(bounds, { padding: [60, 60], maxZoom: 14 });
    }
  }, [bounds, map]);

  useEffect(() => {
    if (targetFocus) {
      map.flyTo([targetFocus.lat, targetFocus.lng], 15, {
        duration: 1.2,
        easeLinearity: 0.25,
      });
    }
  }, [targetFocus, map]);

  return null;
};

// ---------------------------------------------------------------------------
// Main RouteInspectorMap Component
// ---------------------------------------------------------------------------

export interface RouteInspectorMapProps {
  routeData: RouteResponse;
  selectedAnomalyLocation?: GeoPoint | null;
  onSelectCluster?: (cluster: Cluster5km) => void;
  onSelectTechnician?: (techId: string) => void;
  theme?: 'bright' | 'dark';
  className?: string;
}

export const RouteInspectorMap: React.FC<RouteInspectorMapProps> = ({
  routeData,
  selectedAnomalyLocation,
  onSelectCluster,
  onSelectTechnician,
  theme = 'bright',
  className = '',
}) => {
  const [mapMode, setMapMode] = useState<'ROUTE' | 'FLEET'>('ROUTE');

  const polylineCoords = routeData.route_polyline || [];
  const totalPoints = polylineCoords.length;

  // Playback state
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1);
  const [targetFocus, setTargetFocus] = useState<GeoPoint | null>(null);

  // Sync external anomaly selection to map focus
  useEffect(() => {
    if (selectedAnomalyLocation) {
      setTargetFocus(selectedAnomalyLocation);
    }
  }, [selectedAnomalyLocation]);

  // Compute bounding box encompassing polyline and clusters
  const bounds = useMemo<LatLngBoundsExpression | null>(() => {
    if (mapMode === 'FLEET') {
      const fleetPoints: [number, number][] = KRONE_FLEET_MASTER.map(t => [t.punchCoordinates[0], t.punchCoordinates[1]]);
      return L.latLngBounds(fleetPoints);
    }

    const points: [number, number][] = [...polylineCoords];
    routeData.clusters_5km.forEach((c) => {
      points.push([c.centroid.lat, c.centroid.lng]);
    });
    if (points.length === 0) return null;
    return L.latLngBounds(points);
  }, [polylineCoords, routeData.clusters_5km, mapMode]);

  // Animation playback interval timer
  useEffect(() => {
    if (!isPlaying) return;

    const intervalMs = Math.max(40, Math.floor(400 / playbackSpeed));
    const timer = setInterval(() => {
      setCurrentIndex((prev) => {
        if (prev >= totalPoints - 1) {
          setIsPlaying(false);
          return totalPoints - 1;
        }
        return prev + 1;
      });
    }, intervalMs);

    return () => clearInterval(timer);
  }, [isPlaying, totalPoints, playbackSpeed]);

  // Calculate current vehicle location, speed, and heading
  const currentCoord = polylineCoords[currentIndex] || polylineCoords[0] || [30.901, 75.8573];
  const nextCoord = polylineCoords[Math.min(currentIndex + 1, totalPoints - 1)];

  const headingDeg = useMemo(() => {
    if (!nextCoord || !currentCoord) return 0;
    const dy = nextCoord[0] - currentCoord[0];
    const dx = Math.cos((currentCoord[0] * Math.PI) / 180) * (nextCoord[1] - currentCoord[1]);
    const angle = (Math.atan2(dx, dy) * 180) / Math.PI;
    return (angle + 360) % 360;
  }, [currentCoord, nextCoord]);

  // Subdivided polyline for progress visualization
  const traveledPolyline = useMemo(() => {
    return polylineCoords.slice(0, currentIndex + 1);
  }, [polylineCoords, currentIndex]);

  // Telemetry HUD metadata
  const currentSpeed = isPlaying ? 55 + (currentIndex % 15) : 0;
  const progressPercent = totalPoints > 1 ? Math.round((currentIndex / (totalPoints - 1)) * 100) : 0;
  const coveredKm = ((routeData.journey_summary.total_distance_km * progressPercent) / 100).toFixed(1);

  const startLoc = routeData.journey_summary?.start_location || (routeData as any).start_location || { lat: 30.901, lng: 75.8573, name: 'Ludhiana Hub' };
  const destLoc = routeData.journey_summary?.destination || (routeData as any).destination_location || { lat: 30.3753, lng: 76.7821, name: 'Job Site' };

  const isDark = theme === 'dark';
  const cardBg = isDark ? 'bg-[#0B121E] border-slate-800 text-white' : 'bg-white border-slate-200 text-slate-900 shadow-sm';

  return (
    <div className={`rounded-2xl border overflow-hidden ${cardBg} ${className}`}>
      {/* Top Header Bar */}
      <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-emerald-100 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-400">
            <Navigation className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-extrabold text-sm sm:text-base">
                {mapMode === 'ROUTE' ? 'Autonomous Route Inspector' : 'All-India Fleet Telematics Radar'}
              </h3>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                5 KM GEOFENCE ENGINE
              </span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              {mapMode === 'ROUTE'
                ? `${routeData.technician_name} (${routeData.technician_id}) • Vehicle: Bolero Camper 4x4`
                : '14 Field Engineers across Punjab, Haryana, UP, MP, AP & Maharashtra'}
            </p>
          </div>
        </div>

        {/* Mode Selector Toggle */}
        <div className="flex items-center gap-2">
          <div className="inline-flex p-1 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs">
            <button
              onClick={() => setMapMode('ROUTE')}
              className={`px-3 py-1.5 rounded-lg font-bold transition-all cursor-pointer ${
                mapMode === 'ROUTE'
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
              }`}
            >
              Route Inspector
            </button>
            <button
              onClick={() => setMapMode('FLEET')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-bold transition-all cursor-pointer ${
                mapMode === 'FLEET'
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
              }`}
            >
              <Users className="w-3.5 h-3.5" />
              <span>Fleet Radar (14 Techs)</span>
            </button>
          </div>
        </div>
      </div>

      {/* Map Canvas Container */}
      <div className="relative w-full h-[520px] bg-slate-100">
        <MapContainer
          center={[startLoc.lat, startLoc.lng]}
          zoom={10}
          scrollWheelZoom={true}
          className="w-full h-full z-0"
        >
          {/* OpenStreetMap Standard Tiles (Zero API Key, High Visibility Bright) */}
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            maxZoom={19}
          />

          <MapController bounds={bounds} targetFocus={targetFocus} />

          {/* MODE 1: FLEET RADAR — ALL TECHNICIANS PLOTTED */}
          {mapMode === 'FLEET' && (
            <>
              {KRONE_FLEET_MASTER.map((tech) => (
                <Marker
                  key={tech.id}
                  position={[tech.punchCoordinates[0], tech.punchCoordinates[1]]}
                  icon={createFleetTechIcon(tech)}
                >
                  <Popup>
                    <div className="p-1 min-w-[180px] text-xs">
                      <div className="font-bold text-slate-900 text-sm">{tech.name}</div>
                      <div className="text-[11px] text-emerald-600 font-semibold">{tech.role}</div>
                      <div className="mt-1 pt-1 border-t border-slate-200 space-y-1">
                        <div>Status: <span className="font-bold">{tech.status}</span></div>
                        <div>Clock In: <span className="font-mono">{tech.clockInTime}</span></div>
                        <div>Region: <span>{tech.region}</span></div>
                        {tech.todayJobId && (
                          <div className="text-emerald-700 font-mono font-bold">
                            Job: {tech.todayJobId}
                          </div>
                        )}
                        {tech.customerCompany && (
                          <div className="truncate text-slate-500">{tech.customerCompany}</div>
                        )}
                      </div>
                      {onSelectTechnician && (
                        <button
                          onClick={() => {
                            onSelectTechnician(tech.id);
                            setMapMode('ROUTE');
                          }}
                          className="mt-2 w-full px-2 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded text-[11px] font-bold flex items-center justify-center gap-1 cursor-pointer"
                        >
                          <span>Inspect Route</span>
                          <ArrowRight className="w-3 h-3" />
                        </button>
                      )}
                    </div>
                  </Popup>
                </Marker>
              ))}
            </>
          )}

          {/* MODE 2: ROUTE INSPECTOR — SELECTED TECHNICIAN ROUTE & 5KM GEOFENCES */}
          {mapMode === 'ROUTE' && (
            <>
              {/* 1. 5 km Geofence Operational Clusters */}
              {routeData.clusters_5km.map((cluster) => {
                const isJob = cluster.is_job_site || cluster.zone_type === 'CUSTOMER_SITE';
                const isUnauthorized = cluster.zone_type === 'UNAUTHORIZED_STOP' || cluster.zone_type === 'UNAUTHORIZED_3RD_PARTY';
                const strokeColor = isUnauthorized ? '#DC2626' : isJob ? '#4F46E5' : '#059669';
                const fillColor = isUnauthorized ? '#EF4444' : isJob ? '#6366F1' : '#10B981';

                return (
                  <React.Fragment key={cluster.cluster_id}>
                    <Circle
                      center={[cluster.centroid.lat, cluster.centroid.lng]}
                      radius={5000}
                      pathOptions={{
                        color: strokeColor,
                        fillColor: fillColor,
                        fillOpacity: 0.15,
                        weight: 2,
                        dashArray: isUnauthorized ? '4, 4' : '6, 6',
                      }}
                      eventHandlers={{
                        click: () => onSelectCluster && onSelectCluster(cluster),
                      }}
                    >
                      <Tooltip direction="top" offset={[0, -20]} opacity={0.95}>
                        <div className="text-xs font-sans">
                          <div className="font-bold text-slate-900">{cluster.location_name}</div>
                          <div className="text-[10px] text-slate-600">
                            Operational Zone (5 km Radius) • {Math.round(cluster.duration_minutes)}m Dwell
                          </div>
                        </div>
                      </Tooltip>
                    </Circle>

                    <Marker
                      position={[cluster.centroid.lat, cluster.centroid.lng]}
                      icon={createStopBadgeIcon(
                        cluster.location_name,
                        cluster.duration_minutes,
                        isUnauthorized
                      )}
                    />
                  </React.Fragment>
                );
              })}

              {/* 2. Full Planned Route Polyline */}
              {polylineCoords.length > 1 && (
                <Polyline
                  positions={polylineCoords}
                  pathOptions={{
                    color: '#64748B',
                    weight: 4,
                    opacity: 0.6,
                    dashArray: '8, 6',
                  }}
                />
              )}

              {/* 3. Traveled Live Route Polyline */}
              {traveledPolyline.length > 1 && (
                <Polyline
                  positions={traveledPolyline}
                  pathOptions={{
                    color: '#059669',
                    weight: 5,
                    opacity: 0.9,
                  }}
                />
              )}

              {/* 4. Origin & Destination Markers */}
              <Marker position={[startLoc.lat, startLoc.lng]} icon={createBaseIcon(startLoc.name || 'Base Depot')} />
              <Marker position={[destLoc.lat, destLoc.lng]} icon={createDestIcon(destLoc.name || 'Job Site')} />

              {/* 5. Live Moving Vehicle Marker */}
              {currentCoord && (
                <Marker
                  position={[currentCoord[0], currentCoord[1]]}
                  icon={createVehicleIcon(headingDeg, currentSpeed)}
                  zIndexOffset={1000}
                />
              )}
            </>
          )}
        </MapContainer>

        {/* Floating Telemetry HUD */}
        {mapMode === 'ROUTE' && (
          <div className="absolute top-4 right-4 z-[400] bg-white/95 dark:bg-slate-900/95 backdrop-blur-md p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-xl text-xs space-y-2 min-w-[200px]">
            <div className="flex items-center justify-between text-[11px] font-bold pb-1 border-b border-slate-200 dark:border-slate-800">
              <span className="text-slate-500">Live Telemetry</span>
              <span className="text-emerald-600 dark:text-emerald-400 flex items-center gap-1 font-mono">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                ACTIVE
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-[11px]">
              <div>
                <span className="text-slate-400 block text-[10px]">Speed</span>
                <span className="font-mono font-bold text-slate-800 dark:text-slate-100">{Math.round(currentSpeed)} km/h</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px]">Distance</span>
                <span className="font-mono font-bold text-slate-800 dark:text-slate-100">{coveredKm} / {routeData.journey_summary.total_distance_km} km</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px]">Progress</span>
                <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400">{progressPercent}%</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px]">Heading</span>
                <span className="font-mono font-bold text-slate-800 dark:text-slate-100">{Math.round(headingDeg)}°</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Route Playback Scrubber (Only in Route Mode) */}
      {mapMode === 'ROUTE' && (
        <div className="p-4 bg-slate-50 dark:bg-slate-900/90 border-t border-slate-200 dark:border-slate-800 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="p-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold transition shadow-sm cursor-pointer"
              title={isPlaying ? 'Pause' : 'Play Journey'}
            >
              {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            </button>
            <button
              onClick={() => {
                setIsPlaying(false);
                setCurrentIndex(0);
              }}
              className="p-2.5 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100 transition cursor-pointer"
              title="Reset"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
            <span className="text-xs font-mono font-bold text-slate-700 dark:text-slate-300 ml-2">
              Progress: {progressPercent}% ({coveredKm} km)
            </span>
          </div>

          <div className="flex-1 max-w-md mx-2">
            <input
              type="range"
              min={0}
              max={Math.max(0, totalPoints - 1)}
              value={currentIndex}
              onChange={(e) => {
                setIsPlaying(false);
                setCurrentIndex(Number(e.target.value));
              }}
              className="w-full accent-emerald-600 cursor-pointer"
            />
          </div>

          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-500 font-semibold">Speed:</span>
            {[1, 2, 4].map((spd) => (
              <button
                key={spd}
                onClick={() => setPlaybackSpeed(spd)}
                className={`px-2 py-1 rounded-md text-xs font-bold transition cursor-pointer ${
                  playbackSpeed === spd
                    ? 'bg-emerald-600 text-white'
                    : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700'
                }`}
              >
                {spd}x
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
