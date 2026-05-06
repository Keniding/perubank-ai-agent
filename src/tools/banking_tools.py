"""Banking tools for customer data and financial calculations."""

import random

# Mock Database en memoria - Clientes reales para demo
MOCK_CUSTOMERS = {
    "CLI-2026-001": {
        "name": "Juan Pérez García",
        "dni": "12345678",
        "monthly_income": 8500.00,
        "current_debt": 1200.00,
        "credit_score": 745,
        "account_soles": 15420.50,
        "account_dolares": 3200.00,
        "employment_type": "dependiente",
        "years_employed": 3,
        "sector": "servicios",
    },
    "CLI-2026-002": {
        "name": "María Rodriguez Lopez",
        "dni": "87654321",
        "monthly_income": 12000.00,
        "current_debt": 3500.00,
        "credit_score": 820,
        "account_soles": 32500.75,
        "account_dolares": 8500.00,
        "employment_type": "independiente",
        "years_employed": 5,
        "sector": "comercio",
    },
    "CLI-2026-003": {
        "name": "Carlos Gomez Sanchez",
        "dni": "45678912",
        "monthly_income": 5500.00,
        "current_debt": 1800.00,
        "credit_score": 680,
        "account_soles": 8200.30,
        "account_dolares": 1500.00,
        "employment_type": "dependiente",
        "years_employed": 2,
        "sector": "manufactura",
    },
    "CLI-2026-DEMO": {
        "name": "Cliente Demo Hackathon",
        "dni": "99999999",
        "monthly_income": 8500.00,
        "current_debt": 1200.00,
        "credit_score": 745,
        "account_soles": 15420.50,
        "account_dolares": 3200.00,
        "employment_type": "dependiente",
        "years_employed": 3,
        "sector": "tecnologia",
    },
}

MOCK_TRANSACTIONS = {
    "CLI-2026-001": [
        {"date": "2026-05-04", "amount": -250.00, "type": "pago", "desc": "Luz del Sur"},
        {"date": "2026-05-03", "amount": 5000.00, "type": "deposito", "desc": "Nómina"},
        {"date": "2026-05-02", "amount": -1200.00, "type": "transferencia", "desc": "Alquiler"},
        {"date": "2026-05-01", "amount": -85.50, "type": "compra", "desc": "Supermercado"},
        {"date": "2026-04-30", "amount": -120.00, "type": "pago", "desc": "Teléfono"},
    ],
    "CLI-2026-002": [
        {"date": "2026-05-05", "amount": 8000.00, "type": "deposito", "desc": "Venta comercio"},
        {"date": "2026-05-03", "amount": -2500.00, "type": "pago", "desc": "Proveedor"},
        {
            "date": "2026-05-01",
            "amount": -450.00,
            "type": "transferencia",
            "desc": "Alquiler local",
        },
        {"date": "2026-04-29", "amount": 6500.00, "type": "deposito", "desc": "Venta comercio"},
    ],
}


def check_customer_balance(customer_id: str) -> dict:
    """
    Consulta saldo y perfil del cliente.

    Args:
        customer_id: ID del cliente (ej: CLI-2026-001)

    Returns:
        Dict con balance, transacciones, scoring y perfil
    """
    if customer_id not in MOCK_CUSTOMERS:
        # Cliente nuevo - generar perfil aleatorio para testing
        return _generate_random_customer(customer_id)

    customer = MOCK_CUSTOMERS[customer_id]
    transactions = MOCK_TRANSACTIONS.get(customer_id, [])

    return {
        "customer_id": customer_id,
        "name": customer["name"],
        "balance_soles": customer["account_soles"],
        "balance_dolares": customer["account_dolares"],
        "last_transactions": transactions[:5],  # Últimas 5 transacciones
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
    max_debt_ratio_sbs = 0.30  # 30% según SBS

    # Capacidad mensual disponible
    max_monthly_debt = monthly_income * max_debt_ratio_sbs
    available_capacity = max_monthly_debt - existing_debt

    # TEA (Tasa Efectiva Anual) promedio mercado peruano 2026: 18%
    # Fuente: SBS - Tasa promedio préstamos personales
    tea = 0.18

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

    return {
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
        "calculation_note": "TEA 18% (promedio mercado peruano SBS 2026)",
    }


def _generate_random_customer(customer_id: str) -> dict:
    """
    Genera perfil aleatorio para clientes nuevos (testing/demo).

    Args:
        customer_id: ID del cliente a generar

    Returns:
        Dict con perfil aleatorio realista
    """
    # Rangos de ingreso realistas en Perú
    income_ranges = [3000, 4500, 5500, 8000, 10000, 12000, 15000]
    income = random.choice(income_ranges)

    # Deuda proporcional al ingreso (10-40%)
    debt_ratio = random.uniform(0.1, 0.4)
    debt = round(income * debt_ratio, 2)

    # Score crediticio realista
    score = random.randint(550, 850)

    return {
        "customer_id": customer_id,
        "name": f"Cliente {customer_id[-4:]}",
        "balance_soles": round(random.uniform(1000, 50000), 2),
        "balance_dolares": round(random.uniform(500, 10000), 2),
        "last_transactions": [],
        "credit_score": score,
        "monthly_income": income,
        "current_debt": debt,
        "employment_type": random.choice(["dependiente", "independiente"]),
        "years_employed": random.randint(1, 10),
        "sector": random.choice(["servicios", "comercio", "manufactura", "tecnologia"]),
    }
