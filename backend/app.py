# app.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router
import logging
import os # Necesario para usar getenv
from dotenv import load_dotenv # <--- ¡NUEVO IMPORTANTE!

# -----------------------------------------------------------
# Esto DEBE ejecutarse antes de cualquier código que intente leer las variables.
load_dotenv() 
# -------------------------------------------------------------

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Check-now",
    description="API for querying weather conditions and risks using Meteomatics",
    version="1.0.0"
)

origins = [
    "http://localhost:5173", 
    "http://127.0.0.1:5173",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,     
    allow_credentials=True,    
    allow_methods=["*"],       # Permite todos los métodos, incluyendo OPTIONS y POST
    allow_headers=["*"],       
)

# -------------------------------------------------------------

# El router api.routes.py ahora puede importar meteomatics.py, que leerá las variables
app.include_router(api_router, prefix="/api")