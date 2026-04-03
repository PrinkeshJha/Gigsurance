import { Skeleton } from '@/components/ui/skeleton';

export const CardSkeleton = () => (
  <div className="rounded-lg border bg-card p-5 space-y-3">
    <Skeleton className="h-4 w-24" />
    <Skeleton className="h-8 w-32" />
    <Skeleton className="h-3 w-20" />
  </div>
);

export const ListSkeleton = ({ rows = 5 }: { rows?: number }) => (
  <div className="space-y-3">
    {Array.from({ length: rows }).map((_, i) => (
      <div key={i} className="flex items-center gap-4 rounded-lg border bg-card p-4">
        <Skeleton className="h-10 w-10 rounded-lg" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-4 w-48" />
          <Skeleton className="h-3 w-32" />
        </div>
        <Skeleton className="h-6 w-16 rounded-full" />
      </div>
    ))}
  </div>
);

export const ChartSkeleton = () => (
  <div className="rounded-lg border bg-card p-5 space-y-4">
    <Skeleton className="h-5 w-36" />
    <Skeleton className="h-64 w-full rounded" />
  </div>
);

export const PageSkeleton = () => (
  <div className="space-y-6 p-6">
    <Skeleton className="h-8 w-48" />
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {Array.from({ length: 4 }).map((_, i) => <CardSkeleton key={i} />)}
    </div>
    <ChartSkeleton />
  </div>
);
