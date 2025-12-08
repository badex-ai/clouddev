import type { NextConfig } from 'next';
import { withSentryConfig } from '@sentry/nextjs';

const nextConfig: NextConfig = {
  /* config options here */
  output: 'standalone',
  async redirects() {
    return [
      {
        source: '/settings',
        destination: '/settings/general',
        permanent: false, // Use false for temporary redirect (302)
      },
    ];
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ];
  },
};

// Only wrap with Sentry in staging or production
const appEnv = process.env.NEXT_PUBLIC_APP_ENV;
const isEnabled = appEnv === 'staging' || appEnv === 'production';

export default isEnabled
  ? withSentryConfig(nextConfig, {
      // Minimal Sentry build config for free tier
      silent: true, // Suppress build logs
      disableLogger: true,

      // Disable source maps upload for free tier (saves auth token requirement)
      sourcemaps: {
        disable: true,
      },

      // Disable telemetry
      telemetry: false,
    })
  : nextConfig;
