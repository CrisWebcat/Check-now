# api/models.py (Crear este archivo)

from pydantic import BaseModel
from typing import Optional

class WeatherQueryData(BaseModel):
    """
    Define la estructura de los datos que se reciben del Frontend.
    """
    lat: Optional[float] = None
    lon: Optional[float] = None
    country: Optional[str] = None
    city: Optional[str] = None
    locality: Optional[str] = None
    dateTime: str # Campo requerido