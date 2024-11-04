import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

export const EnhancedCarrierAnalytics = ({ carrierData }) => {
    // Validate incoming data
    if (!carrierData) {
        return <div>No carrier data available</div>;
    }

    // Destructure the JSON data
    const {
        dot_number,
        legal_name,
        safety_metrics = {},
        fleet_info = {},
        status = {}
    } = carrierData;

    return (
        <div className="analytics-container">
            {/* Basic Info */}
            <div className="info-section">
                <h2>{legal_name}</h2>
                <p>DOT Number: {dot_number}</p>
            </div>

            {/* Safety Metrics */}
            <div className="metrics-section">
                <h3>Safety Metrics</h3>
                <div className="metrics-grid">
                    <div className="metric-card">
                        <h4>Safety Rating</h4>
                        <p>{safety_metrics.safety_rating || 'N/A'}</p>
                    </div>
                    <div className="metric-card">
                        <h4>Total Crashes</h4>
                        <p>{safety_metrics.crash_total || 0}</p>
                    </div>
                    <div className="metric-card">
                        <h4>Driver OOS Rate</h4>
                        <p>{safety_metrics.driver_oos_rate || 0}%</p>
                    </div>
                    <div className="metric-card">
                        <h4>Vehicle OOS Rate</h4>
                        <p>{safety_metrics.vehicle_oos_rate || 0}%</p>
                    </div>
                </div>
            </div>

            {/* Fleet Info */}
            <div className="fleet-section">
                <h3>Fleet Information</h3>
                <div className="metrics-grid">
                    <div className="metric-card">
                        <h4>Power Units</h4>
                        <p>{fleet_info.total_power_units || 0}</p>
                    </div>
                    <div className="metric-card">
                        <h4>Drivers</h4>
                        <p>{fleet_info.total_drivers || 0}</p>
                    </div>
                </div>
            </div>

            {/* Status Information */}
            <div className="status-section">
                <h3>Operating Status</h3>
                <div className="status-grid">
                    <div className="status-card">
                        <h4>Operating Status</h4>
                        <p className={`status ${status.operating_status?.toLowerCase()}`}>
                            {status.operating_status || 'Unknown'}
                        </p>
                    </div>
                    <div className="status-card">
                        <h4>Authority Status</h4>
                        <p className={`status ${status.authority_status?.toLowerCase()}`}>
                            {status.authority_status || 'Unknown'}
                        </p>
                    </div>
                    <div className="status-card">
                        <h4>Risk Level</h4>
                        <p className={`risk-level ${status.risk_level?.toLowerCase()}`}>
                            {status.risk_level || 'Unknown'}
                        </p>
                    </div>
                </div>
            </div>

            {/* Error handling for missing data */}
            {!safety_metrics && !fleet_info && !status && (
                <div className="error-message">
                    Unable to load carrier metrics. Please try again later.
                </div>
            )}
        </div>
    );
};