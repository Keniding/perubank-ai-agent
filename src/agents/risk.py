"""
Risk Agent - Credit scoring and risk assessment.
Aligned with SBS regulations for the Peruvian market.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from src.config.settings import settings
from src.tools.banking_tools import check_customer_balance, calculate_credit_capacity
from src.prompts.system_prompts import RISK_PROMPT


def risk_agent(state: dict) -> dict:
    """Evaluate credit risk and scoring."""
    llm = ChatOpenAI(
        base_url=settings.VLLM_BASE_URL,
        api_key=settings.VLLM_API_KEY,
        model=settings.VLLM_MODEL,
        temperature=settings.DEFAULT_TEMPERATURE,
        max_tokens=settings.MAX_TOKENS,
    )
    
    customer_data = check_customer_balance(state["customer_id"])
    credit_capacity = calculate_credit_capacity(
        monthly_income=customer_data["monthly_income"],
        existing_debt=1200.0,
    )
    
    messages = [
        SystemMessage(content=RISK_PROMPT),
        HumanMessage(
            content=f"Datos cliente: {customer_data}\n"
            f"Capacidad crediticia: {credit_capacity}\n"
            f"Consulta: {state['messages'][-1].content}"
        ),
    ]
    
    response = llm.invoke(messages)
    
    return {
        **state,
        "risk_score": customer_data["credit_score"] / 1000,
        "messages": state["messages"] + [AIMessage(content=f"[Riesgo] {response.content}")],
        "current_agent": "risk",
    }
