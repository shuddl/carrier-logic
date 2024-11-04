// src/components/CarrierAnalysis.js

import React, { useEffect, useState } from 'react';
import { analyzeCarrier } from '../api';

const CarrierAnalysis = ({ carrierId }) => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await analyzeCarrier(carrierId);
        setData(result);
      } catch (err) {
        setError(err.message);
      }
    };

    fetchData();
  }, [carrierId]);

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!data) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1>Carrier Analysis</h1>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
};

export default CarrierAnalysis;