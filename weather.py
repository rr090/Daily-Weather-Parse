import requests
import json
import csv
import os
import traceback
from datetime import datetime, timezone

CITIES = {
    "Berlin":    {"lat": 52.52, "lon": 13.41},
    "Dresden":   {"lat": 51.05, "lon": 13.74},
    "Munich":    {"lat": 48.14, "lon": 11.58},
    "Hamburg":   {"lat": 53.55, "lon": 9.99},
    "Cologne":   {"lat": 50.94, "lon": 6.96},
    "Frankfurt": {"lat": 50.11, "lon": 8.68},
    "Stuttgart": {"lat": 48.78, "lon": 9.18},
    "Leipzig":   {"lat": 51.34, "lon": 12.37},
}

JSON_FILE = "weather.json"
CSV_FILE = "weather.csv"
FIELDS = ["city", "fetched_at", "temperature_c", "wind_speed_kmh", "weather_code"]

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
            "weather_code": data["current"]["weather_code"],
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

    # JSON — последний снимок (перезаписываем каждый раз)
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # CSV — история (дописываем в конец)
    file_exists = os.path.isfile(CSV_FILE) and os.path.getsize(CSV_FILE) > 0
    with open(CSV_FILE, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerows(results)

    print(f"[DONE] records: {len(results)}")

if __name__ == "__main__":
    main()