import React, { useState } from 'react';
import './index.css'; 
import RotatingEarth from './RotatingEarth'; 

function App() {
  const [menuAbierto, setMenuAbierto] = useState(false); 

  const toggleMenu = () => {
    setMenuAbierto(!menuAbierto);
  };

  return (
    <div className="bienvenida-container">
      {/* Barra de Navegación / Menú */}
      <nav className="navbar">
        <div className="navbar-brand">Check Now</div>
        <button className="menu-toggle" onClick={toggleMenu}>
          {menuAbierto ? '✕' : '☰'} 
        </button>
        <ul className={`nav-links ${menuAbierto ? 'active' : ''}`}>
          <li><a href="#inicio">Home</a></li>
          <li><a href="#clima">weather</a></li>
          <li><a href="#about">About us</a></li>
          <li><a href="#contacto">Contact</a></li>
        </ul>
      </nav>

      {/* Contenido Principal de Bienvenida */}
      <header className="hero-section">
        <div className="hero-content">
          <h1>Explore your future now!</h1>
          <p>Don't worry about whether it will rain at your next destination!</p>
          <button className="btn-explorar">check the weather</button>
        </div>
        
        <div className="planet-container"> 
            <RotatingEarth /> 
        </div>

      </header>

      {/* ... */}
    </div>
  );
}

export default App;