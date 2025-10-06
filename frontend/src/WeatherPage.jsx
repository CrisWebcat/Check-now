import "leaflet/dist/leaflet.css";

import React, { useState, useRef } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import "./WeatherPage.css";

// Icono del marcador
const markerIcon = new L.Icon({
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

// Componente para centrar el mapa
const MapCenter = ({ position }) => {
  const map = useMap();
  if (position) {
    map.setView(position, 12); // Zoom 12 al centrar
  }
  return null;
};

const WeatherPage = () => {
  const [selectedPosition, setSelectedPosition] = useState(null);
  const [country, setCountry] = useState("");
  const [city, setCity] = useState("");
  const [locality, setLocality] = useState("");

  const mapRef = useRef();

  // Función para buscar ubicación usando Nominatim
  const searchLocation = async () => {
    const query = [locality, city, country].filter(Boolean).join(", ");
    if (!query) return;

    const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}`;
    const response = await fetch(url);
    const data = await response.json();
    if (data && data.length > 0) {
      const { lat, lon } = data[0];
      setSelectedPosition([parseFloat(lat), parseFloat(lon)]);
    } else {
      alert("Location not found!");
    }
  };

  return (
    <div className="weather-page" style={{ display: "flex", flexDirection: "row", gap: "20px" }}>
      {/* Columna de inputs */}
      <div className="weather-info" style={{ flex: "1", minWidth: "250px" }}>
        <div className="input-group">
          <label>Country</label>
          <input value={country} onChange={(e) => setCountry(e.target.value)} placeholder="Enter country" />
        </div>
        <div className="input-group">
          <label>City</label>
          <input value={city} onChange={(e) => setCity(e.target.value)} placeholder="Enter city" />
        </div>
        <div className="input-group">
          <label>Locality</label>
          <input value={locality} onChange={(e) => setLocality(e.target.value)} placeholder="Enter locality" />
        </div>
        <button onClick={searchLocation} style={{ marginTop: "10px" }}>Show on Map</button>
      </div>

      {/* Contenedor del mapa */}
      <div className="weather-details" style={{ flex: "2", minWidth: "600px" }}>
        <div style={{ height: "600px", width: "100%" }}>
          <MapContainer
            center={[15.7835, -90.2308]}
            zoom={6}
            scrollWheelZoom={true}
            style={{ height: "100%", width: "100%" }}
            ref={mapRef}
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; OpenStreetMap contributors'
            />

            {selectedPosition && (
              <>
                <Marker position={selectedPosition} icon={markerIcon}>
                  <Popup>
                    Selected location: {selectedPosition[0].toFixed(4)}, {selectedPosition[1].toFixed(4)}
                  </Popup>
                </Marker>
                <MapCenter position={selectedPosition} />
              </>
            )}
          </MapContainer>
        </div>
      </div>
    </div>
  );
};

export default WeatherPage;
