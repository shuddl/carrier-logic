from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from shapely.geometry import Point, LineString, MultiPoint
from shapely.ops import nearest_points
from sklearn.cluster import DBSCAN
import numpy as np
from collections import defaultdict

class RoutePatternDetector:
    def __init__(self, min_inspections: int = 3, time_window_days: int = 365):
        self.min_inspections = min_inspections
        self.time_window = timedelta(days=time_window_days)
        
    def detect_patterns(self, inspections: List[Dict]) -> List[Dict]:
        if len(inspections) < self.min_inspections:
            return []

        # Sort inspections by date
        sorted_inspections = sorted(
            inspections,
            key=lambda x: datetime.strptime(x['inspection_date'], '%Y-%m-%d')
        )

        # Group by time windows
        patterns = []
        current_window = []
        window_start = datetime.strptime(sorted_inspections[0]['inspection_date'], '%Y-%m-%d')

        for inspection in sorted_inspections:
            insp_date = datetime.strptime(inspection['inspection_date'], '%Y-%m-%d')
            if insp_date - window_start <= self.time_window:
                current_window.append(inspection)
            else:
                if len(current_window) >= self.min_inspections:
                    pattern = self._analyze_window(current_window)
                    if pattern:
                        patterns.append(pattern)
                current_window = [inspection]
                window_start = insp_date

        # Process last window
        if len(current_window) >= self.min_inspections:
            pattern = self._analyze_window(current_window)
            if pattern:
                patterns.append(pattern)

        return patterns

    def _analyze_window(self, inspections: List[Dict]) -> Dict:
        # Extract coordinates
        coords = [(insp['longitude'], insp['latitude']) for insp in inspections]
        
        # Perform clustering
        clustering = DBSCAN(eps=0.5, min_samples=2).fit(coords)
        
        # Analyze clusters
        clusters = defaultdict(list)
        for idx, label in enumerate(clustering.labels_):
            if label >= 0:  # Ignore noise points (-1)
                clusters[label].append(inspections[idx])

        # Calculate route segments
        routes = []
        for cluster in clusters.values():
            if len(cluster) >= 2:
                route = self._create_route_segment(cluster)
                routes.append(route)

        if not routes:
            return None

        return {
            'start_date': min(insp['inspection_date'] for insp in inspections),
            'end_date': max(insp['inspection_date'] for insp in inspections),
            'inspection_count': len(inspections),
            'routes': routes,
            'confidence_score': self._calculate_confidence(inspections, routes)
        }

    def _create_route_segment(self, inspections: List[Dict]) -> Dict:
        points = [(insp['longitude'], insp['latitude']) for insp in inspections]
        line = LineString(points)
        
        return {
            'geometry': line,
            'start_point': points[0],
            'end_point': points[-1],
            'distance_miles': self._calculate_distance(line),
            'inspection_count': len(inspections)
        }

    def _calculate_distance(self, line: LineString) -> float:
        # Approximate distance in miles
        return line.length * 69.172

    def _calculate_confidence(self, inspections: List[Dict], routes: List[Dict]) -> float:
        # Factors affecting confidence:
        # 1. Number of inspections
        # 2. Time span coverage
        # 3. Route consistency
        
        insp_count_score = min(len(inspections) / 10, 1.0)
        
        dates = [datetime.strptime(insp['inspection_date'], '%Y-%m-%d') 
                for insp in inspections]
        time_span = (max(dates) - min(dates)).days
        time_score = min(time_span / 180, 1.0)  # Scale based on 6 months
        
        route_score = min(len(routes) / 5, 1.0)
        
        return (insp_count_score * 0.4 + 
                time_score * 0.3 + 
                route_score * 0.3)

class FrequencyAnalyzer:
    def analyze_state_pairs(self, inspections: List[Dict]) -> Dict[str, Any]:
        state_pairs = defaultdict(lambda: {
            'count': 0,
            'dates': [],
            'violations': 0
        })
        
        sorted_inspections = sorted(
            inspections,
            key=lambda x: datetime.strptime(x['inspection_date'], '%Y-%m-%d')
        )
        
        for i in range(len(sorted_inspections) - 1):
            current = sorted_inspections[i]
            next_insp = sorted_inspections[i + 1]
            
            pair_key = f"{current['state']}-{next_insp['state']}"
            state_pairs[pair_key]['count'] += 1
            state_pairs[pair_key]['dates'].append(current['inspection_date'])
            state_pairs[pair_key]['violations'] += (
                current.get('violation_count', 0) + 
                next_insp.get('violation_count', 0)
            )

        return {
            'state_pairs': dict(state_pairs),
            'most_frequent': self._get_most_frequent(state_pairs),
            'total_transitions': sum(p['count'] for p in state_pairs.values())
        }

    def _get_most_frequent(self, state_pairs: Dict) -> List[Dict]:
        sorted_pairs = sorted(
            [(k, v) for k, v in state_pairs.items()],
            key=lambda x: x[1]['count'],
            reverse=True
        )
        
        return [
            {
                'states': pair[0],
                'frequency': pair[1]['count'],
                'violations': pair[1]['violations'],
                'dates': pair[1]['dates']
            }
            for pair in sorted_pairs[:5]  # Top 5 most frequent
        ]

# Create array of coordinates
def create_coordinate_array(inspection_data):
    coordinates = np.array([
        [inspection['longitude'], inspection['latitude']] 
        for inspection in inspection_data
    ])
    return coordinates

# Option 1: Define specific coordinates
longitude1 = -122.6750  # Example: Portland, OR coordinates

# Option 2: Get coordinates from data
inspection_data = [
    {'longitude': -122.6750, 'latitude': 45.5051},  # Example data
    # Add more inspection data as needed
]
longitude1 = inspection_data[0]['longitude']
latitude1 = inspection_data[0]['latitude']

# Define longitude2 and latitude2 for the example
longitude2 = -122.6765  # Example: another coordinate
latitude2 = 45.5231     # Example: another coordinate

# Sample coordinates
coords = np.array([
    [longitude1, latitude1],
    [longitude2, latitude2],
    # ... more coordinates
])

# Create DBSCAN clustering
clustering = DBSCAN(
    eps=0.5,        # Maximum distance between points in cluster
    min_samples=2   # Minimum points to form cluster
).fit(coords)

# Get cluster labels
labels = clustering.labels_