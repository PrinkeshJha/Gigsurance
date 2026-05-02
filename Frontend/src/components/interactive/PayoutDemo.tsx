import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CloudRain, Sun, Zap, CheckCircle2, ShieldAlert } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function PayoutDemo() {
  const [status, setStatus] = useState<'idle' | 'checking' | 'paid'>('idle');
  const [triggerType, setTriggerType] = useState<'rain' | 'heat' | null>(null);

  const simulateTrigger = (type: 'rain' | 'heat') => {
    setTriggerType(type);
    setStatus('checking');
    
    // Simulate API call and weather check
    setTimeout(() => {
      setStatus('paid');
      
      // Reset after showing payout
      setTimeout(() => {
        setStatus('idle');
        setTriggerType(null);
      }, 5000);
    }, 2000);
  };

  return (
    <div className="glass-card rounded-2xl p-6 sm:p-8 w-full max-w-md mx-auto relative overflow-hidden shadow-elevated">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent pointer-events-none" />
      
      <div className="relative z-10 text-center">
        <div className="inline-flex items-center justify-center p-3 bg-primary/10 rounded-full mb-4">
          <Zap className="h-6 w-6 text-primary" />
        </div>
        <h3 className="text-xl font-bold mb-2">Live Demo: Auto-Payouts</h3>
        <p className="text-sm text-muted-foreground mb-6">
          Simulate a weather event to see how fast you get covered. No claims needed.
        </p>

        <div className="flex flex-col gap-3">
          <Button 
            variant="outline" 
            className="w-full justify-start gap-3 h-12"
            onClick={() => simulateTrigger('rain')}
            disabled={status !== 'idle'}
          >
            <CloudRain className="h-5 w-5 text-blue-500" />
            Trigger Heavy Rain (45mm/hr)
          </Button>
          
          <Button 
            variant="outline" 
            className="w-full justify-start gap-3 h-12"
            onClick={() => simulateTrigger('heat')}
            disabled={status !== 'idle'}
          >
            <Sun className="h-5 w-5 text-orange-500" />
            Trigger Extreme Heat (42°C)
          </Button>
        </div>

        <div className="h-28 mt-6 relative flex items-center justify-center border rounded-xl bg-background/50">
          <AnimatePresence mode="wait">
            {status === 'idle' && (
              <motion.div
                key="idle"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="text-muted-foreground flex flex-col items-center gap-2 text-sm"
              >
                <ShieldAlert className="h-5 w-5 opacity-50" />
                Waiting for weather triggers...
              </motion.div>
            )}
            
            {status === 'checking' && (
              <motion.div
                key="checking"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="flex flex-col items-center gap-3 text-sm font-medium"
              >
                <div className="relative flex h-8 w-8 items-center justify-center">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-4 w-4 bg-primary"></span>
                </div>
                Verifying {triggerType === 'rain' ? 'Rainfall' : 'Temperature'} Data...
              </motion.div>
            )}

            {status === 'paid' && (
              <motion.div
                key="paid"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                className="flex flex-col items-center gap-2"
              >
                <div className="bg-success/20 text-success rounded-full p-2">
                  <CheckCircle2 className="h-8 w-8" />
                </div>
                <div className="text-lg font-bold text-success">₹500 Credited!</div>
                <div className="text-xs text-muted-foreground">Instant payout via UPI</div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
