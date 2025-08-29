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

### 1. Full Stack Development (Recommended)

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

Ready for development, testing, and production deployment! 🚀
