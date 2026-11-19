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

CURRENT_PARAMS = [
    "temperature_2m", "relative_humidity_2m", "apparent_temperature",
    "is_day", "precipitation", "rain", "showers", "snowfall",
    "weather_code", "cloud_cover", "pressure_msl", "surface_pressure",
    "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"
]

DAILY_PARAMS = [
    "weather_code", "temperature_2m_max", "temperature_2m_min", "temperature_2m_mean",
    "apparent_temperature_max", "apparent_temperature_min",
    "sunrise", "sunset", "daylight_duration", "sunshine_duration",
    "uv_index_max", "uv_index_clear_sky_max",
    "precipitation_sum", "rain_sum", "showers_sum", "snowfall_sum", "precipitation_hours",
    "precipitation_probability_max", "precipitation_probability_min", "precipitation_probability_mean",
    "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant"
]

def fetch_weather(city, lat, lon):
    current_str = ",".join(CURRENT_PARAMS)
    daily_str = ",".join(DAILY_PARAMS)
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&"
        f"current={current_str}&"
        f"daily={daily_str}&"
        f"timezone=Europe/Berlin&forecast_days=7"
    )
    print(f"[DEBUG] {city}")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        return {
            "city": city,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "current": data.get("current", {}),
            "daily": data.get("daily", {})
        }
    except Exception as e:
        print(f"[ERROR] {city}: {type(e).__name__}: {e}")
        traceback.print_exc()
        return None

def save_results(results):
    # 1. Полный JSON
    with open("weather.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("[DONE] weather.json saved")

    # 2. Текущая погода — CSV
    current_fields = ["city", "fetched_at"] + CURRENT_PARAMS
    file_exists = os.path.isfile("weather_current.csv") and os.path.getsize("weather_current.csv") > 0
    with open("weather_current.csv", "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=current_fields, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        for item in results:
            row = {"city": item["city"], "fetched_at": item["fetched_at"]}
            for p in CURRENT_PARAMS:
                row[p] = item["current"].get(p)
            writer.writerow(row)
    print("[DONE] weather_current.csv updated")

    # 3. Прогноз — CSV
    daily_fields = ["city", "fetched_at", "date"] + DAILY_PARAMS
    file_exists = os.path.isfile("weather_daily.csv") and os.path.getsize("weather_daily.csv") > 0
    with open("weather_daily.csv", "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=daily_fields, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        for item in results:
            daily = item["daily"]
            dates = daily.get("time", [])
            for i, date in enumerate(dates):
                row = {"city": item["city"], "fetched_at": item["fetched_at"], "date": date}
                for p in DAILY_PARAMS:
                    vals = daily.get(p)
                    row[p] = vals[i] if isinstance(vals, list) and i < len(vals) else None
                writer.writerow(row)
    print("[DONE] weather_daily.csv updated")

def main():
    results = []
    for city, coords in CITIES.items():
        w = fetch_weather(city, coords["lat"], coords["lon"])
        if w:
            results.append(w)
            print(f"[OK] {city}")
    save_results(results)
    print(f"[DONE] total cities: {len(results)}")

if __name__ == "__main__":
    main()