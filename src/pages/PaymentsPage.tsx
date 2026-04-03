import { useState, useEffect } from 'react';
import { transactionAPI } from '@/services/api';
import type { Transaction } from '@/services/mockData';
import { ListSkeleton, CardSkeleton } from '@/components/shared/Skeletons';
import MetricCard from '@/components/shared/MetricCard';
import { CreditCard, Wallet, ArrowUpRight, ArrowDownRight, Smartphone } from 'lucide-react';
import { cn } from '@/lib/utils';

const PaymentsPage = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { transactionAPI.getAll().then(t => { setTransactions(t); setLoading(false); }); }, []);

  const totalPremiums = Math.abs(transactions.filter(t => t.type === 'premium').reduce((s, t) => s + t.amount, 0));
  const weeklyCount = transactions.filter(t => t.type === 'premium').length;

  return (
    <div className="p-4 md:p-6 space-y-6 animate-fade-in">
      <h1 className="text-2xl font-bold">Payments</h1>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {loading ? <><CardSkeleton /><CardSkeleton /><CardSkeleton /></> : (
          <>
            <MetricCard title="Subscription Status" value="Active" icon={CreditCard} variant="success" />
            <MetricCard title="Total Premiums Paid" value={`₹${totalPremiums}`} subtitle={`${weeklyCount} weeks`} icon={Wallet} />
            <MetricCard title="Weekly Cap" value="₹49 / ₹49" subtitle="100% utilized" icon={CreditCard} variant="info" />
          </>
        )}
      </div>

      <div className="rounded-lg border bg-card p-6 shadow-card">
        <div className="flex items-center gap-3 mb-4">
          <Smartphone className="h-5 w-5 text-primary" />
          <h2 className="font-semibold">Payment Method</h2>
        </div>
        <div className="rounded-lg bg-muted p-4 flex items-center gap-4">
          <div className="rounded-lg bg-primary/10 p-2"><CreditCard className="h-5 w-5 text-primary" /></div>
          <div>
            <p className="text-sm font-medium">UPI - vikram@paytm</p>
            <p className="text-xs text-muted-foreground">Auto-deduction enabled</p>
          </div>
        </div>
      </div>

      <div>
        <h2 className="font-semibold mb-3">Deduction History</h2>
        {loading ? <ListSkeleton rows={3} /> : (
          <div className="space-y-2">
            {transactions.filter(t => t.type === 'premium').map(tx => (
              <div key={tx.id} className="flex items-center gap-4 rounded-lg border bg-card p-4 shadow-card">
                <div className="rounded-lg bg-muted p-2.5"><ArrowDownRight className="h-4 w-4 text-muted-foreground" /></div>
                <div className="flex-1"><p className="text-sm font-medium">{tx.description}</p><p className="text-xs text-muted-foreground">{new Date(tx.date).toLocaleDateString()}</p></div>
                <span className="text-sm font-bold">₹{Math.abs(tx.amount)}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default PaymentsPage;
