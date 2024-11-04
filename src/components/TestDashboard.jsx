import React, { useEffect, useState } from 'react';
import { EnhancedCarrierAnalytics } from './EnhancedCarrierAnalytics';

export const TestDashboard = () => {
    const [carrierData, setCarrierData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetch('/carriers/2449101/analytics', {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            // Log raw response for debugging
            console.log('Raw response:', response);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Log parsed JSON data
            console.log('Parsed JSON data:', data);
            setCarrierData(data);
            setLoading(false);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            setError(error.message);
            setLoading(false);
        });
    }, []);

    // Show raw JSON data for debugging
    const renderDebugData = () => {
        if (carrierData) {
            return (
                <div className="debug-section">
                    <h3>Raw JSON Data:</h3>
                    <pre style={{ 
                        background: '#f5f5f5', 
                        padding: '1rem',
                        borderRadius: '4px',
                        overflow: 'auto'
                    }}>
                        {JSON.stringify(carrierData, null, 2)}
                    </pre>
                </div>
            );
        }
        return null;
    };

    if (loading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div>Error: {error}</div>;
    }

    return (
        <div>
            {/* Debug section */}
            {renderDebugData()}
            
            {/* Regular component rendering */}
            {carrierData && (
                <EnhancedCarrierAnalytics carrierData={carrierData} />
            )}
        </div>
    );
};