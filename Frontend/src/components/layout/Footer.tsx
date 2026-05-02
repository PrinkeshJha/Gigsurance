import { Link } from 'react-router-dom';
import { Shield } from 'lucide-react';

const Footer = () => (
  <footer className="border-t border-border bg-card py-12">
    <div className="container">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
        <div>
          <div className="flex items-center gap-2 font-bold text-lg mb-3">
            <Shield className="h-5 w-5 text-primary" />
            <span>Gig<span className="text-primary">Surance</span></span>
          </div>
          <p className="text-sm text-muted-foreground">AI-powered parametric insurance for gig workers. No claims, automatic payouts.</p>
        </div>
        <div>
          <h4 className="font-semibold mb-3 text-sm">Product</h4>
          <div className="space-y-2">
            <Link to="/need" className="block text-sm text-muted-foreground hover:text-primary">Why GigSurance</Link>
            <Link to="/pricing" className="block text-sm text-muted-foreground hover:text-primary">Pricing</Link>
            <Link to="/about" className="block text-sm text-muted-foreground hover:text-primary">How It Works</Link>
          </div>
        </div>
        <div>
          <h4 className="font-semibold mb-3 text-sm">Support</h4>
          <div className="space-y-2">
            <Link to="/contact" className="block text-sm text-muted-foreground hover:text-primary">Contact</Link>
            <Link to="/legal" className="block text-sm text-muted-foreground hover:text-primary">Legal</Link>
          </div>
        </div>
        <div>
          <h4 className="font-semibold mb-3 text-sm">Get Started</h4>
          <div className="space-y-2">
            <Link to="/register" className="block text-sm text-muted-foreground hover:text-primary">Create Account</Link>
            <Link to="/login" className="block text-sm text-muted-foreground hover:text-primary">Sign In</Link>
          </div>
        </div>
      </div>
      <div className="mt-8 pt-8 border-t border-border text-center text-sm text-muted-foreground">
        © 2026 GigSurance. All rights reserved.
      </div>
    </div>
  </footer>
);

export default Footer;
