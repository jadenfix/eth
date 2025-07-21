#!/bin/bash
set -e

echo "🚀 Setting up Onchain Command Center local development environment"

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI not found. Please install from https://cloud.google.com/sdk"
    exit 1
fi

if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform not found. Please install from https://terraform.io"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Setup environment
echo "Setting up environment..."

if [ ! -f .env ]; then
    cp .env.sample .env
    echo "📝 Created .env file. Please edit it with your credentials."
    echo "   Required: GOOGLE_CLOUD_PROJECT, ALCHEMY_API_KEY"
fi

# Install Python dependencies
echo "Installing Python dependencies..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Install UI dependencies
echo "Installing UI dependencies..."
cd services/ui/nextjs-app
npm install
cd ../../..

# Setup GCP authentication
echo "Setting up Google Cloud authentication..."
if [ ! -f gcp-service-account.json ]; then
    echo "🔑 Please download your GCP service account key to gcp-service-account.json"
    echo "   Go to: https://console.cloud.google.com/iam-admin/serviceaccounts"
    echo "   Create a key for your service account and save as gcp-service-account.json"
else
    export GOOGLE_APPLICATION_CREDENTIALS="./gcp-service-account.json"
    echo "✅ GCP credentials configured"
fi

# Initialize Terraform
echo "Initializing Terraform..."
cd infra/gcp
terraform init
echo "✅ Terraform initialized"
cd ../..

# Start local services
echo "Starting local development services..."

# Start ingestion service in background
echo "Starting ingestion service..."
source venv/bin/activate
cd services/ingestion
python ethereum_ingester.py &
INGESTION_PID=$!
cd ../..

# Start ontology service in background  
echo "Starting ontology service..."
cd services/ontology
python graph_api.py &
ONTOLOGY_PID=$!
cd ../..

# Start MEV watch agent in background
echo "Starting MEV watch agent..."
cd services/agents/mev_watch
python agent.py &
MEV_AGENT_PID=$!
cd ../../..

# Start UI
echo "Starting UI dashboard..."
cd services/ui/nextjs-app
npm run dev &
UI_PID=$!
cd ../../..

echo "🎉 Local development environment started!"
echo ""
echo "Services running:"
echo "  • Ingestion Service: Running (PID: $INGESTION_PID)"
echo "  • Ontology Service: http://localhost:8000 (PID: $ONTOLOGY_PID)"
echo "  • MEV Watch Agent: Running (PID: $MEV_AGENT_PID)"
echo "  • UI Dashboard: http://localhost:3000 (PID: $UI_PID)"
echo ""
echo "GraphQL Playground: http://localhost:8000/graphql"
echo ""
echo "To stop all services, run: ./scripts/stop_dev_env.sh"

# Save PIDs for cleanup
echo "$INGESTION_PID,$ONTOLOGY_PID,$MEV_AGENT_PID,$UI_PID" > .dev_pids

echo "Press Ctrl+C to view logs..."
sleep 2

# Follow logs
tail -f services/*/logs/*.log 2>/dev/null || echo "No logs found yet. Services starting up..."
