import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Bell, Menu, Shield, X } from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/button';

const publicLinks = [
  { to: '/', label: 'Home' },
  { to: '/need', label: 'Why GigSurance' },
  { to: '/pricing', label: 'Pricing' },
  { to: '/about', label: 'How It Works' },
  { to: '/contact', label: 'Contact' },
];

const Navbar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const isPublic = !user || ['/', '/need', '/pricing', '/about', '/contact', '/legal'].includes(location.pathname);
  const unread = 2;

  if (user && user.onboarded && !['/'].includes(location.pathname) && !['/', '/need', '/pricing', '/about', '/contact', '/legal'].includes(location.pathname)) return null;

  return (
    <nav className="sticky top-0 z-50 border-b border-border bg-card/80 backdrop-blur-md">
      <div className="container flex h-16 items-center justify-between">
        <Link to="/" className="flex items-center gap-2 font-bold text-xl">
          <Shield className="h-6 w-6 text-primary" />
          <span className="text-foreground">Gig<span className="text-primary">Surance</span></span>
        </Link>

        <div className="hidden md:flex items-center gap-6">
          {isPublic && publicLinks.map(l => (
            <Link key={l.to} to={l.to} className={`text-sm font-medium transition-colors hover:text-primary ${location.pathname === l.to ? 'text-primary' : 'text-muted-foreground'}`}>
              {l.label}
            </Link>
          ))}
        </div>

        <div className="hidden md:flex items-center gap-3">
          {user ? (
            <>
              {isPublic && <Link to="/dashboard"><Button size="sm">Dashboard</Button></Link>}
              <Button variant="ghost" size="sm" onClick={logout}>Logout</Button>
            </>
          ) : (
            <>
              <Link to="/login"><Button variant="ghost" size="sm">Sign In</Button></Link>
              <Link to="/register"><Button size="sm">Get Started</Button></Link>
            </>
          )}
        </div>

        <button className="md:hidden" onClick={() => setMobileOpen(!mobileOpen)}>
          {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {mobileOpen && (
        <div className="md:hidden border-t border-border bg-card p-4 animate-fade-in">
          {isPublic && publicLinks.map(l => (
            <Link key={l.to} to={l.to} onClick={() => setMobileOpen(false)}
              className="block py-2 text-sm font-medium text-muted-foreground hover:text-primary">
              {l.label}
            </Link>
          ))}
          <div className="mt-4 flex flex-col gap-2">
            {user ? (
              <>
                <Link to="/dashboard" onClick={() => setMobileOpen(false)}><Button className="w-full" size="sm">Dashboard</Button></Link>
                <Button variant="ghost" size="sm" onClick={() => { logout(); setMobileOpen(false); }}>Logout</Button>
              </>
            ) : (
              <>
                <Link to="/login" onClick={() => setMobileOpen(false)}><Button variant="ghost" className="w-full" size="sm">Sign In</Button></Link>
                <Link to="/register" onClick={() => setMobileOpen(false)}><Button className="w-full" size="sm">Get Started</Button></Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
