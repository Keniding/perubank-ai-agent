"""
Compliance Agent - SBS/BCRP regulatory verification.
Specialized in Peruvian banking regulations.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from src.config.settings import settings
from src.tools.compliance_tools import check_sbs_compliance
from src.prompts.system_prompts import COMPLIANCE_PROMPT


def compliance_agent(state: dict) -> dict:
    """Verify regulatory compliance for banking operations."""
    llm = ChatOpenAI(
        base_url=settings.VLLM_BASE_URL,
        api_key=settings.VLLM_API_KEY,
        model=settings.VLLM_MODEL,
        temperature=settings.DEFAULT_TEMPERATURE,
        max_tokens=settings.MAX_TOKENS,
    )
    
    compliance_result = check_sbs_compliance(
        operation_type="general",
        amount=15000.0,
    )
    
    messages = [
        SystemMessage(content=COMPLIANCE_PROMPT),
        HumanMessage(
            content=f"Resultado compliance: {compliance_result}. "
            f"Consulta: {state['messages'][-1].content}"
        ),
    ]
    
    response = llm.invoke(messages)
    
    return {
        **state,
        "compliance_check": compliance_result,
        "messages": state["messages"] + [AIMessage(content=f"[Compliance] {response.content}")],
        "current_agent": "compliance",
    }
