"""
Fraud Detection Agent - Real-time transaction analysis.
Detects suspicious patterns and recommends actions.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from src.config.settings import settings
from src.tools.fraud_tools import detect_fraud_patterns
from src.prompts.system_prompts import FRAUD_PROMPT


def fraud_agent(state: dict) -> dict:
    """Detect fraudulent activity in transactions."""
    llm = ChatOpenAI(
        base_url=settings.VLLM_BASE_URL,
        api_key=settings.VLLM_API_KEY,
        model=settings.VLLM_MODEL,
        temperature=0.0,
        max_tokens=settings.MAX_TOKENS,
    )
    
    fraud_result = detect_fraud_patterns(
        customer_id=state["customer_id"],
        transaction_amount=5000.0,
    )
    
    messages = [
        SystemMessage(content=FRAUD_PROMPT),
        HumanMessage(
            content=f"AnÃ¡lisis de fraude: {fraud_result}\n"
            f"Consulta: {state['messages'][-1].content}"
        ),
    ]
    
    response = llm.invoke(messages)
    
    return {
        **state,
        "messages": state["messages"] + [AIMessage(content=f"[Anti-Fraude] {response.content}")],
        "current_agent": "fraud",
    }
