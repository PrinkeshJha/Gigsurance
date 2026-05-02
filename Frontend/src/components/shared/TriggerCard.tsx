import { cn } from '@/lib/utils';
import type { TriggerEvent } from '@/services/api';
import { Thermometer, CloudRain, AlertTriangle } from 'lucide-react';

const typeIcons = { heat: Thermometer, rain: CloudRain, disruption: AlertTriangle };
const statusColors = {
  safe: 'bg-success/10 text-success border-success/20',
  warning: 'bg-warning/10 text-warning border-warning/20',
  breached: 'bg-destructive/10 text-destructive border-destructive/20',
};

const StatusBadge = ({ status }: { status: string }) => (
  <span className={cn("inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border", statusColors[status as keyof typeof statusColors] || statusColors.safe)}>
    {status || 'safe'}
  </span>
);

const TriggerCard = ({ trigger }: { trigger: TriggerEvent }) => {
  const Icon = typeIcons[trigger.type as keyof typeof typeIcons] || AlertTriangle;
  return (
    <div className="flex items-center gap-4 rounded-lg border bg-card p-4 shadow-card">
      <div className={cn("rounded-lg p-2.5", trigger.status === 'breached' ? 'bg-destructive/10' : trigger.status === 'warning' ? 'bg-warning/10' : 'bg-success/10')}>
        <Icon className={cn("h-5 w-5", trigger.status === 'breached' ? 'text-destructive' : trigger.status === 'warning' ? 'text-warning' : 'text-success')} />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-card-foreground capitalize">{trigger.type} — {trigger.zone}</p>
        <p className="text-xs text-muted-foreground">{new Date(trigger.timestamp).toLocaleString()}</p>
      </div>
      <div className="text-right">
        <StatusBadge status={trigger.status} />
        {trigger.payoutTriggered && <p className="text-xs font-medium text-success mt-1">₹{trigger.payoutAmount} paid</p>}
      </div>
    </div>
  );
};

export { TriggerCard, StatusBadge };
export default TriggerCard;
