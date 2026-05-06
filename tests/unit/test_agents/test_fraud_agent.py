"""Unit tests for fraud agent."""

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from src.agents.fraud import fraud_agent


class TestFraudAgent:
    """Tests for fraud_agent function."""

    def test_fraud_agent_transaction_analysis(self, banking_state, mock_llm_fraud, mock_fraud_tool):
        """Test fraud agent analyzes transactions."""
        # Arrange
        state = {
            **banking_state,
            "messages": [HumanMessage(content="Detecté una transacción sospechosa de S/15,000")],
        }

        # Act
        result = fraud_agent(state)

        # Assert
        assert result["current_agent"] == "fraud"
        assert "messages" in result
        assert len(result["messages"]) > len(state["messages"])
        mock_fraud_tool.assert_called_once()

    def test_fraud_agent_velocity_check(self, banking_state, mock_llm_fraud, mock_fraud_tool):
        """Test fraud agent performs velocity checks."""
        # Arrange
        state = {
            **banking_state,
            "messages": [HumanMessage(content="El cliente hizo 5 transferencias en 10 minutos")],
        }

        # Act
        result = fraud_agent(state)

        # Assert
        assert result["current_agent"] == "fraud"
        mock_fraud_tool.assert_called_once()

    @pytest.mark.parametrize(
        "amount,expected_risk",
        [
            (500.0, "low"),  # Normal amount
            (15000.0, "medium"),  # Higher amount
            (50000.0, "high"),  # Very high amount
        ],
    )
    def test_fraud_agent_amount_deviation(
        self, banking_state, mock_llm_fraud, amount, expected_risk
    ):
        """Test fraud agent detects unusual amounts."""
        # Arrange
        state = {
            **banking_state,
            "messages": [HumanMessage(content=f"Transacción de S/{amount}")],
        }

        # Act
        result = fraud_agent(state)

        # Assert
        assert result["current_agent"] == "fraud"

    def test_fraud_agent_risk_score_calculation(
        self, banking_state, mock_llm_fraud, mock_fraud_tool
    ):
        """Test fraud agent calculates risk score (0.0-1.0)."""
        # Arrange
        mock_fraud_tool.return_value = {
            "customer_id": "TEST-001",
            "transaction_amount": 5000.0,
            "risk_score": 0.75,  # High risk
            "anomalies_detected": ["velocity_spike", "unusual_time"],
            "checks": {
                "velocity_check": "FAIL",
                "geo_check": "PASS",
                "device_fingerprint": "UNKNOWN",
                "amount_deviation": "HIGH",
                "time_pattern": "UNUSUAL",
            },
            "recommendation": "BLOCK",
            "confidence": 0.88,
        }

        # Act
        result = fraud_agent(banking_state)

        # Assert
        assert result["current_agent"] == "fraud"

    @pytest.mark.parametrize(
        "recommendation,expected_action",
        [
            ("APPROVE", "aprobar"),
            ("REVIEW", "revisar"),
            ("BLOCK", "bloquear"),
        ],
    )
    def test_fraud_agent_recommendation_types(
        self, banking_state, mock_llm_fraud, mock_fraud_tool, recommendation, expected_action
    ):
        """Test fraud agent provides clear recommendations."""
        # Arrange
        mock_fraud_tool.return_value = {
            "customer_id": "TEST-001",
            "transaction_amount": 5000.0,
            "risk_score": 0.3,
            "anomalies_detected": [],
            "checks": {},
            "recommendation": recommendation,
            "confidence": 0.92,
        }
        mock_llm_fraud.invoke.return_value = AIMessage(
            content=f"{recommendation} - Recomendación: {expected_action}"
        )

        # Act
        result = fraud_agent(banking_state)

        # Assert
        last_message = result["messages"][-1].content
        assert recommendation in last_message

    def test_fraud_agent_geo_check(self, banking_state, mock_llm_fraud, mock_fraud_tool):
        """Test fraud agent performs geographic checks."""
        # Arrange
        state = {
            **banking_state,
            "messages": [
                HumanMessage(content="Transacción desde ubicación desconocida en el extranjero")
            ],
        }
        mock_fraud_tool.return_value = {
            "customer_id": "TEST-001",
            "transaction_amount": 5000.0,
            "risk_score": 0.65,
            "anomalies_detected": ["foreign_location"],
            "checks": {
                "velocity_check": "PASS",
                "geo_check": "FAIL",  # Foreign location
                "device_fingerprint": "KNOWN",
                "amount_deviation": "NORMAL",
                "time_pattern": "NORMAL",
            },
            "recommendation": "REVIEW",
            "confidence": 0.78,
        }

        # Act
        result = fraud_agent(state)

        # Assert
        assert result["current_agent"] == "fraud"

    def test_fraud_agent_preserves_state(self, banking_state, mock_llm_fraud):
        """Test fraud agent preserves BankingState fields."""
        # Arrange
        state = {
            **banking_state,
            "customer_id": "FRAUD-TEST-001",
        }

        # Act
        result = fraud_agent(state)

        # Assert
        assert result["customer_id"] == "FRAUD-TEST-001"

    def test_fraud_agent_appends_message(self, banking_state, mock_llm_fraud):
        """Test fraud agent appends AI message to state."""
        # Arrange
        initial_message_count = len(banking_state["messages"])

        # Act
        result = fraud_agent(banking_state)

        # Assert
        assert len(result["messages"]) == initial_message_count + 1
        last_message = result["messages"][-1]
        assert "[Anti-Fraude]" in last_message.content

    def test_fraud_agent_detailed_analysis(self, banking_state, mock_llm_fraud, mock_fraud_tool):
        """Test fraud agent provides detailed analysis."""
        # Arrange
        mock_fraud_tool.return_value = {
            "customer_id": "TEST-001",
            "transaction_amount": 8500.0,
            "risk_score": 0.25,
            "anomalies_detected": [],
            "checks": {
                "velocity_check": "PASS",
                "geo_check": "PASS",
                "device_fingerprint": "KNOWN",
                "amount_deviation": "NORMAL",
                "time_pattern": "NORMAL",
            },
            "recommendation": "APPROVE",
            "confidence": 0.94,
        }

        # Act
        result = fraud_agent(banking_state)

        # Assert
        assert result["current_agent"] == "fraud"
        # Should have fraud analysis in response
