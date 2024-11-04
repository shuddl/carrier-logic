import React from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './components/App';
import './styles/styles.css';

// For debugging
console.log('Starting application...');

// Get the root element
const container = document.getElementById('root');
if (!container) {
    console.error('Root element not found');
    throw new Error('Root element not found');
}

// Create root and render
const root = createRoot(container);
root.render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
);

// Add error handling for JSON parsing
window.addEventListener('error', (event) => {
    if (event.error instanceof SyntaxError) {
        console.error('JSON Parsing Error:', event.error);
    }
});

// Optional: Add global fetch interceptor for JSON
const originalFetch = window.fetch;
window.fetch = async (...args) => {
    const response = await originalFetch(...args);
    // Log all API responses for debugging
    if (response.headers.get('content-type')?.includes('application/json')) {
        response.clone().json().then(data => 
            console.log('API Response:', data)
        ).catch(err => 
            console.error('JSON parse error:', err)
        );
    }
    return response;
};