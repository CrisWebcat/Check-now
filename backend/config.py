from dotenv import load_dotenv
import os

load_dotenv()  # carga .env en desarrollo

METEO_USER = os.getenv("METEO_USER")
METEO_PASS = os.getenv("METEO_PASS")