from typing import Dict, Any
from ..models import CarrierRecord

class CarrierAnalysisService:
    def analyze_carrier(self, carrier: CarrierRecord) -> Dict[str, Any]:
        # Now using CarrierRecord object instead of dict
        return {
            "risk_level": self._assess_risk_level(carrier),
            "warnings": self._get_warnings(carrier),
            "metrics": self._analyze_metrics(carrier)
        }

    def _assess_risk_level(self, carrier: CarrierRecord) -> str:
        if not carrier.status.is_active:
            return "HIGH"
        if not carrier.status.allowed_to_operate:
            return "HIGH"
        return "LOW"