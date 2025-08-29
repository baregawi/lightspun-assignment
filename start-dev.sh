#!/bin/bash

# Lightspun Assignment - Development Startup Script
# This script starts all services using Docker Compose

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_PORT=8000
FRONTEND_PORT=3000
POSTGRES_PORT=5432
COMPOSE_FILE="docker-compose.yml"

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

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
is_port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=60
    local attempt=1

    print_status "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        if [ $((attempt % 10)) -eq 0 ]; then
            print_status "Still waiting for $service_name... (attempt $attempt/$max_attempts)"
        fi
        
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name failed to start within $((max_attempts * 2)) seconds"
    return 1
}

# Function to check Docker service health
check_service_health() {
    local service=$1
    local status=$(docker-compose ps -q $service | xargs docker inspect --format='{{.State.Health.Status}}' 2>/dev/null || echo "none")
    
    if [ "$status" = "healthy" ]; then
        return 0
    elif [ "$status" = "unhealthy" ]; then
        return 1
    elif [ "$status" = "starting" ]; then
        return 2
    else
        # No health check or service not running
        local running=$(docker-compose ps -q $service | xargs docker inspect --format='{{.State.Running}}' 2>/dev/null || echo "false")
        if [ "$running" = "true" ]; then
            return 0
        else
            return 1
        fi
    fi
}

# Function to wait for Docker service to be healthy
wait_for_docker_service() {
    local service=$1
    local service_name=$2
    local max_attempts=60
    local attempt=1

    print_status "Waiting for $service_name to be healthy..."
    
    while [ $attempt -le $max_attempts ]; do
        check_service_health $service
        local health_status=$?
        
        if [ $health_status -eq 0 ]; then
            print_success "$service_name is healthy!"
            return 0
        elif [ $health_status -eq 2 ]; then
            if [ $((attempt % 10)) -eq 0 ]; then
                print_status "$service_name is starting... (attempt $attempt/$max_attempts)"
            fi
        else
            if [ $((attempt % 10)) -eq 0 ]; then
                print_status "Still waiting for $service_name... (attempt $attempt/$max_attempts)"
            fi
        fi
        
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name failed to become healthy within $((max_attempts * 2)) seconds"
    return 1
}

# Function to cleanup on exit
cleanup() {
    print_status "Shutting down services..."
    
    # Stop all services
    docker-compose down >/dev/null 2>&1 || true
    
    print_success "All services stopped"
    exit 0
}

# Trap cleanup on exit
trap cleanup EXIT INT TERM

print_status "🚀 Starting Lightspun Assignment Development Environment"
echo "=================================================================="

# Check prerequisites
print_status "Checking prerequisites..."

if ! command_exists docker; then
    print_error "Docker is not installed. Please install Docker first."
    print_error "Visit: https://docs.docker.com/get-docker/"
    print_error ""
    print_error "Installation guides:"
    print_error "  macOS: Download Docker Desktop from docker.com"
    print_error "  Ubuntu: sudo apt-get install docker.io docker-compose"
    print_error "  CentOS: sudo yum install docker docker-compose"
    exit 1
fi

if ! command_exists docker-compose; then
    # Try docker compose (newer syntax)
    if ! docker compose version >/dev/null 2>&1; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        print_error "Visit: https://docs.docker.com/compose/install/"
        exit 1
    else
        # Use newer docker compose syntax
        DOCKER_COMPOSE_CMD="docker compose"
    fi
else
    DOCKER_COMPOSE_CMD="docker-compose"
fi

# Check if Docker daemon is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker daemon is not running. Please start Docker first."
    print_error "  macOS/Windows: Start Docker Desktop"
    print_error "  Linux: sudo systemctl start docker"
    exit 1
fi

print_success "All prerequisites found"

# Check if compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    print_error "Docker Compose file '$COMPOSE_FILE' not found."
    exit 1
fi

# Check for port conflicts
print_status "Checking for port conflicts..."

if is_port_in_use $BACKEND_PORT; then
    print_warning "Port $BACKEND_PORT is already in use. Attempting to stop conflicting services..."
    $DOCKER_COMPOSE_CMD down >/dev/null 2>&1 || true
    sleep 2
    if is_port_in_use $BACKEND_PORT; then
        print_error "Port $BACKEND_PORT is still in use. Please free the port manually."
        print_error "Try: lsof -ti:$BACKEND_PORT | xargs kill -9"
        exit 1
    fi
