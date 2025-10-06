// RotatingEarth.jsx

import React, { useRef, useEffect } from 'react';
import Globe from 'react-globe.gl';

function RotatingEarth() {
  const globeEl = useRef();

  useEffect(() => {
    
    if (globeEl.current) {
      const controls = globeEl.current.controls();
      

      controls.autoRotate = true;
      controls.autoRotateSpeed = 1; 
      const renderer = globeEl.current.renderer();
      if (renderer) {
          renderer.setClearColor(0x000000, 0); 
      }
    }
  }, []); 

  return (
    <div style={{ width: '100%', height: '100%' }}> 
      <Globe
        ref={globeEl}
        globeImageUrl="//unpkg.com/three-globe/example/img/earth-night.jpg"
        // backgroundImageUrl="//unpkg.com/three-globe/example/img/night-sky.png"

        showAtmosphere={true}
        backgroundColor="rgba(0,0,0,0)" 
      />
    </div>
  );
}

export default RotatingEarth;