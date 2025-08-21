// import type { NextRequest } from "next/server";
// import { auth0 } from "./lib/auth0";

// export async function middleware(request: NextRequest) {

//     console.log('🔍 Middleware triggered for:', request.nextUrl.pathname);
//   console.log('🔍 Request method:', request.method);
//   console.log('🔍 Request headers:', Object.fromEntries(request.headers.entries()));
//    const response = await auth0.middleware(request);

//    console.log('🔍 Auth0 middleware response status:', response?.status);
//   console.log('🔍 Auth0 middleware response headers:', Object.fromEntries(response?.headers.entries() || []));

//   return response;
// }

// export const config = {
//   matcher: [
//     /*
//      * Match all request paths except for the ones starting with:
//      * - _next/static (static files)
//      * - _next/image (image optimization files)
//      * - favicon.ico, sitemap.xml, robots.txt (metadata files)
//      */
//     "/((?!_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt).*)",
    

//     //  "/((?!_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt|dashboard|auth).*)",
//   ],
// };


import { NextRequest, NextResponse } from "next/server";
import { auth0 } from "./lib/auth0";

export async function middleware(request: NextRequest) {
  const authRes = await auth0.middleware(request);

  // console.log('middleware authresponse:  ', authRes)

  // Authentication routes — let the Auth0 middleware handle it.
  if (request.nextUrl.pathname.startsWith("/auth")) {
    return authRes;
  }

  const { origin } = new URL(request.url);
  const session = await auth0.getSession(request);

  // console.log('this is the session for the middleware', session)

  // User does not have a session — redirect to login.
  if (!session) {
    return NextResponse.redirect(`${origin}/auth/login`);
  }
  return authRes;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image, images (image optimization files)
     * - favicon.ico, sitemap.xml, robots.txt (metadata files)
     * - $ (root)
     */
    "/((?!_next/static|_next/image|images|favicon.[ico|png]|sitemap.xml|robots.txt|$).*)",
  ],
};