from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Carrier(Base):
    __tablename__ = "carriers"
    
    id = Column(Integer, primary_key=True, index=True)
    dot_number = Column(String, unique=True, index=True)
    legal_name = Column(String)
    dba_name = Column(String)
    operating_status = Column(String)  # Active/Inactive
    fleet_size = Column(Integer)  # totalPowerUnits
    driver_count = Column(Integer)
    
    # Safety Metrics
    safety_rating = Column(String)
    safety_rating_date = Column(DateTime)
    driver_oos_rate = Column(Float)
    vehicle_oos_rate = Column(Float)
    crash_rate = Column(Float)
    total_crashes = Column(Integer)
    fatal_crashes = Column(Integer)
    injury_crashes = Column(Integer)
    tow_crashes = Column(Integer)
    
    # Insurance
    insurance_on_file = Column(Boolean)
    insurance_amount = Column(Integer)
    
    # Location
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_inspection_date = Column(DateTime)
    mcs150_date = Column(DateTime)

class CarrierHistory(Base):
    __tablename__ = "carrier_history"
    
    id = Column(Integer, primary_key=True, index=True)
    carrier_dot_number = Column(String, index=True)
    record_date = Column(DateTime, default=datetime.utcnow)
    
    # Snapshot Metrics
    safety_rating = Column(String)
    driver_oos_rate = Column(Float)
    vehicle_oos_rate = Column(Float)
    crash_rate = Column(Float)
    total_crashes = Column(Integer)
    driver_count = Column(Integer)
    fleet_size = Column(Integer)

class CarrierInspectionLocation(Base):
    __tablename__ = "carrier_inspection_locations"
    
    id = Column(Integer, primary_key=True, index=True)
    carrier_dot_number = Column(String, index=True)
    inspection_date = Column(DateTime)
    location_city = Column(String)
    location_state = Column(String)