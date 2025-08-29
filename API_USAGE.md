# FastAPI Backend - US States and Addresses API

## Setup and Run

### Prerequisites
- Python 3.7+
- PostgreSQL 12+ (or use Docker Compose)

### 1. Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Setup PostgreSQL Database

#### Option A: Using Docker Compose (Recommended)
```bash
docker-compose up -d postgres
```

#### Option B: Local PostgreSQL Installation
Make sure PostgreSQL is running and create a database named `lightspun_db`.

### 3. Configure Database Connection
Copy the environment configuration:
```bash
cp .env.example .env
```

Edit `.env` if needed to match your PostgreSQL setup:
```
DATABASE_URL=postgresql://user:password@localhost:5432/lightspun_db
```

### 4. Initialize Database
Run the database setup script:
```bash
python setup_db.py
```

### 5. Start the server:

#### Option A: Using Docker Compose (Recommended)
```bash
docker-compose up -d
```
This will start both PostgreSQL and the FastAPI application in containers.

#### Option B: Local Development
```bash
uvicorn lightspun.app:app --host 0.0.0.0 --port 8000
# or
python main.py
```

### Docker Commands
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs api
docker-compose logs postgres

# Stop all services
docker-compose down

# Rebuild containers
docker-compose build --no-cache
```

## API Endpoints

### 1. Get All US States
- **URL**: `GET /states`
- **Description**: Returns all US states with their codes and names
- **Response**: Array of objects with `code` and `name` fields

```bash
curl http://localhost:8000/states
```

### 2. Get Municipalities in State
- **URL**: `GET /states/{state_code}/municipalities`
- **Description**: Returns municipalities (cities, towns) in a specific state
- **Parameters**: `state_code` - Two-letter state code (e.g., "CA", "NY", "TX")
- **Response**: Array of objects with `name` and `type` fields

```bash
curl http://localhost:8000/states/CA/municipalities
```

### 3. Autocomplete Street Address
- **URL**: `GET /addresses/autocomplete?q={query}`
- **Description**: Returns matching street addresses based on query string
- **Parameters**: `q` - Query string (minimum 2 characters)
- **Response**: Array of matching address strings (max 10 results)

```bash
curl "http://localhost:8000/addresses/autocomplete?q=123"
```

## Interactive Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc