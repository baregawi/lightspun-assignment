from fastapi import FastAPI, HTTPException, Query
from typing import List, Dict

app = FastAPI(title="US States and Addresses API", version="1.0.0")

US_STATES = [
    {"code": "CA", "name": "California"},
    {"code": "NY", "name": "New York"},
    {"code": "TX", "name": "Texas"},
]

SAMPLE_MUNICIPALITIES = {
    "CA": [
        {"name": "Los Angeles", "type": "city"},
        {"name": "San Francisco", "type": "city"},
        {"name": "San Diego", "type": "city"},
        {"name": "Sacramento", "type": "city"},
        {"name": "Oakland", "type": "city"}
    ],
    "NY": [
        {"name": "New York City", "type": "city"},
        {"name": "Buffalo", "type": "city"},
        {"name": "Rochester", "type": "city"},
        {"name": "Yonkers", "type": "city"},
        {"name": "Syracuse", "type": "city"}
    ],
    "TX": [
        {"name": "Houston", "type": "city"},
        {"name": "San Antonio", "type": "city"},
        {"name": "Dallas", "type": "city"},
        {"name": "Austin", "type": "city"},
        {"name": "Fort Worth", "type": "city"}
    ]
}

SAMPLE_ADDRESSES = [
    "123 Main Street, Los Angeles, CA",
    "456 Oak Avenue, San Francisco, CA",
    "789 Pine Road, San Diego, CA",
    "321 Elm Street, New York, NY",
    "654 Broadway, Buffalo, NY",
    "987 Cedar Lane, Houston, TX",
    "147 Maple Drive, Dallas, TX",
    "258 Birch Way, Austin, TX"
]

@app.get("/", tags=["Root"])
async def root():
    return {"message": "US States and Addresses API"}


@app.get("/states", tags=["States"])
async def get_all_states() -> List[Dict[str, str]]:
    """Get all US states with their codes and names."""
    return US_STATES


@app.get("/states/{state_code}/municipalities", tags=["Municipalities"])
async def get_municipalities_in_state(state_code: str) -> List[Dict[str, str]]:
    """Get municipalities (cities, towns) in a specific state."""
    state_code = state_code.upper()
    
    if not any(state["code"] == state_code for state in US_STATES):
        raise HTTPException(status_code=404, detail="State not found")
    
    municipalities = SAMPLE_MUNICIPALITIES.get(state_code, [])
    if not municipalities:
        return [{"message": f"No municipalities data available for {state_code}"}]
    
    return municipalities


@app.get("/addresses/autocomplete", tags=["Addresses"])
async def autocomplete_address(q: str = Query(..., description="Address query string")) -> List[str]:
    """Autocomplete street addresses based on query string."""
    if not q or len(q) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters long")
    
    query_lower = q.lower()
    matching_addresses = [
        addr for addr in SAMPLE_ADDRESSES 
        if query_lower in addr.lower()
    ]
    
    return matching_addresses[:10]