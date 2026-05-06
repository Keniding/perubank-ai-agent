"""Pydantic schemas for API requests and responses."""

from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    customer_id: str = Field(default="CLI-ANONYMOUS")
    session_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    agent_used: str
    risk_score: float | None = None
    compliance_check: dict | None = None
    timestamp: datetime = Field(default_factory=datetime.now)


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str
    model: str
    gpu: str = "AMD Instinct MI300X"
    timestamp: datetime = Field(default_factory=datetime.now)
