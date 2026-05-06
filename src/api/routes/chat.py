"""Chat endpoint for the banking agent."""

from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage

from src.models.schemas import ChatRequest, ChatResponse
from src.agents.orchestrator import build_banking_graph

router = APIRouter()

# Compile graph once
graph = None


def get_graph():
    global graph
    if graph is None:
        graph = build_banking_graph()
    return graph


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a banking query through the multi-agent system."""
    try:
        banking_graph = get_graph()
        
        result = await banking_graph.ainvoke({
            "messages": [HumanMessage(content=request.message)],
            "customer_id": request.customer_id,
            "intent": "",
            "risk_score": 0.0,
            "compliance_check": {},
            "recommendation": "",
            "current_agent": "",
        })
        
        # Extract last AI message
        response_text = ""
        for msg in reversed(result["messages"]):
            if hasattr(msg, "content") and msg.content.startswith("["):
                response_text = msg.content
                break
        
        return ChatResponse(
            response=response_text,
            agent_used=result.get("current_agent", "unknown"),
            risk_score=result.get("risk_score"),
            compliance_check=result.get("compliance_check"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
