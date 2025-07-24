#!/bin/bash

# Frontend Startup Script with Error Handling
# Ensures clean, stable launch on localhost:3000

set -e  # Exit on any error

echo "🚀 Starting ETH Hackathon Frontend with Stability Checks..."
echo "================================================================"

# Navigate to frontend directory
cd /Users/jadenfix/eth/services/ui/nextjs-app

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  Port $port is in use"
        return 0
    else
        echo "✅ Port $port is available"
        return 1
    fi
}

# Function to kill processes on port
kill_port() {
    local port=$1
    echo "🔧 Cleaning up port $port..."
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
    sleep 2
}

# Step 1: Clean up any existing processes
echo "🧹 Step 1: Cleaning up existing processes..."
pkill -f "next dev" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true

# Step 2: Check and clean port 3000
echo "🔍 Step 2: Checking port 3000..."
if check_port 3000; then
    kill_port 3000
fi

# Step 3: Clean Next.js cache
echo "🗂️  Step 3: Cleaning Next.js cache..."
rm -rf .next
rm -rf node_modules/.cache

# Step 4: Verify dependencies
echo "📦 Step 4: Verifying dependencies..."
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Step 5: Type check (quick validation)
echo "🔍 Step 5: Running type check..."
npm run type-check

# Step 6: Start development server
echo "🚀 Step 6: Starting development server on port 3000..."
echo "================================================================"
echo "Frontend will be available at: http://localhost:3000"
echo "Press Ctrl+C to stop the server"
echo "================================================================"

# Use exec to replace the shell process with npm
exec npm run dev
