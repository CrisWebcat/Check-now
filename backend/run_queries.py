from fastapi import FastAPI, APIRouter, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime
import logging
from geopy.geocoders import Nominatim
from api.models import WeatherQueryData 


try:
    from api.meteomatics import fetch_meteomatics_timeseries 
    from services.nasa_power import fetch_nasa_power 
except ImportError as e:
    # Esto ocurre si los archivos de servicio no existen o tienen errores de importación/ejecución
    # Si ves este error, el problema está en api/meteomatics.py o services/nasa_power.py
    logging.error(f"Error al importar módulos de servicios externos: {e}")

    def fetch_meteomatics_timeseries(lat, lon, start, end, interval="PT1H"):
        raise HTTPException(status_code=500, detail="Meteomatics service import failed.")
    def fetch_nasa_power(lat, lon, start, end, parameters, community):
        raise HTTPException(status_code=500, detail="NASA Power service import failed.")

# -------------------------------------------------------------------------

logger = logging.getLogger(__name__)
geolocator = Nominatim(user_agent="check_now_app")
app = FastAPI()

# -------------------------------------------------------------------------
# CONFIGURACIÓN CORS 
# -------------------------------------------------------------------------
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5180",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# -------------------------------------------------------------------------


# ---------- UTILS Y VALIDACIONES (MANTENIDOS IGUAL) ----------

def validate_date_input(date_str: str):
    """Valida y convierte la cadena YYYY-MM-DDTmm:ss a datetime."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Fecha/Hora inválida: {date_str}. Usar YYYY-MM-DDTmm:ss.")

def validate_lat_lon(lat: float, lon: float):
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail=f"Lat/Lon fuera de rango: lat={lat}, lon={lon}")

def get_lat_lon_from_location(country: Optional[str], city: Optional[str], locality: Optional[str]):
    """Obtiene Lat/Lon usando Nominatim basado en los campos disponibles."""
    query_parts = [p for p in [locality, city, country] if p]
    query = ", ".join(query_parts)
    
    if not query_parts or not query.strip():
        raise HTTPException(status_code=400, detail="Debe proporcionar coordenadas o al menos un campo de ubicación.")

    try:
        location = geolocator.geocode(query, timeout=10)
    except Exception as e:
        logger.error(f"Error en geocodificación: {e}")
        raise HTTPException(status_code=500, detail="Error al contactar al servicio de ubicación (Nominatim).")

    if not location:
        raise HTTPException(status_code=404, detail=f"No se encontró la ubicación: {query}. Intente ser más específico.")
        
    return location.latitude, location.longitude

def calculate_rain_prediction(data: dict) -> str:
    """Calcula una probabilidad simple de lluvia para el día (Meteomatics)."""
    precip_data = data.get("precip_1h:mm", [])
    total_hours = len(precip_data)
    if total_hours == 0:
        return "No hay datos de precipitación disponibles"
    rainy_hours = sum(1 for h in precip_data if h["value"] > 0.1)
    rain_prob = round((rainy_hours / total_hours) * 100, 1)
    return f"Probabilidad de lluvia: {rain_prob}%"

def format_weather_response(data: dict, rain_prediction: str) -> dict:
    """Formatea la respuesta de Meteomatics."""
    def get_first_value(key):
        values = data.get(key, [])
        return values[0]['value'] if values and values[0].get('value') is not None else None

    temp = get_first_value("t_2m:C")
    precip = get_first_value("precip_1h:mm")
    wind = get_first_value("wind_speed_10m:ms")
    solar = get_first_value("global_rad:wm2")

    return {
        "temperature": f"{temp}°C" if temp is not None else "--",
        "precipitation": f"{precip} mm" if precip is not None else "--",
        "wind": f"{wind} m/s" if wind is not None else "--",
        "solarRadiation": f"{solar} W/m²" if solar is not None else "--",
        "rain_prediction": rain_prediction
    }

def format_nasa_response(nasa_data: dict) -> dict:
    """Formatea la respuesta de NASA POWER."""
    props = nasa_data.get("properties", {})
    parameter = props.get("parameter", {})
    
    date_key = list(parameter.get("T2M", {}).keys())[0] if parameter.get("T2M") and list(parameter.get("T2M", {}).keys()) else None
    
    temp = parameter.get("T2M", {}).get(date_key)
    precip = parameter.get("PRECTOT", {}).get(date_key)
    solar = parameter.get("ALLSKY_SFC_SW_DWN", {}).get(date_key)

    return {
        "temperature": f"{temp}°C (Avg)" if temp is not None else "--",
        "precipitation": f"{precip} mm" if precip is not None else "--",
        "wind": f"N/A", 
        "solarRadiation": f"{solar} W/m²" if solar is not None else "--",
        "rain_prediction": "Datos históricos (NASA POWER)"
    }


# ------------------------------------------------------------------------
# ---------- ENDPOINT PRINCIPAL (RUTA CORREGIDA) ----------
# ------------------------------------------------------------------------

# En run_queries.py
@app.post("/query_weather") # <--- DEBE SER ASÍ
async def query_weather(query_data: WeatherQueryData):
    
    
    # 1. DETERMINAR LAT/LON
    if query_data.lat is None or query_data.lon is None: 
        lat_final, lon_final = get_lat_lon_from_location(
            query_data.country, 
            query_data.city, 
            query_data.locality
        )
    else:
        validate_lat_lon(query_data.lat, query_data.lon)
        lat_final, lon_final = query_data.lat, query_data.lon
        
    # 2. VALIDAR FECHA Y ESCOGER API
    query_dt = validate_date_input(query_data.dateTime) 
    
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    query_date_str = query_dt.strftime("%Y-%m-%d")
    is_future_or_present = query_dt.date() >= today.date()
    
    try:
        if is_future_or_present:
            # A. PRONÓSTICO (Meteomatics - REAL)
            data = fetch_meteomatics_timeseries(
                lat_final, 
                lon_final, 
                query_date_str, 
                query_date_str,
            )
            
            if not isinstance(data, dict) or "error" in data or not data.get("t_2m:C"):
                 raise HTTPException(status_code=502, detail=f"Error en datos de Meteomatics. Detalle: {data.get('error', 'Datos insuficientes o formato incorrecto.')}")

            rain_prediction = calculate_rain_prediction(data)
            return {
                "status": "success", 
                "source": "Meteomatics", 
                "location": {"lat": lat_final, "lon": lon_final},
                **format_weather_response(data, rain_prediction)
            }

        else:
            # B. HISTÓRICO (NASA POWER - REAL)
            nasa_data = fetch_nasa_power(
                lat_final, 
                lon_final, 
                query_date_str, 
                query_date_str,
                parameters="T2M,PRECTOT,ALLSKY_SFC_SW_DWN", 
                community="AG"
            )
            
            if "errors" in nasa_data or not nasa_data.get("properties"):
                raise HTTPException(status_code=502, detail="NASA POWER devolvió error o datos vacíos.")

            return {
                "status": "success", 
                "source": "NASA POWER",
                "location": {"lat": lat_final, "lon": lon_final},
                **format_nasa_response(nasa_data)
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en query_weather: {e}")
        # Este error puede ser por credenciales, red, o la respuesta de la API real.
        raise HTTPException(status_code=500, detail=f"Error al llamar a la API externa. Revise logs: {str(e)}")