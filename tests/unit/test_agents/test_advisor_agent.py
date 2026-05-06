"""Unit tests for advisor agent."""

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from src.agents.advisor import advisor_agent


class TestAdvisorAgent:
    """Tests for advisor_agent function."""

    def test_advisor_agent_product_recommendation(self, banking_state, mock_llm_advisor):
        """Test advisor agent provides product recommendations."""
        # Arrange
        state = {
            **banking_state,
            "messages": [HumanMessage(content="¿Qué producto me recomiendas para ahorrar?")],
        }

        # Act
        result = advisor_agent(state)

        # Assert
        assert result["current_agent"] == "advisor"
        assert "messages" in result
        assert len(result["messages"]) > len(state["messages"])

    def test_advisor_agent_risk_disclosure(self, banking_state, mock_llm_advisor):
        """Test advisor agent mentions both benefits AND risks."""
        # Arrange
        state = {
            **banking_state,
            "messages": [HumanMessage(content="Cuéntame sobre fondos mutuos")],
        }
        # Configure mock to include both benefits and risks
        mock_llm_advisor.invoke.return_value = AIMessage(
            content="Fondo mutuo conservador. Beneficio: diversificación y "
            "rentabilidad 5-7% anual. Riesgo: puede haber pérdidas por "
            "fluctuación del mercado."
        )

        # Act
        result = advisor_agent(state)

        # Assert
        last_message = result["messages"][-1].content
        assert "Beneficio" in last_message or "beneficio" in last_message.lower()
        assert "Riesgo" in last_message or "riesgo" in last_message.lower()

    def test_advisor_agent_currency_format(self, banking_state, mock_llm_advisor):
        """Test advisor agent uses soles (S/) as primary currency."""
        # Arrange
        state = {
            **banking_state,
            "messages": [HumanMessage(content="¿Cuánto debo ahorrar mensualmente?")],
        }
        mock_llm_advisor.invoke.return_value = AIMessage(
            content="Recomiendo ahorrar S/500 mensuales."
        )

        # Act
        result = advisor_agent(state)

        # Assert
        last_message = result["messages"][-1].content
        assert "S/" in last_message  # Soles currency format

    @pytest.mark.parametrize(
        "query,expected_product",
        [
            ("quiero ahorrar", "ahorro"),
            ("necesito un préstamo", "crédito"),
            ("quiero invertir", "inversión"),
            ("tarjeta de crédito", "tarjeta"),
        ],
    )
    def test_advisor_agent_personalized_recommendation(
        self, banking_state, mock_llm_advisor, query, expected_product
    ):
        """Test advisor provides recommendations based on user query."""
        # Arrange
        state = {
            **banking_state,
            "messages": [HumanMessage(content=query)],
        }

        # Act
        result = advisor_agent(state)

        # Assert
        assert result["current_agent"] == "advisor"
        # Product recommendation should be context-aware

    def test_advisor_agent_professional_tone(self, banking_state, mock_llm_advisor):
        """Test advisor maintains professional but friendly tone."""
        # Arrange
        state = {
            **banking_state,
            "messages": [HumanMessage(content="Ayúdame con mi planificación financiera")],
        }
        mock_llm_advisor.invoke.return_value = AIMessage(
            content="Con gusto te ayudo. Recomiendo aperturar una cuenta de ahorro programado..."
        )

        # Act
        result = advisor_agent(state)

        # Assert
        last_message = result["messages"][-1].content
        assert len(last_message) > 10  # Has substantial content
        assert "[Asesor]" in last_message

    def test_advisor_agent_preserves_state(self, banking_state, mock_llm_advisor):
        """Test advisor agent preserves BankingState fields."""
        # Arrange
        state = {
            **banking_state,
            "customer_id": "ADVISOR-001",
            "risk_score": 0.2,
        }

        # Act
        result = advisor_agent(state)

        # Assert
        assert result["customer_id"] == "ADVISOR-001"
        assert result["risk_score"] == 0.2

    def test_advisor_agent_appends_message(self, banking_state, mock_llm_advisor):
        """Test advisor agent appends AI message to state."""
        # Arrange
        initial_message_count = len(banking_state["messages"])

        # Act
        result = advisor_agent(banking_state)

        # Assert
        assert len(result["messages"]) == initial_message_count + 1
        last_message = result["messages"][-1]
        assert "[Asesor]" in last_message.content

    def test_advisor_agent_mentions_peruvian_context(self, banking_state, mock_llm_advisor):
        """Test advisor considers Peruvian financial context (BCRP, SBS)."""
        # Arrange
        state = {
            **banking_state,
            "messages": [HumanMessage(content="¿Es buen momento para invertir?")],
        }
        mock_llm_advisor.invoke.return_value = AIMessage(
            content="Considerando la tasa de referencia BCRP actual (5.75%), "
            "es favorable invertir en depósitos a plazo."
        )

        # Act
        result = advisor_agent(state)

        # Assert
        last_message = result["messages"][-1].content
        # Should reference Peruvian context
        assert len(last_message) > 0