fi

if is_port_in_use $FRONTEND_PORT; then
    print_warning "Port $FRONTEND_PORT is already in use. Attempting to stop conflicting services..."
    $DOCKER_COMPOSE_CMD down >/dev/null 2>&1 || true
    sleep 2
    if is_port_in_use $FRONTEND_PORT; then
        print_error "Port $FRONTEND_PORT is still in use. Please free the port manually."
        print_error "Try: lsof -ti:$FRONTEND_PORT | xargs kill -9"
        exit 1
    fi
fi

# Check if images are built, if not suggest building
print_status "🔍 Checking if Docker images are built..."

# Get project name (used in image naming, keeping hyphens)
PROJECT_NAME=$(basename $(pwd) | tr '[:upper:]' '[:lower:]')

# Check if images exist
BACKEND_IMAGE="${PROJECT_NAME}-backend"
FRONTEND_IMAGE="${PROJECT_NAME}-frontend"

if ! docker images --format "{{.Repository}}" | grep -q "^${BACKEND_IMAGE}$" || \
   ! docker images --format "{{.Repository}}" | grep -q "^${FRONTEND_IMAGE}$"; then
    print_warning "Docker images not found. Building them now..."
    print_status "Running: ./build.sh"
    
    if [ -x "./build.sh" ]; then
        ./build.sh
        if [ $? -ne 0 ]; then
            print_error "Failed to build Docker images"
            print_error "Try running: ./build.sh --clean --force"
            exit 1
        fi
    else
        print_error "build.sh script not found or not executable"
        print_error "Please run: chmod +x build.sh && ./build.sh"
        exit 1
    fi
else
    print_success "Docker images found"
fi

# Start services
print_status "🐳 Starting Docker services..."
$DOCKER_COMPOSE_CMD up -d

# Wait for database to be ready
print_status "🐘 Waiting for PostgreSQL database..."
if ! wait_for_docker_service "postgres" "PostgreSQL Database"; then
    print_error "Failed to start database"
    print_error "Check logs with: $DOCKER_COMPOSE_CMD logs postgres"
    exit 1
fi

# Wait for backend to be ready
print_status "🔥 Waiting for FastAPI backend..."
if ! wait_for_service "http://localhost:$BACKEND_PORT/" "Backend API"; then
    print_error "Failed to start backend API"
    print_error "Check logs with: $DOCKER_COMPOSE_CMD logs backend"
    exit 1
fi

# Wait for frontend to be ready
print_status "⚛️  Waiting for React frontend..."
if ! wait_for_service "http://localhost:$FRONTEND_PORT/" "Frontend App"; then
    print_error "Failed to start frontend app"
    print_error "Check logs with: $DOCKER_COMPOSE_CMD logs frontend"
    exit 1
fi

# Success message
echo ""
print_success "🎉 All services are running successfully!"
echo "=================================================================="
echo ""
echo -e "${GREEN}🌐 Frontend Application: ${BLUE}http://localhost:$FRONTEND_PORT${NC}"
echo -e "${GREEN}🔧 Backend API:          ${BLUE}http://localhost:$BACKEND_PORT${NC}"
echo -e "${GREEN}📚 API Documentation:    ${BLUE}http://localhost:$BACKEND_PORT/docs${NC}"
echo -e "${GREEN}🐘 PostgreSQL Database:  ${BLUE}localhost:$POSTGRES_PORT${NC}"
echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo -e "  📋 View logs:           ${BLUE}$DOCKER_COMPOSE_CMD logs -f${NC}"
echo -e "  📋 View specific logs:  ${BLUE}$DOCKER_COMPOSE_CMD logs -f [backend|frontend|postgres]${NC}"
echo -e "  🔄 Restart service:     ${BLUE}$DOCKER_COMPOSE_CMD restart [service_name]${NC}"
echo -e "  ⚡ Rebuild service:     ${BLUE}$DOCKER_COMPOSE_CMD up -d --build [service_name]${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Keep script running and monitor services
while true; do
    # Check if all services are still running
    if ! $DOCKER_COMPOSE_CMD ps --quiet postgres backend frontend >/dev/null 2>&1; then
        print_error "One or more services have stopped unexpectedly"
        print_status "Current service status:"
        $DOCKER_COMPOSE_CMD ps
        exit 1
    fi
    
    sleep 10
done