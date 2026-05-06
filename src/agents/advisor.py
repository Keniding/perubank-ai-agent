"""
Advisor Agent - Personalized financial recommendations.
Contextualizes advice for the Peruvian market.
"""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.config.settings import settings
from src.prompts.system_prompts import ADVISOR_PROMPT
from src.tools.banking_tools import check_customer_balance


def advisor_agent(state: dict) -> dict:
    """Provide personalized financial advice."""
    llm = ChatOpenAI(
        base_url=settings.VLLM_BASE_URL,
        api_key=settings.VLLM_API_KEY,
        model=settings.VLLM_MODEL,
        temperature=0.3,
        max_tokens=settings.MAX_TOKENS,
    )

    customer_data = check_customer_balance(state["customer_id"])

    messages = [
        SystemMessage(content=ADVISOR_PROMPT),
        HumanMessage(
            content=f"Perfil del cliente: {customer_data}\n"
            f"Consulta: {state['messages'][-1].content}"
        ),
    ]

    response = llm.invoke(messages)

    return {
        **state,
        "recommendation": response.content,
        "messages": state["messages"] + [AIMessage(content=f"[Asesor] {response.content}")],
        "current_agent": "advisor",
    }
