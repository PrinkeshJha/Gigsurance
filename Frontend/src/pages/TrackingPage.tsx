import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { trackingAPI } from '@/services/api';
import { useAuth } from '@/hooks/useAuth';
import { toast } from 'sonner';
import { 
  MapPin, 
  Search, 
  Wifi, 
  WifiOff, 
  Play, 
  Pause, 
  Square, 
  RotateCcw, 
  Activity, 
  Clock, 
  User, 
  Navigation,
  Sparkles,
  ChevronRight,
  Filter,
  Eye
} from 'lucide-react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';

import 'leaflet/dist/leaflet.css';

// Custom SVG Icons for Leaflet
const createWorkerIcon = (name: string, isOnline: boolean, active: boolean) => {
  return L.divIcon({
    className: 'custom-worker-marker-container',
    html: `
      <div class="relative flex items-center justify-center">
        ${isOnline ? `<span class="absolute inline-flex h-8 w-8 animate-ping rounded-full bg-emerald-400 opacity-60"></span>` : ''}
        <div class="relative flex h-8 w-8 items-center justify-center rounded-full ${isOnline ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/30' : 'bg-slate-500 text-slate-100 shadow-lg shadow-slate-500/30'} ${active ? 'ring-4 ring-primary ring-offset-2' : ''} border-2 border-white transition-all duration-300">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-navigation"><polygon points="3 11 22 2 13 21 11 13 3 11"/></svg>
        </div>
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });
};

const createHistoryIcon = () => {
  return L.divIcon({
    className: 'custom-history-marker-container',
    html: `
      <div class="relative flex items-center justify-center">
        <div class="h-3 w-3 rounded-full bg-amber-500 border-2 border-white shadow shadow-amber-500/50"></div>
      </div>
    `,
    iconSize: [12, 12],
    iconAnchor: [6, 6],
  });
};

const createPlaybackIcon = () => {
  return L.divIcon({
    className: 'custom-playback-marker-container',
    html: `
      <div class="relative flex items-center justify-center">
        <span class="absolute inline-flex h-8 w-8 animate-ping rounded-full bg-primary opacity-70"></span>
        <div class="h-7 w-7 rounded-full bg-primary text-primary-foreground border-2 border-white shadow-lg flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-navigation"><polygon points="3 11 22 2 13 21 11 13 3 11"/></svg>
        </div>
      </div>
    `,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
  });
};

// Component to dynamically adjust map center/bounds
const ChangeMapViewport = ({ center, zoom, bounds }: { center?: [number, number]; zoom?: number; bounds?: L.LatLngBoundsExpression }) => {
  const map = useMap();
  useEffect(() => {
    if (bounds) {
      map.fitBounds(bounds, { padding: [50, 50], maxZoom: 16 });
    } else if (center) {
      map.setView(center, zoom || map.getZoom(), { animate: true });
    }
  }, [center, zoom, bounds, map]);
  return null;
};

interface LiveWorker {
  user_id: string;
  name: string;
  email: string;
  mobile: string;
  latitude: number;
  longitude: number;
  is_online: boolean;
  updated_at: string;
}

interface LocationPoint {
  latitude: number;
  longitude: number;
  session_id: string;
  timestamp: string;
}

const TrackingPage = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const socketRef = useRef<WebSocket | null>(null);

  // States
  const [liveWorkers, setLiveWorkers] = useState<Record<string, LiveWorker>>({});
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'online' | 'offline'>('all');
  const [offlineMinutes, setOfflineMinutes] = useState(10);
  const [selectedWorkerId, setSelectedWorkerId] = useState<string | null>(null);
  
  // Replay Session States
  const [sessions, setSessions] = useState<string[]>([]);
  const [selectedSessionId, setSelectedSessionId] = useState<string>('');
  const [historyPoints, setHistoryPoints] = useState<LocationPoint[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  
  // Playback Control States
  const [playbackIndex, setPlaybackIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1); // multiplier
  const playbackTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Default Map center: Ahmedabad coordinates
  const defaultCenter: [number, number] = [23.0225, 72.5714];

  // Fetch Rest live workers
  const { data: initialWorkers, isLoading: loadingRestWorkers } = useQuery({
    queryKey: ['live-workers'],
    queryFn: trackingAPI.getLiveWorkers,
  });

  // Fetch Offline workers
  const { data: offlineWorkers, refetch: refetchOffline } = useQuery({
    queryKey: ['offline-workers', offlineMinutes],
    queryFn: () => trackingAPI.getOfflineWorkers(offlineMinutes),
  });

  // Load initial workers into state
  useEffect(() => {
    if (initialWorkers) {
      const workersMap: Record<string, LiveWorker> = {};
      initialWorkers.forEach((w: any) => {
        workersMap[w.user_id] = {
          ...w,
          is_online: true
        };
      });
      // also merge offline workers
      if (offlineWorkers) {
        offlineWorkers.forEach((w: any) => {
          if (!workersMap[w.user_id]) {
            workersMap[w.user_id] = {
              ...w,
              is_online: false
            };
          }
        });
      }
      setLiveWorkers(workersMap);
    }
  }, [initialWorkers, offlineWorkers]);

  // WebSocket Live Stream Connection
  useEffect(() => {
    const connectWS = () => {
      const base = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
      const wsUrl = new URL('/ws/admin/live-map', base.replace(/^http/, 'ws'));
      const token = localStorage.getItem('gigsurance_token');
      if (token) {
        wsUrl.searchParams.set('token', token);
      }

      const socket = new WebSocket(wsUrl.toString());
      socketRef.current = socket;

      socket.onopen = () => {
        logger.info("Connected to live map WS");
      };

      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.event === 'worker_location_update') {
            const data = payload.data;
            setLiveWorkers(prev => ({
              ...prev,
              [data.user_id]: {
                user_id: data.user_id,
                name: data.name,
                email: prev[data.user_id]?.email || '',
                mobile: prev[data.user_id]?.mobile || '',
                latitude: data.latitude,
                longitude: data.longitude,
                is_online: data.is_online,
                updated_at: data.updated_at
              }
            }));
          } else if (payload.event === 'worker_status_update') {
            const data = payload.data;
            setLiveWorkers(prev => {
              if (prev[data.user_id]) {
                return {
                  ...prev,
                  [data.user_id]: {
                    ...prev[data.user_id],
                    is_online: data.is_online,
                    updated_at: data.updated_at
                  }
                };
              }
              return prev;
            });
          }
        } catch (err) {
          console.error("Error parsing WS packet", err);
        }
      };

      socket.onclose = () => {
        logger.info("WS tracking disconnected, reconnecting in 5s...");
        setTimeout(connectWS, 5000);
      };

      socket.onerror = () => {
        socket.close();
      };
    };

    connectWS();

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, []);

  // Fetch sessions when a worker is selected
  useEffect(() => {
    if (selectedWorkerId) {
      // Reset Replay States
      setSessions([]);
      setSelectedSessionId('');
      setHistoryPoints([]);
      setPlaybackIndex(0);
      setIsPlaying(false);

      trackingAPI.getWorkerSessions(selectedWorkerId)
        .then(res => {
          setSessions(res || []);
          if (res && res.length > 0) {
            setSelectedSessionId(res[0]);
          }
        })
        .catch(err => toast.error("Failed to load worker sessions"));
    }
  }, [selectedWorkerId]);

  // Fetch history when session changes
  useEffect(() => {
    if (selectedWorkerId && selectedSessionId) {
      setLoadingHistory(true);
      trackingAPI.getWorkerHistory(selectedWorkerId)
        .then(res => {
          // Filter by selected session
          const filtered = (res || []).filter((pt: any) => pt.session_id === selectedSessionId);
          setHistoryPoints(filtered);
          setPlaybackIndex(0);
          setIsPlaying(false);
        })
        .catch(err => toast.error("Failed to load session history"))
        .finally(() => setLoadingHistory(false));
    }
  }, [selectedWorkerId, selectedSessionId]);

  // Playback timer ticker
  useEffect(() => {
    if (isPlaying && historyPoints.length > 0) {
      const delay = 1000 / playbackSpeed;
      playbackTimerRef.current = setTimeout(() => {
        setPlaybackIndex(prev => {
          if (prev >= historyPoints.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, delay);
    }

    return () => {
      if (playbackTimerRef.current) {
        clearTimeout(playbackTimerRef.current);
      }
    };
  }, [isPlaying, playbackIndex, playbackSpeed, historyPoints]);

  // Calculations
  const filteredWorkers = useMemo(() => {
    return Object.values(liveWorkers).filter(w => {
      const matchSearch = w.name.toLowerCase().includes(searchTerm.toLowerCase()) || w.user_id.includes(searchTerm);
      const matchStatus = statusFilter === 'all' 
        ? true 
        : statusFilter === 'online' 
          ? w.is_online 
          : !w.is_online;
      return matchSearch && matchStatus;
    });
  }, [liveWorkers, searchTerm, statusFilter]);

  const selectedWorker = selectedWorkerId ? liveWorkers[selectedWorkerId] : null;

  const currentReplayPoint = useMemo(() => {
    if (historyPoints.length > 0 && playbackIndex < historyPoints.length) {
      return historyPoints[playbackIndex];
    }
    return null;
  }, [historyPoints, playbackIndex]);

  const mapViewportParams = useMemo(() => {
    if (currentReplayPoint) {
      return { center: [currentReplayPoint.latitude, currentReplayPoint.longitude] as [number, number], zoom: 16 };
    }
    if (selectedWorker) {
      return { center: [selectedWorker.latitude, selectedWorker.longitude] as [number, number], zoom: 15 };
    }
    // Calculate bounds containing all online workers
    const activeCoords = Object.values(liveWorkers)
      .filter(w => w.is_online && w.latitude && w.longitude)
      .map(w => [w.latitude, w.longitude] as [number, number]);

    if (activeCoords.length > 0) {
      const bounds = L.latLngBounds(activeCoords);
      return { bounds };
    }

    return { center: defaultCenter, zoom: 12 };
  }, [selectedWorker, currentReplayPoint, liveWorkers]);

  // Playback control handlers
  const handlePlayPause = () => {
    if (playbackIndex >= historyPoints.length - 1) {
      setPlaybackIndex(0);
    }
    setIsPlaying(!isPlaying);
  };

  const handleStop = () => {
    setIsPlaying(false);
    setPlaybackIndex(0);
  };

  const handleSpeedToggle = () => {
    const speeds = [1, 2, 5, 10];
    const currentIndex = speeds.indexOf(playbackSpeed);
    const nextIndex = (currentIndex + 1) % speeds.length;
    setPlaybackSpeed(speeds[nextIndex]);
  };

  return (
    <div className="h-[calc(100vh-3.5rem)] flex flex-col md:flex-row overflow-hidden bg-background">
      {/* ================= SIDE PANEL ================= */}
      <div className="w-full md:w-80 lg:w-96 border-r flex flex-col bg-card shrink-0 h-1/2 md:h-full z-10">
        <div className="p-4 border-b space-y-3">
          <div className="flex justify-between items-center">
            <h1 className="text-xl font-bold flex items-center gap-2 text-foreground">
              <Navigation className="h-5 w-5 text-primary rotate-45" /> Live GPS Tracking
            </h1>
            <div className="flex items-center gap-1.5 text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-500">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              WS Active
            </div>
          </div>
          
          {/* Search bar */}
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search by worker..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 text-sm rounded-lg border border-input bg-background focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>

          {/* Filter tabs */}
          <div className="flex gap-2 text-xs">
            <button 
              onClick={() => setStatusFilter('all')}
              className={`flex-1 py-1 rounded font-medium border transition-colors ${statusFilter === 'all' ? 'bg-primary text-primary-foreground border-primary' : 'bg-background hover:bg-muted text-muted-foreground'}`}
            >
              All ({Object.keys(liveWorkers).length})
            </button>
            <button 
              onClick={() => setStatusFilter('online')}
              className={`flex-1 py-1 rounded font-medium border transition-colors ${statusFilter === 'online' ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-500' : 'bg-background hover:bg-muted text-muted-foreground'}`}
            >
              Online ({Object.values(liveWorkers).filter(w => w.is_online).length})
            </button>
            <button 
              onClick={() => setStatusFilter('offline')}
              className={`flex-1 py-1 rounded font-medium border transition-colors ${statusFilter === 'offline' ? 'bg-slate-500/15 border-slate-500/30 text-slate-500' : 'bg-background hover:bg-muted text-muted-foreground'}`}
            >
              Offline ({Object.values(liveWorkers).filter(w => !w.is_online).length})
            </button>
          </div>
        </div>

        {/* Worker list */}
        <div className="flex-1 overflow-y-auto divide-y divide-border">
          {loadingRestWorkers ? (
            <div className="p-4 text-center text-sm text-muted-foreground">
              Loading worker database...
            </div>
          ) : filteredWorkers.length === 0 ? (
            <div className="p-4 text-center text-sm text-muted-foreground">
              No workers match the filters.
            </div>
          ) : (
            filteredWorkers.map(w => {
              const active = selectedWorkerId === w.user_id;
              return (
                <div 
                  key={w.user_id} 
                  onClick={() => setSelectedWorkerId(w.user_id)}
                  className={`p-3 flex items-start gap-3 cursor-pointer hover:bg-muted/40 transition-colors ${active ? 'bg-primary/5 border-l-4 border-primary' : ''}`}
                >
                  <div className={`mt-0.5 rounded-full p-1.5 ${w.is_online ? 'bg-emerald-500/10 text-emerald-500' : 'bg-slate-500/10 text-slate-500'}`}>
                    <User className="h-4 w-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-center">
                      <p className="text-sm font-semibold text-foreground truncate">{w.name}</p>
                      <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${w.is_online ? 'bg-emerald-500/10 text-emerald-500 font-semibold' : 'bg-slate-500/10 text-slate-500'}`}>
                        {w.is_online ? 'Online' : 'Offline'}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground truncate">{w.user_id}</p>
                    <p className="text-[10px] text-muted-foreground mt-1 flex items-center gap-1">
                      <Clock className="h-3 w-3" /> Last Active: {w.updated_at ? new Date(w.updated_at).toLocaleTimeString() : 'Never'}
                    </p>
                  </div>
                  <ChevronRight className="h-4 w-4 text-muted-foreground self-center shrink-0" />
                </div>
              );
            })
          )}
        </div>

        {/* Selected worker details & Session Replay control panel */}
        {selectedWorker && (
          <div className="p-4 border-t bg-muted/30 space-y-4">
            <div>
              <h3 className="text-sm font-bold text-foreground">Worker Replay Settings</h3>
              <p className="text-xs text-muted-foreground">{selectedWorker.name}</p>
            </div>

            {sessions.length === 0 ? (
              <p className="text-xs text-muted-foreground italic flex items-center gap-1">
                <Clock className="h-3.5 w-3.5" /> No historical trip sessions found.
              </p>
            ) : (
              <div className="space-y-3">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-muted-foreground">Select Session</label>
                  <select 
                    value={selectedSessionId} 
                    onChange={(e) => setSelectedSessionId(e.target.value)}
                    className="w-full p-2 text-xs rounded border border-input bg-background focus:outline-none"
                  >
                    {sessions.map(s => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </div>

                {historyPoints.length > 0 && (
                  <div className="space-y-2">
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-muted-foreground font-medium">Replay Progress</span>
                      <span className="text-foreground font-semibold">
                        {playbackIndex + 1} / {historyPoints.length} pts
                      </span>
                    </div>

                    <input 
                      type="range"
                      min={0}
                      max={historyPoints.length - 1}
                      value={playbackIndex}
                      onChange={(e) => {
                        setPlaybackIndex(Number(e.target.value));
                        setIsPlaying(false);
                      }}
                      className="w-full accent-primary h-1.5 bg-input rounded-lg cursor-pointer"
                    />

                    {/* Playback Controls */}
                    <div className="flex justify-between items-center bg-background rounded-lg border p-1.5">
                      <div className="flex gap-1">
                        <button 
                          onClick={handlePlayPause}
                          className="p-1.5 rounded hover:bg-muted text-foreground transition-colors"
                          title={isPlaying ? 'Pause' : 'Play'}
                        >
                          {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4 fill-current" />}
                        </button>
                        <button 
                          onClick={handleStop}
                          className="p-1.5 rounded hover:bg-muted text-foreground transition-colors"
                          title="Stop"
                        >
                          <Square className="h-4 w-4 fill-current text-rose-500" />
                        </button>
                      </div>

                      <button 
                        onClick={handleSpeedToggle}
                        className="px-2 py-1 text-xs font-bold bg-muted text-foreground hover:bg-muted/80 rounded transition-all shrink-0"
                        title="Change Replay Speed"
                      >
                        {playbackSpeed}x Speed
                      </button>
                    </div>

                    <div className="text-[10px] text-muted-foreground flex justify-between">
                      <span>Time: {currentReplayPoint ? new Date(currentReplayPoint.timestamp).toLocaleTimeString() : ''}</span>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* ================= MAP BOX ================= */}
      <div className="flex-1 relative h-1/2 md:h-full bg-slate-900">
        <MapContainer 
          center={defaultCenter} 
          zoom={12} 
          style={{ height: '100%', width: '100%' }}
          zoomControl={false}
        >
          {/* Custom style to make dark-themed map overlay */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />

          {/* Dynamic center shifting Component */}
          <ChangeMapViewport 
            center={mapViewportParams.center} 
            zoom={mapViewportParams.zoom} 
            bounds={mapViewportParams.bounds} 
          />

          {/* Render All Online / Offline Live Workers */}
          {Object.values(liveWorkers).map(w => {
            if (!w.latitude || !w.longitude) return null;
            
            // If this worker is selected and we are in active session replay mode, hide their live pin to avoid visual clutter
            const isReplaying = selectedWorkerId === w.user_id && historyPoints.length > 0;
            if (isReplaying) return null;

            return (
              <Marker 
                key={w.user_id} 
                position={[w.latitude, w.longitude]} 
                icon={createWorkerIcon(w.name, w.is_online, selectedWorkerId === w.user_id)}
                eventHandlers={{
                  click: () => setSelectedWorkerId(w.user_id)
                }}
              >
                <Popup className="custom-popup">
                  <div className="p-2 space-y-1 text-slate-800">
                    <p className="text-sm font-bold">{w.name}</p>
                    <p className="text-xs">ID: {w.user_id}</p>
                    <p className="text-xs">Mobile: {w.mobile}</p>
                    <p className="text-xs">Status: {w.is_online ? 'Online' : 'Offline'}</p>
                    <p className="text-[10px] text-muted-foreground">Updated: {w.updated_at ? new Date(w.updated_at).toLocaleString() : 'Never'}</p>
                  </div>
                </Popup>
              </Marker>
            );
          })}

          {/* Render Session Replay History Path */}
          {historyPoints.length > 0 && (
            <>
              {/* Polyline path */}
              <Polyline 
                positions={historyPoints.map(pt => [pt.latitude, pt.longitude])} 
                color="#6366f1"
                weight={4}
                opacity={0.8}
                dashArray="5, 10"
              />

              {/* Path node markers */}
              {historyPoints.map((pt, idx) => (
                <Marker 
                  key={`${pt.timestamp}-${idx}`} 
                  position={[pt.latitude, pt.longitude]} 
                  icon={createHistoryIcon()}
                >
                  <Popup>
                    <div className="p-1 text-slate-800 text-xs">
                      <p className="font-semibold">Node {idx + 1}</p>
                      <p>Time: {new Date(pt.timestamp).toLocaleTimeString()}</p>
                    </div>
                  </Popup>
                </Marker>
              ))}

              {/* Moving Playback Head */}
              {currentReplayPoint && (
                <Marker 
                  position={[currentReplayPoint.latitude, currentReplayPoint.longitude]}
                  icon={createPlaybackIcon()}
                >
                  <Popup>
                    <div className="p-1.5 text-slate-800 text-xs">
                      <p className="font-bold text-primary">{selectedWorker?.name}</p>
                      <p className="font-semibold">Current Playback Head</p>
                      <p>Time: {new Date(currentReplayPoint.timestamp).toLocaleTimeString()}</p>
                    </div>
                  </Popup>
                </Marker>
              )}
            </>
          )}
        </MapContainer>

        {/* Float Controls Overlay */}
        <div className="absolute top-4 right-4 z-[1000] bg-slate-950/80 backdrop-blur-md border border-slate-800 rounded-lg p-3 shadow-lg space-y-2 text-white max-w-[240px]">
          <h4 className="text-xs font-bold flex items-center gap-1.5">
            <Activity className="h-3.5 w-3.5 text-primary" /> Live Map Statistics
          </h4>
          <div className="text-[11px] space-y-1">
            <div className="flex justify-between">
              <span className="text-slate-400">Total Active:</span>
              <span className="font-semibold text-emerald-400">
                {Object.values(liveWorkers).filter(w => w.is_online).length} Workers
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Offline Threshold:</span>
              <span className="font-semibold text-slate-200">
                {offlineMinutes} min
              </span>
            </div>
          </div>
          <div className="flex gap-2 pt-1.5">
            <button 
              onClick={() => {
                refetchOffline();
                toast.success("Offline roster refreshed.");
              }}
              className="w-full text-[10px] bg-primary/20 text-primary hover:bg-primary/30 border border-primary/45 rounded py-1 transition-all"
            >
              Refresh Roster
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Mock helper to avoid build issues with missing loggers
const logger = {
  info: (msg: string) => console.log(`[INFO] ${msg}`),
  warn: (msg: string) => console.warn(`[WARN] ${msg}`),
  error: (msg: string) => console.error(`[ERROR] ${msg}`)
};

export default TrackingPage;
