import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Check, ArrowRight } from 'lucide-react';

const tiers = [
  { name: 'Basic', price: '₹29', period: '/week', features: ['Heat trigger coverage', 'Up to ₹500 payout/week', 'Basic zone coverage', 'Email notifications'], popular: false },
  { name: 'Standard', price: '₹49', period: '/week', features: ['Heat + Rain triggers', 'Up to ₹1,000 payout/week', 'Multi-zone coverage', 'Push + SMS alerts', 'AI risk insights'], popular: true },
  { name: 'Premium', price: '₹79', period: '/week', features: ['All trigger types', 'Up to ₹2,000 payout/week', 'Unlimited zones', 'Priority payouts', 'Advanced analytics', 'Dedicated support'], popular: false },
];

const PricingPage = () => (
  <div>
    <section className="gradient-hero py-16 md:py-24">
      <div className="container text-center">
        <h1 className="text-3xl md:text-5xl font-extrabold text-primary-foreground">Simple, Transparent Pricing</h1>
        <p className="mt-4 text-lg text-primary-foreground/70 max-w-2xl mx-auto">Micro-weekly premiums that fit your earnings. No hidden fees, cancel anytime.</p>
      </div>
    </section>

    <section className="py-16 bg-background">
      <div className="container">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {tiers.map(t => (
            <div key={t.name} className={`rounded-lg border p-8 shadow-card relative ${t.popular ? 'border-primary shadow-elevated ring-2 ring-primary/20' : 'bg-card'}`}>
              {t.popular && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 gradient-primary text-primary-foreground text-xs font-bold px-4 py-1 rounded-full">
                  Most Popular
                </span>
              )}
              <h3 className="text-xl font-bold">{t.name}</h3>
              <div className="mt-4">
                <span className="text-4xl font-extrabold">{t.price}</span>
                <span className="text-muted-foreground">{t.period}</span>
              </div>
              <ul className="mt-6 space-y-3">
                {t.features.map(f => (
                  <li key={f} className="flex items-center gap-2 text-sm"><Check className="h-4 w-4 text-success shrink-0" /> {f}</li>
                ))}
              </ul>
              <Link to="/register" className="block mt-8">
                <Button className="w-full gap-2" variant={t.popular ? 'default' : 'outline'}>
                  Get Started <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
            </div>
          ))}
        </div>

        <div className="mt-16 max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-6">How Micro-Deductions Work</h2>
          <div className="rounded-lg border bg-card p-8 shadow-card">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
              <div>
                <p className="text-3xl font-bold text-primary">₹7</p>
                <p className="text-sm text-muted-foreground mt-1">per day, deducted from earnings</p>
              </div>
              <div>
                <p className="text-3xl font-bold text-primary">₹49</p>
                <p className="text-sm text-muted-foreground mt-1">weekly cap, never more</p>
              </div>
              <div>
                <p className="text-3xl font-bold text-success">₹1,000</p>
                <p className="text-sm text-muted-foreground mt-1">max payout per trigger</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
);

export default PricingPage;
