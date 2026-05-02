import { Brain, Cloud, Zap, Shield, CheckCircle2, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';

const steps = [
  { num: '01', title: 'Sign Up & Onboard', desc: 'Select your gig platform, zone, and working hours. Our AI calculates your risk profile instantly.' },
  { num: '02', title: 'Automatic Monitoring', desc: 'We continuously monitor environmental conditions in your zone — temperature, rainfall, AQI, and civil events.' },
  { num: '03', title: 'Trigger Detection', desc: 'When conditions breach predefined thresholds (e.g., >42°C), a trigger event is automatically recorded.' },
  { num: '04', title: 'Instant Payout', desc: 'No claim needed. Payouts are calculated and credited to your account within minutes of a trigger.' },
];

const AboutPage = () => (
  <div>
    <section className="gradient-hero py-16 md:py-24">
      <div className="container text-center">
        <h1 className="text-3xl md:text-5xl font-extrabold text-primary-foreground">How GigSurance Works</h1>
        <p className="mt-4 text-lg text-primary-foreground/70 max-w-2xl mx-auto">AI + parametric triggers = automatic income protection.</p>
      </div>
    </section>

    <section className="py-16 bg-background">
      <div className="container max-w-4xl">
        {/* Workflow */}
        <div className="space-y-6 mb-16">
          {steps.map(s => (
            <div key={s.num} className="flex gap-6 items-start rounded-lg border bg-card p-6 shadow-card">
              <span className="text-3xl font-extrabold text-primary/30">{s.num}</span>
              <div>
                <h3 className="text-lg font-bold">{s.title}</h3>
                <p className="mt-1 text-muted-foreground">{s.desc}</p>
              </div>
            </div>
          ))}
        </div>

        {/* AI/ML */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-16">
          <div className="rounded-lg border bg-card p-8 shadow-card">
            <Brain className="h-8 w-8 text-primary mb-4" />
            <h3 className="text-xl font-bold">AI Risk Scoring</h3>
            <p className="mt-2 text-muted-foreground text-sm leading-relaxed">
              Our machine learning model analyzes your zone's historical weather patterns, platform demand data, 
              and seasonal trends to calculate a personalized risk score. Higher risk = slightly higher premium, 
              but also higher potential payouts.
            </p>
          </div>
          <div className="rounded-lg border bg-card p-8 shadow-card">
            <Shield className="h-8 w-8 text-primary mb-4" />
            <h3 className="text-xl font-bold">Fraud Detection</h3>
            <p className="mt-2 text-muted-foreground text-sm leading-relaxed">
              Since triggers are based on objective, third-party environmental data (weather stations, government APIs), 
              fraud is virtually impossible. No self-reported claims means no false claims.
            </p>
          </div>
        </div>

        {/* Triggers */}
        <div className="rounded-lg border bg-card p-8 shadow-card">
          <h3 className="text-xl font-bold mb-4">Trigger System</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { icon: '🌡️', name: 'Extreme Heat', threshold: 'Temperature > 42°C', payout: '₹150-350' },
              { icon: '🌧️', name: 'Heavy Rainfall', threshold: 'Rainfall > 100mm/day', payout: '₹100-300' },
              { icon: '⚠️', name: 'Civil Disruption', threshold: 'Official advisory issued', payout: '₹200-500' },
            ].map(t => (
              <div key={t.name} className="rounded-lg bg-muted p-4 text-center">
                <p className="text-2xl mb-2">{t.icon}</p>
                <p className="font-semibold text-sm">{t.name}</p>
                <p className="text-xs text-muted-foreground mt-1">{t.threshold}</p>
                <p className="text-xs font-medium text-success mt-1">{t.payout}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="text-center mt-12">
          <Link to="/register"><Button size="lg" className="gap-2">Get Protected Now <ArrowRight className="h-4 w-4" /></Button></Link>
        </div>
      </div>
    </section>
  </div>
);

export default AboutPage;
