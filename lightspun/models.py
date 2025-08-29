from sqlalchemy import Column, Integer, String, ForeignKey, Table, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from .database import Base

class State(Base):
    __tablename__ = "states"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(2), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    
    municipalities = relationship("Municipality", back_populates="state")

class Municipality(Base):
    __tablename__ = "municipalities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)
    state_id = Column(Integer, ForeignKey("states.id"), index=True)  # Index for state lookups
    
    state = relationship("State", back_populates="municipalities")
    
    __table_args__ = (
        UniqueConstraint('name', 'state_id', name='uq_municipality_name_state'),
        Index('ix_municipalities_state_id', 'state_id'),  # Explicit index for state lookups
        Index('ix_municipalities_name', 'name'),  # Index for municipality name searches
    )

class Address(Base):
    __tablename__ = "addresses"
    
    id = Column(Integer, primary_key=True, index=True)
    street_number = Column(String(10), nullable=True)  # e.g., "123", "456A"
    street_name = Column(String(150), nullable=False)  # e.g., "Main Street", "Oak Avenue"
    unit = Column(String(20), nullable=True)  # e.g., "Apt 2B", "Suite 100"
    street_address = Column(String(200), nullable=False)  # Keep for backward compatibility
    city = Column(String(100), nullable=False, index=True)  # Index for city searches
    state_code = Column(String(2), nullable=False, index=True)  # Index for state code searches
    full_address = Column(String(300), unique=True, nullable=False)
    
    __table_args__ = (
        Index('ix_addresses_city', 'city'),  # Explicit index for city lookups
        Index('ix_addresses_state_code', 'state_code'),  # Explicit index for state code lookups  
        Index('ix_addresses_city_state', 'city', 'state_code'),  # Composite index for city+state searches
        Index('ix_addresses_street_address', 'street_address'),  # Index for address autocomplete
        Index('ix_addresses_street_name', 'street_name'),  # Index for street name searches
        Index('ix_addresses_street_number', 'street_number'),  # Index for street number searches
    )