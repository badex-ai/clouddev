interface Config {
  // Auth0 settings
  auth0Secret: string;
  auth0BaseUrl: string;
  auth0IssuerBaseUrl: string;
  auth0ClientId: string;
  auth0ClientSecret: string;
  auth0Scope: string;
  auth0Audience: string;
  auth0Domain: string;

  // App settings
  appBaseUrl: string;
  apiUrl: string;
  environment: string;
  debug: boolean;

  nextUrl: string;
}

let cachedConfig: Config | null = null;

export function getConfig(): Config {
  if (cachedConfig) {
    return cachedConfig;
  }

  const environment = process.env.ENVIRONMENT || 'dev';

  let auth0Secret: string;
  let auth0ClientSecret: string;

  auth0Secret = process.env.AUTH0_SECRET || '';
  auth0ClientSecret = process.env.AUTH0_CLIENT_SECRET || '';

  cachedConfig = {
    // Auth0 settings
    auth0Secret,
    auth0BaseUrl: process.env.AUTH0_BASE_URL || '',
    auth0IssuerBaseUrl: process.env.AUTH0_ISSUER_BASE_URL || '',
    auth0ClientId: process.env.AUTH0_CLIENT_ID || '',
    auth0ClientSecret,
    auth0Scope: process.env.AUTH0_SCOPE || 'openid profile email',
    auth0Audience: process.env.AUTH0_AUDIENCE || '',
    auth0Domain: process.env.AUTH0_DOMAIN || '',

    // App settings
    appBaseUrl: process.env.APP_BASE_URL || '',
    apiUrl: process.env.BACKEND_URL || '',
    nextUrl: process.env.NEXT_PUBLIC_API_URL || '',

    // Environment settings
    environment,
    debug: process.env.DEBUG?.toLowerCase() === 'true' || false,
  };

  return cachedConfig;
}
