# api/routes.py

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime
from api.meteomatics import fetch_meteomatics_timeseries
import logging

# Library for country geocoding
from geopy.geocoders import Nominatim

logger = logging.getLogger(__name__)
router = APIRouter()

geolocator = Nominatim(user_agent="weather_app")

def validate_date(date_str: str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Formato de fecha inválido: {date_str}. Debe ser YYYY-MM-DD")

def validate_lat_lon(lat: float, lon: float):
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail=f"Latitud o longitud fuera de rango: lat={lat}, lon={lon}")

def get_lat_lon_from_country(country_name: str):
    location = geolocator.geocode(country_name)
    if location is None:
        raise HTTPException(status_code=404, detail=f"No se encontró el país: {country_name}")
    return location.latitude, location.longitude

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/weather")
def weather(lat: float = Query(...), lon: float = Query(...),
            start: str = Query(...), end: str = Query(...)):
    validate_lat_lon(lat, lon)
    start_dt = validate_date(start)
    end_dt = validate_date(end)
    if start_dt > end_dt:
        raise HTTPException(status_code=400, detail="start no puede ser mayor que end")

    try:
        data = fetch_meteomatics_timeseries(lat, lon, start, end)
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"Error en endpoint /weather: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/risk")
def risk(lat: float = Query(...), lon: float = Query(...),
         date_query: str = Query(...)):
    validate_lat_lon(lat, lon)
    validate_date(date_query)
    try:
        timeseries = fetch_meteomatics_timeseries(lat, lon, date_query, date_query)
        # Cálculo de riesgo (si se tienes un modelo)
        return {"status": "success", "timeseries": timeseries}
    except Exception as e:
        logger.error(f"Error en endpoint /risk: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/query")
def query_weather(country: str = Query(...), start: str = Query(...), end: str = Query(...)):
    """Recibe un país y devuelve datos de Meteomatics para sus coordenadas."""
    start_dt = validate_date(start)
    end_dt = validate_date(end)
    if start_dt > end_dt:
        raise HTTPException(status_code=400, detail="start no puede ser mayor que end")

    try:
        lat, lon = get_lat_lon_from_country(country)
        data = fetch_meteomatics_timeseries(lat, lon, start, end)
        return {
            "status": "success",
            "country": country,
            "lat": lat,
            "lon": lon,
            "data": data
        }
    except HTTPException as e:
        # Pasar errores de geocodificación directamente
        raise e
    except Exception as e:
        logger.error(f"Error en endpoint /query: {e}")
        raise HTTPException(status_code=500, detail=f"Error en query endpoint: {str(e)}")
