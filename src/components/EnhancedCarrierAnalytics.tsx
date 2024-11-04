// src/static/components/EnhancedCarrierAnalytics.jsx
import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import './static/css/main.css';

const LoadingSkeleton = ({ type }: { type: string }) => {
  const baseClass = "loading-shimmer rounded-lg";
  
  switch (type) {
    case "title":
      return (
        <div className="space-y-2">
          <div className={`${baseClass} h-6 w-48`}></div>
          <div className={`${baseClass} h-4 w-32`}></div>
        </div>
      );
    case "metric":
      return (
        <div className="card animate-pulse">
          <div className={`${baseClass} h-4 w-24 mb-2`}></div>
          <div className={`${baseClass} h-8 w-16`}></div>
          <div className={`${baseClass} h-4 w-32 mt-2`}></div>
        </div>
      );
    case "chart":
      return (
        <div className="card">
          <div className={`${baseClass} h-4 w-32 mb-4`}></div>
          <div className={`${baseClass} h-[300px]`}></div>
        </div>
      );
    default:
      return null;
  }
};

const MetricCard = ({ title, value, trend, isLoading }: { title: string; value: string; trend?: number; isLoading: boolean }) => {
  if (isLoading) {
    return <LoadingSkeleton type="metric" />;
  }

  return (
    <div className="card metric-card animate-fade-in">
      <h3 className="metric-title">{title}</h3>
      <div className="metric-value">{value}</div>
      {trend && (
        <div className={`metric-trend ${trend > 0 ? 'trend-up' : 'trend-down'}`}>
          {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
        </div>
      )}
    </div>
  );
};

const ChartCard = ({ title, children, isLoading }: { title: string; children: React.ReactNode; isLoading: boolean }) => {
  if (isLoading) {
    return <LoadingSkeleton type="chart" />;
  }

  return (
    <div className="card animate-fade-in">
      <h3 className="text-lg font-bold mb-4">{title}</h3>
      <div className="chart-container">
        {children}
      </div>
    </div>
  );
};

interface CarrierData {
  legal_name: string;
  dot_number: string;
  safety_score?: number;
  safety_trend?: number;
  risk_level?: string;
  states_covered?: number;
  coverage_trend?: number;
  safety_history?: { date: string; score: number }[];
  state_distribution?: { state: string; inspections: number }[];
}

const EnhancedCarrierAnalytics = ({ carrierData, isLoading = false }: { carrierData: CarrierData; isLoading?: boolean }) => {
    const [loadingStates, setLoadingStates] = useState({
        metrics: true,
        charts: true,
        details: true
    });
    const [timeRange, setTimeRange] = useState('1y');

    // Simulate progressive loading
    useEffect(() => {
        if (!isLoading) {
            const loadSequence = async () => {
                // Load metrics first
                await new Promise(resolve => setTimeout(resolve, 500));
                setLoadingStates(prev => ({ ...prev, metrics: false }));
                
                // Then charts
                await new Promise(resolve => setTimeout(resolve, 800));
                setLoadingStates(prev => ({ ...prev, charts: false }));
                
                // Finally details
                await new Promise(resolve => setTimeout(resolve, 400));
                setLoadingStates(prev => ({ ...prev, details: false }));
            };
            
            loadSequence();
        }
    }, [isLoading]);

    return (
        <div className="container">
            {/* Header with Loading State */}
            <div className="card card-header">
                {isLoading ? (
                    <LoadingSkeleton type="title" />
                ) : (
                    <div className="animate-fade-in">
                        <h1 className="text-xl font-bold">{carrierData.legal_name}</h1>
                        <p className="text-gray-600">DOT: {carrierData.dot_number}</p>
                    </div>
                )}
                <select 
                    className={`select ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                    value={timeRange}
                    onChange={(e) => setTimeRange(e.target.value)}
                    disabled={isLoading}
                >
                    <option value="3m">Last 3 Months</option>
                    <option value="6m">Last 6 Months</option>
                    <option value="1y">Last Year</option>
                </select>
            </div>

            {/* Metrics Grid with Loading States */}
            <div className="grid grid-cols-3 gap-4">
                <MetricCard 
                    title="Safety Score"
                    value={`${carrierData?.safety_score || 0}%`}
                    trend={carrierData?.safety_trend}
                    isLoading={loadingStates.metrics}
                />
                <MetricCard 
                    title="Risk Level"
                    value={carrierData?.risk_level || 'N/A'}
                    isLoading={loadingStates.metrics}
                />
                <MetricCard 
                    title="Coverage"
                    value={`${carrierData?.states_covered || 0} States`}
                    trend={carrierData?.coverage_trend}
                    isLoading={loadingStates.metrics}
                />
            </div>

            {/* Charts with Loading States */}
            <div className="grid grid-cols-2 gap-4">
                <ChartCard 
                    title="Safety Trends" 
                    isLoading={loadingStates.charts}
                >
                    <LineChart width={500} height={300} data={carrierData?.safety_history}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line 
                            type="monotone" 
                            dataKey="score" 
                            stroke="var(--primary-color)"
                            strokeWidth={2}
                        />
                    </LineChart>
                </ChartCard>

                <ChartCard 
                    title="Geographic Distribution" 
                    isLoading={loadingStates.charts}
                >
                    <BarChart width={500} height={300} data={carrierData?.state_distribution}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="state" />
                        <YAxis />
                        <Tooltip />
                        <Bar 
                            dataKey="inspections" 
                            fill="var(--primary-light)"
                        />
                    </BarChart>
                </ChartCard>
            </div>

            {/* Loading Indicator */}
            {isLoading && (
                <div className="fixed bottom-4 right-4 animate-fade-in">
                    <div className="bg-white rounded-lg shadow-lg p-4 flex items-center gap-3">
                        <div className="animate-pulse h-4 w-4 rounded-full bg-primary-light"></div>
                        <span>Loading carrier data...</span>
                    </div>
                </div>
            )}
        </div>
    );
};

export default EnhancedCarrierAnalytics;