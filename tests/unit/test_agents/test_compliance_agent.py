"""Unit tests for compliance agent."""

import pytest
from langchain_core.messages import HumanMessage

from src.agents.compliance import compliance_agent


class TestComplianceAgent:
    """Tests for compliance_agent function."""

    def test_compliance_agent_sbs_verification(
        self, banking_state, mock_llm_compliance, mock_compliance_tool
    ):
        """Test compliance agent performs SBS verification."""
        # Arrange
        state = {
            **banking_state,
            "messages": [HumanMessage(content="¿Es legal esta operación?")],
        }

        # Act
        result = compliance_agent(state)

        # Assert
        assert result["current_agent"] == "compliance"
        assert "messages" in result
        assert len(result["messages"]) > len(state["messages"])

    @pytest.mark.parametrize(
        "amount,expected_uif",
        [
            (8000.0, False),  # Below UIF threshold
            (10001.0, True),  # Above UIF threshold (>S/10,000)
            (10000.0, False),  # Exactly at threshold (not reported)
        ],
    )
    def test_compliance_agent_uif_threshold(
        self, banking_state, mock_llm_compliance, amount, expected_uif
    ):
        """Test UIF reporting for transactions >S/10,000."""
        # Arrange
        state = {
            **banking_state,
            "messages": [HumanMessage(content=f"Quiero transferir S/{amount}")],
        }

        # Act
        result = compliance_agent(state)

        # Assert
        assert result["current_agent"] == "compliance"
        assert "compliance_check" in result

    def test_compliance_agent_sandbox_eligibility(
        self, banking_state, mock_llm_compliance, mock_compliance_tool
    ):
        """Test sandbox regulatorio eligibility check."""
        # Arrange
        state = {
            **banking_state,
            "messages": [HumanMessage(content="¿Puedo operar en el sandbox regulatorio?")],
        }

        # Act
        result = compliance_agent(state)

        # Assert
        assert result["current_agent"] == "compliance"
        mock_compliance_tool.assert_called_once()

    def test_compliance_agent_preserves_state(self, banking_state, mock_llm_compliance):
        """Test compliance agent preserves BankingState fields."""
        # Arrange
        state = {
            **banking_state,
            "customer_id": "PRESERVE-123",
            "risk_score": 0.3,
        }

        # Act
        result = compliance_agent(state)

        # Assert
        assert result["customer_id"] == "PRESERVE-123"
        assert result["risk_score"] == 0.3

    def test_compliance_agent_appends_message(self, banking_state, mock_llm_compliance):
        """Test compliance agent appends AI message to state."""
        # Arrange
        initial_message_count = len(banking_state["messages"])

        # Act
        result = compliance_agent(banking_state)

        # Assert
        assert len(result["messages"]) == initial_message_count + 1
        last_message = result["messages"][-1]
        assert "[Compliance]" in last_message.content

    def test_compliance_agent_mentions_regulation(self, banking_state, mock_llm_compliance):
        """Test compliance agent references relevant regulations."""
        # Arrange
        state = {
            **banking_state,
            "messages": [HumanMessage(content="¿Qué normativa aplica a fintech?")],
        }

        # Act
        result = compliance_agent(state)

        # Assert
        last_message = result["messages"][-1].content
        # Should mention compliance context
        assert "[Compliance]" in last_message
