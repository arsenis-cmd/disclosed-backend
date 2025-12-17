/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ['@poc/shared', '@poc/database'],
}

module.exports = nextConfig
