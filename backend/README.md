# Check-now Backend

Este repositorio contiene el backend del proyecto **Check-now**, desarrollado con **FastAPI**. Su función principal es proveer datos meteorológicos desde Meteomatics y calcular riesgos según los datos obtenidos.

---

## 🔧 Requisitos

* Python 3.10+
* Virtualenv
* Dependencias listadas en `requirements.txt`

---

## 📁 Estructura del proyecto

```
backend/
├─ api/
│  ├─ __init__.py
│  ├─ routes.py          # Endpoints principales: health, weather, risk, query por país
│  └─ meteomatics.py     # Funciones para consultar API de Meteomatics
├─ config.py             # Configuración general, carga de .env
├─ run_queries.py        # Funciones auxiliares para consultas de país
├─ .env                  # No subir al repositorio, contiene credenciales
├─ .gitignore
├─ README.md
├─ venv/                 # Virtualenv local
└─ tests/                # Pruebas unitarias
```

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

### 1. Health check

```
GET /api/health
```

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

---

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
