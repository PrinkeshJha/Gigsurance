import { useState, useEffect } from 'react';
import { triggerAPI, weatherAPI, type TriggerEvent, type WeatherData } from '@/services/api';
import { TriggerCard } from '@/components/shared/TriggerCard';
import { ListSkeleton } from '@/components/shared/Skeletons';
import ErrorState from '@/components/shared/ErrorState';
import { useAuth } from '@/hooks/useAuth';
import { Activity, Thermometer, CloudRain, AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';

const MonitorPage = () => {
  const { user } = useAuth();
  const [triggers, setTriggers] = useState<TriggerEvent[]>([]);
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async () => {
    setLoading(true); setError('');
    try {
      const [t, w] = await Promise.all([triggerAPI.getAll(), weatherAPI.getCurrent(user?.zone || '')]);
      setTriggers(t); setWeather(w);
    } catch { setError('Failed to load'); }
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  if (error) return <div className="p-6"><ErrorState onRetry={load} /></div>;

  const statusCounts = {
    safe: triggers.filter(t => t.status === 'safe').length,
    warning: triggers.filter(t => t.status === 'warning').length,
    breached: triggers.filter(t => t.status === 'breached').length,
  };

  return (
    <div className="p-4 md:p-6 space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold">Real-Time Monitor</h1>
        <p className="text-muted-foreground text-sm">Live trigger monitoring for {user?.zone}</p>
      </div>

      {!loading && (
        <div className="grid grid-cols-3 gap-4">
          <div className="rounded-lg border bg-success/10 border-success/20 p-4 text-center">
            <p className="text-2xl font-bold text-success">{statusCounts.safe}</p>
            <p className="text-xs text-muted-foreground">Safe</p>
          </div>
          <div className="rounded-lg border bg-warning/10 border-warning/20 p-4 text-center">
            <p className="text-2xl font-bold text-warning">{statusCounts.warning}</p>
            <p className="text-xs text-muted-foreground">Warning</p>
          </div>
          <div className="rounded-lg border bg-destructive/10 border-destructive/20 p-4 text-center">
            <p className="text-2xl font-bold text-destructive">{statusCounts.breached}</p>
            <p className="text-xs text-muted-foreground">Breached</p>
          </div>
        </div>
      )}

      <div>
        <h2 className="font-semibold mb-3">Trigger Events</h2>
        {loading ? <ListSkeleton /> : (
          <div className="space-y-3">
            {triggers.map(t => <TriggerCard key={t.id} trigger={t} />)}
          </div>
        )}
      </div>
    </div>
  );
};

export default MonitorPage;
