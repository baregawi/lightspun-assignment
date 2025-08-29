# Lightspun Assignment - US States and Addresses API

A full-stack web application providing a comprehensive API for US states, municipalities, and addresses with fuzzy search capabilities and a React frontend interface.

## 🏗️ Architecture Overview

- **Backend**: FastAPI with PostgreSQL database
- **Frontend**: React 18 with modular component architecture
- **Database**: PostgreSQL with advanced search capabilities (trigram, soundex)
- **Testing**: Comprehensive unit and integration test suite
- **Deployment**: Docker-based containerization

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Manual Setup](#-manual-setup)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Project Structure](#-project-structure)

## 🚀 Quick Start

### ⚡ One-Command Setup (Recommended)

**Start the entire application with a single command:**

```bash
# Build and start everything
./start-dev.sh
```

This script will:
- ✅ Check Docker and Docker Compose are installed
- ✅ Build all Docker images if needed
- ✅ Start PostgreSQL database
- ✅ Start FastAPI backend
- ✅ Start React frontend
- ✅ Initialize the database
- ✅ Display all service URLs

### 🔧 Build Images (Optional)

**If you need to rebuild the Docker images:**

```bash
# Build all Docker images
./build.sh

# Build with options
./build.sh --clean --force  # Clean rebuild with no cache
```

### 📱 Access the Application

Once started, you can access:

- **Frontend App**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432

### 🛑 Stop the Application

Press `Ctrl+C` in the terminal where you ran `./start-dev.sh`, or run:

```bash
docker-compose down
```

## 🔧 Manual Setup

**Only use this if the quick start doesn't work for your system.**

### Prerequisites

- Docker and Docker Compose
- Python 3.9+ (for local development)
- Node.js 16+ and npm (for local development)

### Manual Docker Setup

```bash
# 1. Build images manually
docker-compose build

# 2. Start all services
docker-compose up -d

# 3. Initialize database
docker-compose exec backend python -m lightspun.init_db

# 4. Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

### Local Development Setup (Without Docker)

```bash
# 1. Start database only
docker-compose up postgres -d

# 2. Set up backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m lightspun.init_db
uvicorn lightspun.app:app --reload

# 3. In another terminal, set up frontend
cd frontend
npm install
npm start
```

## 🧪 Testing

### Backend Tests

```bash
# Run all tests
python3 -m pytest

# Run specific tests
python3 tests/unit/test_address_parsing.py
python3 tests/unit/test_street_standardization.py
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 📚 API Documentation

### Interactive Documentation

When the backend is running, view the complete API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoints

- **States**: `/states` - List and manage US states
- **Municipalities**: `/states/{state_code}/municipalities` - Cities/towns by state  
- **Addresses**: `/addresses/autocomplete` - Address search with autocomplete

The API includes fuzzy search, real-time autocomplete, and comprehensive data validation.

## 📁 Project Structure

```
lightspun-assignment/
├── build.sh                 # Build Docker images
├── start-dev.sh             # Start development environment
├── docker-compose.yml       # Container orchestration
├── lightspun/               # Backend (FastAPI)
├── frontend/                # Frontend (React)
└── tests/                   # Test suite
```

## 🔧 Troubleshooting

### Common Issues

**Script permissions:**
```bash
chmod +x build.sh start-dev.sh
```

**Docker not running:**
```bash
# Check Docker status
docker --version
docker info
```

**Port conflicts:**
```bash
# Stop existing services
docker-compose down
```

**Clean rebuild:**
```bash
./build.sh --clean --force
```

## 🎯 Features

- ✅ **FastAPI Backend** with PostgreSQL database
- ✅ **React Frontend** with responsive design
- ✅ **Address Autocomplete** with fuzzy search
- ✅ **Docker Deployment** with one-command setup
- ✅ **Comprehensive Testing** suite
- ✅ **Interactive API Documentation**

Ready for development and production! 🚀
