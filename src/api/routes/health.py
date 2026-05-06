"""Health check endpoint."""

from datetime import datetime

from fastapi import APIRouter

from src.config.settings import settings
from src.models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        model=settings.VLLM_MODEL,
        gpu="AMD Instinct MI300X",
        timestamp=datetime.now(),
    )
