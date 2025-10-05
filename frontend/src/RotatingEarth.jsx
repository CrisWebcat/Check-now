// RotatingEarth.jsx

import React from 'react';
import Globe from 'react-globe.gl';

function RotatingEarth() {
  return (
    // Es crucial que el div interno tenga height: '100%' para que Globe lo llene
    <div style={{ width: '100%', height: '100%' }}> 
      <Globe
        globeImageUrl="//unpkg.com/three-globe/example/img/earth-night.jpg"
        backgroundImageUrl="//unpkg.com/three-globe/example/img/night-sky.png"
        globeRotateSpeed={0.1} 
        showAtmosphere={true}
        backgroundColor="rgba(0,0,0,0)" // Transparente para que el fondo se vea
      />
    </div>
  );
}

export default RotatingEarth;