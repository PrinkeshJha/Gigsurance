import { useState, useEffect } from 'react';
import { adminAPI } from '@/services/api';
import MetricCard from '@/components/shared/MetricCard';
import { CardSkeleton, ChartSkeleton } from '@/components/shared/Skeletons';
import { Users, Wallet, Zap, CreditCard, ShieldCheck, TrendingUp } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const mockRiskPool = [
  { month: 'Oct', inflow: 450000, outflow: 320000 },
  { month: 'Nov', inflow: 480000, outflow: 280000 },
  { month: 'Dec', inflow: 520000, outflow: 350000 },
  { month: 'Jan', inflow: 490000, outflow: 310000 },
  { month: 'Feb', inflow: 540000, outflow: 420000 },
  { month: 'Mar', inflow: 580000, outflow: 480000 },
];

const AdminPage = () => {
  const [kpis, setKpis] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { adminAPI.getKPIs().then(k => { setKpis(k); setLoading(false); }); }, []);

  return (
    <div className="p-4 md:p-6 space-y-6 animate-fade-in">
      <h1 className="text-2xl font-bold">Admin Panel</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {loading ? Array.from({ length: 6 }).map((_, i) => <CardSkeleton key={i} />) : (
          <>
            <MetricCard title="Active Users" value={kpis.activeUsers.toLocaleString()} icon={Users} variant="info" trend={{ value: 8, label: 'this month' }} />
            <MetricCard title="Total Payouts" value={`₹${(kpis.totalPayouts / 100000).toFixed(1)}L`} icon={Wallet} variant="success" />
            <MetricCard title="Trigger Events" value={kpis.triggerFrequency.toLocaleString()} icon={Zap} variant="warning" />
            <MetricCard title="Avg Premium" value={`₹${kpis.avgPremium}/wk`} icon={CreditCard} />
            <MetricCard title="Risk Pool" value={`₹${(kpis.riskPoolBalance / 100000).toFixed(1)}L`} icon={ShieldCheck} variant="info" />
            <MetricCard title="Claims Ratio" value={`${(kpis.claimsRatio * 100).toFixed(0)}%`} icon={TrendingUp} />
          </>
        )}
      </div>

      <div className="rounded-lg border bg-card p-6 shadow-card">
        <h2 className="font-semibold mb-4">Risk Pool Overview</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={mockRiskPool}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" fontSize={12} />
            <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} tickFormatter={v => `₹${v/1000}K`} />
            <Tooltip contentStyle={{ background: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: '8px' }} />
            <Bar dataKey="inflow" fill="hsl(160, 84%, 39%)" name="Premium Inflow" radius={[4, 4, 0, 0]} />
            <Bar dataKey="outflow" fill="hsl(221, 83%, 53%)" name="Payout Outflow" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default AdminPage;
