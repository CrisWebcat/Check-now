// RotatingEarth.jsx

import React, { useRef, useEffect } from 'react';
import Globe from 'react-globe.gl';

function RotatingEarth() {
  const globeEl = useRef(); // 1. Creamos una referencia

  useEffect(() => {
    // Este código se ejecuta una vez que el componente se monta
    if (globeEl.current) {
      const controls = globeEl.current.controls();
      
      // 2. Activamos la rotación automática
      controls.autoRotate = true;
      
      // 3. Definimos la velocidad (ajusta este valor si quieres que gire más rápido o más lento)
      controls.autoRotateSpeed = 0.5; 
    }
  }, []); // El array vacío asegura que se ejecute solo al inicio

  return (
    <div style={{ width: '100%', height: '100%' }}> 
      <Globe
        ref={globeEl} // 4. Asignamos la referencia al componente Globe
        globeImageUrl="//unpkg.com/three-globe/example/img/earth-night.jpg"
        backgroundImageUrl="//unpkg.com/three-globe/example/img/night-sky.png"
        // globeRotateSpeed={0.1} <-- Eliminamos o comentamos esta línea, ya que usamos autoRotate
        showAtmosphere={true}
        backgroundColor="rgba(0,0,0,0)" // Transparente para que el fondo CSS se vea
      />
    </div>
  );
}

export default RotatingEarth;