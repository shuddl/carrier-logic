import React from 'react';

function App() {
  return (
    <div className="App">
      <h1>Carrier Logic</h1>
    </div>
  );
}

export default App;

// server.js
const express = require('express');
const path = require('path');
const app = express();

// Import your API router
const apiRouter = require('./routes/api'); // Adjust the path as necessary

// Parse JSON bodies (as sent by API clients)
app.use(express.json());

// **Define API routes before any other routes**
app.use('/api', apiRouter);

// Serve static files from the React app build directory
app.use(express.static(path.join(__dirname, 'build')));

// The catch-all handler: serves `index.html` for any request that doesn't match above
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

const PORT = process.env.PORT || 8000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});