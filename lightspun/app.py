from fastapi import FastAPI, HTTPException, Query, Path, Body, status, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List, Dict, Optional
import time
import uuid
from .config import get_config
from .database import init_database, connect_db, disconnect_db
from .schemas import (
    State, StateCreate, StateUpdate, StateListResponse,
    Municipality, MunicipalityCreate, MunicipalityUpdate, MunicipalityListResponse,
    Address, AddressCreate, AddressUpdate, AddressAutocompleteQuery, AddressAutocompleteResponse,
    ErrorResponse, SuccessResponse
)
from .services import StateService, MunicipalityService, AddressService
from .logging_config import get_logger, set_request_id

# Load configuration (logging setup is automatic)
config = get_config()

# Initialize database with configuration
init_database(config)

# Initialize logger
logger = get_logger('lightspun.app')

# Request logging middleware
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate request ID and set in context
        request_id = str(uuid.uuid4())[:8]
        set_request_id(request_id)
        
        # Log request start
        start_time = time.time()
        logger.info(
            f"Request started - {request.method} {request.url.path}",
            extra={
                'request_id': request_id,
                'method': request.method,
                'path': request.url.path,
                'query_params': str(request.query_params),
                'client_ip': request.client.host if request.client else 'unknown'
            }
        )
        
        try:
            response = await call_next(request)
            duration = (time.time() - start_time) * 1000
            
            # Log successful response
            logger.info(
                f"Request completed - {response.status_code}",
                extra={
                    'request_id': request_id,
                    'status_code': response.status_code,
                    'duration': duration
                }
            )
            return response
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(
                f"Request failed - {str(e)}",
                extra={
                    'request_id': request_id,
                    'duration': duration,
                    'error': str(e)
                },
                exc_info=True
            )
            raise

app = FastAPI(
    title=config.api.title,
    description=config.api.description,
    version=config.api.version,
    docs_url=config.api.docs_url,
    redoc_url=config.api.redoc_url,
    openapi_url=config.api.openapi_url,
    debug=config.api.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.security.cors_origins,
    allow_credentials=config.security.cors_allow_credentials,
    allow_methods=config.security.cors_allow_methods,
    allow_headers=config.security.cors_allow_headers,
)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

@app.on_event("startup")
async def startup():
    logger.info("Starting up FastAPI application...")
    await connect_db()
    logger.info("FastAPI application startup completed")

@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutting down FastAPI application...")
    await disconnect_db()
    logger.info("FastAPI application shutdown completed")

@app.get("/", tags=["Root"])
async def root() -> SuccessResponse:
    """API root endpoint"""
    return SuccessResponse(message="US States and Addresses API")


# ===== STATE ENDPOINTS =====

@app.get("/states", 
         response_model=StateListResponse,
         tags=["States"],
         summary="Get all US states",
         description="Retrieve all US states with their codes and names")
async def get_all_states():
    """Get all US states with their codes and names."""
    logger.debug("Retrieving all states")
    states = await StateService.get_all_states()
    logger.debug(f"Retrieved {len(states)} states")
    return StateListResponse(states=states, total_count=len(states))


@app.get("/states/{state_code}",
         response_model=State,
         responses={404: {"model": ErrorResponse}},
         tags=["States"],
         summary="Get state by code",
         description="Retrieve a specific state by its two-letter code")
async def get_state_by_code(
    state_code: str = Path(..., description="Two-letter state code", min_length=2, max_length=2)
):
    """Get a specific state by its code."""
    state = await StateService.get_state_by_code(state_code)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"State with code '{state_code.upper()}' not found"
        )
    return state


@app.post("/states",
          response_model=State,
          status_code=status.HTTP_201_CREATED,
          responses={400: {"model": ErrorResponse}},
          tags=["States"],
          summary="Create a new state",
          description="Create a new state with code and name")
async def create_state(state_data: StateCreate):
    """Create a new state."""
    try:
        state = await StateService.create_state(state_data)
        return state
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create state: {str(e)}"
        )


@app.put("/states/{state_id}",
         response_model=State,
         responses={404: {"model": ErrorResponse}},
         tags=["States"],
         summary="Update a state",
         description="Update an existing state")
async def update_state(
    state_id: int = Path(..., description="State ID"),
    state_data: StateUpdate = Body(...)
):
    """Update an existing state."""
    state = await StateService.update_state(state_id, state_data)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"State with ID {state_id} not found"
        )
    return state


@app.delete("/states/{state_id}",
            response_model=SuccessResponse,
            responses={404: {"model": ErrorResponse}},
            tags=["States"],
            summary="Delete a state",
            description="Delete an existing state")
async def delete_state(state_id: int = Path(..., description="State ID")):
    """Delete an existing state."""
    deleted = await StateService.delete_state(state_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"State with ID {state_id} not found"
        )
    return SuccessResponse(message=f"State with ID {state_id} deleted successfully")


