const LegalPage = () => (
  <div>
    <section className="gradient-hero py-16 md:py-24">
      <div className="container text-center">
        <h1 className="text-3xl md:text-5xl font-extrabold text-primary-foreground">Legal</h1>
        <p className="mt-4 text-lg text-primary-foreground/70">Terms, privacy, and coverage details.</p>
      </div>
    </section>
    <section className="py-16 bg-background">
      <div className="container max-w-3xl prose prose-sm">
        <div className="rounded-lg border bg-card p-8 shadow-card mb-8">
          <h2 className="text-2xl font-bold mb-4">Terms & Conditions</h2>
          <div className="space-y-3 text-sm text-muted-foreground">
            <p>By using GigSurance, you agree to these terms. GigSurance provides parametric insurance coverage where payouts are determined by objective, measurable environmental triggers.</p>
            <p><strong className="text-foreground">Eligibility:</strong> Active gig workers aged 18+ registered on supported platforms in covered zones.</p>
            <p><strong className="text-foreground">Premium Payments:</strong> Weekly micro-deductions from linked earnings. Coverage lapses if premium is unpaid for 2 consecutive weeks.</p>
            <p><strong className="text-foreground">Payouts:</strong> Automatic upon trigger verification. Payouts are credited within 24 hours of trigger confirmation.</p>
            <p><strong className="text-foreground">Dispute Resolution:</strong> All disputes shall be resolved through arbitration in Mumbai, India.</p>
          </div>
        </div>

        <div className="rounded-lg border bg-card p-8 shadow-card mb-8">
          <h2 className="text-2xl font-bold mb-4">Privacy Policy</h2>
          <div className="space-y-3 text-sm text-muted-foreground">
            <p>We collect: name, email, location zone, platform data, and working hours. This data is used solely for risk assessment and service delivery.</p>
            <p>We do not sell personal data to third parties. Environmental and weather data is sourced from public APIs and government databases.</p>
            <p>You may request data deletion at any time by contacting support@gigsurance.com.</p>
          </div>
        </div>

        <div className="rounded-lg border bg-card p-8 shadow-card">
          <h2 className="text-2xl font-bold mb-4">Coverage Exclusions</h2>
          <ul className="space-y-2 text-sm text-muted-foreground list-disc list-inside">
            <li>Self-inflicted inability to work</li>
            <li>Pre-existing medical conditions</li>
            <li>Voluntary absence from work</li>
            <li>Platform account suspension or deactivation</li>
            <li>Events outside covered zones</li>
            <li>Nuclear, biological, or chemical events</li>
            <li>Fraudulent activity or misrepresentation</li>
          </ul>
        </div>
      </div>
    </section>
  </div>
);

export default LegalPage;
