import { useState, useEffect } from 'react';
import { triggerAPI, type TriggerEvent } from '@/services/api';
import { TriggerCard } from '@/components/shared/TriggerCard';
import { ListSkeleton } from '@/components/shared/Skeletons';
import ErrorState from '@/components/shared/ErrorState';
import EmptyState from '@/components/shared/EmptyState';
import { Zap } from 'lucide-react';
import { cn } from '@/lib/utils';

const TriggersPage = () => {
  const [triggers, setTriggers] = useState<TriggerEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState<'all' | 'heat' | 'rain' | 'disruption'>('all');

  const load = async () => { setLoading(true); setError(''); try { setTriggers(await triggerAPI.getAll()); } catch { setError('Failed'); } setLoading(false); };
  useEffect(() => { load(); }, []);

  if (error) return <div className="p-6"><ErrorState onRetry={load} /></div>;

  const filtered = filter === 'all' ? triggers : triggers.filter(t => t.type === filter);

  return (
    <div className="p-4 md:p-6 space-y-6 animate-fade-in">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold">Trigger Log</h1>
          <p className="text-muted-foreground text-sm">Complete history of all trigger events</p>
        </div>
        <div className="flex gap-2">
          {(['all', 'heat', 'rain', 'disruption'] as const).map(f => (
            <button key={f} onClick={() => setFilter(f)}
              className={cn("px-3 py-1.5 rounded-full text-xs font-medium transition-colors capitalize",
                filter === f ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground hover:bg-muted/80")}>
              {f}
            </button>
          ))}
        </div>
      </div>

      {loading ? <ListSkeleton /> : filtered.length === 0 ? (
        <EmptyState icon={Zap} title="No triggers" description="No trigger events match your filter." />
      ) : (
        <div className="space-y-3">{filtered.map(t => <TriggerCard key={t.id} trigger={t} />)}</div>
      )}
    </div>
  );
};

export default TriggersPage;
