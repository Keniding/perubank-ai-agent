"""Integration tests for the agent graph."""

import pytest


class TestBankingGraph:
    @pytest.mark.skip(reason="Requires vLLM server running")
    def test_graph_compilation(self):
        from src.agents.orchestrator import build_banking_graph
        graph = build_banking_graph()
        assert graph is not None

    @pytest.mark.skip(reason="Requires vLLM server running")
    async def test_advisor_flow(self, sample_state):
        from src.agents.orchestrator import build_banking_graph
        graph = build_banking_graph()
        result = await graph.ainvoke(sample_state)
        assert result["current_agent"] != ""
