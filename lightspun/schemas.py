from pydantic import BaseModel, Field, validator
from typing import List, Optional
from enum import Enum

class MunicipalityType(str, Enum):
    """Enumeration for municipality types"""
    city = "city"
    town = "town"
    village = "village"
    borough = "borough"

class StateBase(BaseModel):
    """Base schema for State"""
    code: str = Field(..., min_length=2, max_length=2, description="Two-letter state code")
    name: str = Field(..., min_length=1, max_length=100, description="Full state name")

    @validator('code')
    def validate_state_code(cls, v):
        return v.upper()

class StateCreate(StateBase):
    """Schema for creating a new state"""
    pass

class StateUpdate(BaseModel):
    """Schema for updating a state"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)

class State(StateBase):
    """Schema for State response"""
    id: int = Field(..., description="Unique state identifier")

    class Config:
        from_attributes = True

class MunicipalityBase(BaseModel):
    """Base schema for Municipality"""
    name: str = Field(..., min_length=1, max_length=100, description="Municipality name")
    type: MunicipalityType = Field(..., description="Type of municipality")

class MunicipalityCreate(MunicipalityBase):
    """Schema for creating a new municipality"""
    state_id: int = Field(..., description="ID of the state this municipality belongs to")

class MunicipalityUpdate(BaseModel):
    """Schema for updating a municipality"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[MunicipalityType] = None

class Municipality(MunicipalityBase):
    """Schema for Municipality response"""
    id: int = Field(..., description="Unique municipality identifier")
    state_id: int = Field(..., description="ID of the state this municipality belongs to")

    class Config:
        from_attributes = True

class MunicipalityWithState(Municipality):
    """Schema for Municipality response with state information"""
    state: State

class AddressBase(BaseModel):
    """Base schema for Address"""
    street_number: Optional[str] = Field(None, max_length=10, description="Street number (e.g., '123', '456A')")
    street_name: str = Field(..., min_length=1, max_length=150, description="Street name (e.g., 'Main Street')")
    unit: Optional[str] = Field(None, max_length=20, description="Unit/apartment/suite (e.g., 'Apt 2B')")
    street_address: str = Field(..., min_length=1, max_length=200, description="Complete street address (backward compatibility)")
    city: str = Field(..., min_length=1, max_length=100, description="City name")
    state_code: str = Field(..., min_length=2, max_length=2, description="Two-letter state code")

    @validator('state_code')
    def validate_state_code(cls, v):
        return v.upper()


class AddressCreate(AddressBase):
    """Schema for creating a new address"""
    pass

class AddressCreateMinimal(BaseModel):
    """Schema for creating address with automatic component parsing"""
    street_address: str = Field(..., min_length=1, max_length=200, description="Complete street address")
    city: str = Field(..., min_length=1, max_length=100, description="City name")
    state_code: str = Field(..., min_length=2, max_length=2, description="Two-letter state code")

    @validator('state_code')
    def validate_state_code(cls, v):
        return v.upper()

class AddressUpdate(BaseModel):
    """Schema for updating an address"""
    street_number: Optional[str] = Field(None, max_length=10, description="Street number")
    street_name: Optional[str] = Field(None, min_length=1, max_length=150, description="Street name")
    unit: Optional[str] = Field(None, max_length=20, description="Unit/apartment/suite")
    street_address: Optional[str] = Field(None, min_length=1, max_length=200, description="Complete street address")
    city: Optional[str] = Field(None, min_length=1, max_length=100, description="City name")
    state_code: Optional[str] = Field(None, min_length=2, max_length=2, description="Two-letter state code")

    @validator('state_code')
    def validate_state_code(cls, v):
        if v:
            return v.upper()
        return v

class Address(AddressBase):
    """Schema for Address response"""
    id: int = Field(..., description="Unique address identifier")
    full_address: str = Field(..., description="Complete formatted address")

    class Config:
        from_attributes = True

class AddressAutocompleteQuery(BaseModel):
    """Schema for address autocomplete query"""
    q: str = Field(..., min_length=2, max_length=200, description="Search query")
    limit: Optional[int] = Field(10, ge=1, le=50, description="Maximum number of results")

class AddressAutocompleteResponse(BaseModel):
    """Schema for address autocomplete response"""
    addresses: List[str] = Field(..., description="List of matching addresses")
    total_count: int = Field(..., description="Total number of matches found")

class StateListResponse(BaseModel):
    """Schema for state list response"""
    states: List[State] = Field(..., description="List of states")
    total_count: int = Field(..., description="Total number of states")

class MunicipalityListResponse(BaseModel):
    """Schema for municipality list response"""
    municipalities: List[Municipality] = Field(..., description="List of municipalities")
    state: State = Field(..., description="State information")
    total_count: int = Field(..., description="Total number of municipalities")

class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")

class SuccessResponse(BaseModel):
    """Schema for success responses"""
    message: str = Field(..., description="Success message")
    data: Optional[dict] = Field(None, description="Optional data payload")