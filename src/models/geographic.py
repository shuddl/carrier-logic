from geoalchemy2 import Geography
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from ..database.database import Base
from datetime import datetime, timezone

class InspectionLocation(Base):
    __tablename__ = "inspection_locations"
    
    id = Column(Integer, primary_key=True, index=True)
    carrier_id = Column(Integer, ForeignKey("carrier_records.id"))
    inspection_date = Column(DateTime)
    location = Column(Geography(geometry_type='POINT', srid=4326))
    state = Column(String)
    city = Column(String)
    
    # Inspection details
    level = Column(Integer)
    violation_count = Column(Integer)
    raw_data = Column(JSON)
    
    # Relationships
    carrier = relationship("CarrierRecord", back_populates="inspection_locations")

class CarrierRoute(Base):
    __tablename__ = "carrier_routes"
    
    id = Column(Integer, primary_key=True, index=True)
    carrier_id = Column(Integer, ForeignKey("carrier_records.id"))
    route_geometry = Column(Geography(geometry_type='LINESTRING', srid=4326))
    confidence_score = Column(Float)
    first_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    inspection_count = Column(Integer, default=0)
    
    # Relationships
    carrier = relationship("CarrierRecord", back_populates="routes")