export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    await import('./sentry.server.config');
  }

  if (process.env.NEXT_RUNTIME === 'edge') {
    await import('./sentry.edge.config');
  }
}

export const onRequestError = async (
  error: Error & { digest?: string },
  request: {
    path: string;
    method: string;
    headers: Record<string, string>;
  },
  context: {
    routerKind: string;
    routePath: string;
    routeType: string;
    renderSource: string;
    revalidateReason: string | undefined;
    renderType: string;
  }
) => {
  // Only report in staging or production
  const appEnv = process.env.NEXT_PUBLIC_APP_ENV;
  const isEnabled = appEnv === 'staging' || appEnv === 'production';
  if (!isEnabled) return;

  const Sentry = await import('@sentry/nextjs');
  Sentry.captureException(error, {
    tags: {
      routerKind: context.routerKind,
      routePath: context.routePath,
      routeType: context.routeType,
    },
    extra: {
      request: {
        path: request.path,
        method: request.method,
      },
    },
  });
};
