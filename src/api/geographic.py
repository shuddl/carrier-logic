# geographic.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from ..services.location_service import LocationProcessor, RouteAnalyzer, CarrierGeographicAnalysis, GeoVisualizer
from ..database.models import CarrierRecord, CarrierRoute, InspectionLocation
from ..database.database import get_db
from ..repositories.carrier_repository import CarrierRepository

# Ensure these functions are defined or imported
def calculate_safety_score(base_analysis: Dict[str, Any]) -> float:
    # Implement the logic to calculate safety score
    return 0.0

def get_comparison_data(base_analysis: Dict[str, Any], history: Any) -> Dict[str, Any]:
    # Implement the logic to get comparison data
    return {}

def get_compliance_status(base_analysis: Dict[str, Any]) -> Dict[str, Any]:
    # Implement the logic to get compliance status
    return {}

def format_historical_data(history: Any) -> Dict[str, Any]:
    # Implement the logic to format historical data
    return {}

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/carriers/{dot_number}/coverage")
async def get_carrier_coverage(dot_number: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get carrier's geographic coverage analysis"""
    carrier = db.query(CarrierRecord).filter(
        CarrierRecord.dot_number == dot_number
    ).first()
    
    if not carrier:
        raise HTTPException(status_code=404, detail="Carrier not found")
    
    analyzer = RouteAnalyzer(db)
    coverage = analyzer.get_carrier_coverage(carrier.id)
    
    return coverage

@router.get("/carriers/{dot_number}/routes")
async def get_carrier_routes(dot_number: str, db: Session = Depends(get_db)):
    """Get carrier's detected routes"""
    carrier = db.query(CarrierRecord).filter(
        CarrierRecord.dot_number == dot_number
    ).first()
    
    if not carrier:
        raise HTTPException(status_code=404, detail="Carrier not found")
    
    routes = db.query(CarrierRoute).filter(
        CarrierRoute.carrier_id == carrier.id
    ).all()
    
    return {
        "route_count": len(routes),
        "routes": [
            {
                "confidence": route.confidence_score,
                "first_seen": route.first_seen,
                "last_seen": route.last_seen,
                "distance_miles": route.distance_miles
            } for route in routes
        ]
    }

@router.get("/carriers/{dot_number}/analytics")
async def get_carrier_analytics(dot_number: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get carrier's geographic analytics"""
    try:
        logger.debug(f"Fetching carrier data for DOT: {dot_number}")
        carrier = db.query(CarrierRecord).filter(
            CarrierRecord.dot_number == dot_number
        ).first()
        
        if not carrier:
            logger.error(f"Carrier {dot_number} not found")
            raise HTTPException(status_code=404, detail="Carrier not found")
        
        analysis = CarrierGeographicAnalysis()
        analytics = analysis.analyze(carrier)
        
        logger.debug(f"Analytics for carrier {dot_number}: {analytics}")
        return analytics
    except Exception as e:
        logger.error(f"Error analyzing carrier {dot_number}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/carriers/{dot_number}/geographic-analysis")
async def get_geographic_analysis(
    dot_number: str, 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive geographic analysis for carrier
    
    Args:
        dot_number: DOT number of carrier to analyze
        db: Database session dependency
        
    Returns:
        Dict containing geographic analysis results
        
    Raises:
        HTTPException: If carrier not found or analysis fails
    """
    try:
        analyzer = CarrierGeographicAnalysis(db)
        analysis = analyzer.analyze_carrier(dot_number)
        
        if "error" in analysis:
            raise HTTPException(
                status_code=404,
                detail=analysis["error"]
            )
            
        return {
            "carrier": analysis["carrier_info"],
            "analysis": {
                "geographic": analysis["geographic_analysis"],
                "timestamp": analysis["analysis_date"]
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

@router.get("/carriers/{dot_number}/route-stats")
async def get_route_statistics(dot_number: str, db: Session = Depends(get_db)):
    """Get detailed statistics about carrier routes"""
    analyzer = CarrierGeographicAnalysis(db)
    analysis = analyzer.analyze_carrier(dot_number)
    
    if "error" in analysis:
        raise HTTPException(status_code=404, detail=analysis["error"])
        
    return {
        "route_patterns": analysis['geographic_analysis']['patterns'],
        "state_coverage": len(analysis['geographic_analysis']['frequency_analysis']['state_pairs']),
        "most_frequent_routes": analysis['geographic_analysis']['frequency_analysis']['most_frequent'],
        "total_distance": sum(p['distance_miles'] for p in analysis['geographic_analysis']['patterns'])
    }

@router.get("/carriers/{dot_number}/map-data")
async def get_carrier_map_data(dot_number: str, db: Session = Depends(get_db)):
    """Get carrier data formatted for map visualization"""
    analyzer = CarrierGeographicAnalysis(db)
    visualizer = GeoVisualizer()
    
    # Get base analysis
    analysis = analyzer.analyze_carrier(dot_number)
    
    if ("error" in analysis):
        raise HTTPException(status_code=404, detail=analysis["error"])
    
    # Get routes and inspections
    routes = db.query(CarrierRoute).filter(
        CarrierRoute.carrier_id == analysis['carrier_info']['id']
    ).all()
    
    inspections = db.query(InspectionLocation).filter(
        InspectionLocation.carrier_id == analysis['carrier_info']['id']
    ).all()
    
    return {
        "carrier_info": analysis['carrier_info'],
        "routes": visualizer.create_route_geojson(routes),
        "inspections": visualizer.create_inspection_geojson(inspections),
        "stats": {
            "total_routes": len(routes),
            "total_inspections": len(inspections),
            "state_frequency": analysis['geographic_analysis']['frequency_analysis']['state_pairs']
        }
    }