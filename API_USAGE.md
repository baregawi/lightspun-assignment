# FastAPI Backend - US States and Addresses API

## Setup and Run

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
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