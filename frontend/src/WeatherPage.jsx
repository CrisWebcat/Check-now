import "leaflet/dist/leaflet.css";
import React, { useState, useRef } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from "react-leaflet";
import L from "leaflet";
import "./WeatherPage.css";

// ------------------------------------
// Componentes Auxiliares para Leaflet
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
// Componente Principal
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
    // Ajusta la hora a la zona horaria local y formatea
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    return now.toISOString().slice(0, 16);
  };
  
  // Función llamada por el doble clic en el mapa
  const handleMapSelect = async (latlng) => {
    const [lat, lng] = latlng;
    setSelectedPosition(latlng);
    
    // 1. Geocodificación Inversa (Nominatim)
    const geoUrl = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`;
    
    try {
      const response = await fetch(geoUrl);
      const data = await response.json();
      
      const address = data.address || {};
      
      // Intentar obtener los nombres de ubicación
      const newCountry = address.country || "";
      const newCity = address.city || address.town || address.village || address.county || "";
      const newLocality = address.suburb || address.neighbourhood || address.road || "";
      
      // 2. Actualizar los estados
      setCountry(newCountry);
      setCity(newCity);
      setLocality(newLocality);
      
      // 3. Cargar la fecha y hora actuales
      setDateTime(getCurrentDateTimeLocal());
      
    } catch (error) {
      console.error("Error fetching location data (Nominatim):", error);
      alert("Error al obtener el nombre de la ubicación. Intente la búsqueda manual.");
    }
  };

  const searchLocation = async () => {
    // Validaciones
    if (!dateTime) {
      alert("Por favor, selecciona una fecha y hora.");
      return;
    }

    if (!selectedPosition && !country && !city && !locality) {
      alert("Por favor, ingresa una ubicación o haz doble clic en el mapa.");
      return;
    }

    // 1. Crear el objeto de parámetros
    let bodyParams = { dateTime };

    if (selectedPosition) {
        // Opción 1: Coordenadas (prioridad del doble clic)
        bodyParams.lat = selectedPosition[0];
        bodyParams.lon = selectedPosition[1];
    } else {
        // Opción 2: Campos de texto
        bodyParams.country = country;
        bodyParams.city = city;
        bodyParams.locality = locality;
    }

    // ⚠️ LA URL CORREGIDA: Asume que FastAPI corre en el puerto 8000
    const endpoint = "http://localhost:8000/query_weather"; 
    
    try {
      const weatherResponse = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        // Enviamos los parámetros como JSON en el cuerpo
        body: JSON.stringify(bodyParams),
      });

      if (!weatherResponse.ok) {
        // Manejo detallado de errores del backend
        let errorDetail = weatherResponse.statusText;
        try {
          const errorData = await weatherResponse.json();
          errorDetail = errorData.detail || errorResponse.statusText;
        } catch (e) {
          errorDetail = `Error de servidor (${weatherResponse.status}). Verifique la consola de FastAPI.`;
        }
        
        alert(`Error al obtener datos: ${errorDetail}`);
        return;
      }

      const weather = await weatherResponse.json();
      
      // 2. Actualizar los datos de clima
      setWeatherData({
          temperature: weather.temperature,
          precipitation: weather.precipitation,
          wind: weather.wind,
          solarRadiation: weather.solarRadiation,
          rain_prediction: weather.rain_prediction 
      });
      
      // Si se buscó por texto, el backend devuelve la posición encontrada
      if (weather.location && !selectedPosition) {
          setSelectedPosition([weather.location.lat, weather.location.lon]);
      }

      setTimeout(() => {
        resultRef.current?.scrollIntoView({ behavior: "smooth" });
      }, 200);

    } catch (error) {
      console.error("Error en la búsqueda (Red/CORS):", error);
      alert("Error de Red o CORS: No se pudo conectar con el servidor (¿Está corriendo en el puerto 8000?).");
    }
  };

  // Función para recomendaciones según clima (se mantiene igual)
  const getActivityRecommendations = () => {
    if (!weatherData.rain_prediction) return ["Busca una ubicación y hora para obtener recomendaciones de actividad."];

    const recs = [];
    // Limpia y extrae los valores numéricos
    const tempMatch = weatherData.temperature ? weatherData.temperature.match(/(\d+\.?\d*)/) : null;
    const windMatch = weatherData.wind ? weatherData.wind.match(/(\d+\.?\d*)/) : null;
    const rainString = weatherData.rain_prediction;
    
    const temp = tempMatch ? parseFloat(tempMatch[1]) : null;
    const wind = windMatch ? parseFloat(windMatch[1]) : null;
    
    // Lógica de recomendación simplificada
    const rainExpected = rainString.includes("Probabilidad") && parseFloat(rainString.match(/(\d+\.?\d*)/)[1]) > 30;

    if (temp) {
        if (temp > 28) recs.push("☀️ **Caluroso:** Natación, deportes acuáticos, o actividades interiores con aire acondicionado.");
        else if (temp >= 18 && temp <= 28) recs.push("🚶‍♀️ **Agradable:** Senderismo, ciclismo, o picnic. ¡Perfecto para exteriores!");
        else if (temp < 18) recs.push("🧣 **Frío:** Visita un museo, una galería o disfruta de una película en casa.");
    }
    
    if (rainExpected) recs.push("☔ **Lluvia:** Juegos de mesa, lectura, o visita un centro comercial.");
    
    if (wind) {
        if (wind > 25) recs.push("🌬️ **Viento Fuerte:** Evita actividades elevadas. ¡Ideal para interiores!");
        else if (wind > 10) recs.push("🪁 **Viento Moderado:** Volar una cometa o hacer vela ligera.");
    }
    
    if (!recs.length && rainString) recs.push("No hay una recomendación específica, ¡pero revisa el clima!");
    
    return recs;
  };

  const recommendations = getActivityRecommendations();

  return (
    <div className="weather-page">
      
      <div className="weather-info">
        <p style={{fontSize: '85%', color: '#007bff', borderBottom: '1px solid #ddd'}}>*Doble clic en el mapa carga ubicación y hora actual.</p>
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