import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Shield, Loader2, CheckCircle2, ArrowRight, ArrowLeft } from 'lucide-react';
import { cn } from '@/lib/utils';

const platforms = ['Uber', 'Ola', 'Swiggy', 'Zomato', 'Dunzo', 'Rapido', 'Other'];
const zones = ['Mumbai - Zone A', 'Mumbai - Zone B', 'Delhi - Zone C', 'Bangalore - Zone D', 'Hyderabad - Zone E'];
const hours = ['6AM - 2PM', '8AM - 4PM', '10AM - 6PM', '12PM - 8PM', '2PM - 10PM', '6PM - 2AM'];

const OnboardingPage = () => {
  const { completeOnboarding } = useAuth();
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [platform, setPlatform] = useState('');
  const [zone, setZone] = useState('');
  const [workingHours, setWorkingHours] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ riskScore: number; weeklyPremium: number } | null>(null);

  const canProceed = [platform, zone, workingHours][step] !== '';

  const handleComplete = async () => {
    setLoading(true);
    try {
      await completeOnboarding({ platform, zone, workingHours });
      navigate('/dashboard');
    } catch {
      setLoading(false);
    }
  };

  const handleCalculate = async () => {
    setLoading(true);
    const riskScore = Math.floor(Math.random() * 40) + 50;
    const weeklyPremium = Math.floor(riskScore * 0.7) + 10;
    setTimeout(() => {
      setResult({ riskScore, weeklyPremium });
      setLoading(false);
      setStep(3);
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-lg">
        <div className="flex items-center gap-2 font-bold text-2xl justify-center mb-8">
          <Shield className="h-7 w-7 text-primary" />
          <span>Gig<span className="text-primary">Surance</span></span>
        </div>

        {/* Progress */}
        <div className="flex gap-2 mb-8">
          {[0, 1, 2, 3].map(i => (
            <div key={i} className={cn("h-1.5 flex-1 rounded-full transition-colors", i <= step ? "bg-primary" : "bg-muted")} />
          ))}
        </div>

        <div className="rounded-lg border bg-card p-8 shadow-card">
          {step === 0 && (
            <div className="animate-fade-in">
              <h2 className="text-xl font-bold mb-2">Select Your Platform</h2>
              <p className="text-sm text-muted-foreground mb-6">Which gig platform do you primarily work on?</p>
              <div className="grid grid-cols-2 gap-3">
                {platforms.map(p => (
                  <button key={p} onClick={() => setPlatform(p)}
                    className={cn("rounded-lg border p-3 text-sm font-medium transition-colors",
                      platform === p ? "border-primary bg-primary/10 text-primary" : "hover:bg-muted")}>
                    {p}
                  </button>
                ))}
              </div>
            </div>
          )}

          {step === 1 && (
            <div className="animate-fade-in">
              <h2 className="text-xl font-bold mb-2">Select Your Zone</h2>
              <p className="text-sm text-muted-foreground mb-6">Where do you primarily operate?</p>
              <div className="space-y-2">
                {zones.map(z => (
                  <button key={z} onClick={() => setZone(z)}
                    className={cn("w-full rounded-lg border p-3 text-sm font-medium text-left transition-colors",
                      zone === z ? "border-primary bg-primary/10 text-primary" : "hover:bg-muted")}>
                    {z}
                  </button>
                ))}
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="animate-fade-in">
              <h2 className="text-xl font-bold mb-2">Working Hours</h2>
              <p className="text-sm text-muted-foreground mb-6">What's your typical working schedule?</p>
              <div className="grid grid-cols-2 gap-3">
                {hours.map(h => (
                  <button key={h} onClick={() => setWorkingHours(h)}
                    className={cn("rounded-lg border p-3 text-sm font-medium transition-colors",
                      workingHours === h ? "border-primary bg-primary/10 text-primary" : "hover:bg-muted")}>
                    {h}
                  </button>
                ))}
              </div>
            </div>
          )}

          {step === 3 && result && (
            <div className="animate-fade-in text-center">
              <CheckCircle2 className="h-12 w-12 text-success mx-auto mb-4" />
              <h2 className="text-xl font-bold mb-2">Your AI Risk Profile</h2>
              <p className="text-sm text-muted-foreground mb-6">Based on your zone, platform, and schedule</p>
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="rounded-lg bg-muted p-4">
                  <p className="text-3xl font-bold text-primary">{result.riskScore}</p>
                  <p className="text-xs text-muted-foreground mt-1">Risk Score</p>
                </div>
                <div className="rounded-lg bg-muted p-4">
                  <p className="text-3xl font-bold text-success">₹{result.weeklyPremium}</p>
                  <p className="text-xs text-muted-foreground mt-1">Weekly Premium</p>
                </div>
              </div>
              <Button onClick={handleComplete} className="w-full gap-2" disabled={loading}>
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <>Activate Coverage <ArrowRight className="h-4 w-4" /></>}
              </Button>
            </div>
          )}

          {step < 3 && (
            <div className="flex justify-between mt-6">
              <Button variant="ghost" onClick={() => setStep(s => s - 1)} disabled={step === 0}>
                <ArrowLeft className="h-4 w-4 mr-1" /> Back
              </Button>
              {step < 2 ? (
                <Button onClick={() => setStep(s => s + 1)} disabled={!canProceed} className="gap-1">
                  Next <ArrowRight className="h-4 w-4" />
                </Button>
              ) : (
                <Button onClick={handleCalculate} disabled={!canProceed || loading} className="gap-1">
                  {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <>Calculate Risk <ArrowRight className="h-4 w-4" /></>}
                </Button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default OnboardingPage;
