# api/meteomatics.py

import os
from dotenv import load_dotenv
import requests
import logging

logger = logging.getLogger(__name__)

load_dotenv()

METEO_USER = os.getenv("METEO_USER")
METEO_PASS = os.getenv("METEO_PASS")

if not METEO_USER or not METEO_PASS:
    raise ValueError("Meteomatics credentials were not found in the .env")

def fetch_meteomatics_timeseries(lat, lon, start, end):
    """
    Devuelve series temporales de Meteomatics para lat/lon y rango de fechas.
    start y end deben ser strings 'YYYY-MM-DD'.
    """
    parameters = "t_2m:C,precip_1h:mm,wind_speed_10m:ms"
    url = f"https://api.meteomatics.com/{start}T00:00:00Z--{end}T00:00:00Z:PT1H/{parameters}/{lat},{lon}/json"
    
    try:
        logger.info(f"Consultando Meteomatics: {url}")
        response = requests.get(url, auth=(METEO_USER, METEO_PASS), timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTPError: {http_err}")
        raise RuntimeError(f"Error al consultar Meteomatics: {http_err}")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"RequestException: {req_err}")
        raise RuntimeError(f"Error de conexión con Meteomatics: {req_err}")
    except Exception as e:
        logger.error(f"Error desconocido: {e}")
        raise RuntimeError(f"Error desconocido al consultar Meteomatics: {e}")
