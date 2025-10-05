import numpy as np
import pandas as pd

def compute_risk_probabilities(timeseries: dict) -> dict:
    """
    Calcula riesgos climáticos básicos a partir de datos crudos (temperatura, viento, precipitación, etc.)
    timeseries: dict con datos del clima obtenidos desde Meteomatics.
    Retorna: diccionario con probabilidades (%) de riesgo.
    """

    try:
        # Convierte a DataFrame si los datos vienen en formato JSON Meteomatics
        if "data" in timeseries:
            df = pd.DataFrame(timeseries["data"])
        else:
            df = pd.DataFrame(timeseries)

        # Normaliza nombres de columnas
        df.columns = [col.lower() for col in df.columns]

        # ----------------------------
        # 1️⃣  Identificar variables principales
        # ----------------------------
        temp_col = next((c for c in df.columns if "temp" in c or "t_2m" in c), None)
        wind_col = next((c for c in df.columns if "wind" in c or "speed" in c), None)
        precip_col = next((c for c in df.columns if "precip" in c or "rain" in c), None)

        if not any([temp_col, wind_col, precip_col]):
            raise ValueError("No se encontraron variables adecuadas en los datos del clima.")

        # ----------------------------
        # 2️⃣  Calcular valores promedio recientes
        # ----------------------------
        mean_temp = df[temp_col].mean() if temp_col else np.nan
        mean_wind = df[wind_col].mean() if wind_col else np.nan
        mean_precip = df[precip_col].mean() if precip_col else np.nan

        # ----------------------------
        # 3️⃣  Calcular riesgos simples (placeholder estadístico)
        # ----------------------------
        # Escalas normalizadas básicas
        risk_hot = np.clip((mean_temp - 25) / 10, 0, 1)
        risk_cold = np.clip((15 - mean_temp) / 10, 0, 1)
        risk_windy = np.clip(mean_wind / 15, 0, 1)
        risk_wet = np.clip(mean_precip / 10, 0, 1)

        # ----------------------------
        # 4️⃣  Normalización final (para que sumen 1)
        # ----------------------------
        risks = np.array([risk_hot, risk_cold, risk_windy, risk_wet])
        risks = risks / (risks.sum() + 1e-9)

        # ----------------------------
        # 5️⃣  Generar salida con etiquetas claras
        # ----------------------------
        return {
            "hot": round(float(risks[0]) * 100, 2),
            "cold": round(float(risks[1]) * 100, 2),
            "windy": round(float(risks[2]) * 100, 2),
            "wet": round(float(risks[3]) * 100, 2)
        }

    except Exception as e:
        raise RuntimeError(f"Error al calcular riesgos: {e}")
