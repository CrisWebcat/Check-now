import requests
from geopy.geocoders import Nominatim
import pandas as pd
from datetime import datetime

BACKEND_URL = "http://127.0.0.1:8000"  # Cambia si lo despliegas en otro host
geolocator = Nominatim(user_agent="check_now_app_test")

def get_lat_lon(country_name: str):
    location = geolocator.geocode(country_name)
    if location is None:
        raise ValueError(f"Country '{country_name}' not found.")
    return location.latitude, location.longitude

def fetch_nasa_data(lat, lon, start, end):
    url = f"{BACKEND_URL}/api/nasa"
    params = {"lat": lat, "lon": lon, "start": start, "end": end, "community": "AG"}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def main():
    country = input("Enter country (in English): ")
    start_date = input("Enter start date (YYYY-MM-DD): ")
    end_date = input("Enter end date (YYYY-MM-DD): ")

    try:
        lat, lon = get_lat_lon(country)
        print(f"Coordinates for {country}: {lat}, {lon}")

        data = fetch_nasa_data(lat, lon, start_date, end_date)
        print("NASA POWER data fetched successfully!")

        # Guardar en CSV
        if "data" in data:
            df = pd.DataFrame(data["data"])
            df.to_csv("nasa_data.csv", index=False)
            print("Data saved to nasa_data.csv")
        else:
            print("No data returned from NASA POWER API.")

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
