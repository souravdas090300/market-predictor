import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Remove build error ignoring - fix actual errors for better performance
  typescript: {
    ignoreBuildErrors: false,
  },
  transpilePackages: [],
  
  // Enable React strict mode for better performance
  reactStrictMode: true,
  
  // Compress responses for faster loading
  compress: true,
  
  // Optimize images
  images: {
    formats: ['image/avif', 'image/webp'],
    minimumCacheTTL: 60,
  },
  
  // Optimize production builds
  productionBrowserSourceMaps: false,
  
  // Static generation for landing page
  output: 'standalone',
  
  // Cache headers for API routes
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Cache-Control', value: 'public, max-age=60, s-maxage=60' },
        ],
      },
      {
        source: '/:path*',
        headers: [
          { key: 'X-DNS-Prefetch-Control', value: 'on' },
          { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
        ],
      },
    ];
  },
  
  // Use webpack for better path resolution compatibility
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': require('path').resolve(__dirname, 'src'),
    };
    return config;
  },
};

export default nextConfig;
