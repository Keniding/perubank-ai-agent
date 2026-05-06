"""Banking tools for customer data and financial calculations."""


def check_customer_balance(customer_id: str) -> dict:
    """Query customer balance and recent transactions."""
    # TODO: Connect to actual core banking system
    return {
        "customer_id": customer_id,
        "balance_soles": 15420.50,
        "balance_dolares": 3200.00,
        "last_transactions": [
            {"date": "2026-05-04", "amount": -250.00, "desc": "Pago servicios"},
            {"date": "2026-05-03", "amount": 5000.00, "desc": "Deposito nomina"},
            {"date": "2026-05-02", "amount": -1200.00, "desc": "Transferencia"},
        ],
        "credit_score": 745,
        "monthly_income": 8500.00,
        "employer": "Tech Corp SAC",
        "account_age_months": 36,
    }


def calculate_credit_capacity(monthly_income: float, existing_debt: float) -> dict:
    """Calculate credit capacity per SBS regulations."""
    max_debt_ratio = 0.30  # SBS maximum debt-to-income ratio
    available_capacity = (monthly_income * max_debt_ratio) - existing_debt

    return {
        "monthly_income": monthly_income,
        "existing_monthly_debt": existing_debt,
        "available_monthly_capacity": round(available_capacity, 2),
        "max_loan_12_months": round(available_capacity * 12 * 0.85, 2),
        "max_loan_24_months": round(available_capacity * 24 * 0.75, 2),
        "max_loan_36_months": round(available_capacity * 36 * 0.65, 2),
        "debt_ratio_current": round(existing_debt / monthly_income, 4),
        "debt_ratio_max": max_debt_ratio,
        "compliant_sbs": (existing_debt / monthly_income) < max_debt_ratio,
    }
