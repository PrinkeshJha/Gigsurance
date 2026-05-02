import { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { weatherAPI, triggerAPI, transactionAPI, policyAPI, type Policy, type WeatherData, type TriggerEvent, type Transaction } from '@/services/api';
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
const [policy, setPolicy] = useState<Policy | null>(null);

const [loading, setLoading] = useState(true);
const [error, setError] = useState('');

// -------------------------------
// LOAD DATA (FIXED SAFE)
// -------------------------------
const loadData = async () => {
setLoading(true);
setError('');

try {
  const [w, t, tx, p] = await Promise.all([
    weatherAPI.getCurrent(user?.zone || '').catch(() => null),
    triggerAPI.getAll().catch(() => []),
    transactionAPI.getAll().catch(() => []),
    policyAPI.get().catch(() => null),
  ]);

  setWeather(w);
  setTriggers(t || []);
  setTransactions(tx || []);
  setPolicy(p);

} catch (err) {
  console.error(err);
  setError('Failed to load dashboard data');
} finally {
  setLoading(false);
}

};

// -------------------------------
// TOGGLE POLICY
// -------------------------------
const handleTogglePolicy = async () => {
if (!policy) return;

setLoading(true);
setError('');

try {
  const updated = await policyAPI.toggleCoverage(policy.status !== 'active');
  setPolicy(updated);
} catch (err) {
  console.error(err);
  setError('Unable to update policy status');
} finally {
  setLoading(false);
}

};

useEffect(() => {
loadData();
}, []);

if (error) {
return ( <div className="p-6"> <ErrorState onRetry={loadData} /> </div>
);
}

// -------------------------------
// FIXED CALCULATIONS 🔥
// -------------------------------

// backend sends type: "payout"
const totalPayouts = transactions
.filter(t => t.type === 'payout')
.reduce((sum, t) => sum + (t.amount || 0), 0);

const weeklyPremium = policy?.weeklyPremium ?? 49;

const coverage =
policy?.coverageAmount ??
0;

const riskScore = policy?.riskScore ?? user?.risk_score ?? 0;

const riskLevel =
riskScore > 2 ? 'High' :
riskScore > 1 ? 'Medium' : 'Low';

const riskColor =
riskLevel === 'High'
? 'text-destructive'
: riskLevel === 'Medium'
? 'text-warning'
: 'text-success';

// -------------------------------
// UI
// -------------------------------
return ( <div className="p-4 md:p-6 space-y-6 animate-fade-in">

  {/* HEADER */}
  <div>
    <h1 className="text-2xl font-bold">
      Welcome back, {user?.name?.split(' ')[0] || 'User'}
    </h1>
    <p className="text-muted-foreground text-sm">
      Here's your coverage overview.
    </p>
  </div>

  {/* METRICS */}
  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    {loading
      ? Array.from({ length: 4 }).map((_, i) => <CardSkeleton key={i} />)
      : (
        <>
          <MetricCard
            title="Earnings Protected"
            value={`₹${totalPayouts.toLocaleString()}`}
            icon={Wallet}
            variant="success"
            trend={{ value: 12, label: 'vs last month' }}
          />

          <MetricCard
            title="Active Coverage"
            value={`₹${coverage}`}
            subtitle="Max weekly payout"
            icon={ShieldCheck}
            variant="default"
          />

          <MetricCard
            title="Weekly Premium"
            value={`₹${weeklyPremium}`}
            subtitle="Auto-deducted"
            icon={CreditCard}
          />

          <MetricCard
            title="Risk Level"
            value={riskLevel}
            subtitle={`Score: ${riskScore}`}
            icon={Activity}
            variant={riskLevel === 'High' ? 'warning' : 'default'}
          />
        </>
      )}
  </div>

  {/* POLICY */}
  {policy && !loading && (
    <div className="rounded-lg border bg-card p-6 shadow-card">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="font-semibold text-lg">Policy Status</h2>
          <p className="text-sm text-muted-foreground">
            Your policy is currently {policy.status === 'active' ? 'active' : 'paused'}.
          </p>
        </div>

        <button
          onClick={handleTogglePolicy}
          className="rounded-lg border border-primary bg-primary/10 px-4 py-2 text-sm font-medium text-primary transition hover:bg-primary/20"
        >
          {policy.status === 'active'
            ? 'Pause Coverage'
            : 'Activate Coverage'}
        </button>
      </div>
    </div>
  )}

  {/* WEATHER */}
  {weather && !loading && (
    <div className="rounded-lg border bg-card p-6 shadow-card">
      <h2 className="font-semibold mb-4">
        Live Environmental Conditions — {weather.zone || user?.zone}
      </h2>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">

        <div className="rounded-lg bg-muted p-4 text-center">
          <Thermometer className="h-5 w-5 mx-auto mb-1 text-muted-foreground" />
          <p className="text-2xl font-bold">{weather.temperature ?? '--'}°C</p>
          <p className="text-xs text-muted-foreground">Temperature</p>
        </div>

        <div className="rounded-lg bg-muted p-4 text-center">
          <Droplets className="h-5 w-5 mx-auto mb-1 text-primary" />
          <p className="text-2xl font-bold">{weather.rainfall ?? 0}mm</p>
          <p className="text-xs text-muted-foreground">Rainfall</p>
        </div>

        <div className="rounded-lg bg-muted p-4 text-center">
          <Wind className="h-5 w-5 mx-auto mb-1 text-muted-foreground" />
          <p className="text-2xl font-bold">{weather.humidity ?? 0}%</p>
          <p className="text-xs text-muted-foreground">Humidity</p>
        </div>

        <div className="rounded-lg bg-muted p-4 text-center">
          <Activity className="h-5 w-5 mx-auto mb-1 text-muted-foreground" />
          <p className="text-2xl font-bold">{weather.aqi ?? 0}</p>
          <p className="text-xs text-muted-foreground">AQI</p>
        </div>

      </div>
    </div>
  )}

  {/* TRIGGERS */}
  {!loading && (
    <div>
      <h2 className="font-semibold mb-3">Recent Trigger Events</h2>
      <div className="space-y-3">
        {triggers.length > 0
          ? triggers.slice(0, 3).map(t => (
              <TriggerCard key={t.id} trigger={t} />
            ))
          : <p className="text-sm text-muted-foreground">No triggers yet</p>
        }
      </div>
    </div>
  )}
</div>

);
};

export default DashboardPage;
