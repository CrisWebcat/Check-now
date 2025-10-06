import "leaflet/dist/leaflet.css";
import React, { useState, useRef, useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap, useMapEvents } from "react-leaflet";
import L from "leaflet";
import "./WeatherPage.css";

const markerIcon = new L.Icon({
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

const MapCenter = ({ position }) => {
  const map = useMap();
  useEffect(() => {
    if (position) map.setView(position, 12);
  }, [position, map]);
  return null;
};

const MapClickHandler = ({ onSelect }) => {
  useMapEvents({
    dblclick(e) {
      onSelect([e.latlng.lat, e.latlng.lng]);
    },
  });
  return null;
};

const WeatherPage = () => {
  const [selectedPosition, setSelectedPosition] = useState(null);
  const [country, setCountry] = useState("");
  const [city, setCity] = useState("");
  const [locality, setLocality] = useState("");
  const [dateTime, setDateTime] = useState("");
  const [weatherData, setWeatherData] = useState({});
  const resultRef = useRef(null);

  useEffect(() => {
    const container = document.querySelector(".weather-page");
    container.classList.add("blurred");
    setTimeout(() => {
      container.classList.remove("blurred");
      container.classList.add("fade-in");
    }, 100);
  }, []);

  const currentYear = new Date().getFullYear();
  const minYear = currentYear - 40;
  const maxYear = currentYear + 5;

  const searchLocation = async () => {
    if (!country && !city && !locality) {
      alert("Please enter at least one field (Country, City, or Locality).");
      return;
    }
    if (!dateTime) {
      alert("Please select a date and time.");
      return;
    }

    const selectedDate = new Date(dateTime);
    const today = new Date();

    if (selectedDate.getFullYear() < minYear || selectedDate.getFullYear() > maxYear) {
      alert(`Date must be between ${minYear} and ${maxYear}`);
      return;
    }

    const query = [locality, city, country].filter(Boolean).join(", ");
    const url = `https://nominatim.openstreetmap.org/search?format=json&accept-language=en&q=${encodeURIComponent(query)}`;
    try {
      const response = await fetch(url);
      const data = await response.json();

      if (!data || data.length === 0) {
        alert("Location not found!");
        return;
      }

      const { lat, lon } = data[0];
      const position = [parseFloat(lat), parseFloat(lon)];
      setSelectedPosition(position);

      let endpoint = selectedDate > today
        ? "http://localhost:5000/query"
        : "http://localhost:5000/query_nasa";

      const weatherResponse = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ country, city, locality, dateTime }),
      });

      if (!weatherResponse.ok) {
        alert("Error fetching weather data from backend.");
        return;
      }

      const weather = await weatherResponse.json();
      setWeatherData(weather);

      setTimeout(() => {
        resultRef.current.scrollIntoView({ behavior: "smooth" });
      }, 200);

    } catch (error) {
      console.error(error);
      alert("Error fetching location or weather data.");
    }
  };

  return (
    <div className="weather-page">
      {/* PANEL IZQUIERDO */}
      <div className="weather-info">
        <div className="input-group">
          <label>Country</label>
          <input value={country} onChange={(e) => setCountry(e.target.value)} placeholder="Enter country" />
        </div>

        <div className="input-group">
          <label>City / District / State</label>
          <input value={city} onChange={(e) => setCity(e.target.value)} placeholder="Enter city, district, or state" />
        </div>

        <div className="input-group">
          <label>Locality</label>
          <input value={locality} onChange={(e) => setLocality(e.target.value)} placeholder="Enter locality" />
        </div>

        <div className="input-row">
          <input
            type="datetime-local"
            className="date-input"
            value={dateTime}
            onChange={(e) => setDateTime(e.target.value)}
            min={`${minYear}-01-01T00:00`}
            max={`${maxYear}-12-31T23:59`}
          />
          <button className="show-btn" onClick={searchLocation}>Show on Map</button>
        </div>
      </div>

      {/* PANEL DERECHO - MAPA */}
      <div className="weather-details">
        <MapContainer
          center={[15.7835, -90.2308]}
          zoom={6}
          scrollWheelZoom={true}
          style={{ height: "100%", width: "100%", minHeight: "300px" }}
          doubleClickZoom={false}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; OpenStreetMap contributors'
          />
          <MapClickHandler onSelect={(latlng) => setSelectedPosition(latlng)} />
          {selectedPosition && (
            <>
              <Marker position={selectedPosition} icon={markerIcon}>
                <Popup>
                  Selected location:<br />
                  Lat: {selectedPosition[0].toFixed(4)}, Lon: {selectedPosition[1].toFixed(4)}
                </Popup>
              </Marker>
              <MapCenter position={selectedPosition} />
            </>
          )}
        </MapContainer>
      </div>

      {/* CUADRO DE RESULTADOS SIEMPRE VISIBLE */}
      <div className="weather-result below-map" ref={resultRef}>
        <h4>Weather Data</h4>
        <p>Temperature: {weatherData.temperature || "--"}</p>
        <p>Precipitation: {weatherData.precipitation || "--"}</p>
        <p>Wind: {weatherData.wind || "--"}</p>
        <p>Solar Radiation: {weatherData.solarRadiation || "--"}</p>
      </div>
    </div>
  );
};

export default WeatherPage;
