from fastapi.testclient import TestClient

from main import app
from storage import clear_predictions

client = TestClient(app)

VALID_PAYLOAD = {
    "farm_id": "FARM-001",
    "region": "Krasnodar",
    "crop_type": "wheat",
    "area_ha": 2500,
    "temperature_avg": 24.3,
    "precipitation_mm": 320,
    "payment_delay_days": 45,
    "previous_defaults": 1,
    "debt": 6_500_000,
}


def setup_function():
    clear_predictions()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_model_info():
    response = client.get("/model-info")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_predict_and_get_prediction():
    response = client.post("/predict", json=VALID_PAYLOAD)
    assert response.status_code == 200

    data = response.json()
    assert data["risk_score"] == 0.9
    assert data["risk_level"] == "high"

    request_id = data["request_id"]

    by_id = client.get(f"/predictions/{request_id}")
    assert by_id.status_code == 200
    assert by_id.json()["request_id"] == request_id


def test_pydantic_validation():
    payload = {**VALID_PAYLOAD, "area_ha": -100}
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_unknown_region():
    payload = {**VALID_PAYLOAD, "region": "Moscow"}
    response = client.post("/predict", json=payload)
    assert response.status_code == 400


def test_not_found():
    response = client.get("/predictions/not-existing-id")
    assert response.status_code == 404


def test_predictions_filters_and_limit_validation():
    client.post("/predict", json=VALID_PAYLOAD)

    response = client.get("/predictions?limit=2")
    assert response.status_code == 200
    assert len(response.json()) <= 2

    response = client.get("/predictions?risk_level=high")
    assert response.status_code == 200
    assert all(item["risk_level"] == "high" for item in response.json())

    response = client.get("/predictions?limit=-5")
    assert response.status_code == 422


def test_invalid_risk_level():
    response = client.get("/predictions?risk_level=unknown")
    assert response.status_code == 400
