'use client';

import { ErrorBoundary } from '@/components/error-boundary';

export default function SettingsError({
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
      title="Settings error"
      description="We couldn't load your settings. Please try again."
    />
  );
}
