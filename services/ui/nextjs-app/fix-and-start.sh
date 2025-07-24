#!/bin/bash

# Fix Next.js Development Issues
echo "🔧 Fixing Next.js development environment..."

# Kill any existing Next.js processes
echo "🛑 Stopping existing processes..."
pkill -f "next dev" || true

# Clear Next.js cache
echo "🧹 Clearing Next.js cache..."
rm -rf .next

# Clear node_modules cache for problematic packages
echo "🧹 Clearing package cache..."
rm -rf node_modules/.cache

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build the application
echo "🏗️ Building application..."
npm run build

# Start development server
echo "🚀 Starting development server..."
npm run dev
