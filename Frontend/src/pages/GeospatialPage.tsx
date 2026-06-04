import React, { useState, useEffect, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { geoAPI } from '@/services/api';
import { toast } from 'sonner';
import { 
  Map as MapIcon, 
  Layers, 
  TrendingUp, 
  ShieldAlert, 
  DollarSign, 
  CloudRain, 
  MapPin, 
  Database,
  BarChart3,
  Search,
  Sparkles,
  Info
} from 'lucide-react';
import { MapContainer, TileLayer, Circle, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';

import 'leaflet/dist/leaflet.css';

// Component to dynamically adjust map center/bounds
const ChangeMapViewport = ({ center, zoom }: { center?: [number, number]; zoom?: number }) => {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.setView(center, zoom || map.getZoom(), { animate: true });
    }
  }, [center, zoom, map]);
  return null;
};

// Custom Marker for K-Means Clusters
const createClusterIcon = (size: number) => {
  return L.divIcon({
    className: 'custom-cluster-marker-container',
    html: `
      <div class="relative flex items-center justify-center">
        <span class="absolute inline-flex h-12 w-12 animate-ping rounded-full bg-indigo-500/20 opacity-60"></span>
        <div class="h-10 w-10 rounded-full bg-indigo-600 border-2 border-white shadow-lg text-white font-bold text-xs flex items-center justify-center">
          ${size}
        </div>
      </div>
    `,
    iconSize: [40, 40],
    iconAnchor: [20, 20],
  });
};

interface HeatmapPoint {
  lat: number;
  lng: number;
  weight: number;
}

interface WorkerCluster {
  latitude: number;
  longitude: number;
  size: number;
}

interface ParametricZone {
  id: string;
  name: string;
  center: {
    lat: number;
    lon: number;
  };
  radius_km: number;
}

interface ZoneStats {
  zone_id: string;
  total_workers: number;
  active_triggers_count: number;
  total_payout_amount: number;
  payouts_count: number;
}

