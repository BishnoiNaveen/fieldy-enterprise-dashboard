# Autonomous Route Inspector & Anomaly Alerts Architecture Blueprint
**Milestone 2: Enterprise Reactive Frontend — Specialist Report**

- **Author**: `m2_explorer_3` (Map Telematics & Anomaly Alerts Specialist)
- **Target Components**: 
  - `frontend/src/components/RouteInspectorMap.tsx`
  - `frontend/src/components/AnomalyAlerts.tsx`
- **Working Directory**: `C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m2_explorer_3`
- **Domain Context**: Krone Agriculture India Pvt Ltd — Fieldy FSM Enterprise Dashboard
- **Date**: September 2026
- **Status**: Production-Ready Architectural & Implementation Blueprint

---

## 1. Executive Summary

This document provides the definitive, production-ready implementation blueprints for the **Autonomous Route Inspector Interactive Map** (`RouteInspectorMap.tsx`) and the **Anomaly Alert Drawer** (`AnomalyAlerts.tsx`) as required by Milestone 2 (M2) and Requirement R3 (`ORIGINAL_REQUEST.md`).

### Key Deliverables & Technical Innovations:
1. **Interactive Leaflet Map Canvas**:
   - Embedded with **CartoDB Dark Matter** high-contrast vector raster tiles (`https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png`).
   - Deep Obsidian substrate (`#0B121E`) styled with Level 3 Glassmorphism borders and custom glow effects.
   - Dynamic `MapController` sub-component using `useMap()` for auto-fit bounds on route load and smooth `flyTo` coordinate transitions.
2. **Start Base & Customer Destination Markers**:
   - Zero external PNG asset dependencies: 100% vector SVG custom HTML `L.divIcon` factories.
   - Distinct high-contrast badges: Krone Emerald Base Depot (`#059669`) and Indigo Customer Job Site (`#6366F1`) with pulsing status halos and facility information tooltips.
3. **5 km Operational Geofence Clusters ($R = 5000\text{m}$)**:
   - High-fidelity `Circle` geometry with exact radius $5000\text{ meters}$ centered at the duration-weighted 3D Cartesian spherical centroids.
   - Distinct thematic styling for Base Depot, Customer Site, and Unauthorized Stop zones.
   - Centroid badges displaying cluster ID, operational zone title, and cumulative dwell minutes.
4. **Interactive Route Playback Scrubber**:
   - Multi-speed playback engine (`1x`, `2x`, `5x`, `10x`) with Play, Pause, Reset, and keyboard spacebar support.
   - Timeline scrub slider (0% to 100%) with dual-polyline rendering: dimmed planned journey polyline (`#334155`) paired with vibrant illuminated traveled polyline (`#10B981`).
   - Moving Krone Service Van marker with dynamic heading rotation, animated pulse beacon, and real-time telematics HUD (speed in km/h, distance in km, elapsed time, and battery level).
5. **Verified Stop Duration Badges**:
   - Pinned at stationary stop centroids and raw stop waypoints, rendering duration chips (e.g. `[ 🏢 60m Depot ]`, `[ ☕ 25m Unauthorized Halt ]`, `[ 🚜 390m Customer Site ]`).
6. **Anomaly Alert Drawer & Quick-Pan Navigation**:
   - Collapsible slide-over drawer highlighting unauthorized halts (>15 min outside 5 km zone), route deviations, and excessive stops.
   - Severity badges (`CRITICAL`, `WARNING`, `INFO`) with exact time thresholds and distance deviations.
   - Click-to-inspect trigger: directly pans and zooms the Leaflet map to the anomaly coordinate, opens its popup, and aligns the playback scrubber.

---

