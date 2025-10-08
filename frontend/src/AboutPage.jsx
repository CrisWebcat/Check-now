import React from 'react';
import { Link } from 'react-router-dom'; // 👈 1. Importar el componente Link
import './AboutUs.css'; 

function AboutPage() {
  return (
    <div className="about-container">
      {/* Welcome/Title Section */}
      <header className="about-header">
        <h1> Check Now: Navigating Your Weather, Planning Your Day </h1>
        <p className="subtitle">
          Are you tired of going on a trip and it raining? we avoid that!
        </p>
      </header>

      {/* Main Mission Section */}
      <section className="about-mission-section">
        <div className="mission-card">
          <h2>Our Mission: Predict and Empower</h2>
          <p>
            At Check Now , we believe weather should be a guide, not an obstacle. Our project was born from the frustration of uncertain planning.
            We provide clear weather predictions and, most importantly,  Say goodbye to plans ruined by unexpected rain!
          </p>
          <span className="mission-icon">🗺️</span>
        </div>
      </section>

      {/* Philosophy Section - Card Style */}
      <section className="about-team-philosophy">
        <h2>Our Mentality</h2>
        <div className="philosophy-grid">
          <div className="philosophy-item">
            <span className="icon">💡</span>
            <h3>Absolute Clarity</h3>
            <p>Don't worry about complicated data due to the weather, we will explain it to you in the best way.</p>
          </div>
          <div className="philosophy-item">
            <span className="icon">🚀</span>
            <h3>Constant Innovation</h3>
            <p>We use technology so that no one worries about their outdoor activities and they know what is happening around us..</p>
          </div>
          <div className="philosophy-item">
            <span className="icon">🤝</span>
            <h3>User Focus</h3>
            <p>Designed to make planning an adventure, a dinner, anextreme travel, agriculture or a relaxing day a seamless experience.</p>
          </div>
        </div>
      </section>

      {/* Call to Action or Footer */}
      <footer className="about-footer">
        <p>Ready to plan your next activity without worries? ☁️</p>
        {/* 🛑 CORRECCIÓN: Reemplazar <button> con <Link to="/weather"> 🛑 */}
        <Link to="/weather" className="cta-button">
            Start Exploring Now!
        </Link>
      </footer>
    </div>
  );
}

export default AboutPage;