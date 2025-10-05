from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime
from api.meteomatics import fetch_meteomatics_timeseries
from geopy.geocoders import Nominatim
from services.nasa_power import fetch_nasa_power
from models.risk_model import compute_risk_probabilities

import logging

logger = logging.getLogger(__name__)
router = APIRouter()

geolocator = Nominatim(user_agent="check_now_app")

# ---------- VALIDACIONES ----------

def validate_date(date_str: str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Fecha inválida: {date_str}, usar YYYY-MM-DD")

def validate_lat_lon(lat: float, lon: float):
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail=f"Lat/Lon fuera de rango: lat={lat}, lon={lon}")

def get_lat_lon_from_country(country_name: str):
    location = geolocator.geocode(country_name)
    if not location:
        raise HTTPException(status_code=404, detail=f"No se encontró país: {country_name}")
    return location.latitude, location.longitude

# ---------- ENDPOINTS ----------
@router.get("/")
def root():
    return {"message": "Welcome to Check-now API"}

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/weather")
def weather(
    lat: float = Query(..., description="Latitud en grados decimales"),
    lon: float = Query(..., description="Longitud en grados decimales"),
    start: str = Query(..., description="Fecha de inicio (YYYY-MM-DD)"),
    end: str = Query(..., description="Fecha de fin (YYYY-MM-DD)")
):
    validate_lat_lon(lat, lon)
    start_dt = validate_date(start)
    end_dt = validate_date(end)
    if start_dt > end_dt:
        raise HTTPException(status_code=400, detail="start no puede ser mayor que end")

    try:
        data = fetch_meteomatics_timeseries(lat, lon, start, end)
        if "error" in data:
            raise HTTPException(status_code=502, detail=data["error"])
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"Error en endpoint /weather: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/risk")
def risk(
    lat: float = Query(..., description="Latitud"),
    lon: float = Query(..., description="Longitud"),
    date_query: str = Query(..., description="Fecha de consulta (YYYY-MM-DD)")
):
    validate_lat_lon(lat, lon)
    validate_date(date_query)
    try:
        timeseries = fetch_meteomatics_timeseries(lat, lon, date_query, date_query)
        
        risks = compute_risk_probabilities(timeseries)
        
        return {
            "status": "success",
            "timeseries": timeseries,
            "risks": risks
        }
    except Exception as e:
        logger.error(f"Error en endpoint /risk: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/query")
def query_weather(
    country: str = Query(..., description="Nombre del país"),
    start: str = Query(..., description="Fecha de inicio (YYYY-MM-DD)"),
    end: str = Query(..., description="Fecha de fin (YYYY-MM-DD)")
):
    # Validación de fechas
    start_dt = validate_date(start)
    end_dt = validate_date(end)
    if start_dt > end_dt:
        raise HTTPException(status_code=400, detail="start no puede ser mayor que end")

    try:
        # Obtener latitud y longitud desde el país
        lat, lon = get_lat_lon_from_country(country)

        # Llamada a Meteomatics
        data = fetch_meteomatics_timeseries(lat, lon, start, end)

        # ✅ Validación robusta para evitar el error 'str' object has no attribute get
        if not isinstance(data, dict) or "error" in data:
            logger.error(f"Error desde Meteomatics: {data}")
            raise HTTPException(
                status_code=502,
                detail=f"Error desde Meteomatics: {data.get('error', str(data))}"
            )

        # Respuesta final
        return {
            "status": "success",
            "country": country,
            "lat": lat,
            "lon": lon,
            "data": data
        }

    except HTTPException:
        raise  # Reenvía errores de FastAPI
    except Exception as e:
        logger.error(f"Error en endpoint /query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error en query endpoint: {str(e)}"
        )

@router.get("/nasa")
def get_nasa_weather(
    lat: float = Query(..., description="Latitud"),
    lon: float = Query(..., description="Longitud"),
    start: str = Query(..., description="Fecha inicio YYYY-MM-DD"),
    end: str = Query(..., description="Fecha fin YYYY-MM-DD"),
    community: str = Query("AG", description="Comunidad NASA POWER, default AG")
):
    try:
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise HTTPException(status_code=400, detail="Latitud o longitud fuera de rango")

        start_dt = datetime.strptime(start, "%Y-%m-%d")
        end_dt = datetime.strptime(end, "%Y-%m-%d")
        if start_dt > end_dt:
            raise HTTPException(status_code=400, detail="start no puede ser mayor que end")

        today = datetime.today()
        if start_dt > today or end_dt > today:
            return {"status": "warning", "message": "NASA POWER no tiene datos para fechas futuras"}

        params = "T2M,PRECTOT,ALLSKY_SFC_SW_DWN"
        data = fetch_nasa_power(lat, lon, start, end, parameters=params, community=community)

        if "errors" in data or not data.get("properties"):
            raise HTTPException(status_code=502, detail="NASA POWER devolvió error o datos vacíos")

        return {"status": "success", "source": "NASA POWER", "data": data}

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching NASA POWER data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching NASA POWER data: {e}")
