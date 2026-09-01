/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://pharos-backend-deployment--ojilerekingsley.replit.app',
  },
}

export default nextConfig
