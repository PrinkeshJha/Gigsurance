import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import {
  LayoutDashboard, Activity, FileText, History, BarChart3,
  User, Bell, CreditCard, Zap, ShieldCheck, Menu, X, LogOut, Shield,
} from 'lucide-react';
import { useState } from 'react';
import { cn } from '@/lib/utils';

const links = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/monitor', label: 'Monitor', icon: Activity },
  { to: '/policy', label: 'Policy', icon: FileText },
  { to: '/history', label: 'History', icon: History },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/triggers', label: 'Triggers', icon: Zap },
  { to: '/payments', label: 'Payments', icon: CreditCard },
  { to: '/notifications', label: 'Notifications', icon: Bell },
  { to: '/profile', label: 'Profile', icon: User },
];

const MobileNav = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [open, setOpen] = useState(false);

  if (!user?.onboarded) return null;

  const allLinks = user.role === 'admin' ? [...links, { to: '/admin', label: 'Admin', icon: ShieldCheck }] : links;

  return (
    <div className="md:hidden">
      <div className="flex items-center justify-between px-4 h-14 border-b border-border bg-card">
        <div className="flex items-center gap-2 font-bold">
          <Shield className="h-5 w-5 text-primary" />
          <span>Gig<span className="text-primary">Surance</span></span>
        </div>
        <button onClick={() => setOpen(!open)}>
          {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>
      {open && (
        <div className="border-b border-border bg-card p-3 animate-fade-in">
          {allLinks.map(l => (
            <Link key={l.to} to={l.to} onClick={() => setOpen(false)}
              className={cn("flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium",
                location.pathname === l.to ? "bg-primary/10 text-primary" : "text-muted-foreground hover:bg-muted"
              )}>
              <l.icon className="h-4 w-4" /><span>{l.label}</span>
            </Link>
          ))}
          <button onClick={() => { logout(); setOpen(false); }}
            className="flex items-center gap-3 px-3 py-2.5 w-full rounded-md text-sm font-medium text-muted-foreground hover:bg-muted mt-1">
            <LogOut className="h-4 w-4" /><span>Logout</span>
          </button>
        </div>
      )}
    </div>
  );
};

export default MobileNav;
