# Check-now Backend


Check-now es un backend en **FastAPI** que permite consultar datos meteorológicos y riesgos relacionados para cualquier país, utilizando la API de Meteomatics y NASA POWER.
---

## 🔧 Requisitos

* Python 3.10+
* Virtualenv
* Dependencias listadas en `requirements.txt`

---

## 📁 Estructura del proyecto

```
Check-now/
└── backend/
    ├── app.py                  # Punto de entrada principal de FastAPI
    ├── requirements.txt        # Dependencias del proyecto
    ├── .env                    # Variables de entorno (credenciales Meteomatics)
    ├── venv/                   # Entorno virtual
    ├── api/
    │   ├── __init__.py
    │   ├── routes.py           # Todos los endpoints y validaciones
    │   └── meteomatics.py      # Lógica para consumir API de Meteomatics
    ├── services/
    │   ├── __init__.py
    │   └── nasa_power.py       # Lógica para consumir API de NASA POWER
    └── models/
        ├── __init__.py
        └── risk_model.py       # Función opcional compute_risk_probabilities


---

## ⚙️ Configuración

1. Clonar el repositorio:

```bash
git clone https://github.com/CrisWebcat/Check-now.git
cd Check-now/backend
```

2. Crear virtualenv e instalar dependencias:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Crear archivo `.env` (NO subirlo) con tus credenciales de Meteomatics:

```
METEO_USER=tu_usuario
METEO_PASS=tu_password
```

> El backend usa estas variables para autenticar las consultas a Meteomatics.

---

## 🚀 Ejecutar el servidor

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

* El servidor correrá en `http://127.0.0.1:8000`
* Puedes probar los endpoints con `curl` o Postman.

---

## 📡 Endpoints disponibles

| Endpoint       | Método | Parámetros                                                         | Descripción                                                        | Ejemplo                                                                                  |
| -------------- | ------ | ------------------------------------------------------------------ | ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| `/api/`        | GET    | —                                                                  | Mensaje de bienvenida                                              | `http://127.0.0.1:8000/api/`                                                             |
| `/api/health`  | GET    | —                                                                  | Estado del servidor                                                | `http://127.0.0.1:8000/api/health`                                                       |
| `/api/weather` | GET    | `lat`, `lon`, `start`, `end`                                       | Consulta Meteomatics para lat/lon y rango de fechas                | `http://127.0.0.1:8000/api/weather?lat=15.59&lon=-90.34&start=2025-10-05&end=2025-10-06` |
| `/api/risk`    | GET    | `lat`, `lon`, `date_query`                                         | Consulta riesgo basado en Meteomatics (solo un día)                | `http://127.0.0.1:8000/api/risk?lat=15.59&lon=-90.34&date_query=2025-10-05`              |
| `/api/query`   | GET    | `country`, `start`, `end`                                          | Consulta Meteomatics para un país, obtiene lat/lon automáticamente | `http://127.0.0.1:8000/api/query?country=Guatemala&start=2025-10-05&end=2025-10-06`      |
| `/api/nasa`    | GET    | `lat`, `lon`, `start`, `end`, `community` (opcional, default="AG") | Consulta NASA POWER (solar, temperatura, precipitación)            | `http://127.0.0.1:8000/api/nasa?lat=15.59&lon=-90.34&start=2025-10-05&end=2025-10-06`    |


* **Respuesta**:

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

* **Errores comunes**:

  * 400: Fechas inválidas o lat/lon fuera de rango
  * 500: Error al consultar Meteomatics (revisar credenciales o conexión)
    

---Notas importantes

/api/query permite obtener datos solo indicando el país; las coordenadas se calculan automáticamente.

/api/nasa solo devuelve datos hasta la fecha actual; si se solicita una fecha futura, se recibe un warning.

Todos los endpoints están preparados para manejar errores HTTP y de conexión con las APIs externas.

El formato de fechas debe ser siempre YYYY-MM-DD.

Las coordenadas lat/lon deben estar en grados decimales válidos.

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
