import * as Sentry from '@sentry/nextjs';

// Initialize Sentry in staging or production environments
const appEnv = process.env.NEXT_PUBLIC_APP_ENV;
const isEnabled = appEnv === 'staging' || appEnv === 'production';
const dsn = process.env.NEXT_PUBLIC_SENTRY_DSN;

if (isEnabled && dsn) {
  Sentry.init({
    dsn,
    environment: appEnv,

    // Minimal configuration for free tier - just error logging
    tracesSampleRate: 0, // Disable performance tracing to save quota
    replaysSessionSampleRate: 0, // Disable session replays
    replaysOnErrorSampleRate: 0, // Disable error replays

    // Only capture errors, not warnings or info
    beforeSend(event) {
      // Filter out non-error events to save quota
      if (event.level && event.level !== 'error' && event.level !== 'fatal') {
        return null;
      }
      return event;
    },

    // Ignore common non-critical errors
    ignoreErrors: [
      // Network errors that are usually transient
      'Network request failed',
      'Failed to fetch',
      'Load failed',
      // Browser extension errors
      /^chrome-extension:\/\//,
      /^moz-extension:\/\//,
      // User aborted requests
      'AbortError',
      'The operation was aborted',
    ],
  });
}
