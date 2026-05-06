"""Pytest configuration and fixtures."""

from unittest.mock import patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage


@pytest.fixture
def sample_customer_id():
    """Sample customer ID for testing."""
    return "CLI-2026-TEST"


@pytest.fixture
def banking_state():
    """Sample BankingState for testing."""
    return {
        "messages": [HumanMessage(content="Quiero un préstamo de S/20,000")],
        "customer_id": "TEST-001",
        "intent": "",
        "risk_score": 0.0,
        "compliance_check": {},
        "recommendation": "",
        "current_agent": "",
    }


@pytest.fixture
def sample_state(banking_state):
    """Alias for backward compatibility."""
    return banking_state


@pytest.fixture
def customer_profile():
    """Sample customer data for risk assessment."""
    return {
        "id": "TEST-001",
        "monthly_income": 5000.0,
        "current_debt": 1200.0,
        "credit_score": 750,
        "employment_type": "dependiente",
        "years_employed": 3,
        "sector": "servicios",
    }


@pytest.fixture
def mock_llm_compliance():
    """Mock ChatOpenAI for compliance agent responses."""
    with patch("src.agents.compliance.ChatOpenAI") as mock:
        mock_instance = mock.return_value
        mock_instance.invoke.return_value = AIMessage(
            content="La operación cumple con normativa SBS. No requiere reporte UIF."
        )
        yield mock_instance


@pytest.fixture
def mock_llm_risk():
    """Mock ChatOpenAI for risk agent responses."""
    with patch("src.agents.risk.ChatOpenAI") as mock:
        mock_instance = mock.return_value
        mock_instance.invoke.return_value = AIMessage(
            content="VIABLE - Ratio deuda/ingreso: 24%. Score crediticio: 750/1000."
        )
        yield mock_instance


@pytest.fixture
def mock_llm_advisor():
    """Mock ChatOpenAI for advisor agent responses."""
    with patch("src.agents.advisor.ChatOpenAI") as mock:
        mock_instance = mock.return_value
        mock_instance.invoke.return_value = AIMessage(
            content="Recomiendo cuenta ahorro premium con tasa 3.5% anual. "
            "Beneficio: rentabilidad. Riesgo: tasa variable según BCRP."
        )
        yield mock_instance


@pytest.fixture
def mock_llm_fraud():
    """Mock ChatOpenAI for fraud agent responses."""
    with patch("src.agents.fraud.ChatOpenAI") as mock:
        mock_instance = mock.return_value
        mock_instance.invoke.return_value = AIMessage(
            content="APROBAR - Riesgo: 0.15. Checks: velocity PASS, geo PASS."
        )
        yield mock_instance


@pytest.fixture
def mock_llm_orchestrator():
    """Mock ChatOpenAI for orchestrator routing."""
    with patch("src.agents.orchestrator.ChatOpenAI") as mock:
        mock_instance = mock.return_value
        mock_instance.invoke.return_value = AIMessage(content="compliance")
        yield mock_instance


@pytest.fixture
def mock_compliance_tool():
    """Mock compliance tools."""
    with patch("src.agents.compliance.check_sbs_compliance") as mock:
        mock.return_value = {
            "compliant": True,
            "regulations": ["Res. SBS 4142-2025"],
            "checks": {"uif_threshold": "PASS", "sandbox_eligible": True},
        }
        yield mock


@pytest.fixture
def mock_fraud_tool():
    """Mock fraud detection tools."""
    with patch("src.agents.fraud.detect_fraud_patterns") as mock:
        mock.return_value = {
            "customer_id": "TEST-001",
            "transaction_amount": 5000.0,
            "risk_score": 0.15,
            "anomalies_detected": [],
            "checks": {
                "velocity_check": "PASS",
                "geo_check": "PASS",
                "device_fingerprint": "KNOWN",
                "amount_deviation": "NORMAL",
                "time_pattern": "NORMAL",
            },
            "recommendation": "APPROVE",
            "confidence": 0.92,
        }
        yield mock
