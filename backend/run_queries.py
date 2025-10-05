import requests
import pandas as pd
import os
import time
from dotenv import load_dotenv
from geopy.geocoders import Nominatim

# Cargar variables de entorno si es necesario
load_dotenv()

# Configuración
BACKEND_URL = "http://127.0.0.1:8000"
geolocator = Nominatim(user_agent="weather_challenge_script")

def fetch_country_data(country, start, end):
    """Llama al endpoint /query para obtener weather + risk automáticamente."""
    url = f"{BACKEND_URL}/api/query"
    params = {"country": country, "start": start, "end": end}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def get_lat_lon(country_name):
    """Devuelve latitud y longitud del país usando geopy."""
    location = geolocator.geocode(country_name)
    if location:
        return location.latitude, location.longitude
    else:
        raise ValueError(f"Country '{country_name}' not found.")

def fetch_nasa_power(lat, lon, start, end, parameters="T2M,ALLSKY_SFC_SW_DWN,PRECTOT", community="AG"):
    """Fetch NASA POWER daily data para las coordenadas y fechas dadas."""
    base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "start": start.replace("-", ""),
        "end": end.replace("-", ""),
        "latitude": lat,
        "longitude": lon,
        "parameters": parameters,
        "community": community,
        "format": "JSON"
    }
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    return response.json()

def fetch_nasa_power_retry(lat, lon, start, end, retries=3, delay=5):
    """Intenta consultar NASA POWER varias veces en caso de error 500."""
    for attempt in range(1, retries+1):
        try:
            return fetch_nasa_power(lat, lon, start, end)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 500:
                print(f"[NASA POWER] Attempt {attempt} failed with 500. Retrying in {delay}s...")
                time.sleep(delay)
            else:
                raise
    print("[NASA POWER] API unreachable after multiple attempts.")
    return None

def process_nasa_data(nasa_data):
    """Convierte los datos de NASA POWER a un DataFrame listo para CSV."""
    timeseries = nasa_data.get("properties", {}).get("parameter", {})
    if timeseries:
        df = pd.DataFrame(timeseries)
        return df
    return None

def main():
    country = input("Enter country (in English, e.g., Guatemala): ") or "Guatemala"
    start_date = input("Enter start date (YYYY-MM-DD): ") or "2025-10-10"
    end_date = input("Enter end date (YYYY-MM-DD): ") or "2025-10-11"

    try:
        # Weather + Risk
        data = fetch_country_data(country, start_date, end_date)
        weather_data = data.get("weather", [])
        risk_data = data.get("risk", [])

        if weather_data:
            pd.DataFrame(weather_data).to_csv("weather_data.csv", index=False)
        if risk_data:
            pd.DataFrame(risk_data).to_csv("risk_data.csv", index=False)
        print(f"Weather and Risk data saved!")

        # NASA POWER
        lat, lon = get_lat_lon(country)
        nasa_data = fetch_nasa_power_retry(lat, lon, start_date, end_date)
        if nasa_data:
            df_nasa = process_nasa_data(nasa_data)
            if df_nasa is not None:
                df_nasa.to_csv("nasa_power_data.csv", index=False)
                print("NASA POWER data saved to nasa_power_data.csv")
            else:
                print("Warning: No NASA POWER data returned.")
        else:
            print("Skipped NASA POWER data due to server error.")

        print(f"All data for {country} processed successfully!")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        if http_err.response is not None:
            print("Response content:", http_err.response.text)
    except Exception as e:
        print("Unexpected error:", e)

if __name__ == "__main__":
    main()
