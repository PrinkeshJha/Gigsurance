import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Shield, Loader2, AlertCircle } from 'lucide-react';

const LoginPage = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('rider@gigsurance.com');
  const [password, setPassword] = useState('password');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen">
      <div className="hidden lg:flex lg:w-1/2 gradient-hero items-center justify-center p-12">
        <div className="max-w-md text-center">
          <Shield className="h-16 w-16 text-primary mx-auto mb-6" />
          <h2 className="text-3xl font-bold text-primary-foreground">Welcome Back</h2>
          <p className="mt-4 text-primary-foreground/70">Access your income protection dashboard and see your coverage status.</p>
        </div>
      </div>
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <div className="flex items-center gap-2 font-bold text-2xl mb-2">
            <Shield className="h-7 w-7 text-primary" />
            <span>Gig<span className="text-primary">Surance</span></span>
          </div>
          <p className="text-muted-foreground mb-8">Sign in to your account</p>

          {error && (
            <div className="flex items-center gap-2 rounded-lg bg-destructive/10 border border-destructive/20 p-3 mb-4 text-sm text-destructive">
              <AlertCircle className="h-4 w-4 shrink-0" /> {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div><label className="text-sm font-medium">Email</label><Input type="email" value={email} onChange={e => setEmail(e.target.value)} required /></div>
            <div><label className="text-sm font-medium">Password</label><Input type="password" value={password} onChange={e => setPassword(e.target.value)} required /></div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Signing in...</> : 'Sign In'}
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-muted-foreground">
            Don't have an account? <Link to="/register" className="text-primary font-medium hover:underline">Sign up</Link>
          </p>
          <div className="mt-4 text-center text-xs text-muted-foreground">
            Demo: rider@gigsurance.com / admin@gigsurance.com (any password)
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
