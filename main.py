import logging
import time
import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Request, status

from model import MODEL_NAME, MODEL_TYPE, MODEL_VERSION
from schemas import (
    FarmRequest,
    HealthResponse,
    ModelInfoResponse,
    PredictionResponse,
)
from services import ALLOWED_RISK_LEVELS, build_prediction, validate_region
from storage import get_prediction, get_predictions, save_prediction

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agro Scoring API",
    description=(
        "REST API для оценки риска "
        "сельскохозяйственных предприятий."
    ),
    version="1.0.0",
)

# Имитируем состояние ML-модели.
MODEL_READY = True


@app.middleware("http")
async def add_process_time(request: Request, call_next):
    """Добавляет в ответ время обработки X-Process-Time."""
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(round(process_time, 6))
    return response


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Проверка состояния API",
    description="Проверяет, что REST API запущен и отвечает.",
)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get(
    "/model-info",
    response_model=ModelInfoResponse,
    summary="Информация о модели",
    description="Возвращает название, версию, тип и состояние модели.",
)
def model_info() -> ModelInfoResponse:
    return ModelInfoResponse(
        model_name=MODEL_NAME,
        model_version=MODEL_VERSION,
        model_type=MODEL_TYPE,
        status="ready" if MODEL_READY else "unavailable",
    )


@app.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Оценить риск хозяйства",
    description=(
        "Принимает характеристики хозяйства, выполняет "
        "Pydantic- и бизнес-валидацию, затем выполняет инференс."
    ),
)
def predict(request: FarmRequest) -> PredictionResponse:
    if not MODEL_READY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is temporarily unavailable",
        )

    validate_region(request.region)

    logger.info(
        "Prediction request received | farm_id=%s",
        request.farm_id,
    )

    request_id = str(uuid.uuid4())
    result = build_prediction(request, request_id, MODEL_VERSION)
    prediction = PredictionResponse(**result)

    save_prediction(prediction)

    logger.info(
        "Prediction completed | request_id=%s | farm_id=%s | "
        "risk_score=%s | risk_level=%s",
        prediction.request_id,
        prediction.farm_id,
        prediction.risk_score,
        prediction.risk_level,
    )

    return prediction


@app.get(
    "/predictions",
    response_model=list[PredictionResponse],
    summary="Получить список прогнозов",
    description=(
        "Возвращает сохранённые прогнозы с ограничением количества "
        "и необязательной фильтрацией по уровню риска."
    ),
)
def get_predictions_endpoint(
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Количество результатов: от 1 до 100",
    ),
    risk_level: Optional[str] = Query(
        default=None,
        description="Фильтр: low, medium или high",
    ),
) -> list[PredictionResponse]:
    if risk_level is not None and risk_level not in ALLOWED_RISK_LEVELS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="risk_level must be 'low', 'medium' or 'high'",
        )

    values = get_predictions()

    if risk_level is not None:
        values = [
            item for item in values
            if item.risk_level == risk_level
        ]

    return values[:limit]


@app.get(
    "/predictions/{request_id}",
    response_model=PredictionResponse,
    summary="Получить прогноз по request_id",
    description="Возвращает сохранённый прогноз по уникальному идентификатору.",
)
def get_prediction_endpoint(request_id: str) -> PredictionResponse:
    prediction = get_prediction(request_id)

    if prediction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found",
        )

    return prediction


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
