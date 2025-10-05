import os
import requests
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv()

METEO_USER = os.getenv("METEO_USER")
METEO_PASS = os.getenv("METEO_PASS")

if not METEO_USER or not METEO_PASS:
    raise ValueError("Meteomatics credentials not found in .env")

def fetch_meteomatics_timeseries(lat, lon, start, end):
    """
    Consulta la API de Meteomatics y devuelve series temporales limpias.
    """
    parameters = "t_2m:C,precip_1h:mm,wind_speed_10m:ms"
    url = f"https://api.meteomatics.com/{start}T00:00:00Z--{end}T00:00:00Z:PT1H/{parameters}/{lat},{lon}/json"

    try:
        logger.info(f"Consultando Meteomatics: {url}")
        response = requests.get(url, auth=(METEO_USER, METEO_PASS), timeout=20)
        response.raise_for_status()

        try:
            data = response.json()
        except ValueError:
            logger.error("Respuesta no es JSON válido.")
            raise RuntimeError("Respuesta no válida de Meteomatics (no es JSON).")

        if not isinstance(data, dict) or "data" not in data:
            logger.error(f"Estructura inesperada: {data}")
            raise RuntimeError("Estructura inesperada recibida desde Meteomatics.")

        series = {}
        for variable in data.get("data", []):
            variable_name = variable.get("parameter")
            coordinates = variable.get("coordinates", [])
            if not variable_name or not coordinates:
                continue
            dates_list = coordinates[0].get("dates", [])
            values = [{"datetime": val.get("date"), "value": val.get("value")} for val in dates_list if val.get("date") and val.get("value") is not None]
            series[variable_name] = values

        if not series:
            logger.warning("No se extrajeron datos de Meteomatics.")
        else:
            logger.info("Datos de Meteomatics obtenidos correctamente.")

        return series

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTPError: {http_err}")
        raise RuntimeError(f"Error HTTP al consultar Meteomatics: {http_err}")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Error de conexión con Meteomatics: {req_err}")
        raise RuntimeError(f"Error de conexión con Meteomatics: {req_err}")
    except Exception as e:
        logger.error(f"Error desconocido Meteomatics: {e}")
        raise RuntimeError(f"Error desconocido al consultar Meteomatics: {e}")
