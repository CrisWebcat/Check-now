import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Cargar credenciales del .env si es necesario
load_dotenv()

# Configuración del backend
BACKEND_URL = "http://127.0.0.1:8000"  # Cambiar si se despliega en otro host

def fetch_country_data(country, start, end):
    """Llama al endpoint /query para obtener weather + risk automáticamente."""
    url = f"{BACKEND_URL}/api/query"
    params = {"country": country, "start": start, "end": end}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def main():
    country = "Guatemala"  # Puedes cambiarlo por cualquier país en inglés
    start_date = "2025-10-10"
    end_date = "2025-10-11"

    try:
        data = fetch_country_data(country, start_date, end_date)
        
        # Guardamos los datos separados
        weather_data = data.get("weather", [])
        risk_data = data.get("risk", [])

        pd.DataFrame(weather_data).to_csv("weather_data.csv", index=False)
        pd.DataFrame(risk_data).to_csv("risk_data.csv", index=False)

        print(f"Data for {country} saved successfully!")
        print("Files: weather_data.csv, risk_data.csv")

    except Exception as e:
        print("Error fetching data:", e)

if __name__ == "__main__":
    main()
