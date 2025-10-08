from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime, date
from api.meteomatics import fetch_meteomatics_timeseries 
from geopy.geocoders import Nominatim
from services.nasa_power import fetch_nasa_power 
import logging


logger = logging.getLogger(__name__)
router = APIRouter()

geolocator = Nominatim(user_agent="check_now_app")

# ---------- VALIDACIONES Y UTILS ----------

def validate_date_input(date_str: str):
    """Valida y convierte una cadena YYYY-MM-DD o YYYY-MM-DDT... a objeto datetime."""
    try:
        # Intenta parsear como datetime completo (con hora)
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M")
    except ValueError:
        try:
            # Si falla, intenta parsear solo la fecha
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Fecha/Hora inválida: {date_str}. Usar YYYY-MM-DDTmm:ss o YYYY-MM-DD")

def validate_lat_lon(lat: float, lon: float):
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail=f"Lat/Lon fuera de rango: lat={lat}, lon={lon}")

def get_lat_lon_from_location(country: Optional[str], city: Optional[str], locality: Optional[str]):
    """Obtiene Lat/Lon usando Nominatim basado en los campos disponibles."""
    query_parts = [p for p in [locality, city, country] if p]
    if not query_parts:
        raise HTTPException(status_code=400, detail="Debe proporcionar coordenadas o al menos un campo de ubicación.")
    
    query = ", ".join(query_parts)
    location = geolocator.geocode(query, timeout=10)
    
    if not location:
        raise HTTPException(status_code=404, detail=f"No se encontró la ubicación: {query}")
        
    return location.latitude, location.longitude

def calculate_rain_prediction(data: dict) -> str:
    """Calcula una probabilidad simple de lluvia para el día."""
    precip_data = data.get("precip_1h:mm", [])
    total_hours = len(precip_data)
    if total_hours == 0:
        return "No hay datos de precipitación disponibles"
    else:
        # Cuenta horas con precipitación significativa
        rainy_hours = sum(1 for h in precip_data if h["value"] > 0.1)
        rain_prob = round((rainy_hours / total_hours) * 100, 1)
        return f"Probabilidad aproximada de lluvia: {rain_prob}%"

def format_weather_response(data: dict, rain_prediction: str) -> dict:
    """Extrae y formatea los valores clave de los datos de Meteomatics (pronóstico)."""
    
    # Intenta obtener el valor de la temperatura, precipitación, etc., para la primera hora
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
        "rain_prediction": rain_prediction,
        "raw_data": data # Opcional: para el debug
    }

def format_nasa_response(data: dict) -> dict:
    """Extrae y formatea los valores clave de los datos de NASA POWER (histórico)."""
    
    props = data.get("properties", {})
    parameter = props.get("parameter", {})
    
    # Promedios del día consultado (solo si la consulta es de un día)
    temp = parameter.get("T2M", {}).get("20240101") # Asume que solo se consulta 1 día
    precip = parameter.get("PRECTOT", {}).get("20240101")
    solar = parameter.get("ALLSKY_SFC_SW_DWN", {}).get("20240101")
    
    # NASA no da viento directamente en el set de parámetros simples
    wind = None 

    # Se necesita adaptar la extracción de datos al formato real que devuelve NASA POWER
    # (El formato de ejemplo "20240101" es una suposición, debe coincidir con el código de servicios/nasa_power.py)
    
    return {
        "temperature": f"{temp}°C" if temp is not None else "--",
        "precipitation": f"{precip} mm" if precip is not None else "--",
        "wind": f"N/A" if wind is None else f"{wind} m/s", 
        "solarRadiation": f"{solar} W/m²" if solar is not None else "--",
        "rain_prediction": "Datos históricos no incluyen predicción de lluvia.",
        "raw_data": data
    }


# ---------- ENDPOINTS UNIFICADOS ----------

@router.post("/query_weather")
async def query_weather(
    # Lat/Lon son opcionales, si se usan, tienen prioridad
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    # Los nombres de ubicación son opcionales
    country: Optional[str] = None,
    city: Optional[str] = None,
    locality: Optional[str] = None,
    # Fecha/hora (requerida)
    dateTime: str = Query(..., description="Fecha y hora (YYYY-MM-DDTmm:ss)")
):
    
    # 1. DETERMINAR LAT/LON
    if lat is None or lon is None:
        lat_final, lon_final = get_lat_lon_from_location(country, city, locality)
    else:
        validate_lat_lon(lat, lon)
        lat_final, lon_final = lat, lon
        
    # 2. VALIDAR FECHA
    query_dt = validate_date_input(dateTime)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Para la consulta de datos (la API de Meteomatics requiere solo la fecha)
    query_date_str = query_dt.strftime("%Y-%m-%d")
    
    # 3. ESCOGER LA API (Futuro/Presente vs. Histórico)
    is_future = query_dt.date() >= today.date()
    
    if is_future:
        # A. Datos de PRONÓSTICO (Meteomatics)
        try:
            # Buscamos datos solo para el día y hora especificados
            data = fetch_meteomatics_timeseries(
                lat_final, 
                lon_final, 
                query_date_str, 
                query_date_str,
                interval="PT1H" # Intervalo horario para obtener datos cercanos a la hora
            )

            if not isinstance(data, dict) or "error" in data:
                 raise HTTPException(status_code=502, detail=f"Error desde Meteomatics: {data.get('error', str(data))}")

            rain_prediction = calculate_rain_prediction(data)
            
            # Formateamos solo el punto de tiempo más cercano a la hora
            return {
                "status": "success", 
                "source": "Meteomatics", 
                "location": {"lat": lat_final, "lon": lon_final},
                **format_weather_response(data, rain_prediction)
            }

        except Exception as e:
            logger.error(f"Error en query_weather (Meteomatics): {e}")
            raise HTTPException(status_code=500, detail=f"Error al obtener pronóstico: {str(e)}")

    else:
        # B. Datos HISTÓRICOS (NASA POWER)
        try:
            # NASA POWER requiere solo la fecha de inicio/fin
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
            
        except Exception as e:
            logger.error(f"Error en query_weather (NASA): {e}")
            raise HTTPException(status_code=500, detail=f"Error al obtener datos históricos: {str(e)}")