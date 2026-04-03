import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { AlertTriangle, TrendingDown, CloudRain, Thermometer, ArrowRight } from 'lucide-react';

const NeedPage = () => (
  <div>
    <section className="gradient-hero py-16 md:py-24">
      <div className="container text-center">
        <h1 className="text-3xl md:text-5xl font-extrabold text-primary-foreground">Why Gig Workers Need GigSurance</h1>
        <p className="mt-4 text-lg text-primary-foreground/70 max-w-2xl mx-auto">Traditional insurance wasn't built for you. We are.</p>
      </div>
    </section>

    <section className="py-16 bg-background">
      <div className="container max-w-4xl">
        <div className="rounded-lg border bg-card p-8 shadow-card mb-8">
          <h2 className="text-2xl font-bold mb-4">Meet Vikram</h2>
          <p className="text-muted-foreground leading-relaxed">
            Vikram drives for a ride-hailing platform in Mumbai. During last summer's heatwave, temperatures hit 45°C. 
            Demand plummeted — riders stayed indoors. Vikram lost ₹3,000 in potential earnings that week. He had no insurance that covered this. 
            No claim to file, because technically nothing "happened" to him.
          </p>
          <p className="mt-4 text-muted-foreground leading-relaxed">
            With GigSurance, Vikram would have received an automatic payout of ₹350 the moment temperatures crossed the 42°C threshold. 
            No forms. No waiting. No claim denial.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          {[
            { icon: Thermometer, title: 'Extreme Heat', desc: 'When it\'s too hot to work safely, demand drops and earnings vanish.' },
            { icon: CloudRain, title: 'Heavy Rainfall', desc: 'Floods and heavy rain make roads unsafe and reduce ride requests.' },
            { icon: AlertTriangle, title: 'Civil Disruptions', desc: 'Strikes, protests, or shutdowns can halt gig work entirely.' },
          ].map(r => (
            <div key={r.title} className="rounded-lg border bg-card p-6 shadow-card text-center">
              <div className="rounded-full bg-destructive/10 p-3 w-fit mx-auto"><r.icon className="h-6 w-6 text-destructive" /></div>
              <h3 className="mt-3 font-semibold">{r.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{r.desc}</p>
            </div>
          ))}
        </div>

        <div className="rounded-lg border bg-card p-8 shadow-card">
          <div className="flex items-start gap-4">
            <TrendingDown className="h-8 w-8 text-destructive shrink-0 mt-1" />
            <div>
              <h3 className="text-xl font-bold">The Market Gap</h3>
              <p className="mt-2 text-muted-foreground leading-relaxed">
                Over 15 million gig workers in India alone have zero income protection. Traditional insurance requires claims, 
                medical evidence, or property damage. Parametric insurance solves this by paying out based on measurable, 
                objective triggers — no questions asked.
              </p>
            </div>
          </div>
        </div>

        <div className="text-center mt-12">
          <Link to="/register"><Button size="lg" className="gap-2">Protect Your Income <ArrowRight className="h-4 w-4" /></Button></Link>
        </div>
      </div>
    </section>
  </div>
);

export default NeedPage;
