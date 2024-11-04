from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List, Any
from datetime import datetime
from dataclasses import dataclass
import json

class HazmatMetrics(BaseModel):
    hazmat_inspections: int = Field(default=0)
    hazmat_oos_inspections: int = Field(default=0)
    hazmat_oos_rate: float = Field(default=0.0)
    hazmat_oos_national_average: float = Field(default=0.0)

class SafetyMetrics(BaseModel):
    safety_rating: Optional[str]
    safety_rating_date: Optional[datetime]
    safety_rating_age_years: Optional[float]
    
    review_date: Optional[datetime]
    review_type: Optional[str]
    safety_review_date: Optional[datetime]
    safety_review_type: Optional[str]
    
    crash_total: int = Field(default=0)
    fatal_crashes: int = Field(default=0)
    injury_crashes: int = Field(default=0)
    tow_crashes: int = Field(default=0)
    crash_rate: float = Field(default=0.0)
    
    driver_inspections: int = Field(default=0)
    driver_oos_inspections: int = Field(default=0)
    driver_oos_rate: float = Field(default=0.0)
    driver_oos_national_average: float = Field(default=0.0)
    
    vehicle_inspections: int = Field(default=0)
    vehicle_oos_inspections: int = Field(default=0)
    vehicle_oos_rate: float = Field(default=0.0)
    vehicle_oos_national_average: float = Field(default=0.0)
    
    hazmat_metrics: HazmatMetrics = Field(default_factory=HazmatMetrics)

class CarrierOperation(BaseModel):
    code: Optional[str]
    description: Optional[str]

class CensusInfo(BaseModel):
    census_type: Optional[str]
    census_type_desc: Optional[str]
    census_type_id: Optional[int]

@dataclass
class CarrierStatus:
    is_active: bool
    operating_status: str
    allowed_to_operate: bool

class AuthorityStatus(BaseModel):
    common_authority: Optional[str]
    contract_authority: Optional[str]
    broker_authority: Optional[str]
    enterprise_authority: Optional[str]

class InsuranceInfo(BaseModel):
    bipd_required: bool = Field(default=False)
    bipd_on_file: Optional[str]
    bipd_required_amount: Optional[str]
    cargo_required: Optional[str]
    cargo_on_file: Optional[str]
    bond_required: Optional[str]
    bond_on_file: Optional[str]

@dataclass
class CarrierProfile:
    dot_number: str
    legal_name: str
    status: CarrierStatus
    
    @classmethod
    def from_fmcsa_data(cls, data: Dict[str, Any]) -> 'CarrierProfile':
        # Extract carrier info from nested structure
        carrier = data.get('content', {}).get('carrier', {})
        
        # Add debugging
        print("Parsing carrier data:", json.dumps(carrier, indent=2))
        
        return cls(
            dot_number=str(carrier.get('dotNumber')),
            legal_name=carrier.get('legalName', ''),
            status=CarrierStatus(
                is_active=carrier.get('statusCode') == 'A',
                operating_status=carrier.get('operatingStatus', ''),
                allowed_to_operate=carrier.get('allowedToOperate') == 'Y'
            )
        )

class CarrierProfile(BaseModel):
    dot_number: str
    legal_name: str
    dba_name: Optional[str]
    ein: Optional[str]
    
    status: CarrierStatus
    authority: AuthorityStatus
    insurance: InsuranceInfo
    
    fleet_size: Optional[int]
    driver_count: Optional[int]
    
    safety_metrics: SafetyMetrics
    
    physical_address: Dict[str, str]
    
    last_update: datetime
    snapshot_date: Optional[datetime]

    @validator('dot_number', pre=True)
    def convert_dot_number_to_string(cls, v):
        return str(v) if v is not None else None

    @classmethod
    def from_fmcsa_data(cls, data: Dict[str, Any]) -> 'CarrierProfile':
        # Extract carrier info from nested structure
        carrier_info = data.get('content', {}).get('carrier', {})
        
        return cls(
            dot_number=str(carrier_info.get('dotNumber')),
            legal_name=carrier_info.get('legalName', ''),
            status=CarrierStatus(
                is_active=carrier_info.get('statusCode') == 'A',
                operating_status=carrier_info.get('operatingStatusDesc', ''),
                allowed_to_operate=carrier_info.get('allowedToOperate') == 'Y'
            ),
            # ... other fields
        )

    def _assess_risk(self, profile: 'CarrierProfile') -> Dict[str, Any]:
        risk_factors = []
        risk_level = "LOW"
        warnings = []

        # Status checks
        if not profile.status.is_active:
            risk_factors.append("Carrier is inactive")
            risk_level = "HIGH"
        
        if not profile.status.allowed_to_operate:
            risk_factors.append("Not allowed to operate")
            risk_level = "HIGH"

        # Insurance checks
        if profile.insurance.bipd_required and not profile.insurance.bipd_on_file:
            risk_factors.append("Required BIPD insurance not on file")
            risk_level = "HIGH"

        # Add metrics analysis
        metrics_analysis = {
            "driver_oos_rate": {
                "value": profile.safety_metrics.driver_oos_rate,
                "national_average": profile.safety_metrics.driver_oos_national_average,
                "status": self._get_metric_status(
                    profile.safety_metrics.driver_oos_rate,
                    profile.safety_metrics.driver_oos_national_average
                )
            },
            "vehicle_oos_rate": {
                "value": profile.safety_metrics.vehicle_oos_rate,
                "national_average": profile.safety_metrics.vehicle_oos_national_average,
                "status": self._get_metric_status(
                    profile.safety_metrics.vehicle_oos_rate,
                    profile.safety_metrics.vehicle_oos_national_average
                )
            }
        }

        # Adjust risk level based on metrics
        for metric in metrics_analysis.values():
            if metric["status"] == "CRITICAL":
                risk_level = "HIGH"
            elif metric["status"] == "WARNING" and risk_level == "LOW":
                risk_level = "MEDIUM"

        return {
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "warnings": warnings,
            "metrics_analysis": metrics_analysis
        }