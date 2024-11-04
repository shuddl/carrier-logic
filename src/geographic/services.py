from typing import List, Dict, Any
from datetime import datetime
from geoalchemy2.shape import from_shape
from shapely.geometry import Point, LineString
from sqlalchemy.orm import Session
from functools import lru_cache
from ..database.models import CarrierRecord
from ..models.geographic import InspectionLocation, CarrierRoute
import logging

class LocationProcessor:
    def __init__(self, db: Session):
        self.db = db

    def process_inspection_data(self, carrier_data: Dict[str, Any]) -> List[InspectionLocation]:
        # Creates InspectionLocation objects from FMCSA inspection data
        # Uses PostGIS to store geographic points
        carrier = carrier_data['carrier']
        dot_number = str(carrier['dotNumber'])
        
        # Get carrier record
        carrier_record = self.db.query(CarrierRecord).filter(
            CarrierRecord.dot_number == dot_number
        ).first()
        
        if not carrier_record:
            return []

        locations = []
        # Process each inspection location
        if 'inspections' in carrier_data:
            logging.info(f"Processing {len(carrier_data['inspections'])} inspections")
            for inspection in carrier_data['inspections']:
                if 'latitude' not in inspection or 'longitude' not in inspection:
                    continue
                if not (-90 <= inspection['latitude'] <= 90) or not (-180 <= inspection['longitude'] <= 180):
                    continue
                location = InspectionLocation(
                    carrier_id=carrier_record.id,
                    inspection_date=datetime.strptime(inspection['date'], '%Y-%m-%d'),
                    state=inspection['state'],
                    city=inspection['city'],
                    level=inspection.get('level'),
                    violation_count=len(inspection.get('violations', [])),
                    raw_data=inspection,
                    # Create PostGIS point from lat/long
                    location=from_shape(Point(
                        inspection['longitude'], 
                        inspection['latitude']
                    ), srid=4326)
                )
                locations.append(location)
                
        return locations

    def detect_routes(self, carrier_id: int) -> List[CarrierRoute]:
        # Analyzes inspection locations to detect common routes
        # Creates CarrierRoute objects for frequently traveled paths
        # Get all inspection locations for carrier
        locations = self.db.query(InspectionLocation).filter(
            InspectionLocation.carrier_id == carrier_id
        ).order_by(InspectionLocation.inspection_date).all()
        
        if len(locations) < 2:
            return []

        routes = []
        # Group points by state pairs
        state_pairs = {}
        
        for i in range(len(locations)-1):
            state_a = locations[i].state
            state_b = locations[i+1].state
            
            if state_a != state_b:
                key = f"{state_a}-{state_b}"
                if key not in state_pairs:
                    state_pairs[key] = {
                        'points': [],
                        'count': 0,
                        'first_seen': locations[i].inspection_date,
                        'last_seen': locations[i+1].inspection_date
                    }
                
                state_pairs[key]['points'].extend([
                    locations[i].location,
                    locations[i+1].location
                ])
                state_pairs[key]['count'] += 1

        # Create routes from frequent state pairs
        for key, data in state_pairs.items():
            if data['count'] >= 3:  # Minimum frequency threshold
                confidence = min(data['count'] / 10, 1.0)  # Scale confidence 0-1
                
                route = CarrierRoute(
                    carrier_id=carrier_id,
                    route_geometry=LineString(data['points']),
                    confidence_score=confidence,
                    first_seen=data['first_seen'],
                    last_seen=data['last_seen'],
                    inspection_count=data['count']
                )
                routes.append(route)

        return routes

class RouteAnalyzer:
    def __init__(self, db: Session):
        self.db = db

    @lru_cache(maxsize=128)
    def get_carrier_coverage(self, carrier_id: int) -> Dict[str, Any]:
        # Returns statistics about carrier's geographic presence
        # Includes route count, locations, state coverage
        routes = self.db.query(CarrierRoute).filter(
            CarrierRoute.carrier_id == carrier_id
        ).all()
        
        locations = self.db.query(InspectionLocation).filter(
            InspectionLocation.carrier_id == carrier_id
        ).all()

        states = {}
        for location in locations:
            if location.state not in states:
                states[location.state] = {
                    'inspection_count': 0,
                    'violation_count': 0
                }
            states[location.state]['inspection_count'] += 1
            states[location.state]['violation_count'] += location.violation_count

        return {
            'route_count': len(routes),
            'location_count': len(locations),
            'state_coverage': len(states),
            'state_details': states,
            'confidence_avg': sum(r.confidence_score for r in routes) / len(routes) if routes else 0
        }