const GeospatialPage = () => {
  // States
  const [activeTab, setActiveTab] = useState<'workers' | 'fraud' | 'triggers' | 'payouts'>('workers');
  const [showClusters, setShowClusters] = useState(true);
  const [showZones, setShowZones] = useState(true);
  const [selectedZoneId, setSelectedZoneId] = useState<string | null>(null);
  const [zoneStats, setZoneStats] = useState<ZoneStats | null>(null);
  const [loadingStats, setLoadingStats] = useState(false);

  // Default Map center: Ahmedabad coordinates
  const defaultCenter: [number, number] = [23.0225, 72.5714];

  // Queries
  const { data: workerHeatmap, isLoading: loadingWorkerHeat } = useQuery<HeatmapPoint[]>({
    queryKey: ['heatmap-workers'],
    queryFn: geoAPI.getWorkerHeatmap,
  });

  const { data: fraudHeatmap, isLoading: loadingFraudHeat } = useQuery<HeatmapPoint[]>({
    queryKey: ['heatmap-fraud'],
    queryFn: geoAPI.getFraudHeatmap,
  });

  const { data: triggerHeatmap, isLoading: loadingTriggerHeat } = useQuery<HeatmapPoint[]>({
    queryKey: ['heatmap-triggers'],
    queryFn: geoAPI.getTriggerHeatmap,
  });

  const { data: payoutHeatmap, isLoading: loadingPayoutHeat } = useQuery<HeatmapPoint[]>({
    queryKey: ['heatmap-payouts'],
    queryFn: geoAPI.getPayoutHeatmap,
  });

  const { data: clustersData, isLoading: loadingClusters } = useQuery<WorkerCluster[]>({
    queryKey: ['worker-clusters'],
    queryFn: geoAPI.getWorkerClusters,
  });

  const { data: zonesResponse, isLoading: loadingZones } = useQuery<{ data: ParametricZone[] }>({
    queryKey: ['parametric-zones'],
    queryFn: geoAPI.getAllZones,
  });

  const zones = zonesResponse?.data || [];

  // Fetch specific zone stats when selected
  useEffect(() => {
    if (selectedZoneId) {
      setLoadingStats(true);
      geoAPI.getZoneStats(selectedZoneId)
        .then(res => {
          setZoneStats(res);
        })
        .catch(err => {
          toast.error("Failed to load zone analytics");
        })
        .finally(() => setLoadingStats(false));
    } else {
      setZoneStats(null);
    }
  }, [selectedZoneId]);

  // Heatmap configuration selection
  const currentHeatmapData = useMemo(() => {
    switch (activeTab) {
      case 'workers': return workerHeatmap || [];
      case 'fraud': return fraudHeatmap || [];
      case 'triggers': return triggerHeatmap || [];
      case 'payouts': return payoutHeatmap || [];
      default: return [];
    }
  }, [activeTab, workerHeatmap, fraudHeatmap, triggerHeatmap, payoutHeatmap]);

  const heatmapConfig = useMemo(() => {
    switch (activeTab) {
      case 'workers':
        return {
          title: 'Worker Density Map',
          description: 'Aggregated location updates highlighting gig worker concentrations.',
          color: '#10b981', // emerald
          fillColor: '#10b981',
          radiusMultiplier: 250,
          kpiLabel: 'Tracked Workers Count',
          kpiVal: workerHeatmap?.length || 0,
        };
      case 'fraud':
        return {
          title: 'Fraud Hotspots (Anomalies)',
          description: 'Spatiotemporal spoofing indicators representing high risk GPS locations.',
          color: '#f43f5e', // rose
          fillColor: '#f43f5e',
          radiusMultiplier: 350,
          kpiLabel: 'Suspected Anomalies',
          kpiVal: fraudHeatmap?.length || 0,
        };
      case 'triggers':
        return {
          title: 'Parametric Weather Triggers',
          description: 'Atmospheric sensor breaches mapped to geographic centers.',
          color: '#f59e0b', // amber
          fillColor: '#f59e0b',
          radiusMultiplier: 400,
          kpiLabel: 'Trigger Incidents',
          kpiVal: triggerHeatmap?.length || 0,
        };
      case 'payouts':
        return {
          title: 'Insurance Payout Distribution',
          description: 'Volume and weight of Parametric cash releases across grids.',
          color: '#8b5cf6', // purple
          fillColor: '#8b5cf6',
          radiusMultiplier: 300,
          kpiLabel: 'Payout Nodes Mapped',
          kpiVal: payoutHeatmap?.length || 0,
        };
      default:
        return {
          title: 'Geospatial Analytics',
          description: '',
          color: '#3b82f6',
          fillColor: '#3b82f6',
          radiusMultiplier: 200,
          kpiLabel: 'Data Points',
          kpiVal: 0,
        };
    }
  }, [activeTab, workerHeatmap, fraudHeatmap, triggerHeatmap, payoutHeatmap]);

  // Center on first node of selected zone
  const activeCenter = useMemo(() => {
    if (selectedZoneId && zones.length > 0) {
      const activeZone = zones.find(z => z.id === selectedZoneId);
      if (activeZone?.center?.lat && activeZone?.center?.lon) {
        return [activeZone.center.lat, activeZone.center.lon] as [number, number];
      }
    }
    return defaultCenter;
  }, [selectedZoneId, zones]);

  const selectedZoneDetails = zones.find(z => z.id === selectedZoneId);

  return (
    <div className="p-4 md:p-6 space-y-6 animate-fade-in bg-background min-h-[calc(100vh-3.5rem)] flex flex-col">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <MapIcon className="h-6 w-6 text-primary" /> Geospatial Insights Dashboard
          </h1>
          <p className="text-sm text-muted-foreground">Spatial intelligence, K-Means clustering, and weather triggers mapping.</p>
        </div>

        {/* Tab Selector controls */}
        <div className="flex bg-muted p-1 rounded-lg border text-sm shrink-0 w-full md:w-auto">
          <button 
            onClick={() => setActiveTab('workers')}
            className={`flex-1 md:flex-initial flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md font-medium transition-colors ${activeTab === 'workers' ? 'bg-background text-foreground shadow' : 'text-muted-foreground hover:text-foreground'}`}
          >
            <TrendingUp className="h-4 w-4 text-emerald-500" /> Workers
          </button>
          <button 
            onClick={() => setActiveTab('fraud')}
            className={`flex-1 md:flex-initial flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md font-medium transition-colors ${activeTab === 'fraud' ? 'bg-background text-foreground shadow' : 'text-muted-foreground hover:text-foreground'}`}
          >
            <ShieldAlert className="h-4 w-4 text-rose-500" /> Fraud
          </button>
          <button 
            onClick={() => setActiveTab('triggers')}
            className={`flex-1 md:flex-initial flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md font-medium transition-colors ${activeTab === 'triggers' ? 'bg-background text-foreground shadow' : 'text-muted-foreground hover:text-foreground'}`}
          >
            <CloudRain className="h-4 w-4 text-amber-500" /> Triggers
          </button>
          <button 
            onClick={() => setActiveTab('payouts')}
            className={`flex-1 md:flex-initial flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md font-medium transition-colors ${activeTab === 'payouts' ? 'bg-background text-foreground shadow' : 'text-muted-foreground hover:text-foreground'}`}
          >
            <DollarSign className="h-4 w-4 text-violet-500" /> Payouts
          </button>
        </div>
      </div>

      {/* Grid: Map + Side statistics */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1">
        {/* Left Side: Map configuration + Filters */}
        <div className="lg:col-span-1 space-y-6 flex flex-col">
          {/* Controls Card */}
          <div className="rounded-xl border bg-card p-5 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
              <Layers className="h-4 w-4 text-primary" /> Map Configurations
            </h3>
            
            <div className="space-y-3 pt-2">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <label className="text-xs font-semibold text-foreground">K-Means Clusters</label>
                  <p className="text-[10px] text-muted-foreground">Plot spatial worker groups</p>
                </div>
                <input
                  type="checkbox"
                  checked={showClusters}
                  onChange={(e) => setShowClusters(e.target.checked)}
                  className="rounded border-input text-primary focus:ring-primary h-4 w-4 cursor-pointer accent-primary"
                />
              </div>

              <div className="flex items-center justify-between border-t pt-3">
                <div className="space-y-0.5">
                  <label className="text-xs font-semibold text-foreground">Parametric Zones</label>
                  <p className="text-[10px] text-muted-foreground">Outline coverage boundaries</p>
                </div>
                <input
                  type="checkbox"
                  checked={showZones}
                  onChange={(e) => setShowZones(e.target.checked)}
                  className="rounded border-input text-primary focus:ring-primary h-4 w-4 cursor-pointer accent-primary"
                />
              </div>
            </div>
          </div>

          {/* Stats Summary Card */}
          <div className="rounded-xl border bg-card p-5 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-primary" /> Layer Metrics
            </h3>
            <div className="space-y-3 pt-2">
              <div>
                <p className="text-[10px] uppercase font-bold text-muted-foreground">{heatmapConfig.kpiLabel}</p>
                <p className="text-2xl font-black text-foreground mt-0.5">
                  {heatmapConfig.kpiVal}
                </p>
              </div>
              <div className="border-t pt-3">
                <p className="text-[10px] uppercase font-bold text-muted-foreground">Clustering Centroids</p>
                <p className="text-2xl font-black text-foreground mt-0.5">
                  {loadingClusters ? '...' : clustersData?.length || 0}
                </p>
              </div>
              <div className="border-t pt-3">
                <p className="text-[10px] uppercase font-bold text-muted-foreground">Active Policy Zones</p>
                <p className="text-2xl font-black text-foreground mt-0.5">
                  {loadingZones ? '...' : zones.length}
                </p>
              </div>
            </div>
          </div>

          {/* Interactive Zone Inspector details */}
          <div className="rounded-xl border bg-card p-5 shadow-sm space-y-4 flex-1">
            <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
              <Info className="h-4 w-4 text-primary" /> Zone Inspector
            </h3>
            
            {!selectedZoneId ? (
              <p className="text-xs text-muted-foreground italic">
                Select a zone outline or marker on the map to inspect its real-time analytics.
              </p>
            ) : loadingStats ? (
              <div className="space-y-2 text-xs text-muted-foreground">
                <p>Loading telemetry stats...</p>
              </div>
            ) : zoneStats ? (
              <div className="space-y-4">
                <div>
                  <h4 className="text-xs uppercase font-bold text-muted-foreground">Selected Grid</h4>
                  <p className="text-sm font-bold text-primary">{selectedZoneDetails?.name || selectedZoneId}</p>
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="bg-muted/40 p-2.5 rounded-lg border">
                    <span className="text-[10px] text-muted-foreground block font-medium">Workers</span>
                    <span className="text-base font-bold text-foreground">{zoneStats.total_workers}</span>
                  </div>
                  <div className="bg-muted/40 p-2.5 rounded-lg border">
                    <span className="text-[10px] text-muted-foreground block font-medium">Breaches</span>
                    <span className="text-base font-bold text-foreground">{zoneStats.active_triggers_count}</span>
                  </div>
                  <div className="bg-muted/40 p-2.5 rounded-lg border col-span-2">
                    <span className="text-[10px] text-muted-foreground block font-medium">Total Paid Out</span>
                    <span className="text-base font-bold text-emerald-500">₹{zoneStats.total_payout_amount.toLocaleString('en-IN')}</span>
                  </div>
                </div>

                <div className="text-[10px] text-muted-foreground border-t pt-3 flex flex-col gap-1">
                  <div className="flex justify-between">
                    <span>Payouts Cleared:</span>
                    <span className="font-semibold text-foreground">{zoneStats.payouts_count} items</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Radius Limit:</span>
                    <span className="font-semibold text-foreground">{selectedZoneDetails?.radius_km} km</span>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-xs text-rose-500">Failed to load zone details.</p>
            )}
          </div>
        </div>

        {/* Right Side: Map Container */}
        <div className="lg:col-span-3 rounded-xl border overflow-hidden relative shadow-md bg-slate-950 min-h-[500px]">
          <MapContainer 
            center={defaultCenter} 
            zoom={12} 
            style={{ height: '100%', width: '100%' }}
            zoomControl={false}
          >
            {/* Custom dark map layout */}
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            />

            {/* Dynamic viewport adjustments */}
            <ChangeMapViewport center={activeCenter} />

            {/* 1. Heatmap layer nodes representation (SVG Circle representation) */}
            {currentHeatmapData.map((pt, idx) => (
              <Circle
                key={`heatmap-${activeTab}-${idx}`}
                center={[pt.lat, pt.lng]}
                radius={pt.weight * heatmapConfig.radiusMultiplier}
                pathOptions={{
                  color: heatmapConfig.color,
                  fillColor: heatmapConfig.fillColor,
                  fillOpacity: pt.weight * 0.45,
                  weight: 1.5,
                  opacity: pt.weight * 0.7,
                }}
              >
                <Popup>
                  <div className="p-1 text-slate-800 text-xs">
                    <p className="font-bold uppercase text-xs">{activeTab} Intensity</p>
                    <p>Weight: {(pt.weight * 100).toFixed(1)}%</p>
                  </div>
                </Popup>
              </Circle>
            ))}

            {/* 2. K-Means Cluster overlay */}
            {showClusters && !loadingClusters && clustersData && clustersData.map((c, idx) => (
              <Marker 
                key={`cluster-${idx}`} 
                position={[c.latitude, c.longitude]} 
                icon={createClusterIcon(c.size)}
              >
                <Popup>
                  <div className="p-2 text-slate-800 text-xs">
                    <p className="font-bold">K-Means Cluster Center</p>
                    <p>Group Size: {c.size} active workers</p>
                    <p className="text-[10px] text-muted-foreground mt-1">Coordinates: {c.latitude.toFixed(4)}, {c.longitude.toFixed(4)}</p>
                  </div>
                </Popup>
              </Marker>
            ))}

            {/* 3. Parametric Zones overlay */}
            {showZones && !loadingZones && zones.map(z => {
              if (!z.center?.lat || !z.center?.lon) return null;
              
              const active = selectedZoneId === z.id;
              
              return (
                <React.Fragment key={z.id}>
                  {/* Outer zone circle limit */}
                  <Circle
                    center={[z.center.lat, z.center.lon]}
                    radius={z.radius_km * 1000} // radius in meters
                    pathOptions={{
                      color: active ? '#6366f1' : '#475569',
                      fillColor: active ? '#6366f1' : '#475569',
                      fillOpacity: active ? 0.15 : 0.03,
                      weight: active ? 3.0 : 1.5,
                      dashArray: active ? 'none' : '4, 6',
                    }}
                    eventHandlers={{
                      click: () => setSelectedZoneId(z.id)
                    }}
                  />
                  {/* Small zone center pin */}
                  <Marker
                    position={[z.center.lat, z.center.lon]}
                    icon={L.divIcon({
                      className: 'zone-center-icon',
                      html: `
                        <div class="flex h-5 w-5 items-center justify-center rounded-full bg-slate-800 border border-slate-600 shadow">
                          <div class="h-2 w-2 rounded-full ${active ? 'bg-indigo-500' : 'bg-slate-400'}"></div>
                        </div>
                      `,
                      iconSize: [20, 20],
                      iconAnchor: [10, 10],
                    })}
                    eventHandlers={{
                      click: () => setSelectedZoneId(z.id)
                    }}
                  />
                </React.Fragment>
              );
            })}
          </MapContainer>

          {/* Floating explanation label */}
          <div className="absolute bottom-4 left-4 z-[1000] bg-slate-950/80 backdrop-blur-md border border-slate-800 rounded-lg p-3 text-white max-w-[280px]">
            <h4 className="text-xs font-bold mb-1 flex items-center gap-1">
              <Sparkles className="h-3.5 w-3.5 text-primary" /> {heatmapConfig.title}
            </h4>
            <p className="text-[10px] text-slate-300 leading-relaxed">
              {heatmapConfig.description}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GeospatialPage;
