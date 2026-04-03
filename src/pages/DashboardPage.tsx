import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { weatherAPI, triggerAPI, transactionAPI } from '@/services/api';
import type { WeatherData, TriggerEvent, Transaction } from '@/services/mockData';
import MetricCard from '@/components/shared/MetricCard';
import { TriggerCard } from '@/components/shared/TriggerCard';
import { CardSkeleton } from '@/components/shared/Skeletons';
import ErrorState from '@/components/shared/ErrorState';
import { ShieldCheck, Wallet, CreditCard, Thermometer, Droplets, Wind, Activity } from 'lucide-react';
import { cn } from '@/lib/utils';

const DashboardPage = () => {
  const { user } = useAuth();
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [triggers, setTriggers] = useState<TriggerEvent[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadData = async () => {
    setLoading(true);
    setError('');
    try {
      const [w, t, tx] = await Promise.all([weatherAPI.getCurrent(user?.zone || ''), triggerAPI.getAll(), transactionAPI.getAll()]);
      setWeather(w);
      setTriggers(t);
      setTransactions(tx);
    } catch { setError('Failed to load dashboard data'); }
    setLoading(false);
  };

  useEffect(() => { loadData(); }, []);

  if (error) return <div className="p-6"><ErrorState onRetry={loadData} /></div>;

  const totalPayouts = transactions.filter(t => t.type === 'payout').reduce((s, t) => s + t.amount, 0);
  const riskLevel = user?.riskScore ? (user.riskScore > 75 ? 'High' : user.riskScore > 50 ? 'Medium' : 'Low') : 'Low';
  const riskColor = riskLevel === 'High' ? 'text-destructive' : riskLevel === 'Medium' ? 'text-warning' : 'text-success';

  return (
    <div className="p-4 md:p-6 space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold">Welcome back, {user?.name?.split(' ')[0]}</h1>
        <p className="text-muted-foreground text-sm">Here's your coverage overview.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {loading ? Array.from({ length: 4 }).map((_, i) => <CardSkeleton key={i} />) : (
          <>
            <MetricCard title="Earnings Protected" value={`₹${totalPayouts.toLocaleString()}`} icon={Wallet} variant="success" trend={{ value: 12, label: 'vs last month' }} />
            <MetricCard title="Active Coverage" value="₹5,000" subtitle="Max weekly payout" icon={ShieldCheck} variant="info" />
            <MetricCard title="Weekly Premium" value={`₹${user?.weeklyPremium || 49}`} subtitle="Auto-deducted" icon={CreditCard} />
            <MetricCard title="Risk Level" value={riskLevel} subtitle={`Score: ${user?.riskScore || 72}`} icon={Activity} variant={riskLevel === 'High' ? 'warning' : 'default'} />
          </>
        )}
      </div>

      {/* Environmental Conditions */}
      {weather && !loading && (
        <div className="rounded-lg border bg-card p-6 shadow-card">
          <h2 className="font-semibold mb-4">Live Environmental Conditions — {weather.zone}</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="rounded-lg bg-muted p-4 text-center">
              <Thermometer className={cn("h-5 w-5 mx-auto mb-1", weather.temperature > 40 ? "text-destructive" : "text-muted-foreground")} />
              <p className="text-2xl font-bold">{weather.temperature}°C</p>
              <p className="text-xs text-muted-foreground">Temperature</p>
            </div>
            <div className="rounded-lg bg-muted p-4 text-center">
              <Droplets className="h-5 w-5 mx-auto mb-1 text-primary" />
              <p className="text-2xl font-bold">{weather.rainfall}mm</p>
              <p className="text-xs text-muted-foreground">Rainfall</p>
            </div>
            <div className="rounded-lg bg-muted p-4 text-center">
              <Wind className="h-5 w-5 mx-auto mb-1 text-muted-foreground" />
              <p className="text-2xl font-bold">{weather.humidity}%</p>
              <p className="text-xs text-muted-foreground">Humidity</p>
            </div>
            <div className="rounded-lg bg-muted p-4 text-center">
              <Activity className={cn("h-5 w-5 mx-auto mb-1", weather.aqi > 150 ? "text-destructive" : weather.aqi > 100 ? "text-warning" : "text-success")} />
              <p className="text-2xl font-bold">{weather.aqi}</p>
              <p className="text-xs text-muted-foreground">AQI</p>
            </div>
          </div>
        </div>
      )}

      {/* Recent Triggers */}
      {!loading && (
        <div>
          <h2 className="font-semibold mb-3">Recent Trigger Events</h2>
          <div className="space-y-3">
            {triggers.slice(0, 3).map(t => <TriggerCard key={t.id} trigger={t} />)}
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;
