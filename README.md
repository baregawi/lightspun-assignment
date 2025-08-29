# Lightspun Assignment - US States and Addresses API

A full-stack web application providing a comprehensive API for US states, municipalities, and addresses with fuzzy search capabilities and a React frontend interface.

## 🏗️ Architecture Overview

- **Backend**: FastAPI with PostgreSQL database
- **Frontend**: React 18 with modular component architecture
- **Database**: PostgreSQL with advanced search capabilities (trigram, soundex)
- **Testing**: Comprehensive unit and integration test suite
- **Deployment**: Docker-based containerization

## 📋 Table of Contents

- [Backend Setup](#-backend-setup)
- [Frontend Setup](#-frontend-setup)  
- [Docker Deployment](#-docker-deployment)
- [Testing](#-testing)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)

## 🚀 Backend Setup

### Prerequisites

- Python 3.9 or higher
- PostgreSQL 12+ (or use Docker)
- pip (Python package manager)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd lightspun-assignment
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**
   
   **Option A: Use Docker (Recommended)**
   ```bash
   # Start PostgreSQL container
   docker-compose up postgres -d
   
   # Wait for database to be ready
   docker-compose logs postgres
   ```
   
   **Option B: Local PostgreSQL**
   ```bash
   # Create database (adapt for your PostgreSQL setup)
   createdb lightspun_db
   ```

5. **Configure environment variables**
   ```bash
   # Create .env file (optional - defaults work with Docker)
   echo "DATABASE_URL=postgresql://user:password@localhost:5432/lightspun_db" > .env
   echo "ENVIRONMENT=development" >> .env
   ```

6. **Initialize database**
   ```bash
   python3 -m lightspun.init_db
   ```

### Starting the Backend Server

```bash
# Development mode (with auto-reload)
uvicorn lightspun.app:app --host 0.0.0.0 --port 8000 --reload

# Production mode
uvicorn lightspun.app:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- **API Base URL**: http://localhost:8000
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

### Backend Testing

```bash
# Run all tests
python3 -m pytest

# Run unit tests only
python3 -m pytest tests/unit/ -v

# Run integration tests only  
python3 -m pytest tests/integration/ -v

# Run with coverage report
python3 -m pytest --cov=lightspun --cov-report=html

# Run specific test categories
python3 -m pytest -m state          # State-related tests
python3 -m pytest -m municipality   # Municipality-related tests
python3 -m pytest -m address        # Address-related tests

# Run standalone test scripts
python3 tests/unit/test_address_parsing.py
python3 tests/unit/test_street_standardization.py
python3 tests/integration/test_config.py
```

### Backend Configuration

The application supports multiple environments:

- **Development**: `ENVIRONMENT=development` (default)
- **Production**: `ENVIRONMENT=production`
- **Testing**: `ENVIRONMENT=testing`

Key configuration options:
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/lightspun_db

# API Settings
API_TITLE="Custom API Title"
API_DEBUG=true

# Logging
LOG_LEVEL=DEBUG
LOG_FORMAT=colored  # colored, json, simple

# Security
SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## 🌐 Frontend Setup

### Prerequisites

- Node.js 16+ and npm
- Backend API running (see above)

### Local Development Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure API endpoint**
   ```bash
   # Create .env file for API URL (optional - defaults work)
   echo "REACT_APP_API_URL=http://localhost:8000" > .env
   ```

### Starting the Frontend

```bash
# Development mode (with hot reload)
npm start

# The application will open at http://localhost:3000
```

### Frontend Testing

```bash
# Run all tests
npm test

# Run tests in CI mode
npm test -- --ci --coverage

# Run tests with coverage
npm test -- --coverage --watchAll=false
```

### Building for Production

```bash
# Create production build
npm run build

# The build files will be in the 'build' directory
# Serve with any static file server:
npx serve -s build -l 3000
```

### Frontend Development

The frontend uses a modular architecture:

- **Components**: Reusable UI components in `src/components/`
- **Hooks**: Custom React hooks in `src/hooks/`
- **Services**: API integration in `src/services/`
- **Utils**: Utility functions in `src/utils/`
- **Constants**: Configuration constants in `src/constants/`

Key features:
- **Progressive Form**: State → Municipality → Address selection
- **Real-time API Integration**: Dynamic data loading
- **Autocomplete**: Fuzzy search for addresses
- **Responsive Design**: Mobile-friendly interface
- **Error Handling**: User-friendly error messages

## 🐳 Docker Deployment

### Quick Start with Docker Compose

```bash
# Start all services (database, backend, frontend)
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

This will start:
- **PostgreSQL**: http://localhost:5432
- **Backend API**: http://localhost:8000
- **Frontend App**: http://localhost:3000

### Individual Service Management

```bash
# Start only database
docker-compose up postgres -d

# Start backend (requires database)
docker-compose up backend -d

# Start frontend (requires backend)
docker-compose up frontend -d

# Scale backend for load balancing
docker-compose up --scale backend=3
```

### Production Deployment

```bash
# Build production images
docker-compose build

# Start with production environment
ENVIRONMENT=production docker-compose up -d

# Monitor health
docker-compose ps
docker-compose logs backend
```

## 🧪 Testing

### Comprehensive Test Suite

The project includes comprehensive unit and integration tests:

```bash
# Run all tests with coverage
python3 -m pytest --cov=lightspun --cov-report=html

# Test specific components
python3 -m pytest tests/unit/services/test_state_service.py
python3 -m pytest tests/integration/api/test_states_api.py

# Test with different markers
python3 -m pytest -m "not slow"     # Skip slow tests
python3 -m pytest -m integration    # Integration tests only
python3 -m pytest -m unit          # Unit tests only
```

### Test Categories

- **Unit Tests**: Service layer, utilities, parsing logic
- **Integration Tests**: API endpoints, database operations, configuration
- **Frontend Tests**: React components, hooks, utilities

### Manual Testing Scripts

```bash
# Test address parsing
python3 tests/unit/test_address_parsing.py

# Test street standardization  
python3 tests/unit/test_street_standardization.py

# Test configuration system
python3 tests/integration/test_config.py

# Test fuzzy search (requires database)
python3 tests/integration/test_fuzzy_search.py
```

## 📚 API Documentation

### Main Endpoints

**States**
```
GET    /states                    # List all states
GET    /states/{state_code}       # Get state by code (e.g., "CA")
POST   /states                    # Create new state
PUT    /states/{state_id}         # Update state
DELETE /states/{state_id}         # Delete state
```

**Municipalities**
```
GET    /states/{state_code}/municipalities  # Get municipalities by state
GET    /municipalities/{municipality_id}    # Get municipality by ID
POST   /municipalities                     # Create municipality
PUT    /municipalities/{municipality_id}    # Update municipality  
DELETE /municipalities/{municipality_id}    # Delete municipality
```

**Addresses**
```
GET    /addresses/autocomplete             # Autocomplete search
GET    /addresses/{address_id}             # Get address by ID
GET    /municipalities/{id}/addresses      # Get addresses by municipality
POST   /addresses                         # Create address
PUT    /addresses/{address_id}            # Update address
DELETE /addresses/{address_id}            # Delete address
```

### Interactive Documentation

When the backend is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Features

- **Fuzzy Search**: Typo-tolerant address search using trigram similarity
- **Phonetic Matching**: Soundex-based street name matching
- **Autocomplete**: Real-time address suggestions
- **Data Validation**: Pydantic schema validation
- **Error Handling**: Comprehensive error responses
- **CORS Support**: Frontend integration ready

## 📁 Project Structure

```
lightspun-assignment/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── docker-compose.yml          # Multi-container deployment
├── Dockerfile                  # Backend container
├── docker-entrypoint.sh       # Backend startup script
├── build.sh                    # Docker container build script
├── start-dev.sh                # One-command development startup
│
├── lightspun/                  # Backend Python package
│   ├── __init__.py
│   ├── app.py                 # FastAPI application
│   ├── database.py            # Database configuration
│   ├── models.py              # SQLAlchemy models
│   ├── schemas.py             # Pydantic schemas
│   ├── services.py            # Legacy service imports
│   ├── init_db.py            # Database initialization
│   ├── logging_config.py     # Logging configuration
│   │
│   ├── config/               # Configuration system
│   │   ├── __init__.py
│   │   ├── base.py          # Base configuration
│   │   ├── development.py   # Development settings
│   │   ├── production.py    # Production settings
│   │   └── testing.py       # Testing settings
│   │
│   ├── services/            # Business logic layer
│   │   ├── __init__.py
│   │   ├── state_service.py
│   │   ├── municipality_service.py
│   │   └── address_service.py
│   │
│   ├── core/               # Core functionality
│   │   ├── __init__.py
│   │   ├── address_processing.py
│   │   └── fuzzy_search.py
│   │
│   └── utils/              # Utility functions
│       ├── __init__.py
│       ├── database_operations.py
│       └── street_standardization.py
│
├── frontend/               # React frontend
│   ├── package.json       # Node.js dependencies
│   ├── Dockerfile         # Frontend container
│   ├── public/           # Static assets
│   └── src/
│       ├── components/   # React components
│       │   ├── AddressForm.js
│       │   ├── StateSelect.js
│       │   ├── MunicipalitySelect.js
│       │   ├── AddressAutocomplete.js
│       │   └── ui/       # Reusable UI components
│       ├── hooks/        # Custom React hooks
│       ├── services/     # API integration
│       ├── utils/        # Utility functions
│       └── constants/    # Configuration constants
│
└── tests/                # Comprehensive test suite
    ├── README.md         # Testing documentation
    ├── pytest.ini       # Test configuration
    ├── conftest.py      # Global test fixtures
    ├── requirements.txt # Test dependencies
    │
    ├── unit/            # Unit tests
    │   ├── services/    # Service layer tests
    │   └── test_*.py    # Individual unit tests
    │
    ├── integration/     # Integration tests
    │   ├── api/        # API endpoint tests
    │   └── test_*.py   # Integration tests
    │
    ├── utils/          # Test utilities
    └── fixtures/       # Test data fixtures
```

## 🚀 Quick Start Guide

### ⚡ Quick Start (Recommended)

**Start everything with Docker (no local setup needed):**

```bash
./start-dev.sh
```

This script will:
- ✅ Check Docker and Docker Compose are installed
- ✅ Build all Docker images automatically (calls build.sh if needed)
- ✅ Start PostgreSQL database container
- ✅ Start FastAPI backend container
- ✅ Start React frontend container
- ✅ Initialize database with required tables
- ✅ Display all service URLs
- ✅ Monitor services and provide graceful shutdown

### 🔧 Manual Build (If Needed)

**Build Docker images manually:**

```bash
# Build all Docker images
./build.sh

# Build with options
./build.sh --clean --force  # Clean build with no cache
./build.sh --verbose        # Show detailed build output
```

### 🔧 Alternative Setup (Local Development)

**If you prefer local development without Docker:**

```bash
# 1. Install dependencies manually
sudo apt-get install docker.io python3.9 nodejs npm  # Ubuntu/Debian
brew install docker python node                      # macOS

# 2. Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Set up frontend
cd frontend && npm install && cd ..

# 4. Start services manually
docker-compose up postgres -d          # Database only
uvicorn lightspun.app:app --reload     # Backend
cd frontend && npm start               # Frontend
```

## 🔨 Build Script (`build.sh`)

### Usage

```bash
# Make script executable (if needed)
chmod +x build.sh

# Build all Docker images
./build.sh

# Build with options
./build.sh --clean          # Clean up old Docker resources first
./build.sh --force          # Force rebuild (no cache)
./build.sh --verbose        # Show detailed build output
./build.sh --clean --force  # Complete clean rebuild
```

### What It Builds

**Docker Images:**
- ✅ **Backend Image** - FastAPI application with Python dependencies
- ✅ **Frontend Image** - React application with Node.js build environment
- ✅ **PostgreSQL** - Uses official postgres:15 image (no build needed)

**Build Process:**
- ✅ **System Resource Check** - Verifies available disk space and Docker resources
- ✅ **Docker Cleanup** - Removes old containers and dangling images (with --clean)
- ✅ **Image Building** - Builds backend and frontend containers
- ✅ **Verification** - Confirms all images built successfully
- ✅ **Size Report** - Shows built image information and sizes

### Supported Platforms

The build script works on any system with Docker installed:

| Platform | Docker Support | Status |
|----------|----------------|--------|
| Ubuntu 18.04+ | Docker CE | ✅ Fully Supported |
| Ubuntu 20.04+ | Docker CE | ✅ Fully Supported |
| Ubuntu 22.04+ | Docker CE | ✅ Fully Supported |
| Debian 10+ | Docker CE | ✅ Fully Supported |
| CentOS 7+ | Docker CE | ✅ Supported |
| CentOS 8+ | Docker CE | ✅ Fully Supported |
| RHEL 8+ | Docker CE | ✅ Fully Supported |
| Fedora 35+ | Docker CE | ✅ Fully Supported |
| macOS 11+ | Docker Desktop | ✅ Fully Supported |
| macOS 12+ | Docker Desktop | ✅ Fully Supported |
| macOS 13+ | Docker Desktop | ✅ Fully Supported |
| Windows 10+ | Docker Desktop | ✅ Supported |

### Build Process

The script follows this automated process:

1. **🔍 Prerequisites Check**
   ```bash
   # Checks Docker and Docker Compose installation
   # Verifies Docker daemon is running
   # Confirms docker-compose.yml exists
   ```

2. **💾 System Resource Check**
   ```bash
   # Checks available disk space (minimum 2GB)
   # Verifies Docker system resources
   # Reports Docker space usage
   ```

3. **🧹 Docker Cleanup (Optional)**
   ```bash
   # Removes stopped containers
   # Removes dangling images
   # Frees up disk space for build
   ```

4. **🔨 Image Building**
   ```bash
   # Builds FastAPI backend image
   # Builds React frontend image
   # Uses Docker Compose build system
   ```

5. **✅ Verification**
   ```bash
   # Confirms all images were built
   # Shows image sizes and information
   # Provides next steps
   ```

6. **📊 Build Summary**
   ```bash
   # Reports build success/failure
   # Shows troubleshooting steps if needed
   # Displays useful commands
   ```

### Smart Features

**Version Management:**
- Checks minimum required versions (Python 3.9+, Node.js 16+)
- Upgrades existing installations if below minimum
- Uses latest stable versions when installing fresh

**Intelligent Installation:**
- Skips components already installed and up-to-date
- Automatically retries failed installations
- Provides alternative installation methods

**Cross-Platform Compatibility:**
- Detects package managers automatically
- Uses appropriate installation commands for each OS
- Handles platform-specific configurations

**Error Handling:**
- Validates each installation step
- Provides clear error messages with solutions
- Offers manual installation guidance for unsupported platforms

### Installation Output

**Successful build shows:**
```bash
🚀 Lightspun Assignment - Docker Build
================================

[INFO] Checking prerequisites...
[SUCCESS] All prerequisites found
[INFO] Using Docker Compose command: docker-compose
[INFO] Checking Docker system resources...
[SUCCESS] Docker system check completed

🔨 Building Docker Images
================================
[BUILD] Building FastAPI Backend...
[SUCCESS] FastAPI Backend built successfully
[BUILD] Building React Frontend...
[SUCCESS] React Frontend built successfully
[INFO] PostgreSQL Database: Using official postgres:15 image

[INFO] Build Summary:
[INFO]   Services built: 2
[SUCCESS]   All services built successfully

[INFO] Verifying built images...
[SUCCESS] ✓ lightspunassignment-backend
[SUCCESS] ✓ lightspunassignment-frontend
[SUCCESS] All images verified successfully

🎉 Build Complete!
================================
[SUCCESS] All Docker images built successfully

Next steps:
  1. Start the application: ./start-dev.sh
  2. View images: docker images
  3. Clean up: docker system prune
```

### Requirements

**Minimum System Requirements:**
- **RAM**: 4GB (8GB recommended for building)
- **Storage**: 2GB free space for Docker images
- **OS**: 64-bit operating system with Docker support
- **Network**: Internet connection for base image downloads

**Required Software:**
- **Docker Engine** 20.10+ or Docker Desktop
- **Docker Compose** v2.0+ (or docker compose plugin)
- **User permissions** to run Docker commands

### After Building

After successful build:

1. **Verify Built Images**
   ```bash
   # Check Docker images
   docker images | grep lightspun
   
   # View image details
   docker image inspect lightspunassignment-backend
   docker image inspect lightspunassignment-frontend
   ```

2. **Start Development**
   ```bash
   # Start all services
   ./start-dev.sh
   ```

3. **Rebuild When Needed**
   ```bash
   # Rebuild after code changes
   ./build.sh --force
   
   # Clean rebuild
   ./build.sh --clean --force
   ```

**Output example:**
```
🚀 Starting Lightspun Assignment Development Environment
==================================================================
[INFO] Checking prerequisites...
[SUCCESS] All prerequisites found
[INFO] Checking for port conflicts...
[INFO] 🔨 Building Docker images (if needed)...
[INFO] 🐳 Starting Docker services...
[INFO] 🐘 Waiting for PostgreSQL database...
[SUCCESS] PostgreSQL Database is healthy!
[INFO] 🔥 Waiting for FastAPI backend...
[SUCCESS] Backend API is ready!
[INFO] ⚛️  Waiting for React frontend...
[SUCCESS] Frontend App is ready!

🎉 All services are running successfully!
==================================================================

🌐 Frontend Application: http://localhost:3000
🔧 Backend API:          http://localhost:8000
📚 API Documentation:    http://localhost:8000/docs
🐘 PostgreSQL Database:  localhost:5432

Useful Commands:
  📋 View logs:           docker-compose logs -f
  📋 View specific logs:  docker-compose logs -f [backend|frontend|postgres]
  🔄 Restart service:     docker-compose restart [service_name]
  ⚡ Rebuild service:     docker-compose up -d --build [service_name]

Press Ctrl+C to stop all services
```

### 1. Manual Full Stack Setup

```bash
# Start database
docker-compose up postgres -d

# Install backend dependencies and start API
pip install -r requirements.txt
python3 -m lightspun.init_db
uvicorn lightspun.app:app --reload

# In another terminal, start frontend
cd frontend
npm install
npm start
```

### 2. Docker Development

```bash
# One command to start everything
docker-compose up

# Access:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### 3. Testing Everything

```bash
# Test backend
python3 -m pytest

# Test frontend
cd frontend && npm test

# Test configuration
python3 tests/integration/test_config.py
```

## 🔧 Troubleshooting

### Build Script Issues

**Script permissions error**
```bash
# Make scripts executable
chmod +x build.sh
chmod +x start-dev.sh

# If chmod fails, check file ownership
ls -la build.sh
sudo chown $USER:$USER build.sh
```

**Build script fails to run**
```bash
# Check if bash is available
which bash

# Run with explicit bash
bash build.sh

# Check for syntax errors
bash -n build.sh
```

**Docker not available**
```bash
# Check if Docker is installed
docker --version
docker-compose --version

# Install Docker if missing:
# Linux: Follow https://docs.docker.com/engine/install/
# macOS/Windows: Install Docker Desktop from https://docker.com

# Start Docker daemon
# macOS/Windows: Start Docker Desktop
# Linux: sudo systemctl start docker
```

**Docker build fails**
```bash
# Check Docker daemon status
docker info

# Clean up Docker system
docker system prune -a

# Try manual build
docker-compose build --no-cache

# Check individual services
docker-compose build backend
docker-compose build frontend
```

**Backend build fails**
```bash
# Check Dockerfile syntax
docker build -t test-backend -f Dockerfile .

# Check Python dependencies
cat requirements.txt

# Manual troubleshooting
docker-compose logs backend
docker-compose build backend --progress=plain
```

**Frontend build fails**
```bash
# Check frontend Dockerfile
cat frontend/Dockerfile

# Check Node.js dependencies
cat frontend/package.json

# Manual troubleshooting
docker-compose logs frontend
docker-compose build frontend --progress=plain

# Test local build
cd frontend && npm install && npm run build
```

**Image verification fails**
```bash
# List all Docker images
docker images

# Check specific images
docker images | grep lightspun

# Remove corrupted images and rebuild
docker rmi lightspunassignment-backend lightspunassignment-frontend
./build.sh --force
```

**Permission denied errors**
```bash
# Docker permission issues
sudo usermod -aG docker $USER
newgrp docker

# If still having issues, restart terminal or system
# Test Docker without sudo
docker run hello-world

# File permission issues
sudo chown -R $USER:$USER .
chmod -R 755 .
```

**Network/Download failures**
```bash
# Check internet connection
ping google.com

# Check if behind corporate firewall
# Configure proxy if needed
export http_proxy=http://proxy:port
export https_proxy=https://proxy:port

# For npm behind proxy
npm config set proxy http://proxy:port
npm config set https-proxy https://proxy:port

# For pip behind proxy
pip install --proxy http://proxy:port -r requirements.txt
```

**Disk space issues**
```bash
# Check available space
df -h

# Clean up if needed
# Remove old Docker images
docker system prune -a

# Clean npm cache
npm cache clean --force

# Clean pip cache
pip cache purge
```

**Build incomplete/corrupted**
```bash
# Complete cleanup and rebuild
docker system prune -a
docker volume prune -f

# Remove project images
docker images | grep lightspun | awk '{print $3}' | xargs docker rmi -f

# Re-run build
./build.sh --clean --force

# Manual step-by-step if script fails
docker-compose build --no-cache backend
docker-compose build --no-cache frontend
```

### Startup Script Issues

**Script permissions error**
```bash
# Make script executable
chmod +x start-dev.sh
```

**Docker not running**
```bash
# Check if Docker is running
docker info

# Start Docker (varies by system)
# macOS: Open Docker Desktop
# Linux: sudo systemctl start docker
# Windows: Start Docker Desktop
```

**Docker Compose not found**
```bash
# Check Docker Compose version
docker-compose --version

# Or try newer syntax
docker compose version

# Install Docker Compose if missing
# Visit: https://docs.docker.com/compose/install/
```

**Port conflicts**
```bash
# Check what's using the ports
lsof -i :3000  # Frontend port
lsof -i :8000  # Backend port
lsof -i :5432  # PostgreSQL port

# Kill processes using the ports
kill $(lsof -t -i:3000)
kill $(lsof -t -i:8000)
kill $(lsof -t -i:5432)

# Or stop previous Docker services
docker-compose down
```

**Services won't start**
```bash
# Check service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres

# Rebuild images
docker-compose build --no-cache

# Clean up and restart
docker-compose down -v
docker system prune
./start-dev.sh
```

### Common Issues

**Backend won't start**
```bash
# Check database connection
docker-compose up postgres -d
docker-compose logs postgres

# Check Python dependencies
pip install -r requirements.txt

# Check environment variables
echo $DATABASE_URL
```

**Frontend API errors**
```bash
# Verify backend is running
curl http://localhost:8000/

# Check CORS configuration
# Ensure CORS_ORIGINS includes frontend URL
```

**Database connection issues**
```bash
# Reset database
docker-compose down -v
docker-compose up postgres -d
python3 -m lightspun.init_db
```

**Tests failing**
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run simple tests first
python3 tests/unit/test_address_parsing.py
```

For more detailed testing information, see [tests/README.md](tests/README.md).

---

## 🎯 Features Implemented

- ✅ **FastAPI Backend** with professional configuration system
- ✅ **PostgreSQL Database** with advanced search capabilities  
- ✅ **React Frontend** with modular component architecture
- ✅ **Fuzzy Search** using trigram similarity and soundex matching
- ✅ **Address Autocomplete** with real-time suggestions
- ✅ **Comprehensive Testing** with unit and integration tests
- ✅ **Docker Deployment** with multi-container orchestration
- ✅ **Professional Logging** with environment-specific formats
- ✅ **Error Handling** throughout the entire stack
- ✅ **API Documentation** with interactive Swagger UI
- ✅ **Automated Installation** with cross-platform dependency setup
- ✅ **One-Command Startup** with automated development setup

Ready for development, testing, and production deployment! 🚀
