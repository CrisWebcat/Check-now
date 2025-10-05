import requests

BASE_URL = "http://127.0.0.1:8000/api"

def test_health():
    url = f"{BASE_URL}/health"
    try:
        r = requests.get(url)
        r.raise_for_status()
        print("✅ /health OK:", r.json())
    except Exception as e:
        print("❌ /health FAILED:", e)

def test_weather():
    url = f"{BASE_URL}/weather"
    params = {"lat": 14.6349, "lon": -90.5069, "start": "2023-01-01", "end": "2023-01-02"}
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        print("✅ /weather OK:", r.json())
    except Exception as e:
        print("❌ /weather FAILED:", e)

def test_risk():
    url = f"{BASE_URL}/risk"
    params = {"lat": 14.6349, "lon": -90.5069, "date_query": "2023-01-01"}
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        print("✅ /risk OK:", r.json())
    except Exception as e:
        print("❌ /risk FAILED:", e)

def test_query():
    url = f"{BASE_URL}/query"
    params = {"country": "Guatemala", "start": "2023-01-01", "end": "2023-01-02"}
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        print("✅ /query OK:", r.json())
    except Exception as e:
        print("❌ /query FAILED:", e)

def test_nasa():
    url = f"{BASE_URL}/nasa"
    params = {"lat": 14.6349, "lon": -90.5069, "start": "2023-01-01", "end": "2023-01-02"}
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        print("✅ /nasa OK:", r.json())
    except Exception as e:
        print("❌ /nasa FAILED:", e)

if __name__ == "__main__":
    test_health()
    test_weather()
    test_risk()
    test_query()
    test_nasa()
