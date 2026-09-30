# Agro Scoring API

Рефакторинг практической работы №1 по разработке REST API для AI-сервиса на FastAPI.

## Структура

```text
agro_api/
├── main.py
├── schemas.py
├── model.py
├── services.py
├── storage.py
├── test_api.py
├── requirements.txt
├── report.tex
└── screenshots/
    ├── swagger.png
    ├── predict_success.png
    ├── pydantic_error.png
    └── not_found.png
```

## Запуск в Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

После запуска:

- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI: http://127.0.0.1:8000/openapi.json
- Health: http://127.0.0.1:8000/health

## Основные тестовые данные

```json
{
  "farm_id": "FARM-001",
  "region": "Krasnodar",
  "crop_type": "wheat",
  "area_ha": 2500,
  "temperature_avg": 24.3,
  "precipitation_mm": 320,
  "payment_delay_days": 45,
  "previous_defaults": 1,
  "debt": 6500000
}
```

Эти данные дают `risk_score = 0.9` и `risk_level = high`.

## Что сфотографировать для отчёта

1. `/docs` — общий Swagger UI со всеми пятью endpoints.
2. `POST /predict` — успешный ответ 200.
3. `POST /predict` с `"area_ha": -100` — ошибка Pydantic 422.
4. `GET /predictions/not-existing-id` — ошибка 404.
5. При необходимости дополнительно показать `GET /predictions?limit=2` и `GET /predictions?risk_level=high`.

## Автоматические тесты

```powershell
pytest -q
```

Все тесты должны завершиться успешно.
