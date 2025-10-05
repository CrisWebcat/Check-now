// ===============================
// 📁 App.jsx
// ===============================

// Importaciones principales de React y React Router
import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';

// Importación del archivo CSS global
import './index.css';

// Importación del componente del planeta 3D
import RotatingEarth from './RotatingEarth';

// Importaciones de las páginas internas (asegúrate de que existan estos archivos)
import WeatherPage from './WeatherPage';
import AboutPage from './AboutPage';
import ContactPage from './ContactPage';

// ============================================
// 🏠 Componente para la vista principal (Home)
// ============================================
const HomeHero = () => (
  <header className="hero-section">
    <div className="hero-content">
      {/* Título principal */}
      <h1>Explore your future now!</h1>

      {/* Subtítulo o descripción */}
      <p>Don't worry about whether it will rain at your next destination!</p>

      {/* Botón que lleva a la página del clima */}
      {/* Usamos <Link> en lugar de <a> para navegación interna con React Router */}
      <Link to="/weather" className="btn-explorar">
        Check the weather
      </Link>
    </div>

    {/* Contenedor del planeta giratorio */}
    <div className="planet-container">
      <RotatingEarth />
    </div>
  </header>
);

// ============================================
// ⚙️ Componente Principal de la Aplicación
// ============================================
function App() {
  // Estado para controlar si el menú móvil está abierto o cerrado
  const [menuAbierto, setMenuAbierto] = useState(false);

  // Función para alternar el estado del menú
  const toggleMenu = () => setMenuAbierto(!menuAbierto);

  return (
    // Envolvemos toda la app dentro del Router para habilitar las rutas
    <Router>
      <div className="bienvenida-container">
        
        {/* ============================
            🔝 Barra de navegación superior
           ============================ */}
        <nav className="navbar">
          {/* Nombre o logo de la aplicación */}
          <div className="navbar-brand">Check Now</div>

          {/* Botón de menú (hamburguesa) para pantallas pequeñas */}
          <button className="menu-toggle" onClick={toggleMenu}>
            {/* Cambia el ícono según el estado del menú */}
            {menuAbierto ? '✕' : '☰'}
          </button>

          {/* Lista de enlaces de navegación */}
          {/* className usa template literals para aplicar la clase 'active' cuando el menú está abierto */}
          <ul className={`nav-links ${menuAbierto ? 'active' : ''}`}>
            {/* Enlaces internos de la aplicación */}
            <li><Link to="/">Home</Link></li>
            <li><Link to="/weather">Weather</Link></li>
            <li><Link to="/about">About us</Link></li>
            <li><Link to="/contact">Contact</Link></li>
            {/* Si quisieras un enlace externo, usa <a> en lugar de <Link> */}
            {/* <li><a href="https://externo.com" target="_blank" rel="noopener noreferrer">External</a></li> */}
          </ul>
        </nav>

        {/* ============================
            📍 Definición de rutas (páginas)
           ============================ */}
        <Routes>
          {/* Ruta principal: muestra la pantalla de inicio */}
          <Route path="/" element={<HomeHero />} />

          {/* Página del clima */}
          <Route path="/weather" element={<WeatherPage />} />

          {/* Página "Acerca de" */}
          <Route path="/about" element={<AboutPage />} />

          {/* Página de contacto */}
          <Route path="/contact" element={<ContactPage />} />

          {/* Ruta por defecto si no se encuentra la dirección */}
          <Route
            path="*"
            element={
              <h1 style={{ padding: '10rem', color: 'white' }}>
                404 - Page Not Found
              </h1>
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

// Exportamos el componente principal
export default App;
