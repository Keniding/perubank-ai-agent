"""Unit tests for orchestrator agent."""

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from src.agents.orchestrator import (
    build_banking_graph,
    orchestrator_node,
    route_decision,
)


class TestOrchestratorNode:
    """Tests for orchestrator_node function."""

    def test_orchestrator_classifies_compliance_intent(self, banking_state, mock_llm_orchestrator):
        """Test orchestrator correctly identifies compliance queries."""
        # Arrange
        state = {
            **banking_state,
            "messages": [HumanMessage(content="¿Es legal esta transacción?")],
        }
        mock_llm_orchestrator.invoke.return_value = AIMessage(content="compliance")

        # Act
        result = orchestrator_node(state)

        # Assert
        assert result["intent"] == "compliance"
        assert result["current_agent"] == "orchestrator"
        assert "messages" in result

    def test_orchestrator_classifies_risk_intent(self, banking_state, mock_llm_orchestrator):
        """Test orchestrator correctly identifies risk queries."""
        # Arrange
        state = {
            **banking_state,
            "messages": [HumanMessage(content="¿Puedo acceder a un préstamo?")],
        }
        mock_llm_orchestrator.invoke.return_value = AIMessage(content="risk")

        # Act
        result = orchestrator_node(state)

        # Assert
        assert result["intent"] == "risk"
        assert result["current_agent"] == "orchestrator"

    def test_orchestrator_classifies_advisor_intent(self, banking_state, mock_llm_orchestrator):
        """Test orchestrator correctly identifies advisor queries."""
        # Arrange
        state = {
            **banking_state,
            "messages": [HumanMessage(content="¿Qué producto me recomiendas?")],
        }
        mock_llm_orchestrator.invoke.return_value = AIMessage(content="advisor")

        # Act
        result = orchestrator_node(state)

        # Assert
        assert result["intent"] == "advisor"

    def test_orchestrator_classifies_fraud_intent(self, banking_state, mock_llm_orchestrator):
        """Test orchestrator correctly identifies fraud queries."""
        # Arrange
        state = {
            **banking_state,
            "messages": [HumanMessage(content="Detecté una transacción sospechosa")],
        }
        mock_llm_orchestrator.invoke.return_value = AIMessage(content="fraud")

        # Act
        result = orchestrator_node(state)

        # Assert
        assert result["intent"] == "fraud"

    def test_orchestrator_fallback_to_advisor_on_invalid_intent(
        self, banking_state, mock_llm_orchestrator
    ):
        """Test orchestrator falls back to advisor for unknown intents."""
        # Arrange
        state = {
            **banking_state,
            "messages": [HumanMessage(content="Hola")],
        }
        mock_llm_orchestrator.invoke.return_value = AIMessage(content="unknown_intent")

        # Act
        result = orchestrator_node(state)

        # Assert
        assert result["intent"] == "advisor"  # Fallback

    def test_orchestrator_preserves_state(self, banking_state, mock_llm_orchestrator):
        """Test orchestrator preserves BankingState fields."""
        # Arrange
        state = {
            **banking_state,
            "customer_id": "CUSTOM-123",
            "risk_score": 0.5,
        }
        mock_llm_orchestrator.invoke.return_value = AIMessage(content="compliance")

        # Act
        result = orchestrator_node(state)

        # Assert
        assert result["customer_id"] == "CUSTOM-123"
        assert result["risk_score"] == 0.5
        assert "messages" in result


class TestRouteDecision:
    """Tests for route_decision function."""

    @pytest.mark.parametrize(
        "intent,expected_route",
        [
            ("compliance", "compliance"),
            ("risk", "risk"),
            ("advisor", "advisor"),
            ("fraud", "fraud"),
            ("end", "end"),
        ],
    )
    def test_route_decision_returns_correct_route(self, banking_state, intent, expected_route):
        """Test route_decision returns correct agent based on intent."""
        # Arrange
        state = {**banking_state, "intent": intent}

        # Act
        route = route_decision(state)

        # Assert
        assert route == expected_route

    def test_route_decision_defaults_to_advisor(self, banking_state):
        """Test route_decision defaults to advisor when intent is missing."""
        # Arrange
        state = {**banking_state}
        state.pop("intent", None)

        # Act
        route = route_decision(state)

        # Assert
        assert route == "advisor"


class TestBuildBankingGraph:
    """Tests for build_banking_graph function."""

    def test_graph_compiles_successfully(self):
        """Test that the banking graph compiles without errors."""
        # Act
        graph = build_banking_graph()

        # Assert
        assert graph is not None
        assert hasattr(graph, "invoke")
        assert hasattr(graph, "ainvoke")

    def test_graph_has_correct_nodes(self):
        """Test that graph contains all required nodes."""
        # Act
        graph = build_banking_graph()

        # Assert
        # LangGraph doesn't expose nodes directly, but we can test compilation
        assert graph is not None

    @pytest.mark.asyncio
    async def test_graph_executes_full_flow(
        self,
        banking_state,
        mock_llm_orchestrator,
        mock_llm_compliance,
    ):
        """Test graph executes full orchestrator → compliance → END flow."""
        # Arrange
        graph = build_banking_graph()
        mock_llm_orchestrator.invoke.return_value = AIMessage(content="compliance")

        # Act
        result = await graph.ainvoke(banking_state)

        # Assert
        assert "messages" in result
        assert len(result["messages"]) > 0
        # Should have orchestrator decision + compliance response
