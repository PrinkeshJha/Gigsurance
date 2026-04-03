import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Shield, Zap, Brain, Cloud, ArrowRight, CheckCircle2 } from 'lucide-react';

const features = [
  { icon: Zap, title: 'Instant Payouts', desc: 'No claims process. When triggers are met, money hits your account automatically.' },
  { icon: Brain, title: 'AI-Powered Pricing', desc: 'Smart premiums based on your zone, schedule, and real-time risk assessment.' },
  { icon: Cloud, title: 'Parametric Triggers', desc: 'Coverage activated by heat, rain, and civil disruption — verified by real data.' },
  { icon: Shield, title: 'Always Protected', desc: 'Continuous coverage with micro-weekly premiums. Cancel anytime.' },
];

const trustPoints = ['Trusted by 12,000+ gig workers', 'Zero claim denials', '₹23.4L+ paid out', '< 5 min payout time'];

const LandingPage = () => (
  <div>
    {/* Hero */}
    <section className="gradient-hero py-20 md:py-32">
      <div className="container text-center">
        <div className="inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary mb-6">
          <Zap className="h-3.5 w-3.5" /> AI-Powered Parametric Insurance
        </div>
        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-primary-foreground max-w-4xl mx-auto leading-tight">
          Income Protection That<br />
          <span className="text-primary">Works Automatically</span>
        </h1>
        <p className="mt-6 text-lg md:text-xl text-primary-foreground/70 max-w-2xl mx-auto">
          GigSurance protects gig workers from income loss due to extreme weather and disruptions. No claims — just automatic payouts when conditions are met.
        </p>
        <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
          <Link to="/register">
            <Button size="lg" className="gap-2 px-8">Get Started Free <ArrowRight className="h-4 w-4" /></Button>
          </Link>
          <Link to="/about">
            <Button size="lg" variant="outline" className="border-primary-foreground/20 text-primary-foreground hover:bg-primary-foreground/10">
              How It Works
            </Button>
          </Link>
        </div>
        <div className="mt-12 flex flex-wrap justify-center gap-6">
          {trustPoints.map(t => (
            <div key={t} className="flex items-center gap-2 text-sm text-primary-foreground/60">
              <CheckCircle2 className="h-4 w-4 text-accent" /> {t}
            </div>
          ))}
        </div>
      </div>
    </section>

    {/* Features */}
    <section className="py-20 bg-background">
      <div className="container">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold">Insurance, Reimagined</h2>
          <p className="mt-3 text-muted-foreground max-w-xl mx-auto">Built from scratch for the gig economy. No paperwork, no waiting, no denied claims.</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map(f => (
            <div key={f.title} className="rounded-lg border bg-card p-6 shadow-card hover:shadow-elevated transition-shadow">
              <div className="rounded-lg bg-primary/10 p-3 w-fit"><f.icon className="h-6 w-6 text-primary" /></div>
              <h3 className="mt-4 font-semibold text-card-foreground">{f.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>

    {/* CTA */}
    <section className="py-20 bg-muted">
      <div className="container text-center">
        <h2 className="text-3xl font-bold">Ready to Protect Your Income?</h2>
        <p className="mt-3 text-muted-foreground max-w-lg mx-auto">Join thousands of gig workers who never worry about lost income from bad weather or disruptions.</p>
        <Link to="/register">
          <Button size="lg" className="mt-8 gap-2 px-8">Start Free Trial <ArrowRight className="h-4 w-4" /></Button>
        </Link>
      </div>
    </section>
  </div>
);

export default LandingPage;
