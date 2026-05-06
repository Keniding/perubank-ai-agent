"""Pydantic schemas for API requests and responses."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    customer_id: str = Field(default="CLI-ANONYMOUS")
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    agent_used: str
    risk_score: Optional[float] = None
    compliance_check: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str
    model: str
    gpu: str = "AMD Instinct MI300X"
    timestamp: datetime = Field(default_factory=datetime.now)
