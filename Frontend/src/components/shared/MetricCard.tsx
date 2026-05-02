import { cn } from '@/lib/utils';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: { value: number; label: string };
  variant?: 'default' | 'success' | 'warning' | 'info';
}

const variantStyles = {
  default: 'bg-card',
  success: 'bg-card border-success/20',
  warning: 'bg-card border-warning/20',
  info: 'bg-card border-primary/20',
};

const iconVariants = {
  default: 'bg-muted text-muted-foreground',
  success: 'bg-success/10 text-success',
  warning: 'bg-warning/10 text-warning',
  info: 'bg-primary/10 text-primary',
};

const MetricCard = ({ title, value, subtitle, icon: Icon, trend, variant = 'default' }: MetricCardProps) => (
  <div className={cn("rounded-lg border p-5 shadow-card transition-shadow hover:shadow-elevated", variantStyles[variant])}>
    <div className="flex items-start justify-between">
      <div>
        <p className="text-sm font-medium text-muted-foreground">{title}</p>
        <p className="mt-1 text-2xl font-bold text-card-foreground">{value}</p>
        {subtitle && <p className="mt-0.5 text-xs text-muted-foreground">{subtitle}</p>}
        {trend && (
          <p className={cn("mt-1 text-xs font-medium", trend.value >= 0 ? "text-success" : "text-destructive")}>
            {trend.value >= 0 ? '↑' : '↓'} {Math.abs(trend.value)}% {trend.label}
          </p>
        )}
      </div>
      <div className={cn("rounded-lg p-2.5", iconVariants[variant])}>
        <Icon className="h-5 w-5" />
      </div>
    </div>
  </div>
);

export default MetricCard;
