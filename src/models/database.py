"""Database models for MongoDB collections."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Customer(BaseModel):
    """Customer profile model."""

    customer_id: str = Field(..., description="Unique customer ID")
    name: str
    dni: str
    monthly_income: float
    current_debt: float
    credit_score: int
    account_soles: float
    account_dolares: float
    employment_type: str
    years_employed: int
    sector: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        """Pydantic config."""

        json_encoders = {datetime: lambda v: v.isoformat()}


class Transaction(BaseModel):
    """Transaction record model."""

    transaction_id: str = Field(..., description="Unique transaction ID")
    customer_id: str
    amount: float
    type: str  # deposito, pago, transferencia, compra
    description: str
    date: datetime
    location_country: str = "PE"
    device_fingerprint: str = "known"
    fraud_check: dict[str, Any] | None = None
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        """Pydantic config."""

        json_encoders = {datetime: lambda v: v.isoformat()}


class Conversation(BaseModel):
    """Conversation history model."""

    conversation_id: str = Field(..., description="Unique conversation ID")
    customer_id: str
    session_id: str
    messages: list[dict[str, Any]]  # LangChain messages serialized
    started_at: datetime
    last_message_at: datetime
    agents_used: list[str]
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic config."""

        json_encoders = {datetime: lambda v: v.isoformat()}


class ComplianceCheck(BaseModel):
    """Compliance check record."""

    check_id: str = Field(..., description="Unique check ID")
    customer_id: str
    operation_type: str
    amount: float
    result: dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        """Pydantic config."""

        json_encoders = {datetime: lambda v: v.isoformat()}


class FraudCheck(BaseModel):
    """Fraud detection check record."""

    fraud_check_id: str = Field(..., description="Unique fraud check ID")
    customer_id: str
    transaction_amount: float
    location_country: str
    device_fingerprint: str
    hour_of_day: int
    risk_score: float
    risk_category: str
    anomalies_detected: list[str]
    recommendation: str
    action_required: str
    confidence: float
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        """Pydantic config."""

        json_encoders = {datetime: lambda v: v.isoformat()}


class SystemConfiguration(BaseModel):
    """System configuration model - Replaces hardcoded constants."""

    config_id: str = Field(..., description="Configuration identifier")
    config_type: str  # sbs_regulations, fraud_config, applicable_laws, etc.
    config_data: dict[str, Any]
    version: str
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        """Pydantic config."""

        json_encoders = {datetime: lambda v: v.isoformat()}


class CreditCapacityCalculation(BaseModel):
    """Credit capacity calculation record."""

    calculation_id: str = Field(..., description="Unique calculation ID")
    customer_id: str
    monthly_income: float
    existing_monthly_debt: float
    available_monthly_capacity: float
    max_loan_12_months: float
    max_loan_24_months: float
    max_loan_36_months: float
    debt_ratio_current: float
    debt_ratio_max_sbs: float
    compliant_sbs: bool
    tea_assumed: float
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        """Pydantic config."""

        json_encoders = {datetime: lambda v: v.isoformat()}
