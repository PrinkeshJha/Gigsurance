import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import {
  LayoutDashboard, Activity, FileText, History, BarChart3,
  User, Bell, CreditCard, Zap, ShieldCheck, LogOut, ChevronLeft, ChevronRight,
  Wallet, Navigation, Globe,
} from 'lucide-react';
import { useState } from 'react';
import { cn } from '@/lib/utils';

const userLinks = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/wallet', label: 'Wallet', icon: Wallet },
  { to: '/monitor', label: 'Monitor', icon: Activity },
  { to: '/policy', label: 'Policy', icon: FileText },
  { to: '/history', label: 'History', icon: History },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/triggers', label: 'Triggers', icon: Zap },
  { to: '/payments', label: 'Payments', icon: CreditCard },
  { to: '/notifications', label: 'Notifications', icon: Bell },
  { to: '/profile', label: 'Profile', icon: User },
];

const adminLinks = [
  { to: '/admin', label: 'Admin Panel', icon: ShieldCheck },
  { to: '/admin/tracking', label: 'Live Tracking', icon: Navigation },
  { to: '/admin/geospatial', label: 'Geo Analytics', icon: Globe },
];

const AppSidebar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);

  if (!user || !user.is_onboarded) return null;

  const links = user.role === 'admin' ? [...userLinks, ...adminLinks] : userLinks;

  return (
    <aside className={cn(
      "hidden md:flex flex-col border-r border-sidebar-border bg-sidebar transition-all duration-300 min-h-screen",
      collapsed ? "w-16" : "w-60"
    )}>
      <div className="flex items-center justify-between p-4 border-b border-sidebar-border">
        {!collapsed && (
          <span className="font-bold text-sidebar-accent-foreground">
            Gig<span className="text-sidebar-primary">Surance</span>
          </span>
        )}
        <button onClick={() => setCollapsed(!collapsed)} className="text-sidebar-foreground hover:text-sidebar-accent-foreground p-1 rounded">
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </button>
      </div>

      <nav className="flex-1 p-2 space-y-1">
        {links.map(l => {
          const active = location.pathname === l.to;
          return (
            <Link key={l.to} to={l.to}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors",
                active ? "bg-sidebar-accent text-sidebar-accent-foreground" : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
              )}>
              <l.icon className="h-4 w-4 shrink-0" />
              {!collapsed && <span>{l.label}</span>}
            </Link>
          );
        })}
      </nav>

      <div className="p-2 border-t border-sidebar-border">
        <button onClick={logout}
          className="flex items-center gap-3 px-3 py-2.5 w-full rounded-md text-sm font-medium text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground transition-colors">
          <LogOut className="h-4 w-4 shrink-0" />
          {!collapsed && <span>Logout</span>}
        </button>
      </div>
    </aside>
  );
};

export default AppSidebar;
