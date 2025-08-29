from sqlalchemy import Column, Integer, String, ForeignKey, Table
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
    state_id = Column(Integer, ForeignKey("states.id"))
    
    state = relationship("State", back_populates="municipalities")

class Address(Base):
    __tablename__ = "addresses"
    
    id = Column(Integer, primary_key=True, index=True)
    street_address = Column(String(200), nullable=False)
    city = Column(String(100), nullable=False)
    state_code = Column(String(2), nullable=False)
    full_address = Column(String(300), nullable=False)