'use client';

import { ErrorBoundary } from '@/components/error-boundary';

export default function MainError({
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
      title="Unable to load this page"
      description="We encountered an error loading this page. Please try again or return to the dashboard."
    />
  );
}
