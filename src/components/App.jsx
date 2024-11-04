import React, { ErrorBoundary } from 'react';
import { TestDashboard } from './TestDashboard';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        console.error('Error caught by boundary:', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return <div>Something went wrong with the data loading.</div>;
        }

        return this.props.children;
    }
}

export const App = () => {
    return (
        <ErrorBoundary>
            <div>
                <header>
                    <h1>CarrierLogic Analytics</h1>
                </header>
                <main>
                    <TestDashboard />
                </main>
            </div>
        </ErrorBoundary>
    );
};