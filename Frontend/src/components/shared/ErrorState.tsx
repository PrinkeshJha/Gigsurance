import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

const ErrorState = ({ title = 'Something went wrong', message = 'Failed to load data. Please try again.', onRetry }: ErrorStateProps) => (
  <div className="flex flex-col items-center justify-center py-12 text-center">
    <div className="rounded-full bg-destructive/10 p-4 mb-4">
      <AlertCircle className="h-8 w-8 text-destructive" />
    </div>
    <h3 className="text-lg font-semibold text-card-foreground">{title}</h3>
    <p className="mt-1 text-sm text-muted-foreground max-w-sm">{message}</p>
    {onRetry && (
      <Button variant="outline" size="sm" className="mt-4" onClick={onRetry}>
        <RefreshCw className="h-4 w-4 mr-2" /> Try Again
      </Button>
    )}
  </div>
);

export default ErrorState;
