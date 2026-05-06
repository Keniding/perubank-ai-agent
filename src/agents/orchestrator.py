"""
Orchestrator Agent - Routes queries to specialized agents.
Uses LangGraph state machine for workflow management.
"""

from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

from src.config.settings import settings
from src.agents.compliance import compliance_agent
from src.agents.risk import risk_agent
from src.agents.advisor import advisor_agent
from src.agents.fraud import fraud_agent
from src.prompts.system_prompts import ORCHESTRATOR_PROMPT


class BankingState(TypedDict):
    messages: Annotated[list, add_messages]
    customer_id: str
    intent: str
    risk_score: float
    compliance_check: dict
    recommendation: str
    current_agent: str


def get_llm() -> ChatOpenAI:
    """Initialize LLM connected to vLLM on AMD MI300X."""
    return ChatOpenAI(
        base_url=settings.VLLM_BASE_URL,
        api_key=settings.VLLM_API_KEY,
        model=settings.VLLM_MODEL,
        temperature=settings.DEFAULT_TEMPERATURE,
        max_tokens=settings.MAX_TOKENS,
    )


def orchestrator_node(state: BankingState) -> BankingState:
    """Orchestrator: analyzes query and routes to appropriate agent."""
    llm = get_llm()
    messages = [SystemMessage(content=ORCHESTRATOR_PROMPT)] + state["messages"]
    response = llm.invoke(messages)
    
    intent = response.content.strip().lower()
    valid_intents = ["compliance", "risk", "advisor", "fraud", "end"]
    if intent not in valid_intents:
        intent = "advisor"
    
    return {**state, "intent": intent, "current_agent": "orchestrator"}


def route_decision(state: BankingState) -> Literal["compliance", "risk", "advisor", "fraud", "end"]:
    """Route to the appropriate agent based on orchestrator decision."""
    return state.get("intent", "advisor")


def build_banking_graph():
    """Build and compile the multi-agent banking graph."""
    workflow = StateGraph(BankingState)
    
    # Add nodes
    workflow.add_node("orchestrator", orchestrator_node)
    workflow.add_node("compliance", compliance_agent)
    workflow.add_node("risk", risk_agent)
    workflow.add_node("advisor", advisor_agent)
    workflow.add_node("fraud", fraud_agent)
    
    # Set entry point
    workflow.set_entry_point("orchestrator")
    
    # Conditional routing
    workflow.add_conditional_edges(
        "orchestrator",
        route_decision,
        {
            "compliance": "compliance",
            "risk": "risk",
            "advisor": "advisor",
            "fraud": "fraud",
            "end": END,
        },
    )
    
    # All agents terminate after execution
    workflow.add_edge("compliance", END)
    workflow.add_edge("risk", END)
    workflow.add_edge("advisor", END)
    workflow.add_edge("fraud", END)
    
    return workflow.compile()
