import requests
import logging
from typing import Dict, Any
import os
from sqlalchemy.orm import Session
from ..config import settings
from ..database.repository import CarrierRepository
from ..models.carrier_analysis import CarrierProfile

# Configure logging
logger = logging.getLogger(__name__)

class FMCSAClient:
    def __init__(self):
        self.base_url = "https://mobile.fmcsa.dot.gov/qc"
        if not settings.webkey:
            raise ValueError("webkey not found in settings")
        self.webkey = settings.webkey

    def get_carrier_by_dot(self, dot_number: str) -> Dict[str, Any]:
        """Get carrier data by DOT number"""
        url = f"{self.base_url}/services/carriers/{dot_number}"
        print(f"Requesting URL: {url}")  # Debug print
        return self._make_request(url)

    def search_carriers_by_name(self, name: str) -> Dict[str, Any]:
        url = f"{self.base_url}/services/carriers/name/{name}"
        return self._make_request(url)
    
    def _make_request(self, url: str) -> Dict[str, Any]:
        params = {
            "webKey": self.webkey
        }

        print(f"Making request to: {url}")
        print(f"With params: {params}")

        try:
            response = requests.get(url, params=params)
            print(f"Response status: {response.status_code}")
            print(f"Full URL: {response.url}")

            if response.status_code == 200:
                data = response.json()
                if data.get("content"):
                    return data
                else:
                    # Try another request format if content is null
                    alternate_url = url.replace("/services", "")
                    print(f"Trying alternate URL: {alternate_url}")
                    response = requests.get(alternate_url, params=params)
                    return response.json()
            else:
                return {
                    "error": f"Request failed with status {response.status_code}",
                    "raw_text": response.text
                }

        except Exception as e:
            print(f"Request error: {str(e)}")
            return {"error": str(e)}

    def _assess_risk(self, profile: CarrierProfile) -> Dict[str, Any]:
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

        # Safety rating age check
        if profile.safety_metrics.safety_rating_date:
            rating_age = profile.safety_metrics.safety_rating_age_years
            if rating_age and rating_age > 2:
                warnings.append(f"Safety rating is {rating_age:.1f} years old")

        # Data completeness check
        if not profile.fleet_size or not profile.driver_count:
            warnings.append("Missing fleet size or driver count data")

        # Safety metrics checks
        if profile.safety_metrics.crash_total > 0:
            risk_factors.append(f"Has {profile.safety_metrics.crash_total} total crashes")
            if profile.safety_metrics.fatal_crashes > 0:
                risk_factors.append(f"Has {profile.safety_metrics.fatal_crashes} fatal crashes")
                risk_level = "HIGH"

        # Inspection history checks
        total_inspections = (
            profile.safety_metrics.driver_inspections +
            profile.safety_metrics.vehicle_inspections +
            profile.safety_metrics.hazmat_metrics.hazmat_inspections
        )
        
        if total_inspections == 0:
            warnings.append("No inspection history available")
        else:
            # Driver OOS Rate Check
            if profile.safety_metrics.driver_oos_rate > profile.safety_metrics.driver_oos_national_average:
                risk_factors.append("Driver out-of-service rate above national average")
                risk_level = "MEDIUM" if risk_level == "LOW" else risk_level

            # Vehicle OOS Rate Check
            if profile.safety_metrics.vehicle_oos_rate > profile.safety_metrics.vehicle_oos_national_average:
                risk_factors.append("Vehicle out-of-service rate above national average")
                risk_level = "MEDIUM" if risk_level == "LOW" else risk_level

            # Hazmat Check
            if profile.safety_metrics.hazmat_metrics.hazmat_inspections > 0:
                if profile.safety_metrics.hazmat_metrics.hazmat_oos_rate > profile.safety_metrics.hazmat_metrics.hazmat_oos_national_average:
                    risk_factors.append("Hazmat out-of-service rate above national average")
                    risk_level = "MEDIUM" if risk_level == "LOW" else risk_level

        return {
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "warnings": warnings
        }

    def _generate_recommendations(self, profile: CarrierProfile) -> Dict[str, Any]:
        recommendations = []
        monitoring_items = []

        # Status-based recommendations
        if not profile.status.is_active:
            recommendations.append("Verify current operating status before proceeding")
            
        if profile.insurance.bipd_required and not profile.insurance.bipd_on_file:
            recommendations.append("Verify current BIPD insurance coverage")

        # Data completeness recommendations
        if not profile.fleet_size or not profile.driver_count:
            recommendations.append("Request current fleet size and driver count information")

        # Safety recommendations
        if profile.safety_metrics.fatal_crashes > 0:
            monitoring_items.append("Monitor post-fatal crash safety improvements")

        if profile.safety_metrics.safety_rating_age_years:
            if profile.safety_metrics.safety_rating_age_years > 2:
                monitoring_items.append("Recent safety performance due to outdated safety rating")

        # Hazmat specific recommendations
        if profile.safety_metrics.hazmat_metrics.hazmat_inspections > 0:
            if profile.safety_metrics.hazmat_metrics.hazmat_oos_rate > profile.safety_metrics.hazmat_metrics.hazmat_oos_national_average:
                recommendations.append("Review hazmat compliance program")
                monitoring_items.append("Monthly hazmat compliance verification")

        # Authority recommendations
        if profile.authority.common_authority == 'I' and profile.authority.contract_authority == 'I':
            recommendations.append("Verify current operating authority status")

        return {
            "recommendations": recommendations,
            "monitoring_items": monitoring_items
        }

    def get_carrier_analysis(self, dot_number: str) -> Dict[str, Any]:
        try:
            carrier_data = self.get_carrier_by_dot(dot_number)
            print(f"Raw carrier data: {carrier_data}")  # Debug print
            
            if carrier_data.get('error'):
                return carrier_data
            
            profile = CarrierProfile.from_fmcsa_data(carrier_data)
            return {
                "profile": profile.dict(),
                "risk_assessment": self._assess_risk(profile),
                "recommendations": self._generate_recommendations(profile)
            }
        except Exception as e:
            print(f"Analysis error: {str(e)}")  # Debug print
            return {"error": f"Error analyzing carrier: {str(e)}"}

    def _get_metric_status(value: float, national_average: float, lower_is_better: bool = True) -> str:
        if lower_is_better:
            if value < national_average:
                return "GOOD"
            elif value < national_average * 1.5:
                return "WARNING"
            else:
                return "CRITICAL"
        else:
            if value > national_average:
                return "GOOD"
            elif value > national_average * 0.5:
                return "WARNING"
            else:
                return "CRITICAL"