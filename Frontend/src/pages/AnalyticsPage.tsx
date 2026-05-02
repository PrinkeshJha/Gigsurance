import { useState, useEffect } from 'react';
import { analyticsAPI } from '@/services/api';
import { ChartSkeleton } from '@/components/shared/Skeletons';
import ErrorState from '@/components/shared/ErrorState';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const AnalyticsPage = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async () => { setLoading(true); setError(''); try { setData(await analyticsAPI.getData()); } catch { setError('Failed'); } setLoading(false); };
  useEffect(() => { load(); }, []);

  if (error) return <div className="p-6"><ErrorState onRetry={load} /></div>;

  return (
    <div className="p-4 md:p-6 space-y-6 animate-fade-in">
      <h1 className="text-2xl font-bold">Analytics</h1>

      {loading ? <><ChartSkeleton /><ChartSkeleton /></> : data && (
        <>
          <div className="rounded-lg border bg-card p-6 shadow-card">
            <h2 className="font-semibold mb-4">Earnings Saved Over Time</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data.earningsSaved}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <Tooltip contentStyle={{ background: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: '8px' }} />
                <Line type="monotone" dataKey="amount" stroke="hsl(var(--primary))" strokeWidth={2} dot={{ fill: 'hsl(var(--primary))' }} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="rounded-lg border bg-card p-6 shadow-card">
            <h2 className="font-semibold mb-4">Trigger Frequency by Type</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data.triggerFrequency}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <Tooltip contentStyle={{ background: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: '8px' }} />
                <Legend />
                <Bar dataKey="heat" fill="hsl(0, 84%, 60%)" radius={[4, 4, 0, 0]} />
                <Bar dataKey="rain" fill="hsl(221, 83%, 53%)" radius={[4, 4, 0, 0]} />
                <Bar dataKey="disruption" fill="hsl(38, 92%, 50%)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="rounded-lg border bg-card p-6 shadow-card">
            <h2 className="font-semibold mb-4">Seasonal Risk Trends</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {data.seasonalTrends?.map((s: any) => (
                <div key={s.season} className="rounded-lg bg-muted p-4 text-center">
                  <p className="text-sm font-medium">{s.season}</p>
                  <p className="text-2xl font-bold text-primary mt-1">{s.risk}%</p>
                  <p className="text-xs text-muted-foreground">Avg payout: ₹{s.avgPayout}</p>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default AnalyticsPage;
