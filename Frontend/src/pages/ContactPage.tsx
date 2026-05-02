import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Mail, MapPin, Phone, CheckCircle2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const ContactPage = () => {
  const [submitted, setSubmitted] = useState(false);
  const { toast } = useToast();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    toast({ title: 'Message sent!', description: 'We\'ll get back to you within 24 hours.' });
  };

  return (
    <div>
      <section className="gradient-hero py-16 md:py-24">
        <div className="container text-center">
          <h1 className="text-3xl md:text-5xl font-extrabold text-primary-foreground">Get In Touch</h1>
          <p className="mt-4 text-lg text-primary-foreground/70">We're here to help. Reach out anytime.</p>
        </div>
      </section>
      <section className="py-16 bg-background">
        <div className="container max-w-4xl">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h2 className="text-2xl font-bold mb-6">Contact Us</h2>
              {submitted ? (
                <div className="flex flex-col items-center justify-center py-12 text-center rounded-lg border bg-card p-8">
                  <CheckCircle2 className="h-12 w-12 text-success mb-4" />
                  <h3 className="text-lg font-semibold">Message Sent!</h3>
                  <p className="text-muted-foreground mt-2">We'll respond within 24 hours.</p>
                  <Button variant="outline" className="mt-4" onClick={() => setSubmitted(false)}>Send Another</Button>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div><label className="text-sm font-medium">Name</label><Input placeholder="Your name" required /></div>
                  <div><label className="text-sm font-medium">Email</label><Input type="email" placeholder="you@example.com" required /></div>
                  <div><label className="text-sm font-medium">Subject</label><Input placeholder="How can we help?" required /></div>
                  <div><label className="text-sm font-medium">Message</label><Textarea placeholder="Tell us more..." rows={5} required /></div>
                  <Button type="submit" className="w-full">Send Message</Button>
                </form>
              )}
            </div>
            <div className="space-y-6">
              <h2 className="text-2xl font-bold mb-6">Support Info</h2>
              {[
                { icon: Mail, label: 'Email', value: 'support@gigsurance.com' },
                { icon: Phone, label: 'Phone', value: '+91 1800-GIG-SURE' },
                { icon: MapPin, label: 'Office', value: 'Mumbai, Maharashtra, India' },
              ].map(c => (
                <div key={c.label} className="flex items-start gap-4 rounded-lg border bg-card p-4 shadow-card">
                  <div className="rounded-lg bg-primary/10 p-2.5"><c.icon className="h-5 w-5 text-primary" /></div>
                  <div><p className="font-medium text-sm">{c.label}</p><p className="text-sm text-muted-foreground">{c.value}</p></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default ContactPage;
