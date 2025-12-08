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
    tracesSampleRate: 0,

    beforeSend(event) {
      if (event.level && event.level !== 'error' && event.level !== 'fatal') {
        return null;
      }
      return event;
    },
  });
}
