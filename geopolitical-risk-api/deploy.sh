#!/bin/bash

# Geopolitical Risk Assessment API - Deployment Script
# Supports multiple deployment targets and environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="geopolitical-risk-api"
DEFAULT_PORT=8001
HEALTH_CHECK_TIMEOUT=60

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    log_info "Checking deployment requirements..."
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        log_error ".env file not found. Please copy .env.example to .env and configure it."
        exit 1
    fi
    
    # Check for required environment variables
    if ! grep -q "OPENAI_API_KEY=" .env || grep -q "OPENAI_API_KEY=your_openai_api_key_here" .env; then
        log_error "OPENAI_API_KEY not configured in .env file"
        exit 1
    fi
    
    log_success "Requirements check passed"
}

test_api() {
    local base_url=$1
    local timeout=${2:-60}
    
    log_info "Testing API at $base_url (timeout: ${timeout}s)..."
    
    # Wait for service to be ready
    local count=0
    while [ $count -lt $timeout ]; do
        if curl -s -f "$base_url/health" > /dev/null 2>&1; then
            log_success "API is responding"
            break
        fi
        count=$((count + 5))
        sleep 5
        echo -n "."
    done
    
    if [ $count -ge $timeout ]; then
        log_error "API health check failed after ${timeout}s"
        return 1
    fi
    
    # Run quick test
    log_info "Running quick API test..."
    python3 test_api.py --quick --url "$base_url" || {
        log_warning "API tests had issues, but service is responding"
    }
    
    log_success "API testing completed"
}

deploy_local() {
    log_info "Deploying locally..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        log_info "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install/update dependencies
    log_info "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Validate configuration
    log_info "Validating configuration..."
    python3 config.py
    
    # Start the service
    log_info "Starting API service on port $DEFAULT_PORT..."
    
    # Kill existing process if running
    pkill -f "uvicorn main:app" || true
    sleep 2
    
    # Start in background
    nohup python3 main.py > logs/app.log 2>&1 &
    local pid=$!
    echo $pid > .api.pid
    
    log_success "API started with PID $pid"
    
    # Test the deployment
    sleep 5
    test_api "http://localhost:$DEFAULT_PORT"
    
    log_success "Local deployment completed successfully!"
    log_info "API running at: http://localhost:$DEFAULT_PORT"
    log_info "Documentation: http://localhost:$DEFAULT_PORT/docs"
    log_info "Logs: tail -f logs/app.log"
    log_info "Stop with: ./deploy.sh stop"
}

deploy_docker() {
    log_info "Deploying with Docker..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Build and start services
    log_info "Building Docker images..."
    docker-compose build
    
    log_info "Starting services..."
    docker-compose up -d
    
    # Wait for services to be ready
    log_info "Waiting for services to start..."
    sleep 10
    
    # Test the deployment
    test_api "http://localhost:$DEFAULT_PORT"
    
    log_success "Docker deployment completed successfully!"
    log_info "API running at: http://localhost:$DEFAULT_PORT"
    log_info "View logs: docker-compose logs -f"
    log_info "Stop with: docker-compose down"
}

deploy_render() {
    log_info "Preparing deployment for Render.com..."
    
    # Check if render.yaml exists
    if [ ! -f "render.yaml" ]; then
        log_info "Creating render.yaml configuration..."
        cat > render.yaml << EOF
services:
  - type: web
    name: $APP_NAME
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: NEWSAPI_KEY
        sync: false
      - key: PORT
        value: 10000
      - key: DEBUG
        value: false
      - key: LOG_LEVEL
        value: INFO
EOF
        log_success "render.yaml created"
    fi
    
    log_info "Render deployment configuration ready"
    log_info "Next steps:"
    log_info "1. Commit and push to GitHub"
    log_info "2. Connect repository to Render.com"
    log_info "3. Set environment variables in Render dashboard"
    log_info "4. Deploy from Render dashboard"
}

