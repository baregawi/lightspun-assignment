#!/bin/bash

# Lightspun Assignment - Docker Build Script
# This script builds all Docker containers needed for the application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"

# Function to print colored output
print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

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

print_build() {
    echo -e "${YELLOW}[BUILD]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get Docker Compose command
get_docker_compose_cmd() {
    if command_exists docker-compose; then
        echo "docker-compose"
    elif docker compose version >/dev/null 2>&1; then
        echo "docker compose"
    else
        return 1
    fi
}

# Function to check Docker system info
check_docker_system() {
    print_status "Checking Docker system resources..."
    
    # Check available disk space (cross-platform)
    local available_space
    if command -v df >/dev/null 2>&1; then
        # Try different df formats for different systems
        if df -h . | grep -q "G\|T"; then
            available_space=$(df -h . | awk 'NR==2 {print $4}' | sed 's/[GT]//g' | cut -d. -f1)
            if [ -n "$available_space" ] && [ "$available_space" -lt 2 ] 2>/dev/null; then
                print_warning "Low disk space: ${available_space}GB available. Building images requires at least 2GB."
            fi
        fi
    fi
    
    # Check if Docker daemon has enough resources
    docker system df >/dev/null 2>&1 || print_warning "Cannot check Docker system usage"
    
    print_success "Docker system check completed"
}

# Function to clean up old images and containers
cleanup_docker() {
    print_status "Cleaning up old Docker resources..."
    
    # Remove stopped containers
    local stopped_containers=$(docker ps -a -q --filter "status=exited" 2>/dev/null || echo "")
    if [ ! -z "$stopped_containers" ]; then
        print_status "Removing stopped containers..."
        echo "$stopped_containers" | xargs docker rm >/dev/null 2>&1 || true
    fi
    
    # Remove dangling images
    local dangling_images=$(docker images -f "dangling=true" -q 2>/dev/null || echo "")
    if [ ! -z "$dangling_images" ]; then
        print_status "Removing dangling images..."
        echo "$dangling_images" | xargs docker rmi >/dev/null 2>&1 || true
    fi
    
    print_success "Docker cleanup completed"
}

# Function to build a specific service
build_service() {
    local service=$1
    local description=$2
    
    print_build "Building $description..."
    
    if $DOCKER_COMPOSE_CMD build $service; then
        print_success "$description built successfully"
        return 0
    else
        print_error "Failed to build $description"
        return 1
    fi
}

# Function to verify built images
verify_images() {
    print_status "Verifying built images..."
    
    # Use the actual project directory name (keeping hyphens)
    local project_name=$(basename $(pwd) | tr '[:upper:]' '[:lower:]')
    local images=(
        "${project_name}-backend"
        "${project_name}-frontend"
    )
    
    local all_present=true
    
    for image in "${images[@]}"; do
        if docker images --format "{{.Repository}}" | grep -q "^${image}$"; then
            print_success "✓ $image"
        else
            print_error "✗ $image (not found)"
            all_present=false
        fi
    done
    
    if $all_present; then
        print_success "All images verified successfully"
        return 0
    else
        print_error "Some images are missing"
        return 1
    fi
}

# Function to show image sizes
show_image_info() {
    print_status "Docker image information:"
    
    local project_name=$(basename $(pwd) | tr '[:upper:]' '[:lower:]')
    
    echo ""
    printf "%-30s %-15s %-15s %-20s\n" "IMAGE" "SIZE" "CREATED" "ID"
    echo "--------------------------------------------------------------------------------"
    
    docker images --format "table {{.Repository}}\t{{.Size}}\t{{.CreatedSince}}\t{{.ID}}" | grep -E "(${project_name}|postgres)" || true
    
    echo ""
}

# Function to build all services
build_all_services() {
    print_header "🔨 Building Docker Images"
    
    local services_built=0
    local services_failed=0
    
    # Build backend
    if build_service "backend" "FastAPI Backend"; then
        services_built=$((services_built + 1))
    else
        services_failed=$((services_failed + 1))
    fi
    
    # Build frontend
    if build_service "frontend" "React Frontend"; then
        services_built=$((services_built + 1))
    else
        services_failed=$((services_failed + 1))
    fi
    
    # PostgreSQL uses official image, no build needed
    print_status "PostgreSQL Database: Using official postgres:15 image"
    
    echo ""
    print_status "Build Summary:"
    print_status "  Services built: $services_built"
    if [ $services_failed -gt 0 ]; then
        print_error "  Services failed: $services_failed"
        return 1
    else
        print_success "  All services built successfully"
        return 0
    fi
}

# Main function
main() {
    print_header "🚀 Lightspun Assignment - Docker Build"
    
    # Check prerequisites
    print_status "Checking prerequisites..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        print_error "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    DOCKER_COMPOSE_CMD=$(get_docker_compose_cmd)
    if [ $? -ne 0 ]; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        print_error "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    # Check if compose file exists
    if [ ! -f "$COMPOSE_FILE" ]; then
        print_error "Docker Compose file '$COMPOSE_FILE' not found."
        exit 1
    fi
    
    print_success "All prerequisites found"
    print_status "Using Docker Compose command: $DOCKER_COMPOSE_CMD"
    
    # Check system resources
    check_docker_system
    
    # Parse command line arguments
    CLEAN=false
    FORCE=false
    VERBOSE=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --clean)
                CLEAN=true
                shift
                ;;
            --force)
                FORCE=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [options]"
                echo "Options:"
                echo "  --clean    Clean up old Docker resources before building"
                echo "  --force    Force rebuild (no cache)"
                echo "  --verbose  Show detailed build output"
                echo "  -h, --help Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Clean up if requested
    if $CLEAN; then
        cleanup_docker
    fi
    
    # Set build options
    BUILD_ARGS=""
    if $FORCE; then
        BUILD_ARGS="$BUILD_ARGS --no-cache"
        print_status "Force rebuild enabled (no cache)"
    fi
    
    if ! $VERBOSE; then
        BUILD_ARGS="$BUILD_ARGS --quiet"
    fi
    
    # Export build args for docker-compose
    export BUILD_ARGS
    
    # Build all services
    if build_all_services; then
        echo ""
        verify_images
        show_image_info
        
        print_header "🎉 Build Complete!"
        print_success "All Docker images built successfully"
        echo ""
        print_status "Next steps:"
        echo -e "  1. ${GREEN}Start the application:${NC} ./start-dev.sh"
        echo -e "  2. ${GREEN}View images:${NC} docker images"
        echo -e "  3. ${GREEN}Clean up:${NC} docker system prune"
        echo ""
        
        return 0
    else
        print_header "❌ Build Failed!"
        print_error "Some Docker images failed to build"
        print_error "Check the error messages above for details"
        echo ""
        print_status "Troubleshooting:"
        echo -e "  1. ${YELLOW}Check logs:${NC} $DOCKER_COMPOSE_CMD logs"
        echo -e "  2. ${YELLOW}Clean build:${NC} ./build.sh --clean --force"
        echo -e "  3. ${YELLOW}Check space:${NC} docker system df"
        echo ""
        
        return 1
    fi
}

# Run main function
main "$@"