'use client';

import { ErrorBoundary } from '@/components/error-boundary';

export default function Error({
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
      title="Something went wrong"
      description="An unexpected error occurred. Please try again."
    />
  );
}
