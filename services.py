from fastapi import HTTPException, status

from model import calculate_risk
from schemas import FarmRequest

ALLOWED_REGIONS = {
    "Krasnodar",
    "Rostov",
    "Stavropol",
}

ALLOWED_RISK_LEVELS = {"low", "medium", "high"}


def validate_region(region: str) -> None:
    """Проверяет бизнес-ограничение по региону."""
    if region not in ALLOWED_REGIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unknown region: {region}. "
                f"Allowed regions: {sorted(ALLOWED_REGIONS)}"
            ),
        )


def get_risk_level(score: float) -> str:
    """Преобразует числовой score в категорию риска."""
    if score < 0.3:
        return "low"
    if score < 0.7:
        return "medium"
    return "high"


def get_recommendation(level: str) -> str:
    """Формирует рекомендацию оператору."""
    recommendations = {
        "low": "Стандартное рассмотрение",
        "medium": "Требуется дополнительная проверка",
        "high": "Высокий риск. Требуется ручное рассмотрение",
    }
    return recommendations[level]


def build_prediction(data: FarmRequest, request_id: str, model_version: str) -> dict:
    """Выполняет инференс и формирует публичный результат."""
    score = calculate_risk(data)
    level = get_risk_level(score)

    return {
        "request_id": request_id,
        "farm_id": data.farm_id,
        "risk_score": score,
        "risk_level": level,
        "recommendation": get_recommendation(level),
        "model_version": model_version,
    }
