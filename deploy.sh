#!/bin/bash
set -e

echo "🔗 Onchain Command Center - Complete Deployment Script"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_warning "This script is optimized for macOS. Some commands may need adjustment for other platforms."
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Homebrew if not present
install_homebrew() {
    if ! command_exists brew; then
        print_status "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        print_success "Homebrew installed successfully"
    else
        print_success "Homebrew is already installed"
    fi
}

# Function to install Python dependencies
install_python_deps() {
    print_status "Setting up Python environment..."
    
    # Check for Python 3.9+
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
        print_status "Found Python $PYTHON_VERSION"
    else
        print_error "Python 3 is required but not found. Please install Python 3.9+ first."
        exit 1
    fi
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install Python dependencies
    if [ -f "requirements.txt" ]; then
        print_status "Installing Python dependencies..."
        pip install -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Function to install Node.js dependencies
install_node_deps() {
    print_status "Setting up Node.js environment..."
    
    # Check for Node.js
    if ! command_exists node; then
        print_status "Installing Node.js via Homebrew..."
        brew install node
        print_success "Node.js installed"
    else
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION is already installed"
    fi
    
    # Install global packages
    print_status "Installing global npm packages..."
    npm install -g typescript @types/node prettier eslint
    
    # Install project dependencies
    if [ -f "package.json" ]; then
        print_status "Installing Node.js project dependencies..."
        npm install
        print_success "Node.js dependencies installed"
    fi
    
    # Install UI dependencies
    if [ -d "services/ui/nextjs-app" ]; then
        print_status "Installing Next.js dependencies..."
        cd services/ui/nextjs-app
        npm install
        cd ../../..
        print_success "Next.js dependencies installed"
    fi
}

# Function to install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    # Install required system packages
    brew_packages=(
        "docker"
        "docker-compose"
        "terraform"
        "jq"
        "curl"
        "wget"
        "git"
        "redis"
        "postgresql"
        "portaudio"  # For voice recognition
    )
    
    for package in "${brew_packages[@]}"; do
        if brew list "$package" &>/dev/null; then
            print_success "$package is already installed"
        else
            print_status "Installing $package..."
            brew install "$package"
            print_success "$package installed"
        fi
    done
    
    # Start Docker if not running
    if ! docker info &>/dev/null; then
        print_status "Starting Docker..."
        open -a Docker
        print_warning "Please wait for Docker to start, then run this script again"
        exit 1
    else
        print_success "Docker is running"
    fi
}

# Function to setup environment variables
setup_environment() {
    print_status "Setting up environment variables..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.sample" ]; then
            print_status "Copying .env.sample to .env..."
            cp .env.sample .env
            print_warning "Please edit .env file with your actual API keys and configuration"
            print_warning "Required: GCP_PROJECT_ID, ETHEREUM_RPC_URL, ELEVENLABS_API_KEY, etc."
        else
            print_error ".env.sample not found. Please create .env file manually."
        fi
    else
        print_success ".env file already exists"
    fi
}

# Function to setup GCP infrastructure
setup_gcp_infrastructure() {
    print_status "Setting up GCP infrastructure..."
    
    # Check if gcloud is installed
    if ! command_exists gcloud; then
        print_status "Installing Google Cloud SDK..."
        brew install google-cloud-sdk
        print_warning "Please run 'gcloud auth login' and 'gcloud config set project YOUR_PROJECT_ID' before proceeding"
        return
    fi
    
    # Check if authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_warning "Please run 'gcloud auth login' first"
        return
    fi
    
    # Initialize Terraform
    if [ -d "infra/gcp" ]; then
        print_status "Initializing Terraform..."
        cd infra/gcp
        terraform init
        
        print_status "Planning Terraform deployment..."
        terraform plan
        
        print_warning "Review the Terraform plan above. Run 'terraform apply' manually when ready to deploy."
        cd ../..
    fi
}

