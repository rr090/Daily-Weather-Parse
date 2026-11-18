import requests
import json
import traceback
from datetime import datetime, timezone

CITIES = {
    "Berlin": {"lat": 52.52, "lon": 13.41},
    "Dresden": {"lat": 51.05, "lon": 13.74}
}

def fetch_weather(city, lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&"
        f"current=temperature_2m,wind_speed_10m,weather_code&"
        f"timezone=Europe/Berlin"
    )
    print(f"[DEBUG] {city}: {url}")
    try:
        response = requests.get(url, timeout=30)
        print(f"[DEBUG] {city} status: {response.status_code}")
        print(f"[DEBUG] {city} body: {response.text[:1000]}")
        response.raise_for_status()
        data = response.json()
        if "current" not in data:
            print(f"[ERROR] {city}: нет ключа 'current' в ответе")
            return None
        return {
            "city": city,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "temperature_c": data["current"]["temperature_2m"],
            "wind_speed_kmh": data["current"]["wind_speed_10m"],
            "weather_code": data["current"]["weather_code"]
        }
    except Exception as e:
        print(f"[ERROR] {city}: {type(e).__name__}: {e}")
        traceback.print_exc()
        return None

def main():
    results = []
    for city, coords in CITIES.items():
        w = fetch_weather(city, coords["lat"], coords["lon"])
        if w:
            results.append(w)
            print(f"[OK] {city}: {w}")
    with open("weather.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[DONE] records: {len(results)}")

if __name__ == "__main__":
    main()