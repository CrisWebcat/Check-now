// WeatherPage.js - Frontend Code

import "leaflet/dist/leaflet.css";
import React, { useState, useRef } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from "react-leaflet";
import L from "leaflet";
import "./WeatherPage.css";

// ------------------------------------
// Auxiliary Components for Leaflet
// ------------------------------------
const markerIcon = new L.Icon({
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

const MapClickHandler = ({ onSelect }) => {
  useMapEvents({
    dblclick(e) {
      onSelect([e.latlng.lat, e.latlng.lng]);
    },
  });
  return null;
};

// ------------------------------------
// Main Component
// ------------------------------------
const WeatherPage = () => {
  const [selectedPosition, setSelectedPosition] = useState(null);
  const [country, setCountry] = useState("");
  const [city, setCity] = useState("");
  const [locality, setLocality] = useState("");
  const [dateTime, setDateTime] = useState("");
  const [weatherData, setWeatherData] = useState({});
  const resultRef = useRef(null);
  
  const currentYear = new Date().getFullYear();
  const minYear = currentYear - 40;
  const maxYear = currentYear + 5;

  const getCurrentDateTimeLocal = () => {
    const now = new Date();
    // Adjust time to local timezone and format
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    return now.toISOString().slice(0, 16);
  };
  
  // Function called by double-click on the map
  const handleMapSelect = async (latlng) => {
    const [lat, lng] = latlng;
    setSelectedPosition(latlng);
    
    // 1. Reverse Geocoding (Nominatim)
    const geoUrl = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`;
    
    try {
      const response = await fetch(geoUrl);
      const data = await response.json();
      
      const address = data.address || {};
      
      // Attempt to get location names
      const newCountry = address.country || "";
      const newCity = address.city || address.town || address.village || address.county || "";
      const newLocality = address.suburb || address.neighbourhood || address.road || "";
      
      // 2. Update states
      setCountry(newCountry);
      setCity(newCity);
      setLocality(newLocality);
      
      // 3. Load current date and time
      setDateTime(getCurrentDateTimeLocal());
      
    } catch (error) {
      console.error("Error fetching location data (Nominatim):", error);
      alert("Error getting location name. Try a manual search.");
    }
  };

  const searchLocation = async () => {
    // Validations
    if (!dateTime) {
      alert("Please select a date and time.");
      return;
    }

    if (!selectedPosition && !country && !city && !locality) {
      alert("Please enter a location or double-click on the map.");
      return;
    }

    // 1. Create parameters object
    let bodyParams = { dateTime };

    if (selectedPosition) {
        // Option 1: Coordinates (priority from double-click)
        bodyParams.lat = selectedPosition[0];
        bodyParams.lon = selectedPosition[1];
    } else {
        // Option 2: Text fields
        bodyParams.country = country;
        bodyParams.city = city;
        bodyParams.locality = locality;
    }

    // ********************************************************
    // KEY CORRECTION: Endpoint with /api
    // This matches the router prefix in your configuration
    // ********************************************************
 const endpoint = "http://localhost:8000/query_weather";

    try {
      const weatherResponse = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        // The JSON body is correct if the Backend uses Pydantic
        body: JSON.stringify(bodyParams),
      });

      if (!weatherResponse.ok) {
        // Detailed backend error handling
        let errorDetail = weatherResponse.statusText;
        try {
          const errorData = await weatherResponse.json();
          // We use errorData.detail which is the standard FastAPI error field
          errorDetail = errorData.detail || weatherResponse.statusText; 
        } catch (e) {
          errorDetail = `Server Error (${weatherResponse.status}). Check the FastAPI console.`;
        }
        
        alert(`Error fetching data: ${errorDetail}`);
        return;
      }

      const weather = await weatherResponse.json();
      
      // 2. Update weather data
      setWeatherData({
          temperature: weather.temperature,
          precipitation: weather.precipitation,
          wind: weather.wind,
          solarRadiation: weather.solarRadiation,
          rain_prediction: weather.rain_prediction 
      });
      
      // If searched by text, the backend returns the found position
      if (weather.location && !selectedPosition) {
          setSelectedPosition([weather.location.lat, weather.location.lon]);
      }

      setTimeout(() => {
        resultRef.current?.scrollIntoView({ behavior: "smooth" });
      }, 200);

    } catch (error) {
      console.error("Search Error (Network/CORS):", error);
      alert("Network or CORS Error: Could not connect to the server (Is it running on port 8000?).");
    }
  };

  // Function for weather-based recommendations (kept the same)
  const getActivityRecommendations = () => {
    if (!weatherData.rain_prediction) return ["Search a location and time to get activity recommendations."];

    const recs = [];
    // Clean and extract numerical values
    const tempMatch = weatherData.temperature ? weatherData.temperature.match(/(\d+\.?\d*)/) : null;
    const windMatch = weatherData.wind ? weatherData.wind.match(/(\d+\.?\d*)/) : null;
    const rainString = weatherData.rain_prediction;
    
    const temp = tempMatch ? parseFloat(tempMatch[1]) : null;
    const wind = windMatch ? parseFloat(windMatch[1]) : null;
    
    // Simplified recommendation logic
    const rainExpected = rainString.includes("Probabilidad") && parseFloat(rainString.match(/(\d+\.?\d*)/)[1]) > 30;

    if (temp) {
        if (temp > 28) recs.push("☀️ **Hot:** Swimming, water sports, or indoor activities with air conditioning.");
        else if (temp >= 18 && temp <= 28) recs.push("🚶‍♀️ **Pleasant:** Hiking, cycling, or a picnic. Perfect for outdoors!");
        else if (temp < 18) recs.push("🧣 **Cold:** Visit a museum, a gallery, or enjoy a movie at home.");
    }
    
    if (rainExpected) recs.push("☔ **Rain:** Board games, reading, or visit a shopping mall.");
    
    if (wind) {
        if (wind > 25) recs.push("🌬️ **Strong Wind:** Avoid elevated activities. Great for indoors!");
        else if (wind > 10) recs.push("🪁 **Moderate Wind:** Fly a kite or go light sailing.");
    }
    
    if (!recs.length && rainString) recs.push("No specific recommendation, but check the weather!");
    
    return recs;
  };

  const recommendations = getActivityRecommendations();

  return (
    <div className="weather-page">
      
      <div className="weather-info">
        <p style={{fontSize: '85%', color: '#007bff', borderBottom: '1px solid #ddd'}}>*Double-click on the map loads location and current time.</p>
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
          <button className="show-btn" onClick={searchLocation}>Show Weather</button>
        </div>
      </div>

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
          <MapClickHandler onSelect={handleMapSelect} /> 
          
          {selectedPosition && (
            <Marker position={selectedPosition} icon={markerIcon}>
              <Popup>
                Location:<br />
                Lat: {selectedPosition[0].toFixed(4)}, Lon: {selectedPosition[1].toFixed(4)}
              </Popup>
            </Marker>
          )}
        </MapContainer>
      </div>

      <div className="results-activities-container">
          
          <div className="weather-result" ref={resultRef}>
            <h4>🌡️ Weather Data</h4>
            <p>Temperature: {weatherData.temperature || "--"}</p>
            <p>Precipitation: {weatherData.precipitation || "--"}</p>
            <p>Wind: {weatherData.wind || "--"}</p>
            <p>Solar Radiation: {weatherData.solarRadiation || "--"}</p>
          </div>

          <div className="activity-recommendations">
            <h4>💡 Activity Recommendations</h4>
            {recommendations.map((rec, idx) => (
              <p key={idx} dangerouslySetInnerHTML={{ __html: rec }} />
            ))}
            <p style={{fontSize: '90%', marginTop: '10px'}}>{weatherData.rain_prediction || ""}</p>
          </div>
      </div>

    </div>
  );
};

export default WeatherPage;