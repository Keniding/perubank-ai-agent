"""Fraud detection tools for transaction analysis."""

import random
from datetime import datetime

# Configuración de detección de fraude
FRAUD_CONFIG = {
    "max_transactions_per_hour": 10,  # Velocidad máxima normal
    "max_transaction_amount_normal": 15000.00,  # S/ 15,000 monto normal máximo
    "suspicious_countries": ["VE", "NG", "PK", "RU"],  # ISO códigos países alto riesgo
    "device_change_risk_increase": 0.2,  # Incremento por dispositivo desconocido
    "unusual_hour_start": 23,  # 11 PM
    "unusual_hour_end": 6,  # 6 AM
    "high_amount_multiplier": 2.0,  # 2x el monto normal = alto riesgo
}


def detect_fraud_patterns(
    customer_id: str,
    transaction_amount: float,
    location_country: str = "PE",
    device_fingerprint: str = "known",
    hour_of_day: int | None = None,
) -> dict:
    """
    Analiza patrones de fraude en transacción.

    Implementa algoritmos de detección:
    - Velocity checking (frecuencia transacciones)
    - Geographic risk scoring
    - Device fingerprinting
    - Amount deviation analysis
    - Time pattern analysis

    Args:
        customer_id: ID del cliente
        transaction_amount: Monto de la transacción en soles
        location_country: Código país ISO (default: PE)
        device_fingerprint: "known" | "unknown"
        hour_of_day: Hora de la transacción (0-23), None = hora actual

    Returns:
        Dict con scoring de riesgo y recomendación
    """
    if hour_of_day is None:
        hour_of_day = datetime.now().hour

    risk_score = 0.0
    anomalies: list[str] = []
    checks = {}

    # 1. Velocity Check (frecuencia de transacciones)
    # Simula consulta a historial reciente
    # En producción: query a database de últimas transacciones
    transactions_last_hour = random.randint(0, 15)

    if transactions_last_hour > FRAUD_CONFIG["max_transactions_per_hour"]:
        risk_score += 0.3
        anomalies.append("velocity_spike")
        checks["velocity_check"] = "FAIL"
        checks["transactions_last_hour"] = transactions_last_hour
    else:
        checks["velocity_check"] = "PASS"
        checks["transactions_last_hour"] = transactions_last_hour

    # 2. Amount Deviation Analysis
    normal_max = FRAUD_CONFIG["max_transaction_amount_normal"]

    if transaction_amount > normal_max:
        # Calcular desviación
        deviation_factor = transaction_amount / normal_max

        # Riesgo proporcional a la desviación (cap at 0.4)
        amount_risk = min(0.25 * deviation_factor, 0.4)
        risk_score += amount_risk

        if deviation_factor > FRAUD_CONFIG["high_amount_multiplier"]:
            anomalies.append("amount_extreme")
            checks["amount_deviation"] = "EXTREME"
        else:
            anomalies.append("amount_high")
            checks["amount_deviation"] = "HIGH"

        checks["deviation_factor"] = round(deviation_factor, 2)
    elif transaction_amount > normal_max * 0.8:
        checks["amount_deviation"] = "ELEVATED"
        checks["deviation_factor"] = round(transaction_amount / normal_max, 2)
    else:
        checks["amount_deviation"] = "NORMAL"

    # 3. Geographic Check
    if location_country != "PE":
        # Transacción desde el extranjero
        risk_score += 0.15
        anomalies.append("foreign_location")

        if location_country in FRAUD_CONFIG["suspicious_countries"]:
            # País de alto riesgo
            risk_score += 0.25
            anomalies.append("high_risk_country")
            checks["geo_check"] = "CRITICAL"
            checks["country"] = location_country
        else:
            checks["geo_check"] = "WARNING"
            checks["country"] = location_country
    else:
        checks["geo_check"] = "PASS"
        checks["country"] = location_country

    # 4. Device Fingerprint Analysis
    if device_fingerprint == "unknown":
        # Dispositivo nuevo/desconocido
        risk_score += FRAUD_CONFIG["device_change_risk_increase"]
        anomalies.append("unknown_device")
        checks["device_fingerprint"] = "UNKNOWN"
    elif device_fingerprint == "suspicious":
        risk_score += 0.3
        anomalies.append("suspicious_device")
        checks["device_fingerprint"] = "SUSPICIOUS"
    else:
        checks["device_fingerprint"] = "KNOWN"

    # 5. Time Pattern Analysis
    unusual_start = FRAUD_CONFIG["unusual_hour_start"]
    unusual_end = FRAUD_CONFIG["unusual_hour_end"]

    # Horario inusual: 11 PM - 6 AM
    if hour_of_day >= unusual_start or hour_of_day < unusual_end:
        risk_score += 0.1
        anomalies.append("unusual_hour")
        checks["time_pattern"] = "UNUSUAL"
        checks["hour"] = hour_of_day
    else:
        checks["time_pattern"] = "NORMAL"
        checks["hour"] = hour_of_day

    # Normalizar risk_score a rango 0.0-1.0
    risk_score = min(risk_score, 1.0)
    risk_score = round(risk_score, 3)

    # Determinar recomendación basada en score
    if risk_score < 0.3:
        recommendation = "APPROVE"
        confidence = 0.92
        action_required = "none"
    elif risk_score < 0.6:
        recommendation = "REVIEW"
        confidence = 0.75
        action_required = "manual_review"
    elif risk_score < 0.8:
        recommendation = "BLOCK"
        confidence = 0.88
        action_required = "block_and_contact"
    else:
        recommendation = "BLOCK"
        confidence = 0.95
        action_required = "block_and_investigate"
        anomalies.append("critical_risk")

    return {
        "customer_id": customer_id,
        "transaction_amount": transaction_amount,
        "risk_score": risk_score,
        "risk_category": _categorize_risk(risk_score),
        "anomalies_detected": anomalies,
        "anomaly_count": len(anomalies),
        "checks": checks,
        "recommendation": recommendation,
        "action_required": action_required,
        "confidence": confidence,
        "timestamp": datetime.now().isoformat(),
        "fraud_detection_version": "1.0",
    }


def _categorize_risk(score: float) -> str:
    """
    Categoriza el riesgo en niveles.

    Args:
        score: Risk score 0.0-1.0

    Returns:
        Categoría de riesgo
    """
    if score < 0.2:
        return "minimal"
    elif score < 0.4:
        return "low"
    elif score < 0.6:
        return "medium"
    elif score < 0.8:
        return "high"
    else:
        return "critical"
