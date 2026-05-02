import { useState, useEffect } from 'react';
import { policyAPI, type Policy } from '@/services/api';
import { CardSkeleton } from '@/components/shared/Skeletons';
import ErrorState from '@/components/shared/ErrorState';
import { useAuth } from '@/hooks/useAuth';
import { CheckCircle2, Brain, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

const PolicyPage = () => {
const { user } = useAuth();

const [policy, setPolicy] = useState<Policy | null>(null);
const [loading, setLoading] = useState(true);
const [toggling, setToggling] = useState(false);
const [error, setError] = useState('');

// -------------------------------
// LOAD POLICY (SAFE 🔥)
// -------------------------------
const load = async () => {
setLoading(true);
setError('');

try {
  const data = await policyAPI.get();
  setPolicy(data);
} catch (err) {
  console.error(err);
  setError('Failed to load policy');
} finally {
  setLoading(false);
}

};

useEffect(() => {
load();
}, []);

// -------------------------------
// TOGGLE COVERAGE
// -------------------------------
const toggleCoverage = async () => {
if (!policy) return;

setToggling(true);

try {
  const updated = await policyAPI.toggleCoverage(policy.status !== 'active');
  setPolicy(updated);
} catch (err) {
  console.error(err);
} finally {
  setToggling(false);
}

};

if (error) {
return ( <div className="p-6"> <ErrorState onRetry={load} /> </div>
);
}

// -------------------------------
// SAFE DATA EXTRACTION 🔥
// -------------------------------
const triggers = (policy as any)?.triggers ?? [];

const coverage = policy?.coverageAmount ?? 0;

const weeklyPremium = policy?.weeklyPremium ?? 0;

const startDate = (policy as any)?.start_date
? new Date((policy as any).start_date).toLocaleDateString()
: '-';

const riskScore = policy?.riskScore ?? 0;

return ( <div className="p-4 md:p-6 space-y-6 animate-fade-in"> <h1 className="text-2xl font-bold">Your Policy</h1>

  {loading ? (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <CardSkeleton />
      <CardSkeleton />
    </div>
  ) : policy ? (
    <>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* COVERAGE */}
        <div className="rounded-lg border bg-card p-6 shadow-card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold">Coverage Details</h2>

            <span className={cn(
              "inline-flex items-center px-3 py-1 rounded-full text-xs font-medium",
              policy.status === 'active'
                ? "bg-success/10 text-success"
                : "bg-muted text-muted-foreground"
            )}>
              {policy.status}
            </span>
          </div>

          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Policy ID</span>
              <span className="font-medium">{policy.id}</span>
            </div>

            <div className="flex justify-between">
              <span className="text-muted-foreground">Max Coverage</span>
              <span className="font-medium">₹{coverage.toLocaleString()}</span>
            </div>

            <div className="flex justify-between">
              <span className="text-muted-foreground">Weekly Premium</span>
              <span className="font-medium">₹{weeklyPremium}</span>
            </div>

            <div className="flex justify-between">
              <span className="text-muted-foreground">Zone</span>
              <span className="font-medium">{(policy as any).zone ?? '-'}</span>
            </div>

            <div className="flex justify-between">
              <span className="text-muted-foreground">Start Date</span>
              <span className="font-medium">{startDate}</span>
            </div>
          </div>

          {/* TRIGGERS (FIXED 🔥) */}
          <div className="mt-4 pt-4 border-t">
            <p className="text-sm font-medium mb-2">Covered Triggers</p>

            {triggers.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {triggers.map((t: string) => (
                  <span
                    key={t}
                    className="inline-flex items-center gap-1 text-xs bg-primary/10 text-primary px-2 py-1 rounded-full"
                  >
                    <CheckCircle2 className="h-3 w-3" />
                    {t}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-xs text-muted-foreground">
                No triggers available
              </p>
            )}
          </div>

          <Button
            onClick={toggleCoverage}
            variant={policy.status === 'active' ? 'outline' : 'default'}
            className="w-full mt-6"
            disabled={toggling}
          >
            {toggling ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : policy.status === 'active' ? (
              'Pause Coverage'
            ) : (
              'Activate Coverage'
            )}
          </Button>
        </div>

        {/* RISK */}
        <div className="rounded-lg border bg-card p-6 shadow-card">
          <div className="flex items-center gap-2 mb-4">
            <Brain className="h-5 w-5 text-primary" />
            <h2 className="font-semibold">AI Risk Assessment</h2>
          </div>

          <div className="flex items-center justify-center py-8">
            <div className="relative">
              <svg className="w-32 h-32" viewBox="0 0 120 120">
                <circle cx="60" cy="60" r="54" fill="none" stroke="hsl(var(--muted))" strokeWidth="8" />
                <circle
                  cx="60"
                  cy="60"
                  r="54"
                  fill="none"
                  stroke="hsl(var(--primary))"
                  strokeWidth="8"
                  strokeDasharray={`${(riskScore / 100) * 339} 339`}
                  strokeLinecap="round"
                  transform="rotate(-90 60 60)"
                />
              </svg>

              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-3xl font-bold">{riskScore}</span>
                <span className="text-xs text-muted-foreground">
                  Risk Score
                </span>
              </div>
            </div>
          </div>

          <div className="space-y-2 text-sm">
            <p className="text-muted-foreground">
              Your risk score is calculated using:
            </p>

            <ul className="space-y-1 text-muted-foreground list-disc list-inside">
              <li>Zone-specific weather history</li>
              <li>Platform demand patterns</li>
              <li>Seasonal risk factors</li>
              <li>Working hours exposure</li>
            </ul>
          </div>
        </div>

      </div>
    </>
  ) : (
    <p className="text-muted-foreground text-sm">No policy found</p>
  )}
</div>

);
};

export default PolicyPage;
