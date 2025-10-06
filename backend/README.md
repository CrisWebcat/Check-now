# Check-now Backend


Check-now is a **FastAPI** backend that allows you to query meteorological data and related risks for any country, using the Meteomatics API and NASA POWER.
---

## 🔧 Requirements

* Python 3.10+
* Virtualenv
* Dependencies listed in `requirements.txt`

---

## 📁 Project structure

```
Check-now/
└── backend/
    ├── app.py                  # FastAPI main entry point
    ├── requirements.txt        # Project dependencies
    ├── .env                    # Environment variables (Meteomatics credentials)
    ├── venv/                   # Virtual environment
    ├── api/
    │   ├── __init__.py
    │   ├── routes.py           # All endpoints and validations
    │   └── meteomatics.py      # Logic for consuming Meteomatics API
    ├── services/
    │   ├── __init__.py
    │   └── nasa_power.py       # Logic to consume NASA POWER API
    └── models/
        ├── __init__.py
        └── risk_model.py       # Optional function compute_risk_probabilities


---

## ⚙️ Configuration

1. Clone the repository:

```bash
git clone https://github.com/CrisWebcat/Check-now.git
cd Check-now/backend
```

2. Create virtualenv and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Create a `.env` file (DO NOT upload it) with your Meteomatics credentials:

```
METEO_USER = your username
METEO_PASS = your password
```

> The backend uses these variables to authenticate queries to Meteomatics.

---

##  Run the server
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

* The server will run at `http://127.0.0.1:8000`
* You can test the endpoints with `curl` or Postman.

---

## 📡 Available endpoints

| Endpoint       | Método | Parameters                                                        | Description                                                      | example                                                                                  |
| -------------- | ------ | ------------------------------------------------------------------ | ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| `/api/`        | GET    | —                                                                  | Mensaje de bienvenida                                              | `http://127.0.0.1:8000/api/`                                                             |
| `/api/health`  | GET    | —                                                                  | Estado del servidor                                                | `http://127.0.0.1:8000/api/health`                                                       |
| `/api/weather` | GET    | `lat`, `lon`, `start`, `end`                                       | Consulta Meteomatics para lat/lon y rango de fechas                | `http://127.0.0.1:8000/api/weather?lat=15.59&lon=-90.34&start=2025-10-05&end=2025-10-06` |
| `/api/risk`    | GET    | `lat`, `lon`, `date_query`                                         | Consulta riesgo basado en Meteomatics (solo un día)                | `http://127.0.0.1:8000/api/risk?lat=15.59&lon=-90.34&date_query=2025-10-05`              |
| `/api/query`   | GET    | `country`, `start`, `end`                                          | Consulta Meteomatics para un país, obtiene lat/lon automáticamente | `http://127.0.0.1:8000/api/query?country=Guatemala&start=2025-10-05&end=2025-10-06`      |
| `/api/nasa`    | GET    | `lat`, `lon`, `start`, `end`, `community` (opcional, default="AG") | Consulta NASA POWER (solar, temperatura, precipitación)            | `http://127.0.0.1:8000/api/nasa?lat=15.59&lon=-90.34&start=2025-10-05&end=2025-10-06`    |


* **Responses**:

```json
{
  "status": "ok"
}
```

---

### 2. Weather

```
GET /api/weather?lat=<latitud>&lon=<longitud>&start=<YYYY-MM-DD>&end=<YYYY-MM-DD>
```

* **Parámetros**:

  * `lat`: Latitud (-90 a 90)
  * `lon`: Longitud (-180 a 180)
  * `start`: Fecha de inicio (YYYY-MM-DD)
  * `end`: Fecha final (YYYY-MM-DD)
* **Respuesta**:

```json
{
  "status": "success",
  "data": {...}
}
```

* **common errors**:

  * 400: Fechas inválidas o lat/lon fuera de rango
  * 500: Error al consultar Meteomatics (revisar credenciales o conexión)
    

---Notas importantes

/api/query allows you to retrieve data by simply specifying the country; coordinates are calculated automatically.

/api/nasa only returns data up to the current date; requesting a future date will result in a warning.

All endpoints are prepared to handle HTTP and connection errors with external APIs.

Dates must always be formatted as YYYY-MM-DD.

Lat/lon coordinates must be in valid decimal degrees.

### 3. Risk

```
GET /api/risk?lat=<latitud>&lon=<longitud>&date_query=<YYYY-MM-DD>
```

* **Parámetros**:

  * `lat`, `lon`: Ubicación
  * `date_query`: Fecha de consulta
* **Respuesta**:

```json
{
  "status": "success",
  "timeseries": {...}
}
```

---

### 4. Query por país

```
GET /api/query?country=<nombre_del_país>&start=<YYYY-MM-DD>&end=<YYYY-MM-DD>
```

* **Funcionalidad**: Devuelve datos meteorológicos para las coordenadas principales de un país.
* **Parámetros**:

  * `country`: Nombre del país (ej. Guatemala)
  * `start`, `end`: Fechas
* **Errores**:

  * 400: Formato de fechas incorrecto
  * 404: País no encontrado
  * 500: Error en consulta a Meteomatics

---

## ⚠️ Notas importantes

* **No subir el `.env`** al repositorio.
* Todos los errores relacionados con Meteomatics usualmente son por:

  * Credenciales incorrectas
  * Fechas fuera de rango
  * Problemas de conexión
* El frontend debe manejar respuestas 400/404/500 según corresponda.

---

## 📌 Autor / Contacto

* Karla Aguilar