deploy_railway() {
    log_info "Preparing deployment for Railway..."
    
    # Check if railway CLI is installed
    if ! command -v railway &> /dev/null; then
        log_error "Railway CLI not installed. Install with: npm install -g @railway/cli"
        exit 1
    fi
    
    # Check if logged in
    if ! railway whoami &> /dev/null; then
        log_info "Please login to Railway first: railway login"
        exit 1
    fi
    
    # Initialize project if needed
    if [ ! -f "railway.json" ]; then
        log_info "Initializing Railway project..."
        railway init
    fi
    
    # Set environment variables
    log_info "Setting environment variables..."
    railway variables set PORT=$DEFAULT_PORT
    railway variables set DEBUG=false
    railway variables set LOG_LEVEL=INFO
    
    # Deploy
    log_info "Deploying to Railway..."
    railway up
    
    log_success "Railway deployment initiated"
    log_info "Check deployment status: railway status"
}

stop_local() {
    log_info "Stopping local deployment..."
    
    if [ -f ".api.pid" ]; then
        local pid=$(cat .api.pid)
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            log_success "Stopped API process (PID: $pid)"
        else
            log_warning "Process $pid not running"
        fi
        rm -f .api.pid
    else
        log_warning "No PID file found"
    fi
    
    # Also try to kill by process name
    pkill -f "uvicorn main:app" || true
    
    log_success "Local deployment stopped"
}

stop_docker() {
    log_info "Stopping Docker deployment..."
    docker-compose down
    log_success "Docker deployment stopped"
}

backup_data() {
    log_info "Creating backup..."
    
    local backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup configuration
    cp .env "$backup_dir/" 2>/dev/null || log_warning "No .env file to backup"
    
    # Backup logs
    if [ -d "logs" ]; then
        cp -r logs "$backup_dir/"
    fi
    
    # Backup Redis data if running
    if docker-compose ps redis | grep -q "Up"; then
        log_info "Backing up Redis data..."
        docker-compose exec -T redis redis-cli --rdb - > "$backup_dir/redis_backup.rdb"
    fi
    
    log_success "Backup created at $backup_dir"
}

show_status() {
    log_info "Deployment Status"
    echo "===================="
    
    # Local deployment
    if [ -f ".api.pid" ]; then
        local pid=$(cat .api.pid)
        if kill -0 $pid 2>/dev/null; then
            echo "Local: Running (PID: $pid)"
        else
            echo "Local: Stopped (stale PID file)"
        fi
    else
        echo "Local: Stopped"
    fi
    
    # Docker deployment
    if docker-compose ps | grep -q "Up"; then
        echo "Docker: Running"
        docker-compose ps
    else
        echo "Docker: Stopped"
    fi
    
    # Test connectivity
    echo ""
    log_info "Testing connectivity..."
    if curl -s -f "http://localhost:$DEFAULT_PORT/health" > /dev/null 2>&1; then
        echo "✅ API responding at http://localhost:$DEFAULT_PORT"
    else
        echo "❌ API not responding at http://localhost:$DEFAULT_PORT"
    fi
}

show_help() {
    cat << EOF
Geopolitical Risk Assessment API - Deployment Script

Usage: $0 [COMMAND]

Commands:
    local       Deploy locally with Python virtual environment
    docker      Deploy using Docker Compose
    render      Prepare deployment for Render.com
    railway     Deploy to Railway
    stop        Stop local deployment
    stop-docker Stop Docker deployment
    backup      Create backup of data and configuration
    status      Show deployment status
    test        Test running API
    help        Show this help message

Examples:
    $0 local                    # Deploy locally
    $0 docker                   # Deploy with Docker
    $0 test                     # Test running API
    $0 status                   # Check status
    $0 stop                     # Stop local deployment

Environment Variables:
    PORT                        # Service port (default: $DEFAULT_PORT)
    OPENAI_API_KEY             # Required: OpenAI API key
    NEWSAPI_KEY                # Optional: NewsAPI key
    DEBUG                      # Enable debug mode
    
For more information, see README.md
EOF
}

# Main script logic
case "${1:-help}" in
    "local")
        check_requirements
        deploy_local
        ;;
    "docker")
        check_requirements
        deploy_docker
        ;;
    "render")
        check_requirements
        deploy_render
        ;;
    "railway")
        check_requirements
        deploy_railway
        ;;
    "stop")
        stop_local
        ;;
    "stop-docker")
        stop_docker
        ;;
    "backup")
        backup_data
        ;;
    "status")
        show_status
        ;;
    "test")
        test_api "http://localhost:$DEFAULT_PORT"
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac