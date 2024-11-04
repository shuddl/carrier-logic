from typing import Dict, List, TypedDict
from geojson import Feature, FeatureCollection, LineString, Point
from datetime import datetime

class RouteDict(TypedDict):
    geometry: List[List[float]]
    confidence_score: float
    inspection_count: int
    first_seen: datetime
    last_seen: datetime

class GeoVisualizer:
    # Static methods for GeoJSON conversion
    @staticmethod
    def create_route_geojson(routes: List[RouteDict]) -> Dict:
        try:
            features = []
            for route in routes:
                route_feature = Feature(
                    geometry=LineString(route['geometry']),
                    properties={
                        'confidence': route['confidence_score'],
                        'inspection_count': route['inspection_count'],
                        'first_seen': route['first_seen'].isoformat(),
                        'last_seen': route['last_seen'].isoformat()
                    }
                )
                features.append(route_feature)
            return FeatureCollection(features)
        except KeyError as e:
            raise ValueError(f"Missing required field in route data: {e}")

    @staticmethod
    def create_inspection_geojson(inspections: List[Dict]) -> Dict:
        features = []
        for inspection in inspections:
            point_feature = Feature(
                geometry=Point((inspection['longitude'], inspection['latitude'])),
                properties={
                    'date': inspection['inspection_date'],
                    'state': inspection['state'],
                    'city': inspection['city'],
                    'violations': inspection['violation_count']
                }
            )
            features.append(point_feature)
        return FeatureCollection(features)