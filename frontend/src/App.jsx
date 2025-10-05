
import React, { useState } from 'react'; 

function App() {
  const [contador, setContador] = useState(0); 
  return (
    <div className="App">
      {/* 3. Escribe tus elementos HTML y componentes de React aquí */}
      <h1>HELLO NASA</h1>
      <p>
        Este es el contenido de mi archivo <strong>App.jsx</strong>.
      </p>
      
      {/* 4. Puedes inyectar variables de JavaScript con llaves {} */}
      <button onClick={() => setContador(contador + 1)}>
        Clics: {contador}
      </button>
      
      {/* 5. Aquí podrías renderizar otros componentes (como <MiHeader />) */}
    </div>
  );
}

// 6. Exporta el componente para que pueda ser usado en el archivo principal (main.jsx)
export default App;