"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_customer_id():
    return "CLI-2026-TEST"


@pytest.fixture
def sample_state():
    from langchain_core.messages import HumanMessage

    return {
        "messages": [HumanMessage(content="Quiero un prestamo de S/20,000")],
        "customer_id": "CLI-2026-TEST",
        "intent": "",
        "risk_score": 0.0,
        "compliance_check": {},
        "recommendation": "",
        "current_agent": "",
    }
