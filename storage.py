from typing import Optional

from schemas import PredictionResponse

# Временное хранилище для лабораторной работы.
# В промышленной системе здесь может быть PostgreSQL/Redis и т. п.
_predictions: dict[str, PredictionResponse] = {}


def save_prediction(prediction: PredictionResponse) -> None:
    _predictions[prediction.request_id] = prediction


def get_prediction(request_id: str) -> Optional[PredictionResponse]:
    return _predictions.get(request_id)


def get_predictions() -> list[PredictionResponse]:
    return list(_predictions.values())


def clear_predictions() -> None:
    """Используется в тестах."""
    _predictions.clear()
