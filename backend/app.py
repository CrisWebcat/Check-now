# app.py

from fastapi import FastAPI
from api.routes import router as api_router
import logging

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Check-now",
    description="API for querying weather conditions and risks using Meteomatics",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api")