# Function to build Docker images
build_docker_images() {
    print_status "Building Docker images..."
    
    if [ -f "docker-compose.yml" ]; then
        print_status "Building all services with Docker Compose..."
        docker-compose build
        print_success "Docker images built successfully"
    else
        # Build individual services
        services=(
            "services/ethereum_ingester"
            "services/graph_api"
            "services/mev_agent"
            "services/entity_resolution"
            "services/access_control"
            "services/voiceops"
            "services/monitoring"
            "services/dashboard"
        )
        
        for service in "${services[@]}"; do
            if [ -f "$service/Dockerfile" ]; then
                print_status "Building $service..."
                docker build -t "onchain-$(basename $service)" "$service"
                print_success "$service image built"
            fi
        done
    fi
}

# Function to run database migrations and setup
setup_databases() {
    print_status "Setting up databases..."
    
    # Start local Redis for development
    if command_exists redis-server; then
        if ! pgrep redis-server > /dev/null; then
            print_status "Starting Redis server..."
            brew services start redis
            print_success "Redis server started"
        else
            print_success "Redis server is already running"
        fi
    fi
    
    # Setup BigQuery schemas (if credentials are available)
    if [ -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
        print_status "Setting up BigQuery schemas..."
        # This would run the BigQuery schema creation scripts
        print_success "BigQuery schemas would be created here"
    else
        print_warning "GOOGLE_APPLICATION_CREDENTIALS not set. Skipping BigQuery setup."
    fi
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    
    # Activate Python virtual environment
    source venv/bin/activate
    
    # Run Python tests
    if [ -d "tests" ]; then
        print_status "Running Python tests..."
        python -m pytest tests/ -v
        print_success "Python tests passed"
    fi
    
    # Run TypeScript tests
    if [ -f "package.json" ] && npm run | grep -q test; then
        print_status "Running Node.js tests..."
        npm test
        print_success "Node.js tests passed"
    fi
    
    # Run linting
    print_status "Running code linting..."
    
    # Python linting
    if command_exists black; then
        black --check services/ || print_warning "Black formatting issues found"
    fi
    
    if command_exists flake8; then
        flake8 services/ || print_warning "Flake8 linting issues found"
    fi
    
    # TypeScript linting
    if command_exists eslint; then
        npx eslint services/ui/nextjs-app/src/ || print_warning "ESLint issues found"
    fi
}

# Function to start development services
start_dev_services() {
    print_status "Starting development services..."
    
    # Start with Docker Compose if available
    if [ -f "docker-compose.yml" ]; then
        print_status "Starting services with Docker Compose..."
        docker-compose up -d
        print_success "All services started with Docker Compose"
    else
        # Start individual services
        print_status "Starting individual services..."
        
        # Start Python services in background
        source venv/bin/activate
        
        # Ethereum Ingester
        print_status "Starting Ethereum Ingester..."
        cd services/ethereum_ingester
        python ethereum_ingester.py &
        echo $! > ../../pids/ethereum_ingester.pid
        cd ../..
        
        # Graph API
        print_status "Starting Graph API..."
        cd services/graph_api
        python graph_api.py &
        echo $! > ../../pids/graph_api.pid
        cd ../..
        
        # MEV Agent
        print_status "Starting MEV Agent..."
        cd services/mev_agent
        python mev_agent.py &
        echo $! > ../../pids/mev_agent.pid
        cd ../..
        
        # Status Dashboard
        print_status "Starting Status Dashboard..."
        cd services/dashboard
        python status_dashboard.py &
        echo $! > ../../pids/status_dashboard.pid
        cd ../..
        
        # Health Monitoring
        print_status "Starting Health Monitoring..."
        cd services/monitoring
        python health_service.py &
        echo $! > ../../pids/health_service.pid
        cd ../..
        
        # Next.js UI
        print_status "Starting Next.js UI..."
        cd services/ui/nextjs-app
        npm run dev &
        echo $! > ../../../pids/nextjs.pid
        cd ../../..
        
        print_success "All development services started"
    fi
    
    # Create pids directory for process tracking
    mkdir -p pids
}

# Function to show service status
show_status() {
    echo ""
    print_success "🔗 Onchain Command Center Deployment Complete!"
    echo ""
    echo "📊 Service URLs:"
    echo "  • Main Dashboard:      http://localhost:3000"
    echo "  • Status Dashboard:    http://localhost:8004/dashboard"
    echo "  • Graph API:           http://localhost:8002/graphql"
    echo "  • REST API:            http://localhost:8001/docs"
    echo "  • Health Metrics:      http://localhost:8000/metrics"
    echo ""
    echo "🔧 Useful Commands:"
    echo "  • View logs:           docker-compose logs -f [service]"
    echo "  • Stop all services:   docker-compose down"
    echo "  • Restart service:     docker-compose restart [service]"
    echo "  • Run tests:           ./deploy.sh --test-only"
    echo ""
    echo "📁 Key Files:"
    echo "  • Configuration:       .env"
    echo "  • Infrastructure:      infra/gcp/"
    echo "  • Services:            services/"
    echo "  • Documentation:       README.md"
    echo ""
    echo "⚠️  Next Steps:"
    echo "  1. Edit .env with your actual API keys"
    echo "  2. Run 'gcloud auth login' for GCP access"
    echo "  3. Deploy infrastructure: 'cd infra/gcp && terraform apply'"
    echo "  4. Monitor services at status dashboard"
    echo ""
}

# Function to cleanup on exit
cleanup() {
    print_status "Cleaning up..."
    
    # Kill background processes if they exist
    if [ -d "pids" ]; then
        for pidfile in pids/*.pid; do
            if [ -f "$pidfile" ]; then
                pid=$(cat "$pidfile")
                if kill -0 "$pid" 2>/dev/null; then
                    print_status "Stopping process $pid..."
                    kill "$pid"
                fi
                rm "$pidfile"
            fi
        done
        rmdir pids 2>/dev/null || true
    fi
}

# Set up cleanup on script exit
trap cleanup EXIT

# Main deployment logic
main() {
    case "${1:-full}" in
        "deps-only")
            install_homebrew
            install_system_deps
            install_python_deps
            install_node_deps
            ;;
        "build-only")
            build_docker_images
            ;;
        "test-only")
            run_tests
            ;;
        "infra-only")
            setup_gcp_infrastructure
            ;;
        "dev-only")
            start_dev_services
            show_status
            ;;
        "full"|*)
            print_status "Starting full deployment..."
            
            # Check prerequisites
            print_status "Checking prerequisites..."
            
            # Install dependencies
            install_homebrew
            install_system_deps
            install_python_deps
            install_node_deps
            
            # Setup environment
            setup_environment
            
            # Setup databases
            setup_databases
            
            # Build Docker images
            build_docker_images
            
            # Setup GCP infrastructure (optional)
            setup_gcp_infrastructure
            
            # Run tests
            run_tests
            
            # Start development services
            start_dev_services
            
            # Show final status
            show_status
            
            print_success "Deployment completed! Press Ctrl+C to stop all services."
            
            # Keep script running to maintain services
            while true; do
                sleep 30
            done
            ;;
    esac
}

# Script usage
if [[ "${1}" == "--help" ]] || [[ "${1}" == "-h" ]]; then
    echo "Usage: $0 [option]"
    echo ""
    echo "Options:"
    echo "  full        Complete deployment (default)"
    echo "  deps-only   Install dependencies only"
    echo "  build-only  Build Docker images only"
    echo "  test-only   Run tests only"
    echo "  infra-only  Setup GCP infrastructure only"
    echo "  dev-only    Start development services only"
    echo "  --help      Show this help message"
    echo ""
    exit 0
fi

# Run main function
main "$1"
