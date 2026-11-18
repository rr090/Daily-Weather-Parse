```markdown
# 🌤️ Weather Bot

Автоматический парсер погоды для **Берлина** и **Дрездена**.  
GitHub Actions запускается каждый день в 00:00 UTC, получает актуальные данные через [Open-Meteo API](https://open-meteo.com/) и сохраняет их в `weather.json`.

## 📁 Структура

```

.
├── .github/
│   └── workflows/
│       └── weather.yml     # Workflow GitHub Actions
├── weather.py              # Скрипт парсинга
└── weather.json            # Результат (обновляется автоматически)

```

## ⚙️ Как это работает

1. **Триггер** — cron `0 0 * * *` (раз в сутки) или ручной запуск через `workflow_dispatch`.
2. **Скрипт** — `weather.py` запрашивает у Open-Meteo текущую температуру, скорость ветра и код погоды для двух городов.
3. **Сохранение** — результат пишется в `weather.json`, затем коммитится обратно в репозиторий от имени `github-actions[bot]`.

## 🚀 Запуск вручную

1. Перейди во вкладку **Actions**.
2. Выбери workflow **Daily Weather Parse**.
3. Нажми **Run workflow** → **Run workflow**.

## 📊 Формат данных

```json
[
  {
    "city": "Berlin",
    "fetched_at": "2025-01-15T00:00:12.345678Z",
    "temperature_c": 3.4,
    "wind_speed_kmh": 12.6,
    "weather_code": 3
  },
  {
    "city": "Dresden",
    "fetched_at": "2025-01-15T00:00:12.456789Z",
    "temperature_c": 2.1,
    "wind_speed_kmh": 9.8,
    "weather_code": 1
  }
]
```

Расшифровка weather_code (по WMO):

Код Значение
0 Ясно
1–3 Преимущественно ясно / переменная облачность / пасмурно
45, 48 Туман
51–67 Морось и дождь
71–77 Снег
80–82 Ливни
95–99 Гроза

➕ Добавить новый город

Открой weather.py и добавь запись в словарь CITIES:

```python
CITIES = {
    "Berlin":  {"lat": 52.52, "lon": 13.41},
    "Dresden": {"lat": 51.05, "lon": 13.74},
    "Munich":  {"lat": 48.14, "lon": 11.58},
}
```

Координаты можно взять на latlong.net.

🛠️ Требования

· Python 3.11 (устанавливается автоматически в workflow)
· Библиотека requests
· Разрешение contents: write для GITHUB_TOKEN (уже прописано в workflow + включено в настройках репозитория)

📝 Лицензия

MIT — делай что хочешь.

```