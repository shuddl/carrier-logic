from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    risk_level: str
    risk_factors: List[str]
    performance_metrics: Dict[str, float]
    recommendations: List[str]
    analysis_date: datetime

class CarrierAnalysis:
    def __init__(self):
        self.national_averages = {
            'driver_oos_rate': 5.51,
            'vehicle_oos_rate': 20.72,
            'crash_rate': 0.3
        }

    def analyze_carrier_performance(self, carrier_data: Dict[str, Any]) -> AnalysisResult:
        """Analyze carrier safety performance and risk factors"""
        try:
            risk_level, risk_factors = self._assess_risk(carrier_data)
            metrics = self._calculate_performance_metrics(carrier_data)
            recommendations = self._generate_recommendations(risk_factors, metrics)
            
            return AnalysisResult(
                risk_level=risk_level,
                risk_factors=risk_factors,
                performance_metrics=metrics,
                recommendations=recommendations,
                analysis_date=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error analyzing carrier: {str(e)}")
            raise

    def _assess_risk(self, data: Dict[str, Any]) -> tuple[str, List[str]]:
        """Evaluate carrier risk level and identify risk factors"""
        risk_factors = []
        risk_level = "LOW"

        # Check fatal crashes
        if data.get('fatal_crashes', 0) > 0:
            risk_factors.append("Has fatal crashes in record")
            risk_level = "HIGH"

        # Check OOS rates
        driver_oos = float(data.get('driver_oos_rate', 0))
        vehicle_oos = float(data.get('vehicle_oos_rate', 0))

        if driver_oos > self.national_averages['driver_oos_rate']:
            risk_factors.append("Driver out-of-service rate above national average")
            risk_level = "MEDIUM" if risk_level != "HIGH" else "HIGH"

        if vehicle_oos > self.national_averages['vehicle_oos_rate']:
            risk_factors.append("Vehicle out-of-service rate above national average")
            risk_level = "MEDIUM" if risk_level != "HIGH" else "HIGH"

        return risk_level, risk_factors

    def _calculate_performance_metrics(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate key performance metrics"""
        metrics = {}
        
        # Safety metrics
        metrics['crash_rate'] = self._calculate_crash_rate(
            data.get('crash_count', 0),
            data.get('vehicle_count', 1)
        )
        
        # Compliance metrics
        metrics['driver_compliance'] = 100 - float(data.get('driver_oos_rate', 0))
        metrics['vehicle_compliance'] = 100 - float(data.get('vehicle_oos_rate', 0))
        
        # Relative performance
        metrics['safety_score'] = self._calculate_safety_score(data)
        
        return metrics

    def _calculate_crash_rate(self, crashes: int, vehicles: int) -> float:
        """Calculate crashes per vehicle"""
        if vehicles <= 0:
            return 0.0
        return round(crashes / vehicles, 3)

    def _calculate_safety_score(self, data: Dict[str, Any]) -> float:
        """Calculate overall safety score (0-100)"""
        weights = {
            'crash_rate': 0.4,
            'driver_oos': 0.3,
            'vehicle_oos': 0.3
        }
        
        crash_score = max(0, 100 * (1 - self._calculate_crash_rate(
            data.get('crash_count', 0),
            data.get('vehicle_count', 1)
        ) / self.national_averages['crash_rate']))
        
        driver_score = max(0, 100 * (1 - float(data.get('driver_oos_rate', 0)) / 
                                   self.national_averages['driver_oos_rate']))
        
        vehicle_score = max(0, 100 * (1 - float(data.get('vehicle_oos_rate', 0)) / 
                                    self.national_averages['vehicle_oos_rate']))
        
        return round(
            crash_score * weights['crash_rate'] +
            driver_score * weights['driver_oos'] +
            vehicle_score * weights['vehicle_oos'],
            1
        )

    def _generate_recommendations(
        self,
        risk_factors: List[str],
        metrics: Dict[str, float]
    ) -> List[str]:
        """Generate safety recommendations based on analysis"""
        recommendations = []
        
        if "Has fatal crashes in record" in risk_factors:
            recommendations.append("Immediate safety program review recommended")
            recommendations.append("Schedule comprehensive driver training")
            
        if metrics['driver_compliance'] < 90:
            recommendations.append("Implement enhanced driver monitoring program")
            recommendations.append("Review driver qualification procedures")
            
        if metrics['vehicle_compliance'] < 90:
            recommendations.append("Increase preventive maintenance frequency")
            recommendations.append("Review vehicle inspection procedures")
            
        if not recommendations:
            recommendations.append("Maintain current safety programs")
            
        return recommendations

def analyze_carrier_performance(carrier_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for running carrier analysis"""
    analyzer = CarrierAnalysis()
    result = analyzer.analyze_carrier_performance(carrier_data)
    return result.__dict__