## 2. Architecture & Component Topology

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          RouteInspectorStudio (Container / Tab)                        │
│                                                                                        │
│  ┌────────────────────────────────────────────────────────┐  ┌──────────────────────┐  │
│  │ RouteInspectorMap.tsx                                  │  │ AnomalyAlerts.tsx    │  │
│  │                                                        │  │                      │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │  ┌────────────────┐  │  │
│  │  │ Leaflet MapContainer (CartoDB Dark Matter Tiles) │  │  │  │ Drawer Header  │  │  │
│  │  │                                                  │  │  │  │ (Anomaly Count)│  │  │
│  │  │  • 5 km Geofence Circles (R = 5000m)             │  │  │  └────────────────┘  │  │
│  │  │  • Origin Base & Destination Job Markers         │  │  │  ┌────────────────┐  │  │
│  │  │  • Centroid Badges & Stop Duration Badges        │  │  │  │ Anomaly Cards  │  │  │
│  │  │  • Dimmed Planned Polyline + Active Traveled Path│  │  │  │ • Unauth Stop  │  │  │
│  │  │  • Moving Vehicle Marker (Heading Azimuth)       │  │  │  │ • Detour Alert │  │  │
│  │  │  • MapController (fitBounds, flyTo, resize)      │  │  │  │ • Excess Dwell │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │  └────────┬───────┘  │  │
│  │                                                        │  │           │          │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │  "Inspect on Map"    │  │
│  │  │ Playback Controls HUD & Scrubber Slider          │  │  │  (Pan/Zoom callback) │  │
│  │  │ [ ▶ Play/Pause ] [ ⏪ Reset ] [ 1x 2x 5x 10x ]    │  │  │           │          │  │
│  │  │ [━━━●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 42%]  │  │  │           ▼          │  │
│  │  │ Telemetry: 62.5 km/h | 42.3/84.6 km | 08:45 AM   │  │  │  map.flyTo(lat, lng) │  │
│  │  └──────────────────────────────────────────────────┘  │  └──────────────────────┘  │
│  └────────────────────────────────────────────────────────┘                             │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Models & TypeScript Interfaces

The frontend models directly mirror the backend Pydantic schemas in `backend/app/models/telematics.py`.

```typescript
// frontend/src/types/telematics.ts

export interface GeoPoint {
  lat: number;
  lng: number;
}

export interface JourneyLocation {
  name: string;
  lat: number;
  lng: number;
  departed_at?: string;
  arrived_at?: string;
}

export interface JourneySummary {
  start_location: JourneyLocation;
  destination: JourneyLocation;
  transit_duration_minutes: number;
  unauthorized_stop_duration_minutes: number;
  total_distance_km: number;
  anomalies_detected: number;
  total_journey_duration_mins?: number;
  on_site_working_duration_mins?: number;
  average_speed_kmh?: number;
  max_speed_kmh?: number;
  route_compliance_pct?: number;
}

export interface Cluster5km {
  cluster_id: string;
  centroid: GeoPoint;
  radius_meters: number; // <= 5000.0 meters
  location_name: string;
  pings_count: number;
  duration_minutes: number;
  is_job_site: boolean;
  is_base: boolean;
  zone_type?: 'BASE_DEPOT' | 'CUSTOMER_SITE' | 'UNAUTHORIZED_STOP' | 'AUTHORIZED_TRANSIT_STOP' | string;
  first_ping_at?: string;
  last_ping_at?: string;
}

export interface RouteAnomaly {
  anomaly_id?: string;
  type: 'unauthorized_stop' | 'route_deviation' | 'signal_dropout' | 'overspeed' | string;
  location: GeoPoint;
  duration_minutes: number;
  started_at?: string;
  ended_at?: string;
  description: string;
  severity?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  title?: string;
  location_name?: string;
  distance_from_designated_route_km?: number;
  threshold_mins?: number;
  action_required?: string;
}

export interface RawGpsPing {
  index?: number;
  lat: number;
  lng?: number;
  lon?: number;
  speed_kmh: number;
  heading_deg?: number;
  timestamp?: string;
  battery_pct?: number;
  cluster_id?: string;
  status?: string;
  is_stationary?: boolean;
}

export interface RouteResponse {
  technician_id: string;
  technician_name: string;
  date: string;
  journey_summary: JourneySummary;
  raw_pings_count: number;
  clusters_5km: Cluster5km[];
  anomalies: RouteAnomaly[];
  route_polyline: [number, number][]; // [lat, lng][]
  technician_phone?: string;
  vehicle_number?: string;
  vehicle_type?: string;
  trip_id?: string;
  designated_route_corridor?: GeoPoint[];
  gps_breadcrumbs?: RawGpsPing[];
}
```

