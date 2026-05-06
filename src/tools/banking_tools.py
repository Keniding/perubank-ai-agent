"""Banking tools for customer data and financial calculations."""

import logging
import random
import uuid
from datetime import datetime

from src.db.sync_wrapper import (
    get_config,
    get_customer,
    get_customer_transactions,
    save_credit_calculation,
)

logger = logging.getLogger(__name__)

# Default configurations (fallback if MongoDB config not found)
DEFAULT_BANKING_CONFIG = {
    "max_debt_ratio_sbs": 0.30,  # 30% según SBS
    "tea_default": 0.18,  # 18% TEA promedio mercado peruano
    "income_ranges": [3000, 4500, 5500, 8000, 10000, 12000, 15000],
    "credit_score_min": 550,
    "credit_score_max": 850,
    "balance_soles_min": 1000,
    "balance_soles_max": 50000,
    "balance_dolares_min": 500,
    "balance_dolares_max": 10000,
}


def _get_banking_config() -> dict:
    """
    Get banking configuration from MongoDB or use defaults.

    Returns:
        Banking configuration dict
    """
    config = get_config("banking_config")
    if config:
        return config
    logger.warning("Banking config not found in MongoDB, using defaults")
    return DEFAULT_BANKING_CONFIG


def check_customer_balance(customer_id: str) -> dict:
    """
    Consulta saldo y perfil del cliente desde MongoDB.

    Args:
        customer_id: ID del cliente (ej: CLI-2026-001)

    Returns:
        Dict con balance, transacciones, scoring y perfil
    """
    # Try to get customer from MongoDB
    customer = get_customer(customer_id)

    if not customer:
        # Cliente nuevo - generar perfil aleatorio para testing
        logger.info(f"Customer {customer_id} not found, generating random profile")
        return _generate_random_customer(customer_id)

    # Get recent transactions from MongoDB
    transactions = get_customer_transactions(customer_id, limit=5)

    # Format transactions for response
    formatted_transactions = []
    for txn in transactions:
        raw_date = txn.get("date")
        date_str = raw_date.isoformat() if isinstance(raw_date, datetime) else raw_date
        formatted_transactions.append(
            {
                "date": date_str,
                "amount": txn.get("amount"),
                "type": txn.get("type"),
                "desc": txn.get("description", ""),
            }
        )

    return {
        "customer_id": customer_id,
        "name": customer["name"],
        "balance_soles": customer["account_soles"],
        "balance_dolares": customer["account_dolares"],
        "last_transactions": formatted_transactions,
        "credit_score": customer["credit_score"],
        "monthly_income": customer["monthly_income"],
        "current_debt": customer["current_debt"],
        "employment_type": customer["employment_type"],
        "years_employed": customer["years_employed"],
        "sector": customer["sector"],
    }


def calculate_credit_capacity(monthly_income: float, existing_debt: float) -> dict:
    """
    Calcula capacidad crediticia según normativa SBS peruana.

    Regla SBS: Ratio deuda/ingreso máximo 30%
    Calcula montos máximos de préstamo usando TEA real del mercado peruano.

    Args:
        monthly_income: Ingreso mensual del cliente
        existing_debt: Deuda mensual actual

    Returns:
        Dict con capacidad disponible y montos máximos por plazo
    """
    # Get configuration from MongoDB
    config = _get_banking_config()
    max_debt_ratio_sbs = config.get("max_debt_ratio_sbs", 0.30)
    tea = config.get("tea_default", 0.18)

    # Capacidad mensual disponible
    max_monthly_debt = monthly_income * max_debt_ratio_sbs
    available_capacity = max_monthly_debt - existing_debt

    def calculate_max_loan(months: int, available_monthly: float) -> float:
        """
        Calcula monto máximo del préstamo dado plazo y cuota disponible.

        Usa fórmula francesa de amortización:
        P = C * [(1 + i)^n - 1] / [i * (1 + i)^n]

        Donde:
        - P = principal (monto del préstamo)
        - C = cuota mensual
        - i = tasa mensual efectiva
        - n = número de meses
        """
        if available_monthly <= 0:
            return 0.0

        # Convertir TEA a tasa mensual efectiva
        monthly_rate = (1 + tea) ** (1 / 12) - 1

        # Fórmula de valor presente
        denominator = monthly_rate * ((1 + monthly_rate) ** months)
        numerator = ((1 + monthly_rate) ** months) - 1

        if denominator == 0:
            return 0.0

        max_principal = available_monthly * (numerator / denominator)
        return round(max_principal, 2)

    # Calcular máximos por plazo común en Perú
    max_loan_12m = calculate_max_loan(12, available_capacity)
    max_loan_24m = calculate_max_loan(24, available_capacity)
    max_loan_36m = calculate_max_loan(36, available_capacity)

    # Ratio actual
    current_ratio = existing_debt / monthly_income if monthly_income > 0 else 1.0

    result = {
        "monthly_income": monthly_income,
        "existing_monthly_debt": existing_debt,
        "available_monthly_capacity": round(available_capacity, 2),
        "max_loan_12_months": max_loan_12m,
        "max_loan_24_months": max_loan_24m,
        "max_loan_36_months": max_loan_36m,
        "debt_ratio_current": round(current_ratio, 3),
        "debt_ratio_max_sbs": max_debt_ratio_sbs,
        "compliant_sbs": current_ratio < max_debt_ratio_sbs,
        "tea_assumed": tea,
        "calculation_note": f"TEA {tea:.0%} (promedio mercado peruano SBS 2026)",
    }

    # Save calculation to MongoDB for audit trail
    try:
        calc_data = {
            "calculation_id": str(uuid.uuid4()),
            "customer_id": "unknown",  # Will be set by caller if available
            **result,
            "created_at": datetime.now(),
        }
        save_credit_calculation(calc_data)
    except Exception as e:
        logger.error(f"Failed to save credit calculation: {e}")

    return result


def _generate_random_customer(customer_id: str) -> dict:
    """
    Genera perfil aleatorio para clientes nuevos (testing/demo).

    Args:
        customer_id: ID del cliente a generar

    Returns:
        Dict con perfil aleatorio realista
    """
    config = _get_banking_config()

    # Rangos de ingreso realistas en Perú
    income_ranges = config.get("income_ranges", [3000, 4500, 5500, 8000, 10000, 12000, 15000])
    income = random.choice(income_ranges)

    # Deuda proporcional al ingreso (10-40%)
    debt_ratio = random.uniform(0.1, 0.4)
    debt = round(income * debt_ratio, 2)

    # Score crediticio realista
    score_min = config.get("credit_score_min", 550)
    score_max = config.get("credit_score_max", 850)
    score = random.randint(score_min, score_max)

    # Balance ranges
    balance_soles_min = config.get("balance_soles_min", 1000)
    balance_soles_max = config.get("balance_soles_max", 50000)
    balance_dolares_min = config.get("balance_dolares_min", 500)
    balance_dolares_max = config.get("balance_dolares_max", 10000)

    return {
        "customer_id": customer_id,
        "name": f"Cliente {customer_id[-4:]}",
        "balance_soles": round(random.uniform(balance_soles_min, balance_soles_max), 2),
        "balance_dolares": round(random.uniform(balance_dolares_min, balance_dolares_max), 2),
        "last_transactions": [],
        "credit_score": score,
        "monthly_income": income,
        "current_debt": debt,
        "employment_type": random.choice(["dependiente", "independiente"]),
        "years_employed": random.randint(1, 10),
        "sector": random.choice(["servicios", "comercio", "manufactura", "tecnologia"]),
    }
