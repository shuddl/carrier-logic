import React, { useState, useMemo } from 'react';

declare global {
  namespace JSX {
    interface IntrinsicElements {
      [elemName: string]: any;
    }
  }
}
import { JSX } from 'react/jsx-runtime';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

const CarrierMap = ({ carrierData }: { carrierData: any }) => {
  const [selectedRoute, setSelectedRoute] = useState<{
    confidence: number;
    distance: number;
    inspectionCount: number;
  } | null>(null);
  
  // Helper function to convert lat/lng to SVG coordinates
  /**
   * Converts latitude and longitude to SVG coordinates.
   * @param {number} lat - The latitude.
   * @param {number} lng - The longitude.
   * @returns {[number, number]} The x and y coordinates.
   */
  const convertToXY = (lat: number, lng: number): [number, number] => {
    // US bounds roughly: lat: 25-50, lng: -125 to -65
    const mapWidth = 800;
    const mapHeight = 400;
    const x = ((lng + 125) * mapWidth) / 60;  // Scale longitude to width
    const y = ((50 - lat) * mapHeight) / 25;  // Scale latitude to height
    return [x, y];
  };

  const points = useMemo(() => carrierData.inspections.map((insp: { latitude: number; longitude: number; violations: number; city: string; state: string; }) => ({
    ...insp,
    xy: convertToXY(insp.latitude, insp.longitude)
  })), [carrierData.inspections]);

  const routes = useMemo(() => carrierData.routes.map((route: { geometry: { coordinates: [number, number][] }; confidence: number; distance: number; inspectionCount: number; }, index: number) => ({
    ...route,
    points: route.geometry.coordinates.map(([lat, lng]) => convertToXY(lat, lng)),
    name: `Route ${index + 1}`
  })), [carrierData.routes]);

  const constructPathD = (points: [number, number][]) => {
    return `M ${points.map(([x, y]) => `${x},${y}`).join(' L ')}`;
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-4">
      {/* Map Container */}
      <div className="relative bg-white rounded-lg shadow-lg mb-4">
        <div className="bg-gray-50 p-4 rounded-t-lg">
          <h2 className="text-lg font-semibold">Carrier Route Map</h2>
        </div>
        
        <svg 
          width="800" 
          height="400" 
          viewBox="0 0 800 400" 
          className="w-full h-full"
        >
          {/* US Map Background (simplified) */}
          <rect 
            x="0" 
            y="0" 
            width="800" 
            height="400" 
            fill="#f8fafc" 
            stroke="#e2e8f0"
          />
          
          {/* Routes */}
          {routes.map((route: { geometry: { coordinates: [number, number][] }; confidence: number; distance: number; inspectionCount: number; points: [number, number][]; name: string; }, idx: number) => (
            <g key={`route-${idx}`}>
              <path
                d={constructPathD(route.points)}
                stroke={`hsl(${route.confidence * 120}, 70%, 50%)`}
                strokeWidth="2"
                fill="none"
                className="transition-all hover:opacity-80"
                onMouseEnter={() => setSelectedRoute(route)}
                onMouseLeave={() => setSelectedRoute(null)}
              />
            </g>
          ))}
          {points.map((point: { latitude: number; longitude: number; violations: number; city: string; state: string; xy: [number, number] }, idx: number) => {
            const [cx, cy] = point.xy;
            return (
              <circle
                key={`point-${idx}`}
                cx={cx}
                cy={cy}
                r={Math.min(point.violations * 2 + 4, 12)}
                fill="red"
                opacity="0.6"
                className="transition-all hover:opacity-100"
              >
                <title>{`${point.city}, ${point.state} - ${point.violations} violations`}</title>
              </circle>
            );
          })}
        </svg>
      </div>

      {/* Analytics Dashboard */}
      <div className="grid grid-cols-2 gap-4">
        {/* Route Confidence Trends */}
        <div className="bg-white rounded-lg shadow-lg p-4">
          <h3 className="text-lg font-semibold mb-4">Route Confidence Trends</h3>
          <LineChart width={350} height={200} data={routes}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Line 
              type="monotone" 
              dataKey="confidence" 
              stroke="#6366f1" 
              strokeWidth={2}
            />
          </LineChart>
        </div>

        {/* Inspection Frequency */}
        <div className="bg-white rounded-lg shadow-lg p-4">
          <h3 className="text-lg font-semibold mb-4">Inspections by State</h3>
          <LineChart width={350} height={200} data={carrierData.stateStats}>
            <XAxis dataKey="name" />
            <XAxis dataKey="state" />
            <YAxis />
            <Tooltip />
            <Line 
              type="monotone" 
              dataKey="inspections" 
              stroke="#2dd4bf" 
              strokeWidth={2}
            />
          </LineChart>
        </div>
      </div>

      {/* Selected Route Info Overlay */}
      {selectedRoute && (
        <div className="route-overlay">
          <h4 className="font-semibold text-lg mb-2">Route Details</h4>
          <div className="space-y-2">
            <p className="text-sm">
              Confidence: 
              <span className="ml-2 font-medium">
                {(selectedRoute.confidence * 100).toFixed()}%
              </span>
            </p>
            <p className="text-sm">
              Distance: 
              <span className="ml-2 font-medium">
                {selectedRoute.distance} miles
              </span>
            </p>
            <p className="text-sm">
              Inspections: 
              <span className="ml-2 font-medium">
                {selectedRoute.inspectionCount}
              </span>
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default CarrierMap;