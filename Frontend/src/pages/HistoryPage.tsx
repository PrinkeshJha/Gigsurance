import { useState, useEffect } from 'react';
import { transactionAPI, type Transaction } from '@/services/api';
import { ListSkeleton } from '@/components/shared/Skeletons';
import ErrorState from '@/components/shared/ErrorState';
import EmptyState from '@/components/shared/EmptyState';
import { ArrowUpRight, ArrowDownRight, History as HistoryIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

const HistoryPage = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState<'all' | 'payout' | 'premium'>('all');

  const load = async () => { setLoading(true); setError(''); try { setTransactions(await transactionAPI.getAll()); } catch { setError('Failed'); } setLoading(false); };
  useEffect(() => { load(); }, []);

  if (error) return <div className="p-6"><ErrorState onRetry={load} /></div>;

  const filtered = filter === 'all' ? transactions : transactions.filter(t => t.type === filter);

  return (
    <div className="p-4 md:p-6 space-y-6 animate-fade-in">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold">Transaction History</h1>
          <p className="text-muted-foreground text-sm">Payouts and premium deductions</p>
        </div>
        <div className="flex gap-2">
          {(['all', 'payout', 'premium'] as const).map(f => (
            <button key={f} onClick={() => setFilter(f)}
              className={cn("px-3 py-1.5 rounded-full text-xs font-medium transition-colors capitalize",
                filter === f ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground hover:bg-muted/80")}>
              {f}
            </button>
          ))}
        </div>
      </div>

      {loading ? <ListSkeleton /> : filtered.length === 0 ? (
        <EmptyState icon={HistoryIcon} title="No transactions" description="Your transaction history will appear here." />
      ) : (
        <div className="space-y-2">
          {filtered.map(tx => (
            <div key={tx.id} className="flex items-center gap-4 rounded-lg border bg-card p-4 shadow-card">
              <div className={cn("rounded-lg p-2.5", tx.type === 'payout' ? "bg-success/10" : "bg-muted")}>
                {tx.type === 'payout' ? <ArrowUpRight className="h-4 w-4 text-success" /> : <ArrowDownRight className="h-4 w-4 text-muted-foreground" />}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium capitalize">{tx.type} Transaction</p>
                <p className="text-xs text-muted-foreground">{new Date(tx.createdAt).toLocaleDateString()}</p>
              </div>
              <span className={cn("text-sm font-bold", tx.amount > 0 ? "text-success" : "text-foreground")}>
                {tx.amount > 0 ? '+' : ''}₹{Math.abs(tx.amount)}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default HistoryPage;
