#!/bin/bash

echo "🔧 Completely resetting Next.js environment..."

# Kill any existing processes
pkill -f "next dev" || true
pkill -f "node.*next" || true

# Remove all build artifacts
echo "🧹 Cleaning build artifacts..."
rm -rf .next
rm -rf node_modules/.cache
rm -rf .next/cache

# Clear any additional caches
echo "🧹 Clearing additional caches..."
npm cache clean --force || true

echo "🚀 Starting fresh development server..."
npm run dev
