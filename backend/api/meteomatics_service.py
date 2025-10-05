import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables del .env
load_dotenv()

METEOMATICS_USERNAME = os.getenv("METEO_USERNAME")
METEOMATICS_PASSWORD = os.getenv("METEO_PASSWORD")

BASE_URL = "https://api.meteomatics.com"

def get_weather_data(lat: float, lon: float, start: str, end: str):
    """
    Obtiene datos meteorológicos históricos o actuales de Meteomatics.
    """
    try:
        # Formato de fechas requerido por la API
        start_date = datetime.fromisoformat(start)
        end_date = datetime.fromisoformat(end)

        # Variables meteorológicas (puedes agregar más)
        parameters = "t_2m:C,precip_1h:mm,wind_speed_10m:ms"

        url = f"{BASE_URL}/{start_date.strftime('%Y-%m-%dT%H:%M:%SZ')}--{end_date.strftime('%Y-%m-%dT%H:%M:%SZ')}/PT1H/{parameters}/{lat},{lon}/json"

        response = requests.get(url, auth=(METEOMATICS_USERNAME, METEOMATICS_PASSWORD))

        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"Error {response.status_code}: {response.text}"
            }
    except Exception as e:
        return {"error": str(e)}
