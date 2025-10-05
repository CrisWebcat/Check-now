import requests
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def fetch_nasa_power(lat: float, lon: float, start: str, end: str, parameters: str = "T2M,PRECTOT,ALLSKY_SFC_SW_DWN", community: str = "AG"):
    """
    Consulta la API de NASA POWER y devuelve series temporales.
    """
    base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    url = base_url
    params = {
        "start": start.replace("-", ""),
        "end": end.replace("-", ""),
        "latitude": lat,
        "longitude": lon,
        "parameters": parameters,
        "community": community,
        "format": "JSON"
    }

    try:
        logger.info(f"Consultando NASA POWER: {url} con {params}")
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()

        try:
            data = response.json()
        except ValueError:
            logger.error("Respuesta no es JSON válido.")
            raise RuntimeError("Respuesta no válida de NASA POWER (no es JSON).")

        if not isinstance(data, dict) or "properties" not in data:
            logger.error(f"Estructura inesperada: {data}")
            raise RuntimeError("Estructura inesperada recibida desde NASA POWER.")

        if "errors" in data:
            logger.error(f"Errores NASA POWER: {data['errors']}")
            raise RuntimeError(f"Errores desde NASA POWER: {data['errors']}")

        logger.info("Datos de NASA POWER obtenidos correctamente.")
        return data

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTPError NASA POWER: {http_err}")
        raise RuntimeError(f"Error HTTP al consultar NASA POWER: {http_err}")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Error de conexión con NASA POWER: {req_err}")
        raise RuntimeError(f"Error de conexión con NASA POWER: {req_err}")
    except Exception as e:
        logger.error(f"Error desconocido NASA POWER: {e}")
        raise RuntimeError(f"Error desconocido al consultar NASA POWER: {e}")
