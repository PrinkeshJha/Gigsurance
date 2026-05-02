import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Shield, Zap, Brain, Cloud, ArrowRight, CheckCircle2 } from 'lucide-react';
import { ScrollReveal } from '@/components/ui/ScrollReveal';
import { PayoutDemo } from '@/components/interactive/PayoutDemo';

const features = [
  { icon: Zap, title: 'Instant Payouts', desc: 'No claims process. When triggers are met, money hits your account automatically.' },
  { icon: Brain, title: 'AI-Powered Pricing', desc: 'Smart premiums based on your zone, schedule, and real-time risk assessment.' },
  { icon: Cloud, title: 'Parametric Triggers', desc: 'Coverage activated by heat, rain, and civil disruption — verified by real data.' },
  { icon: Shield, title: 'Always Protected', desc: 'Continuous coverage with micro-weekly premiums. Cancel anytime.' },
];

const trustPoints = ['Trusted by 12,000+ gig workers', 'Zero claim denials', '₹23.4L+ paid out', '< 5 min payout time'];

const LandingPage = () => (
  <div className="overflow-hidden">
    {/* Hero Section */}
    <section className="relative mesh-bg py-20 md:py-32 overflow-hidden border-b border-border/50">
      <div className="container relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          
          {/* Left Column - Text */}
          <motion.div 
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7, ease: "easeOut" }}
            className="text-left"
          >
            <div className="inline-flex items-center gap-2 rounded-full glass-panel px-4 py-1.5 text-sm font-medium text-primary mb-6 shadow-sm">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
              </span>
              Live: AI-Powered Parametric Coverage
            </div>
            
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-extrabold tracking-tight text-foreground leading-[1.1]">
              Income Protection That<br />
              <span className="text-primary bg-clip-text text-transparent bg-gradient-to-r from-primary to-accent">
                Works Automatically
              </span>
            </h1>
            
            <p className="mt-6 text-lg md:text-xl text-muted-foreground max-w-xl">
              GigSurance protects gig workers from income loss due to extreme weather and disruptions. No claims — just automatic payouts when conditions are met.
            </p>
            
            <div className="mt-8 flex flex-col sm:flex-row gap-4">
              <Link to="/register">
                <Button size="lg" className="gap-2 px-8 shadow-elevated h-14 text-base">
                  Get Started Free <ArrowRight className="h-5 w-5" />
                </Button>
              </Link>
              <Link to="/about">
                <Button size="lg" variant="outline" className="glass-panel text-foreground hover:bg-background/50 h-14 text-base px-8 border-primary/20">
                  How It Works
                </Button>
              </Link>
            </div>
            
            <div className="mt-12 flex flex-wrap gap-x-6 gap-y-3">
              {trustPoints.map((t, i) => (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 + (i * 0.1) }}
                  key={t} 
                  className="flex items-center gap-2 text-sm font-medium text-muted-foreground"
                >
                  <CheckCircle2 className="h-4 w-4 text-success" /> {t}
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Right Column - Interactive Demo */}
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.7, delay: 0.2, ease: "easeOut" }}
            className="lg:ml-auto w-full"
          >
            <PayoutDemo />
          </motion.div>

        </div>
      </div>
    </section>

    {/* Features */}
    <section className="py-24 bg-background relative">
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>
      <div className="container relative z-10">
        <ScrollReveal direction="up" className="text-center mb-16">
          <h2 className="text-4xl font-bold tracking-tight">Insurance, Reimagined</h2>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            Built from scratch for the gig economy. No paperwork, no waiting, no denied claims.
          </p>
        </ScrollReveal>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((f, i) => (
            <ScrollReveal key={f.title} delay={i * 0.1} direction="up">
              <div className="rounded-2xl glass-card p-8 h-full transition-all duration-300 hover:-translate-y-1 hover:shadow-elevated group relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                <div className="relative z-10">
                  <div className="rounded-xl bg-primary/10 p-4 w-fit mb-6 ring-1 ring-primary/20 group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                    <f.icon className="h-6 w-6" />
                  </div>
                  <h3 className="text-xl font-bold text-foreground mb-3">{f.title}</h3>
                  <p className="text-muted-foreground leading-relaxed">{f.desc}</p>
                </div>
              </div>
            </ScrollReveal>
          ))}
        </div>
      </div>
    </section>

    {/* CTA */}
    <section className="py-24 relative overflow-hidden">
      <div className="absolute inset-0 bg-primary/5" />
      <div className="absolute inset-y-0 w-full mesh-bg opacity-30" />
      
      <div className="container relative z-10">
        <ScrollReveal direction="up" className="glass-panel max-w-4xl mx-auto rounded-3xl p-12 text-center border-primary/20 shadow-elevated">
          <h2 className="text-4xl font-bold tracking-tight mb-6">Ready to Protect Your Income?</h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-10">
            Join thousands of gig workers who never worry about lost income from bad weather or disruptions.
          </p>
          <Link to="/register">
            <Button size="lg" className="h-14 px-10 text-lg shadow-lg hover:shadow-primary/25 transition-all">
              Start Free Trial <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </ScrollReveal>
      </div>
    </section>
  </div>
);

export default LandingPage;
