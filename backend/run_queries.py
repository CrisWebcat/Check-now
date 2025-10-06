# main.py (O el archivo principal donde inicializas FastAPI)

from fastapi import FastAPI, APIRouter, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime
import logging
from geopy.geocoders import Nominatim

# -------------------------------------------------------------------------
# IMPORTACIONES DE SERVICIOS EXTERNOS (ASUME QUE ESTOS ARCHIVOS EXISTEN)
# -------------------------------------------------------------------------
# Asegúrate de que estas funciones existan en tu proyecto
# from api.meteomatics import fetch_meteomatics_timeseries 
# from services.nasa_power import fetch_nasa_power 

# Implementaciones ficticias para que el código compile si no tienes los archivos
# Reemplaza esto con tus importaciones reales:
def fetch_meteomatics_timeseries(lat, lon, start, end, interval="PT1H"):
    # SIMULACIÓN DE RESPUESTA DE METEOMATICS
    print(f"Llamando a Meteomatics para: {lat}, {lon}")
    # Si esta función falla en tu código real (ej. por clave API), causa el error.
    return {
        "dates": [{"date": start + "T12:00:00Z", "value": 25.5}],
        "t_2m:C": [{"date": start + "T12:00:00Z", "value": 25.5}],
        "precip_1h:mm": [{"date": start + "T12:00:00Z", "value": 0.0}],
        "wind_speed_10m:ms": [{"date": start + "T12:00:00Z", "value": 5.2}],
        "global_rad:wm2": [{"date": start + "T12:00:00Z", "value": 600.0}],
    }
def fetch_nasa_power(lat, lon, start, end, parameters, community):
    # SIMULACIÓN DE RESPUESTA DE NASA POWER
    print(f"Llamando a NASA POWER para: {lat}, {lon}")
    return {
        "properties": {
            "parameter": {
                "T2M": {"20241005": 20.1}, 
                "PRECTOT": {"20241005": 1.5},
                "ALLSKY_SFC_SW_DWN": {"20241005": 550.0}
            }
        }
    }
# -------------------------------------------------------------------------

logger = logging.getLogger(__name__)
router = APIRouter()
geolocator = Nominatim(user_agent="check_now_app")
app = FastAPI()

# -------------------------------------------------------------------------
# CONFIGURACIÓN CORS (CRUCIAL PARA LA COMUNICACIÓN)
# -------------------------------------------------------------------------
origins = [
    origins = [
    "http://localhost:5180",
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


# ---------- UTILS Y VALIDACIONES ----------

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
    
    # Asume que el NASA fetch_nasa_power se usa para un solo día (YYYYMMDD)
    # Buscamos la primera (y única) clave de fecha disponible
    date_key = list(parameter.get("T2M", {}).keys())[0] if parameter.get("T2M") else None
    
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


# ---------- ENDPOINT PRINCIPAL (El que usa React) ----------

@app.post("/query_weather") # Usa @app.post si este es el archivo principal
async def query_weather(
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    country: Optional[str] = None,
    city: Optional[str] = None,
    locality: Optional[str] = None,
    dateTime: str = Query(..., description="Fecha y hora (YYYY-MM-DDTmm:ss)")
):
    
    # 1. DETERMINAR LAT/LON
    if lat is None or lon is None:
        lat_final, lon_final = get_lat_lon_from_location(country, city, locality)
    else:
        validate_lat_lon(lat, lon)
        lat_final, lon_final = lat, lon
        
    # 2. VALIDAR FECHA Y ESCOGER API
    query_dt = validate_date_input(dateTime)
    # Usamos today - 1 para asegurar que el día de hoy caiga en Meteomatics (pronóstico)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    query_date_str = query_dt.strftime("%Y-%m-%d")
    is_future_or_present = query_dt.date() >= today.date()
    
    try:
        if is_future_or_present:
            # A. PRONÓSTICO (Meteomatics)
            data = fetch_meteomatics_timeseries(
                lat_final, 
                lon_final, 
                query_date_str, 
                query_date_str,
                interval="PT1H" 
            )
            if not isinstance(data, dict) or "error" in data:
                 raise HTTPException(status_code=502, detail=f"Error desde Meteomatics: {data.get('error', str(data))}")

            rain_prediction = calculate_rain_prediction(data)
            return {
                "status": "success", 
                "source": "Meteomatics", 
                "location": {"lat": lat_final, "lon": lon_final},
                **format_weather_response(data, rain_prediction)
            }

        else:
            # B. HISTÓRICO (NASA POWER)
            nasa_data = fetch_nasa_power(
                lat_final, 
                lon_final, 
                query_date_str, 
                query_date_str,
                parameters="T2M,PRECTOT,ALLSKY_SFC_SW_DWN", 
                community="AG"
            )
            
            if "errors" in nasa_data or not nasa_data.get("properties"):
                raise HTTPException(status_code=502, detail="NASA POWER devolvió error o datos vacíos")

            return {
                "status": "success", 
                "source": "NASA POWER",
                "location": {"lat": lat_final, "lon": lon_final},
                **format_nasa_response(nasa_data)
            }
            
    except HTTPException:
        raise
    except Exception as e:
        # Esto captura errores de red o errores internos en fetch_meteomatics/nasa
        logger.error(f"Error en query_weather: {e}")
        raise HTTPException(status_code=500, detail=f"Error en el servidor al consultar API externa: {str(e)}")

# Si estás usando un router, reemplaza @app.post con @router.post y añade app.include_router(router)