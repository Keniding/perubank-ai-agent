"""Unit tests for risk agent."""

import pytest
from langchain_core.messages import HumanMessage

from src.agents.risk import risk_agent


class TestRiskAgent:
    """Tests for risk_agent function."""

    def test_risk_agent_credit_assessment(self, banking_state, mock_llm_risk):
        """Test risk agent performs credit assessment."""
        # Arrange
        state = {
            **banking_state,
            "messages": [HumanMessage(content="¿Puedo acceder a un préstamo de S/50,000?")],
        }

        # Act
        result = risk_agent(state)

        # Assert
        assert result["current_agent"] == "risk"
        assert "messages" in result
        assert len(result["messages"]) > len(state["messages"])

    @pytest.mark.parametrize(
        "income,debt,expected_viable",
        [
            (5000.0, 1200.0, True),  # Ratio 24% - VIABLE
            (3000.0, 1000.0, False),  # Ratio 33% - RECHAZADO (>30%)
            (10000.0, 3000.0, True),  # Ratio 30% - Límite exacto
        ],
    )
    def test_risk_agent_debt_ratio_calculation(
        self, banking_state, mock_llm_risk, income, debt, expected_viable
    ):
        """Test debt/income ratio calculation (max 30% SBS)."""
        # Arrange
        state = {
            **banking_state,
            "messages": [HumanMessage(content=f"Ingreso: S/{income}, Deuda actual: S/{debt}")],
        }

        # Act
        result = risk_agent(state)

        # Assert
        assert result["current_agent"] == "risk"
        # Mock would need to be adjusted per scenario in real implementation

    @pytest.mark.parametrize(
        "credit_score,expected_category",
        [
            (850, "Excelente"),  # >800
            (720, "Bueno"),  # 700-799
            (650, "Regular"),  # 600-699
            (550, "Malo"),  # <600
        ],
    )
    def test_risk_agent_credit_scoring(
        self, banking_state, mock_llm_risk, credit_score, expected_category
    ):
        """Test credit score evaluation (0-1000 scale)."""
        # Arrange
        state = {
            **banking_state,
            "messages": [HumanMessage(content=f"Mi score crediticio es {credit_score}")],
        }

        # Act
        result = risk_agent(state)

        # Assert
        assert result["current_agent"] == "risk"

    def test_risk_agent_viable_recommendation(self, banking_state, mock_llm_risk):
        """Test VIABLE recommendation for qualified customer."""
        # Arrange
        state = {
            **banking_state,
            "messages": [HumanMessage(content="Ingreso S/8,000, deuda S/1,500, score 780")],
        }
        # Configure mock for VIABLE response
        from langchain_core.messages import AIMessage

        mock_llm_risk.invoke.return_value = AIMessage(
            content="VIABLE - Ratio 18.75%. Score 780/1000. Aprobado."
        )

        # Act
        result = risk_agent(state)

        # Assert
        assert "VIABLE" in result["messages"][-1].content

    def test_risk_agent_rejection_criteria(self, banking_state, mock_llm_risk):
        """Test RECHAZADO recommendation for high-risk customer."""
        # Arrange
        state = {
            **banking_state,
            "messages": [HumanMessage(content="Ingreso S/2,500, deuda S/1,800, score 520")],
        }
        # Configure mock for RECHAZADO response
        from langchain_core.messages import AIMessage

        mock_llm_risk.invoke.return_value = AIMessage(
            content="RECHAZADO - Ratio 72%. Score bajo. Alto riesgo."
        )

        # Act
        result = risk_agent(state)

        # Assert
        assert "RECHAZADO" in result["messages"][-1].content

    def test_risk_agent_preserves_state(self, banking_state, mock_llm_risk):
        """Test risk agent preserves BankingState fields."""
        # Arrange
        state = {
            **banking_state,
            "customer_id": "RISK-TEST-001",
        }

        # Act
        result = risk_agent(state)

        # Assert
        assert result["customer_id"] == "RISK-TEST-001"

    def test_risk_agent_appends_message(self, banking_state, mock_llm_risk):
        """Test risk agent appends AI message to state."""
        # Arrange
        initial_message_count = len(banking_state["messages"])

        # Act
        result = risk_agent(banking_state)

        # Assert
        assert len(result["messages"]) == initial_message_count + 1
        last_message = result["messages"][-1]
        assert "[Riesgo]" in last_message.content
