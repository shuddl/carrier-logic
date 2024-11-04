// src/components/TestDashboard.tsx
import React, { useEffect, useState } from 'react';
import EnhancedCarrierAnalytics from './EnhancedCarrierAnalytics';

interface CarrierData {
    peer_comparisons: any;
    safety_score: number;
    previous_safety_score: number;
    risk_level: string;
    risk_factors: any[];
    states_covered: number;
    previous_states_covered: number;
    inspections: Inspection[];
    routes: Route[];
    legal_name: string;
    dot_number: string;
    comparison_data: any[];
    safety_history: any[];
    state_distribution: { state: string; inspections: number; }[];
}

interface Inspection {
    latitude: number;
    longitude: number;
    // Add other inspection properties as needed
}

interface Route {
    geometry: {
        coordinates: [number, number][];
    };
    // Add other route properties as needed
}

const TestDashboard = () => {
    const [carrierData, setCarrierData] = useState<CarrierData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Fetch real data for Greyhound (DOT: 44110)
        fetch('http://localhost:8000/geographic/carriers/44110/analytics')
            .then(res => res.json())
            .then(data => {
                console.log(data); // Add this line to check the fetched data
                setCarrierData(data);
                setLoading(false);
            })
            .catch(err => {
                setError(err.message);
                setLoading(false);
            });
    }, []);

    if (loading) return (
        <div className="flex items-center justify-center min-h-screen">
            <div className="text-lg">Loading carrier data...</div>
        </div>
    );

    if (error) return (
        <div className="flex items-center justify-center min-h-screen">
            <div className="text-lg text-red-500">Error: {error}</div>
        </div>
    );

    return (
        <div className="min-h-screen bg-gray-100">
            <div className="container mx-auto py-8">
                {carrierData && (
                    <EnhancedCarrierAnalytics 
                        carrierData={carrierData}
                    />
                )}
            </div>
        </div>
    );
};

export default TestDashboard;