# ===== MUNICIPALITY ENDPOINTS =====

@app.get("/states/{state_code}/municipalities",
         response_model=MunicipalityListResponse,
         responses={404: {"model": ErrorResponse}},
         tags=["Municipalities"],
         summary="Get municipalities in state",
         description="Retrieve all municipalities in a specific state")
async def get_municipalities_in_state(
    state_code: str = Path(..., description="Two-letter state code", min_length=2, max_length=2)
):
    """Get municipalities (cities, towns) in a specific state."""
    state_code = state_code.upper()
    
    # Check if state exists
    state = await StateService.get_state_by_code(state_code)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"State with code '{state_code}' not found"
        )
    
    # Get municipalities for the state
    municipalities = await MunicipalityService.get_municipalities_by_state_code(state_code)
    
    return MunicipalityListResponse(
        municipalities=municipalities,
        state=state,
        total_count=len(municipalities)
    )


@app.get("/municipalities/{municipality_id}",
         response_model=Municipality,
         responses={404: {"model": ErrorResponse}},
         tags=["Municipalities"],
         summary="Get municipality by ID",
         description="Retrieve a specific municipality by its ID")
async def get_municipality_by_id(
    municipality_id: int = Path(..., description="Municipality ID")
):
    """Get a specific municipality by its ID."""
    municipality = await MunicipalityService.get_municipality_by_id(municipality_id)
    if not municipality:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Municipality with ID {municipality_id} not found"
        )
    return municipality


@app.post("/municipalities",
          response_model=Municipality,
          status_code=status.HTTP_201_CREATED,
          responses={400: {"model": ErrorResponse}},
          tags=["Municipalities"],
          summary="Create a new municipality",
          description="Create a new municipality")
async def create_municipality(municipality_data: MunicipalityCreate):
    """Create a new municipality."""
    try:
        municipality = await MunicipalityService.create_municipality(municipality_data)
        return municipality
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create municipality: {str(e)}"
        )


# ===== ADDRESS ENDPOINTS =====

@app.get("/addresses/autocomplete",
         response_model=AddressAutocompleteResponse,
         tags=["Addresses"],
         summary="Autocomplete street addresses",
         description="Search and autocomplete street addresses based on query string")
async def autocomplete_address(
    q: str = Query(..., description="Address query string", min_length=2),
    limit: int = Query(10, description="Maximum number of results", ge=1, le=50),
    state_code: Optional[str] = Query(None, description="Filter by state code (e.g., 'CA', 'NY')", max_length=2),
    city: Optional[str] = Query(None, description="Filter by city name")
):
    """Autocomplete street addresses based on query string with optional state/city filtering."""
    addresses = await AddressService.search_addresses(q, limit, state_code=state_code, city=city)
    
    return AddressAutocompleteResponse(
        addresses=addresses,
        total_count=len(addresses)
    )


@app.get("/addresses",
         response_model=List[Address],
         tags=["Addresses"],
         summary="Get all addresses",
         description="Retrieve all addresses")
async def get_all_addresses():
    """Get all addresses."""
    return await AddressService.get_all_addresses()


@app.get("/addresses/{address_id}",
         response_model=Address,
         responses={404: {"model": ErrorResponse}},
         tags=["Addresses"],
         summary="Get address by ID",
         description="Retrieve a specific address by its ID")
async def get_address_by_id(
    address_id: int = Path(..., description="Address ID")
):
    """Get a specific address by its ID."""
    address = await AddressService.get_address_by_id(address_id)
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address with ID {address_id} not found"
        )
    return address


@app.post("/addresses",
          response_model=Address,
          status_code=status.HTTP_201_CREATED,
          responses={400: {"model": ErrorResponse}},
          tags=["Addresses"],
          summary="Create a new address",
          description="Create a new address")
async def create_address(address_data: AddressCreate):
    """Create a new address."""
    try:
        address = await AddressService.create_address(address_data)
        return address
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create address: {str(e)}"
        )


@app.put("/addresses/{address_id}",
         response_model=Address,
         responses={404: {"model": ErrorResponse}},
         tags=["Addresses"],
         summary="Update an address",
         description="Update an existing address")
async def update_address(
    address_id: int = Path(..., description="Address ID"),
    address_data: AddressUpdate = Body(...)
):
    """Update an existing address."""
    address = await AddressService.update_address(address_id, address_data)
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address with ID {address_id} not found"
        )
    return address


@app.delete("/addresses/{address_id}",
            response_model=SuccessResponse,
            responses={404: {"model": ErrorResponse}},
            tags=["Addresses"],
            summary="Delete an address",
            description="Delete an existing address")
async def delete_address(address_id: int = Path(..., description="Address ID")):
    """Delete an existing address."""
    deleted = await AddressService.delete_address(address_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address with ID {address_id} not found"
        )
    return SuccessResponse(message=f"Address with ID {address_id} deleted successfully")