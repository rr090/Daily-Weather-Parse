import requests
import json
from datetime import datetime

# Координаты: Берлин и Дрезден
CITIES = {
    "Berlin": {"lat": 52.52, "lon": 13.41},
    "Dresden": {"lat": 51.05, "lon": 13.74}
}

def fetch_weather(city, lat, lon):
    """Получает данные о погоде для одного города."""
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&"
        f"current=temperature_2m,wind_speed_10m,weather_code&"
        f"timezone=Europe/Berlin"
    )
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status() # Проверка на ошибки HTTP
        data = response.json()
        return {
            "city": city,
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "temperature_c": data["current"]["temperature_2m"],
            "wind_speed_kmh": data["current"]["wind_speed_10m"],
            "weather_code": data["current"]["weather_code"]
        }
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении данных для {city}: {e}")
        return None

def main():
    results = []
    for city, coords in CITIES.items():
        weather_data = fetch_weather(city, coords["lat"], coords["lon"])
        if weather_data:
            results.append(weather_data)
            print(f"Данные для {city} получены: {weather_data}")

    # Сохраняем результаты в файл
    with open("weather.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()