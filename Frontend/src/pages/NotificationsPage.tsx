import { useState, useEffect } from 'react';
import { notificationsAPI } from '@/services/api';
import type { Notification } from '@/services/api';
import { ListSkeleton } from '@/components/shared/Skeletons';
import EmptyState from '@/components/shared/EmptyState';
import { Bell, Zap, CreditCard, Info } from 'lucide-react';
import { cn } from '@/lib/utils';

const typeIcons = {
  trigger: Zap,
  payout: CreditCard,
  system: Info,
  info: Bell,
};

const typeColors = {
  trigger: 'bg-warning/10 text-warning',
  payout: 'bg-success/10 text-success',
  system: 'bg-muted text-muted-foreground',
  info: 'bg-primary/10 text-primary',
};

const NotificationsPage = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const data = await notificationsAPI.getAll();
        setNotifications(data.notifications);
      } catch (err) {
        console.error('Failed to load notifications', err);
      } finally {
        setLoading(false);
      }
    };

    fetchNotifications();
  }, []);

  const markRead = async (id: string) => {
    // Optimistic UI update
    setNotifications(prev =>
      prev.map(n => (n.id === id ? { ...n, read: true } : n))
    );

    try {
      await notificationsAPI.markAsRead(); // ✅ FIXED (no id)
    } catch (err) {
      console.error('Failed to mark as read', err);
    }
  };

  return (
    <div className="p-4 md:p-6 space-y-6 animate-fade-in">
      <h1 className="text-2xl font-bold">Notifications</h1>

      {loading ? (
        <ListSkeleton />
      ) : notifications.length === 0 ? (
        <EmptyState
          icon={Bell}
          title="No notifications"
          description="You're all caught up!"
        />
      ) : (
        <div className="space-y-2">
          {notifications.map(n => {
            const Icon = typeIcons[n.type];

            return (
              <div
                key={n.id}
                onClick={() => markRead(n.id)}
                className={cn(
                  "flex items-start gap-4 rounded-lg border bg-card p-4 shadow-card cursor-pointer transition-colors hover:bg-muted/50",
                  !n.read && "border-primary/30 bg-primary/5"
                )}
              >
                <div className={cn("rounded-lg p-2.5 shrink-0", typeColors[n.type])}>
                  <Icon className="h-4 w-4" />
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium">{n.title}</p>
                    {!n.read && (
                      <span className="h-2 w-2 rounded-full bg-primary shrink-0" />
                    )}
                  </div>

                  <p className="text-xs text-muted-foreground mt-0.5">
                    {n.message}
                  </p>

                  <p className="text-xs text-muted-foreground mt-1">
                    {new Date(n.timestamp).toLocaleString()}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default NotificationsPage;