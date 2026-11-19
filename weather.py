import requests
import json
import csv
import os
import traceback
from datetime import datetime, timezone

CITIES_FILE = "cities.json"
JSON_FILE = "weather.json"
BATCH_SIZE = 50

CURRENT_PARAMS = [
    "temperature_2m","relative_humidity_2m","apparent_temperature","is_day",
    "precipitation","rain","showers","snowfall","weather_code","cloud_cover",
    "pressure_msl","surface_pressure","wind_speed_10m","wind_direction_10m","wind_gusts_10m"
]
DAILY_PARAMS = [
    "weather_code","temperature_2m_max","temperature_2m_min","temperature_2m_mean",
    "apparent_temperature_max","apparent_temperature_min","sunrise","sunset",
    "daylight_duration","sunshine_duration","uv_index_max","uv_index_clear_sky_max",
    "precipitation_sum","rain_sum","showers_sum","snowfall_sum","precipitation_hours",
    "precipitation_probability_max","precipitation_probability_min","precipitation_probability_mean",
    "wind_speed_10m_max","wind_gusts_10m_max","wind_direction_10m_dominant"
]

def fetch_batch(city_items):
    lats = ",".join(str(c["lat"]) for _, c in city_items)
    lons = ",".join(str(c["lon"]) for _, c in city_items)
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lats}&longitude={lons}&"
        f"current={','.join(CURRENT_PARAMS)}&"
        f"daily={','.join(DAILY_PARAMS)}&"
        f"timezone=auto&forecast_days=7"
    )
    print(f"[BATCH] {len(city_items)} cities")
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, dict):
        data = [data]
    return data

def main():
    with open(CITIES_FILE, encoding="utf-8") as f:
        cities = json.load(f)

    items = list(cities.items())
    results = {}
    fetched_at = datetime.now(timezone.utc).isoformat()

    for i in range(0, len(items), BATCH_SIZE):
        batch = items[i:i+BATCH_SIZE]
        try:
            responses = fetch_batch(batch)
        except Exception as e:
            print(f"[ERROR] batch {i}: {e}")
            traceback.print_exc()
            continue
        for j, (city_id, _) in enumerate(batch):
            if j >= len(responses):
                print(f"[WARN] no response for {city_id}")
                continue
            data = responses[j]
            results[city_id] = {
                "city": cities[city_id],
                "fetched_at": fetched_at,
                "current": data.get("current", {}),
                "daily": data.get("daily", {})
            }
            print(f"[OK] {city_id}")

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": fetched_at,
            "cities": results
        }, f, ensure_ascii=False, indent=2)
    print(f"[DONE] weather.json: {len(results)} cities")

    month = datetime.now().strftime("%Y-%m")
    current_csv = f"weather_current_{month}.csv"
    daily_csv = f"weather_daily_{month}.csv"

    current_fields = ["city_id","city_en","country_en","fetched_at"] + CURRENT_PARAMS
    exists = os.path.isfile(current_csv) and os.path.getsize(current_csv) > 0
    with open(current_csv, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=current_fields, extrasaction="ignore")
        if not exists:
            w.writeheader()
        for cid, r in results.items():
            row = {
                "city_id": cid,
                "city_en": r["city"]["name_en"],
                "country_en": r["city"]["country_en"],
                "fetched_at": r["fetched_at"]
            }
            for p in CURRENT_PARAMS:
                row[p] = r["current"].get(p)
            w.writerow(row)
    print(f"[DONE] {current_csv}")

    daily_fields = ["city_id","city_en","date"] + DAILY_PARAMS
    exists = os.path.isfile(daily_csv) and os.path.getsize(daily_csv) > 0
    with open(daily_csv, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=daily_fields, extrasaction="ignore")
        if not exists:
            w.writeheader()
        for cid, r in results.items():
            daily = r["daily"]
            dates = daily.get("time", [])
            for i, d in enumerate(dates):
                row = {"city_id": cid, "city_en": r["city"]["name_en"], "date": d}
                for p in DAILY_PARAMS:
                    vals = daily.get(p)
                    row[p] = vals[i] if isinstance(vals, list) and i < len(vals) else None
                w.writerow(row)
    print(f"[DONE] {daily_csv}")

if __name__ == "__main__":
    main()