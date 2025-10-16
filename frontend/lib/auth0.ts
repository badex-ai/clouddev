import { Auth0Client } from "@auth0/nextjs-auth0/server";
import {getConfig} from "./config"

  const { auth0Domain, auth0ClientId, auth0ClientSecret, auth0BaseUrl, auth0Secret,auth0Scope, auth0Audience} = getConfig()

export const auth0 = new Auth0Client({
  domain: auth0Domain,
  clientId: auth0ClientId,
  clientSecret: auth0ClientSecret,
  appBaseUrl: auth0BaseUrl,
  secret: auth0Secret,
  authorizationParameters: {
    scope: auth0Scope,
    audience: auth0Audience,
  }
});

