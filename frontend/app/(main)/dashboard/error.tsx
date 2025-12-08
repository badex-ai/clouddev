'use client';

import { ErrorBoundary } from '@/components/error-boundary';

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <ErrorBoundary
      error={error}
      reset={reset}
      title="Dashboard error"
      description="We couldn't load your dashboard. Please try again."
    />
  );
}
