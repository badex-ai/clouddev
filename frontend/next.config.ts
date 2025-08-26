import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
   async redirects() {
    return [
      {
        source: '/settings',
        destination: '/settings/general',
        permanent: false, // Use false for temporary redirect (302)
      },
    ]
  },
};

export default nextConfig;
