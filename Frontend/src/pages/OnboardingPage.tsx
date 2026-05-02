import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { Shield, Loader2, CheckCircle2, ArrowRight, ArrowLeft } from 'lucide-react';
import { cn } from '@/lib/utils';
import { metaAPI, onboardingAPI } from '@/services/api';
import { CityZoneSelector } from '@/components/CityZoneSelector';

const hours = ['6AM - 2PM', '8AM - 4PM', '10AM - 6PM', '12PM - 8PM', '2PM - 10PM', '6PM - 2AM'];

const OnboardingPage = () => {
  const { user, completeOnboarding } = useAuth();
  const navigate = useNavigate();

  const [step, setStep] = useState(0);

  const [platform, setPlatform] = useState('');
  const [city, setCity] = useState('');
  const [zone, setZone] = useState('');
  const [workingHours, setWorkingHours] = useState('');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<{ riskScore: number; weeklyPremium: number } | null>(null);

  const [platforms, setPlatforms] = useState<string[]>([]);
  const [fetchingMeta, setFetchingMeta] = useState(true);

  // ✅ IMPORTANT: Prevent loop if already onboarded
  useEffect(() => {
    if (user?.is_onboarded) {
      navigate('/dashboard');
    }
  }, [user, navigate]);

  // ✅ Validation
  const canProceed =
    step === 0 ? platform.trim() !== '' :
    step === 1 ? city.trim() !== '' && zone.trim() !== '' :
    step === 2 ? workingHours.trim() !== '' :
    true;

  // ✅ Load platforms
  useEffect(() => {
    const loadMeta = async () => {
      setFetchingMeta(true);
      setError('');

      try {
        const platformsResponse = await metaAPI.getPlatforms();
        setPlatforms(platformsResponse || []);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Unable to load onboarding options');
      } finally {
        setFetchingMeta(false);
      }
    };

    loadMeta();
  }, []);

  // ✅ COMPLETE ONBOARDING (FIXED 🔥)
  const handleComplete = async () => {
    setLoading(true);
    setError('');

    try {
      if (!result) throw new Error('Please calculate the risk first');

      // ❗ DO NOT NAVIGATE HERE
      await completeOnboarding({
        platform,
        city: city.trim(),
        zone: zone.trim(),
        workingHours,
        riskScore: result.riskScore,
        weeklyPremium: result.weeklyPremium,
      });

      // ✅ Navigation handled by AuthContext automatically

    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to complete onboarding');
    } finally {
      setLoading(false);
    }
  };

  // ✅ Calculate risk
  const handleCalculate = async () => {
    setLoading(true);
    setError('');

    try {
      if (!platform || !city || !zone || !workingHours) {
        throw new Error('Complete all selections before calculating risk');
      }

      const data = await onboardingAPI.calculate({
        platform,
        city: city.trim(),
        zone: zone.trim(),
        working_hours: workingHours,
      });

      setResult(data);
      setStep(3);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to calculate your risk score');
    } finally {
      setLoading(false);
    }
  };

  const canShowContent = !fetchingMeta && platforms.length > 0;

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-lg">

        {/* Logo */}
        <div className="flex items-center gap-2 font-bold text-2xl justify-center mb-8">
          <Shield className="h-7 w-7 text-primary" />
          <span>Gig<span className="text-primary">Surance</span></span>
        </div>

        {/* Progress */}
        <div className="flex gap-2 mb-8">
          {[0, 1, 2, 3].map(i => (
            <div
              key={i}
              className={cn(
                "h-1.5 flex-1 rounded-full transition-colors",
                i <= step ? "bg-primary" : "bg-muted"
              )}
            />
          ))}
        </div>

        <div className="rounded-lg border bg-card p-8 shadow-card">

          {/* Error */}
          {error && (
            <div className="mb-4 rounded-lg border border-destructive/20 bg-destructive/10 p-3 text-sm text-destructive">
              {error}
            </div>
          )}

          {/* Loading */}
          {fetchingMeta && (
            <div className="text-center py-16 text-muted-foreground">
              Loading onboarding options...
            </div>
          )}

          {/* Content */}
          {!fetchingMeta && canShowContent && (
            <>
              {step === 0 && (
                <div>
                  <h2 className="text-xl font-bold mb-2">Select Platform</h2>
                  <div className="grid grid-cols-2 gap-3">
                    {platforms.map(p => (
                      <button
                        key={p}
                        onClick={() => setPlatform(p)}
                        className={cn(
                          "rounded-lg border p-3",
                          platform === p && "border-primary bg-primary/10 text-primary"
                        )}
                      >
                        {p}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {step === 1 && (
                <CityZoneSelector
                  city={city}
                  zone={zone}
                  onCityChange={setCity}
                  onZoneChange={setZone}
                />
              )}

              {step === 2 && (
                <div>
                  <h2 className="text-xl font-bold mb-2">Working Hours</h2>
                  <div className="grid grid-cols-2 gap-3">
                    {hours.map(h => (
                      <button
                        key={h}
                        onClick={() => setWorkingHours(h)}
                        className={cn(
                          "rounded-lg border p-3",
                          workingHours === h && "border-primary bg-primary/10 text-primary"
                        )}
                      >
                        {h}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {step === 3 && result && (
                <div className="text-center">
                  <CheckCircle2 className="h-12 w-12 text-green-500 mx-auto mb-4" />
                  <p className="text-3xl font-bold">{result.riskScore}</p>
                  <p>₹{result.weeklyPremium}</p>

                  <Button onClick={handleComplete} className="w-full mt-4">
                    {loading ? <Loader2 className="animate-spin" /> : "Activate"}
                  </Button>
                </div>
              )}

              {step < 3 && (
                <div className="flex justify-between mt-6">
                  <Button
                    variant="ghost"
                    onClick={() => setStep(s => Math.max(0, s - 1))}
                    disabled={step === 0}
                  >
                    <ArrowLeft className="h-4 w-4 mr-1" /> Back
                  </Button>

                  {step < 2 ? (
                    <Button
                      onClick={() => setStep(s => s + 1)}
                      disabled={!canProceed}
                    >
                      Next <ArrowRight className="h-4 w-4" />
                    </Button>
                  ) : (
                    <Button
                      onClick={handleCalculate}
                      disabled={!canProceed || loading}
                    >
                      {loading ? <Loader2 className="animate-spin" /> : "Calculate Risk"}
                    </Button>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default OnboardingPage;