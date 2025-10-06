import React from 'react';
import './AboutUs.css'; // Assuming you have an external CSS file for the styles

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
            At **Check Now**, we believe weather should be a guide, not an obstacle. Our project was born from the frustration of uncertain planning.
            We provide clear weather predictions and, most importantly, **smart activity suggestions** based on the date and location you choose. Say goodbye to plans ruined by unexpected rain!
          </p>
          <span className="mission-icon">🗺️</span>
        </div>
      </section>

      {/* Philosophy Section - Card Style */}
      <section className="about-team-philosophy">
        <h2>🌱 Our Philosophy</h2>
        <div className="philosophy-grid">
          <div className="philosophy-item">
            <span className="icon">💡</span>
            <h3>Absolute Clarity</h3>
            <p>Complex weather data presented simply for quick, confident decision-making.</p>
          </div>
          <div className="philosophy-item">
            <span className="icon">🚀</span>
            <h3>Constant Innovation</h3>
            <p>We use the best technology to ensure our activity recommendations are highly accurate and relevant.</p>
          </div>
          <div className="philosophy-item">
            <span className="icon">🤝</span>
            <h3>User Focus</h3>
            <p>Designed to make planning an adventure, a dinner, or a relaxing day a seamless experience.</p>
          </div>
        </div>
      </section>

      {/* Call to Action or Footer */}
      <footer className="about-footer">
        <p>Ready to plan your next activity without worries? ☁️</p>
        <button className="cta-button">Start Exploring Now!</button>
      </footer>
    </div>
  );
}

export default AboutPage;