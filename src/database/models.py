from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional
from .database import Base
from dataclasses import dataclass
from sqlalchemy.orm import Mapped

@dataclass
class CarrierStatus:
    is_active: bool
    operating_status: str
    allowed_to_operate: bool

class CarrierRecord(Base):
    __tablename__ = "carrier_records"

    id = Column(Integer, primary_key=True, index=True)
    dot_number = Column(String, index=True)
    legal_name = Column(String)
    dba_name = Column(String, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    operating_status = Column(String)
    allowed_to_operate = Column(Boolean)
    
    # Fleet Info
    fleet_size = Column(Integer)
    driver_count = Column(Integer)
    
    # Safety Ratings
    safety_rating = Column(String)
    safety_rating_date = Column(DateTime, nullable=True)
    
    # Location
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    
    # Tracking
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, 
                       default=lambda: datetime.now(timezone.utc),
                       onupdate=lambda: datetime.now(timezone.utc))
    raw_data = Column(JSON)  # Store complete FMCSA response

    # Relationships
    safety_metrics = relationship("SafetyMetrics", back_populates="carrier", uselist=False)
    inspection_locations = relationship("InspectionLocation", back_populates="carrier")
    routes = relationship("CarrierRoute", back_populates="carrier")
    inspections = relationship("Inspection", back_populates="carrier")
    risk_assessments = relationship("RiskAssessment", back_populates="carrier")

    @property
    def status(self) -> CarrierStatus:
        return CarrierStatus(
            is_active=self.is_active,
            operating_status=self.operating_status,
            allowed_to_operate=self.allowed_to_operate
        )

    def is_data_fresh(self) -> bool:
        """Check if data is less than 24 hours old"""
        if not self.updated_at:
            return False
        return datetime.utcnow() - self.updated_at < timedelta(hours=24)

    def to_dict(self) -> dict:
        """Convert record to dictionary"""
        return {
            "dot_number": self.dot_number,
            "legal_name": self.legal_name,
            "dba_name": self.dba_name,
            "is_active": self.is_active,
            "operating_status": self.operating_status,
            "fleet_size": self.fleet_size,
            "driver_count": self.driver_count,
            "safety_rating": self.safety_rating,
            "safety_rating_date": self.safety_rating_date.isoformat() if self.safety_rating_date else None,
            "address": {
                "street": self.address,
                "city": self.city,
                "state": self.state,
                "zip": self.zip_code
            },
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def to_profile(self) -> Dict:
        """Convert record to profile for analysis"""
        if self.raw_data and 'content' in self.raw_data and 'carrier' in self.raw_data['content']:
            carrier_data = self.raw_data['content']['carrier']
            return {
                "dot_number": str(carrier_data.get('dotNumber')),
                "status": {
                    "is_active": carrier_data.get('statusCode') == 'A',
                    "allowed_to_operate": carrier_data.get('allowedToOperate') == 'Y',
                    "operating_status": carrier_data.get('statusCode', 'Unknown')
                },
                "safety_metrics": {
                    "driver_oos_rate": float(carrier_data.get('driverOosRate', 0)),
                    "vehicle_oos_rate": float(carrier_data.get('vehicleOosRate', 0)),
                    "driver_oos_national_average": float(carrier_data.get('driverOosRateNationalAverage', 0)),
                    "vehicle_oos_national_average": float(carrier_data.get('vehicleOosRateNationalAverage', 0)),
                    "crash_total": int(carrier_data.get('crashTotal', 0)),
                    "fatal_crashes": int(carrier_data.get('fatalCrash', 0)),
                    "safety_rating": carrier_data.get('safetyRating'),
                    "safety_rating_date": carrier_data.get('safetyRatingDate')
                },
                "insurance": {
                    "bipd_required": carrier_data.get('bipdInsuranceRequired') == 'Y',
                    "bipd_on_file": carrier_data.get('bipdInsuranceOnFile')
                },
                "fleet_size": int(carrier_data.get('totalPowerUnits', 0)),
                "driver_count": int(carrier_data.get('totalDrivers', 0))
            }
        else:
            # Fallback to basic profile if raw data isn't available
            return {
                "dot_number": self.dot_number,
                "status": {
                    "is_active": self.is_active,
                    "allowed_to_operate": True,
                    "operating_status": self.operating_status or 'Unknown'
                },
                "safety_metrics": {
                    "driver_oos_rate": 0.0,
                    "vehicle_oos_rate": 0.0,
                    "driver_oos_national_average": 5.51,
                    "vehicle_oos_national_average": 20.72,
                    "crash_total": 0,
                    "fatal_crashes": 0,
                    "safety_rating": self.safety_rating,
                    "safety_rating_date": self.safety_rating_date
                },
                "insurance": {
                    "bipd_required": False,
                    "bipd_on_file": None
                },
                "fleet_size": self.fleet_size or 0,
                "driver_count": self.driver_count or 0
            }

class SafetyMetrics(Base):
    __tablename__ = "safety_metrics"

    id = Column(Integer, primary_key=True, index=True)
    carrier_id = Column(Integer, ForeignKey("carrier_records.id"))
    record_date = Column(DateTime, default=datetime.utcnow)
    
    # Crash Statistics
    crash_total = Column(Integer)
    fatal_crashes = Column(Integer)
    injury_crashes = Column(Integer)
    tow_crashes = Column(Integer)
    
    # Out of Service Rates
    driver_oos_rate = Column(Float)
    vehicle_oos_rate = Column(Float)
    hazmat_oos_rate = Column(Float)
    
    # Inspection Counts
    driver_inspections = Column(Integer)
    vehicle_inspections = Column(Integer)
    hazmat_inspections = Column(Integer)
    
    # National Averages at Time of Record
    driver_oos_national_avg = Column(Float)
    vehicle_oos_national_avg = Column(Float)
    hazmat_oos_national_avg = Column(Float)

    carrier = relationship("CarrierRecord", back_populates="safety_metrics")

class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True)
    carrier_id = Column(Integer, ForeignKey("carrier_records.id"))
    inspection_date = Column(DateTime)
    
    # Location
    state = Column(String)
    city = Column(String)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Results
    level = Column(Integer)
    violations_count = Column(Integer)
    oos_violations_count = Column(Integer)
    
    carrier = relationship("CarrierRecord", back_populates="inspections")

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    carrier_id = Column(Integer, ForeignKey("carrier_records.id"))
    assessment_date = Column(DateTime, default=datetime.utcnow)
    
    risk_level = Column(String)
    risk_factors = Column(JSON)  # Store as JSON array
    warnings = Column(JSON)  # Store as JSON array
    metrics_analysis = Column(JSON)  # Store complete metrics analysis
    
    carrier = relationship("CarrierRecord", back_populates="risk_assessments")

class InspectionLocation(Base):
    __tablename__ = "inspection_locations"

    id = Column(Integer, primary_key=True, index=True)
    carrier_id = Column(Integer, ForeignKey("carrier_records.id"))
    city = Column(String)
    state = Column(String)
    inspection_count = Column(Integer, default=0)
    
    # Relationship back to carrier
    carrier = relationship("CarrierRecord", back_populates="inspection_locations")

class CarrierRoute(Base):
    __tablename__ = "carrier_routes"

    id = Column(Integer, primary_key=True, index=True)
    carrier_id = Column(Integer, ForeignKey("carrier_records.id"))
    origin_state = Column(String)
    destination_state = Column(String)
    frequency = Column(Integer, default=0)
    
    # Relationship back to carrier
    carrier = relationship("CarrierRecord", back_populates="routes")