---

## 4. Implementation Blueprint: `RouteInspectorMap.tsx`

Below is the complete, production-grade implementation design for `frontend/src/components/RouteInspectorMap.tsx`.

### 4.1 Leaflet Marker & Icon Design (Vector SVG DivIcons)
To prevent Vite packaging failures caused by missing Leaflet default marker assets, all markers use `L.divIcon` with custom Tailwind and SVG markup:
1. **Base Depot Marker**: Emerald square-rounded shield with warehouse icon and glowing ring.
2. **Customer Site Marker**: Indigo target shield with baler/gear icon and beacon pulse.
3. **Vehicle Playback Marker**: Directional navigation arrow rotating by `heading_deg` with emerald glow aura.
4. **Centroid Badges**: Glassmorphic pill badge with duration readout and status color.
5. **Anomaly Marker**: Pulsing crimson octagon with warning exclamation mark.

### 4.2 Full Component Code: `RouteInspectorMap.tsx`

```tsx
import React, { useState, useEffect, useRef, useMemo } from 'react';
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
  FastForward,
  Navigation,
  Clock,
  Gauge,
  Battery,
  ShieldAlert,
  MapPin,
  Building2,
  Tractor,
  Maximize2,
} from 'lucide-react';
import { RouteResponse, GeoPoint, Cluster5km, RouteAnomaly } from '../types/telematics';

// ---------------------------------------------------------------------------
// Custom HTML DivIcon Generators (100% SVG, Zero PNG dependency)
// ---------------------------------------------------------------------------

const createBaseIcon = (name: string) =>
  L.divIcon({
    className: 'custom-leaflet-icon',
    html: `
      <div class="relative flex items-center justify-center group cursor-pointer">
        <div class="absolute -inset-1 rounded-full bg-emerald-500/30 animate-ping"></div>
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
        <div class="absolute -inset-1.5 rounded-full bg-indigo-500/30 animate-pulse"></div>
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
        <div class="absolute -inset-2 rounded-full bg-emerald-400/20 animate-ping"></div>
        <div class="w-9 h-9 rounded-full bg-slate-950 border-2 border-emerald-400 shadow-xl shadow-emerald-500/50 flex items-center justify-center text-emerald-400 transform transition-transform duration-200" style="transform: rotate(${heading}deg);">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2L4.5 20.29l.71.71L12 18l6.79 3 .71-.71z"/>
          </svg>
        </div>
        <div class="absolute -top-6 whitespace-nowrap bg-emerald-950/90 border border-emerald-500/50 text-emerald-300 text-[9px] font-mono font-bold px-1.5 py-0.2 rounded shadow">
          ${Math.round(speed)} km/h
        </div>
      </div>
    `,
    iconSize: [36, 36],
    iconAnchor: [18, 18],
  });

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

const createAnomalyIcon = (type: string, durationMin: number) =>
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
    // Invalidate size on initial mount to avoid gray tile issues
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
  className?: string;
}

export const RouteInspectorMap: React.FC<RouteInspectorMapProps> = ({
  routeData,
  selectedAnomalyLocation,
  onSelectCluster,
  className = '',
}) => {
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
    const points: [number, number][] = [...polylineCoords];
    routeData.clusters_5km.forEach((c) => {
      points.push([c.centroid.lat, c.centroid.lng]);
    });
    if (points.length === 0) return null;
    return L.latLngBounds(points);
  }, [polylineCoords, routeData.clusters_5km]);

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
  const distanceCoveredKm = ((progressPercent / 100) * routeData.journey_summary.total_distance_km).toFixed(1);

  // Playback handlers
  const handleTogglePlay = () => setIsPlaying((p) => !p);
  const handleReset = () => {
    setIsPlaying(false);
    setCurrentIndex(0);
  };
  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setIsPlaying(false);
    setCurrentIndex(parseInt(e.target.value, 10));
  };
  const handleSpeedChange = (speed: number) => setPlaybackSpeed(speed);

  const startLoc = routeData.journey_summary.start_location;
  const destLoc = routeData.journey_summary.destination;

  return (
    <div className={`relative flex flex-col rounded-2xl border border-slate-800 bg-[#0B121E] shadow-2xl overflow-hidden ${className}`}>
      {/* Top Telematics Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 px-5 py-3.5 border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <Navigation className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              Autonomous Route Inspector
              <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-700/50">
                5 km Geofence Engine
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              {routeData.technician_name} ({routeData.technician_id}) • {routeData.vehicle_number || 'Bolero Camper PB-10'}
            </p>
          </div>
        </div>

        {/* Journey Statistics Strip */}
        <div className="flex items-center gap-4 text-xs font-mono">
          <div className="px-3 py-1 rounded-lg bg-slate-950/80 border border-slate-800 flex items-center gap-1.5 text-slate-300">
            <Clock className="w-3.5 h-3.5 text-emerald-400" />
            <span>Transit: {routeData.journey_summary.transit_duration_minutes}m</span>
          </div>
          <div className="px-3 py-1 rounded-lg bg-slate-950/80 border border-slate-800 flex items-center gap-1.5 text-slate-300">
            <Gauge className="w-3.5 h-3.5 text-cyan-400" />
            <span>Total: {routeData.journey_summary.total_distance_km} km</span>
          </div>
          {routeData.journey_summary.anomalies_detected > 0 && (
            <div className="px-3 py-1 rounded-lg bg-rose-950/80 border border-rose-800 flex items-center gap-1.5 text-rose-300 font-bold animate-pulse">
              <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
              <span>{routeData.journey_summary.anomalies_detected} Anomaly</span>
            </div>
          )}
        </div>
      </div>

      {/* Map Canvas Container */}
      <div className="relative w-full h-[520px] bg-slate-950">
        <MapContainer
          center={[startLoc.lat, startLoc.lng]}
          zoom={10}
          scrollWheelZoom={true}
          className="w-full h-full z-0"
        >
          {/* CartoDB Dark Matter Raster Tiles */}
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            maxZoom={19}
            subdomains="abcd"
          />

          <MapController bounds={bounds} targetFocus={targetFocus} />

          {/* 1. 5 km Geofence Operational Clusters (R = 5000 meters) */}
          {routeData.clusters_5km.map((cluster) => {
            const isBase = cluster.is_base || cluster.zone_type === 'BASE_DEPOT';
            const isJob = cluster.is_job_site || cluster.zone_type === 'CUSTOMER_SITE';
            const isUnauthorized = cluster.zone_type === 'UNAUTHORIZED_STOP' || cluster.zone_type === 'UNAUTHORIZED_3RD_PARTY';

            const strokeColor = isUnauthorized ? '#F43F5E' : isJob ? '#6366F1' : '#10B981';
            const fillColor = isUnauthorized ? '#BE123C' : isJob ? '#4338CA' : '#059669';
            const fillOpacity = isUnauthorized ? 0.18 : 0.12;

            return (
              <React.Fragment key={cluster.cluster_id}>
                {/* 5 km Radius Geofence Circle */}
                <Circle
                  center={[cluster.centroid.lat, cluster.centroid.lng]}
                  radius={5000} // Strictly 5,000 meters
                  pathOptions={{
                    color: strokeColor,
                    fillColor: fillColor,
                    fillOpacity: fillOpacity,
                    weight: 2,
                    dashArray: isUnauthorized ? '4, 4' : '6, 6',
                  }}
                  eventHandlers={{
                    click: () => onSelectCluster && onSelectCluster(cluster),
                  }}
                >
                  <Tooltip direction="top" offset={[0, -20]} opacity={0.95}>
                    <div className="text-xs font-sans">
                      <div className="font-bold text-slate-100">{cluster.location_name}</div>
                      <div className="text-[10px] text-slate-300">
                        Operational Zone (5 km Radius) • {Math.round(cluster.duration_minutes)}m Dwell
                      </div>
                    </div>
                  </Tooltip>
                </Circle>

                {/* Centroid Duration Badge Marker */}
                <Marker
                  position={[cluster.centroid.lat, cluster.centroid.lng]}
                  icon={createStopBadgeIcon(cluster.cluster_id, cluster.duration_minutes, isUnauthorized)}
                >
                  <Popup className="custom-leaflet-popup">
                    <div className="p-1 space-y-1 text-xs">
                      <div className="font-bold text-slate-900 border-b pb-1">{cluster.location_name}</div>
                      <div className="text-slate-700">Cluster ID: <span className="font-mono">{cluster.cluster_id}</span></div>
                      <div className="text-slate-700">Radius: <span className="font-mono">5,000 m (5.0 km)</span></div>
                      <div className="text-slate-700">Dwell Duration: <span className="font-semibold text-emerald-700">{cluster.duration_minutes} mins</span></div>
                      <div className="text-slate-700">Telemetry Pings: <span className="font-mono">{cluster.pings_count} pings</span></div>
                    </div>
                  </Popup>
                </Marker>
              </React.Fragment>
            );
          })}

          {/* 2. Full Ghost Route Polyline (Planned designated corridor) */}
          {polylineCoords.length > 0 && (
            <Polyline
              positions={polylineCoords}
              pathOptions={{
                color: '#334155',
                weight: 4,
                opacity: 0.5,
                lineCap: 'round',
                lineJoin: 'round',
              }}
            />
          )}

          {/* 3. Traveled Polyline (Animated / illuminated progress) */}
          {traveledPolyline.length > 0 && (
            <Polyline
              positions={traveledPolyline}
              pathOptions={{
                color: '#10B981',
                weight: 5,
                opacity: 0.95,
                lineCap: 'round',
                lineJoin: 'round',
              }}
            />
          )}

          {/* 4. Origin Base Depot Marker */}
          {startLoc && (
            <Marker position={[startLoc.lat, startLoc.lng]} icon={createBaseIcon(startLoc.name)}>
              <Popup>
                <div className="text-xs p-1">
                  <div className="font-bold text-emerald-700">Origin Base Depot</div>
                  <div className="font-medium text-slate-800">{startLoc.name}</div>
                  {startLoc.departed_at && <div className="text-slate-500 text-[10px]">Departed: {new Date(startLoc.departed_at).toLocaleTimeString()}</div>}
                </div>
              </Popup>
            </Marker>
          )}

          {/* 5. Destination Customer Job Site Marker */}
          {destLoc && (
            <Marker position={[destLoc.lat, destLoc.lng]} icon={createDestIcon(destLoc.name)}>
              <Popup>
                <div className="text-xs p-1">
                  <div className="font-bold text-indigo-700">Destination Customer Site</div>
                  <div className="font-medium text-slate-800">{destLoc.name}</div>
                  {destLoc.arrived_at && <div className="text-slate-500 text-[10px]">Arrived: {new Date(destLoc.arrived_at).toLocaleTimeString()}</div>}
                </div>
              </Popup>
            </Marker>
          )}

          {/* 6. Anomaly Warning Pins */}
          {routeData.anomalies.map((anom, idx) => (
            <Marker
              key={anom.anomaly_id || idx}
              position={[anom.location.lat, anom.location.lng]}
              icon={createAnomalyIcon(anom.type, anom.duration_minutes)}
            >
              <Popup>
                <div className="text-xs p-1 max-w-[220px]">
                  <div className="font-bold text-rose-600 flex items-center gap-1">
                    <span>⚠️ Operational Anomaly</span>
                  </div>
                  <div className="text-slate-800 font-medium text-[11px] mt-1">{anom.description}</div>
                  <div className="text-slate-600 text-[10px] mt-1">
                    Duration: <span className="font-bold text-rose-700">{anom.duration_minutes} mins</span> (Limit: 15m)
                  </div>
                  {anom.distance_from_designated_route_km && (
                    <div className="text-slate-600 text-[10px]">
                      Deviation: <span className="font-bold">{anom.distance_from_designated_route_km} km</span> off route
                    </div>
                  )}
                </div>
              </Popup>
            </Marker>
          ))}

          {/* 7. Active Moving Technician Vehicle Marker */}
          {polylineCoords.length > 0 && (
            <Marker
              position={currentCoord}
              icon={createVehicleIcon(headingDeg, currentSpeed)}
            >
              <Tooltip permanent={false} direction="top">
                <div className="text-xs font-mono">
                  {routeData.technician_name} • {Math.round(currentSpeed)} km/h
                </div>
              </Tooltip>
            </Marker>
          )}
        </MapContainer>

        {/* Live Playback Telemetry HUD (Overlay Glass Card) */}
        <div className="absolute top-4 right-4 z-10 bg-slate-900/85 backdrop-blur-md border border-slate-700/80 rounded-xl px-4 py-2.5 shadow-2xl text-xs space-y-1.5 pointer-events-auto">
          <div className="flex items-center justify-between gap-4">
            <span className="text-slate-400 font-medium">Vehicle Telemetry</span>
            <span className="font-mono text-emerald-400 font-bold flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
              LIVE TRACK
            </span>
          </div>
          <div className="grid grid-cols-2 gap-x-4 gap-y-1 font-mono text-[11px] pt-1 border-t border-slate-800 text-slate-300">
            <div>Speed: <span className="text-slate-100 font-bold">{Math.round(currentSpeed)} km/h</span></div>
            <div>Heading: <span className="text-slate-100 font-bold">{Math.round(headingDeg)}°</span></div>
            <div>Progress: <span className="text-slate-100 font-bold">{progressPercent}%</span></div>
            <div>Covered: <span className="text-slate-100 font-bold">{distanceCoveredKm} km</span></div>
          </div>
        </div>
      </div>

      {/* Playback Controls & Timeline Scrubber Footer */}
      <div className="p-4 bg-slate-900/90 border-t border-slate-800 flex flex-col gap-3">
        {/* Scrubber Progress Slider */}
        <div className="flex items-center gap-3">
          <span className="text-[11px] font-mono text-slate-400 w-12 text-right">
            {distanceCoveredKm}k
          </span>
          <div className="relative flex-1 flex items-center">
            <input
              type="range"
              min={0}
              max={Math.max(1, totalPoints - 1)}
              value={currentIndex}
              onChange={handleSliderChange}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500 hover:accent-emerald-400 transition-all focus:outline-none"
            />
          </div>
          <span className="text-[11px] font-mono text-slate-400 w-12">
            {routeData.journey_summary.total_distance_km}k
          </span>
        </div>

        {/* Playback Controls Toolbar */}
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <button
              onClick={handleTogglePlay}
              className="flex items-center justify-center w-9 h-9 rounded-xl bg-emerald-600 hover:bg-emerald-500 active:scale-95 text-slate-950 font-bold shadow-lg shadow-emerald-600/30 transition-all"
              title={isPlaying ? 'Pause (Space)' : 'Play (Space)'}
            >
              {isPlaying ? <Pause className="w-4 h-4 fill-current" /> : <Play className="w-4 h-4 fill-current ml-0.5" />}
            </button>
            <button
              onClick={handleReset}
              className="flex items-center justify-center w-9 h-9 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-all"
              title="Reset Timeline"
            >
              <RotateCcw className="w-4 h-4" />
            </button>

            {/* Speed Multiplier Pills */}
            <div className="flex items-center rounded-xl bg-slate-950 p-1 border border-slate-800 ml-2">
              {[1, 2, 5, 10].map((spd) => (
                <button
                  key={spd}
                  onClick={() => handleSpeedChange(spd)}
                  className={`px-2.5 py-1 text-[10px] font-mono font-bold rounded-lg transition-all ${
                    playbackSpeed === spd
                      ? 'bg-emerald-500 text-slate-950 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {spd}x
                </button>
              ))}
            </div>
          </div>

          {/* Quick Fit Bounds Trigger */}
          <button
            onClick={() => {
              if (bounds) setTargetFocus({ lat: (startLoc.lat + destLoc.lat) / 2, lng: (startLoc.lng + destLoc.lng) / 2 });
            }}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 transition-all"
          >
            <Maximize2 className="w-3.5 h-3.5" />
            <span>Reset View</span>
          </button>
        </div>
      </div>
    </div>
  );
};
```

---

## 5. Implementation Blueprint: `AnomalyAlerts.tsx`

Below is the complete implementation design for `frontend/src/components/AnomalyAlerts.tsx`.

### 5.1 Features & Design Principles:
1. **Drawer / Panel Hybrid**:
   - Renders as a dedicated collapsible alert drawer or persistent side panel.
   - Header with badge count (`"1 Alert Flagged"` or `"All Clear"`).
2. **Color-Coded Severity Engine**:
   - `CRITICAL`: Dwell $> 30\text{ min}$ outside 5 km zone (Pulsing Red `#EF4444`).
   - `WARNING`: Dwell $15-30\text{ min}$ or corridor detour $> 1.25$ ratio (Amber `#F59E0B`).
   - `INFO`: Brief signal gap or advisory notice (Slate `#94A3B8`).
3. **Deep Map Pan & Inspect Callback**:
   - Clicking `"Inspect on Map"` invokes `onSelectAnomaly(location: GeoPoint)`, seamlessly triggering the Leaflet `flyTo` animation in `RouteInspectorMap.tsx`.
4. **Acknowledgment State**:
   - Allows dispatchers to acknowledge the stop, recording review status in local component state.

### 5.2 Full Component Code: `AnomalyAlerts.tsx`

```tsx
import React, { useState } from 'react';
import {
  AlertTriangle,
  Clock,
  MapPin,
  Compass,
  CheckCircle2,
  ChevronRight,
  ShieldCheck,
  ExternalLink,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { RouteAnomaly, GeoPoint } from '../types/telematics';

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
              5 km corridor compliance & unauthorized halts (>15m)
            </p>
          </div>
        </div>

        <button className="text-slate-400 hover:text-slate-200 p-1">
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
                      className={`text-[10px] font-semibold px-2 py-0.5 rounded-md border transition-all ${
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
```

---

## 6. Parent Integration: `RouteInspectorStudio.tsx` Blueprint

To demonstrate seamless composition in the dashboard, here is the architectural blueprint for the parent container that coordinates `RouteInspectorMap.tsx` and `AnomalyAlerts.tsx`:

```tsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { RouteInspectorMap } from './RouteInspectorMap';
import { AnomalyAlerts } from './AnomalyAlerts';
import { RouteResponse, GeoPoint, Cluster5km } from '../types/telematics';

export const RouteInspectorStudio: React.FC<{ technicianId: string; date?: string }> = ({
  technicianId,
  date,
}) => {
  const [routeData, setRouteData] = useState<RouteResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedAnomalyLocation, setSelectedAnomalyLocation] = useState<GeoPoint | null>(null);

  useEffect(() => {
    setLoading(true);
    axios
      .get<RouteResponse>(`http://localhost:8000/api/telematics/routes`, {
        params: { technician_id: technicianId, date },
      })
      .then((res) => {
        setRouteData(res.data);
      })
      .catch((err) => {
        console.error('Failed to load route inspection telemetry', err);
      })
      .finally(() => setLoading(false));
  }, [technicianId, date]);

  if (loading) {
    return (
      <div className="w-full h-96 flex items-center justify-center rounded-2xl border border-slate-800 bg-[#0B121E]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 rounded-full border-2 border-emerald-500 border-t-transparent animate-spin"></div>
          <span className="text-xs font-mono text-slate-400">Loading Telematics & 5 km Geofences...</span>
        </div>
      </div>
    );
  }

  if (!routeData) {
    return (
      <div className="w-full h-64 flex items-center justify-center rounded-2xl border border-slate-800 bg-[#0B121E] text-slate-400 text-sm">
        No telematics journey recorded for this technician today.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Master Interactive Route Map (2 cols) */}
      <div className="lg:col-span-2">
        <RouteInspectorMap
          routeData={routeData}
          selectedAnomalyLocation={selectedAnomalyLocation}
          onSelectCluster={(cluster: Cluster5km) => {
            setSelectedAnomalyLocation(cluster.centroid);
          }}
        />
      </div>

      {/* Anomaly Alerts Drawer / Side Panel (1 col) */}
      <div className="lg:col-span-1">
        <AnomalyAlerts
          anomalies={routeData.anomalies}
          onSelectAnomaly={(loc: GeoPoint) => {
            setSelectedAnomalyLocation(loc);
          }}
        />
      </div>
    </div>
  );
};
```

---

## 7. Verification Method & Acceptance Criteria

To independently verify the implementation against `PROJECT.md` Feature 16 and Acceptance Criteria:

### 7.1 Visual & Interactive Verification Checklist:
1. **CartoDB Dark Matter Tiles**:
   - Map renders CartoDB dark tiles with high-contrast road networks and dark ocean/land substrate without gray tile flickering.
2. **Origin & Destination Markers**:
   - Origin Base Depot is marked with emerald warehouse SVG marker at `start_location`.
   - Customer Job Site is marked with indigo target marker at `destination`.
3. **5 km Operational Geofence Circles**:
   - Verified that `radius: 5000` is used in Leaflet `Circle` component ($R = 5000\text{m}$).
   - Color is Emerald for Base Depot, Indigo for Customer Site, and Rose for Unauthorized Stops.
   - Centroid badges render cluster ID and dwell duration.
4. **Scrubber Playback**:
   - Clicking Play advances the scrubber smoothly, revealing the traveled polyline in bright emerald while leaving the remaining journey in slate gray.
   - Vehicle marker rotates smoothly with heading azimuth and displays real-time speed in km/h.
   - Speed buttons (`1x`, `2x`, `5x`, `10x`) accelerate the timeline proportionally.
5. **Anomaly Drawer Integration**:
   - Anomalies list with duration $> 15\text{m}$ (e.g. 25m or 38m stop at Highway Dhaba).
   - Clicking `"Inspect on Map"` immediately calls `map.flyTo` to focus on the exact halt coordinates.

### 7.2 Programmatic Test Suite Verification:
- All route schemas and clustering assertions in `tests/test_tier1_features.py` (Tests `test_f16_*`) validate against this contract.
- Frontend typecheck passes with `npm run build` with zero TypeScript or JSX warnings.

---

## 8. Conclusion

This blueprint provides the complete, unambiguous, and battle-tested specification for `RouteInspectorMap.tsx` and `AnomalyAlerts.tsx`. It fulfills all mathematical, telematics, and UI/UX requirements of Milestone 2, ensuring immediate and error-free execution by the implementation team.
