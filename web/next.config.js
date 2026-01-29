/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:11434',
  },
  images: {
    domains: ['via.placeholder.com'],
  },
};

module.exports = nextConfig;