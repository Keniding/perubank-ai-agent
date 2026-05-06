"""Fraud detection tools for transaction analysis."""


def detect_fraud_patterns(customer_id: str, transaction_amount: float) -> dict:
    """Analyze transaction patterns for fraud indicators."""
    return {
        "customer_id": customer_id,
        "transaction_amount": transaction_amount,
        "risk_score": 0.15,
        "anomalies_detected": [],
        "checks": {
            "velocity_check": "PASS",
            "geo_check": "PASS",
            "device_fingerprint": "KNOWN",
            "amount_deviation": "NORMAL",
            "time_pattern": "NORMAL",
        },
        "recommendation": "APPROVE",
        "confidence": 0.92,
    }
