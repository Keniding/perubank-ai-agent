# Feature Spec: Real Tools Implementation

**Status**: In Progress
**Created**: 2026-05-06
**Author**: LEAD Team
**Branch**: feature/agents-setup
**Priority**: HIGH (Prioridad 1 del roadmap)

## Overview

Reemplazar implementaciones mock de tools con lógica real basada en regulación bancaria peruana y algoritmos de scoring financiero.

## Motivation

Actualmente los tools retornan datos hardcoded, lo que limita:
- Demo realista del sistema
- Validación de reglas SBS
- Cálculos financieros precisos
- Detección efectiva de fraude

El MVP requiere tools funcionales para demostrar valor business real.

## Scope

### In Scope

1. **banking_tools.py - Lógica Real**
   - `check_customer_balance()`: Simular con datos realistas
   - `calculate_credit_capacity()`: Implementar regla SBS 30% deuda/ingreso
   - Cálculo de cuotas con TEA (Tasa Efectiva Anual)
   - Scoring crediticio 0-1000 (Sentinel/Equifax Perú)

2. **compliance_tools.py - Reglas SBS**
   - `check_sbs_compliance()`: Validación UIF >S/10,000
   - Verificación sandbox Res. SBS 4142-2025
   - Clasificación riesgo operación (low/medium/high)
   - Normativas aplicables por tipo de operación

3. **fraud_tools.py - Algoritmos Detección**
   - `detect_fraud_patterns()`: Velocity checking
   - Análisis geográfico (Perú vs extranjero)
   - Device fingerprinting (known/unknown)
   - Amount deviation detection
   - Risk scoring 0.0-1.0

4. **Mock Database**
   - Estructura en memoria para clientes
   - Transacciones históricas
   - Profiles de clientes (ingresos, deudas, scoring)

### Out of Scope

- Integración con APIs reales de bancos (fuera del MVP)
- Base de datos persistente (PostgreSQL en fase 2)
- OCR real de documentos (otra feature)
- Conexión real con RENIEC/SBS

## Technical Design

### 1. Banking Tools - Implementación Real

```python
# src/tools/banking_tools.py

from typing import Dict, List
from datetime import datetime, timedelta
import random

# Mock Database en memoria
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
}

MOCK_TRANSACTIONS = {
    "CLI-2026-001": [
        {"date": "2026-05-04", "amount": -250.00, "type": "pago", "desc": "Luz del Sur"},
        {"date": "2026-05-03", "amount": 5000.00, "type": "deposito", "desc": "Nómina"},
        {"date": "2026-05-02", "amount": -1200.00, "type": "transferencia", "desc": "Alquiler"},
        {"date": "2026-05-01", "amount": -85.50, "type": "compra", "desc": "Supermercado"},
    ],
}


def check_customer_balance(customer_id: str) -> Dict:
    """
    Consulta saldo y perfil del cliente.
    Retorna datos realistas del mock database.
    """
    if customer_id not in MOCK_CUSTOMERS:
        # Cliente nuevo - generar perfil aleatorio
        return _generate_random_customer(customer_id)

    customer = MOCK_CUSTOMERS[customer_id]
    transactions = MOCK_TRANSACTIONS.get(customer_id, [])

    return {
        "customer_id": customer_id,
        "name": customer["name"],
        "balance_soles": customer["account_soles"],
        "balance_dolares": customer["account_dolares"],
        "last_transactions": transactions[:5],  # Últimas 5
        "credit_score": customer["credit_score"],
        "monthly_income": customer["monthly_income"],
        "current_debt": customer["current_debt"],
        "employment_type": customer["employment_type"],
    }


def calculate_credit_capacity(monthly_income: float, existing_debt: float) -> Dict:
    """
    Calcula capacidad crediticia según normativa SBS peruana.

    Regla SBS: Ratio deuda/ingreso máximo 30%
    """
    MAX_DEBT_RATIO_SBS = 0.30  # 30% según SBS

    # Capacidad mensual disponible
    max_monthly_debt = monthly_income * MAX_DEBT_RATIO_SBS
    available_capacity = max_monthly_debt - existing_debt

    # Proyección de préstamos según plazo
    # TEA promedio Perú: 16-22% (usamos 18%)
    TEA = 0.18

    def calculate_max_loan(months: int, available_monthly: float) -> float:
        """Calcula monto máximo del préstamo dado plazo y cuota disponible."""
        if available_monthly <= 0:
            return 0.0

        # Fórmula: P = C * [(1 + i)^n - 1] / [i * (1 + i)^n]
        # Donde: P = principal, C = cuota, i = tasa mensual, n = meses
        monthly_rate = (1 + TEA) ** (1/12) - 1

        denominator = monthly_rate * ((1 + monthly_rate) ** months)
        numerator = ((1 + monthly_rate) ** months) - 1

        if denominator == 0:
            return 0.0

        max_principal = available_monthly * (numerator / denominator)
        return round(max_principal, 2)

    # Calcular máximos por plazo
    max_loan_12m = calculate_max_loan(12, available_capacity)
    max_loan_24m = calculate_max_loan(24, available_capacity)
    max_loan_36m = calculate_max_loan(36, available_capacity)

    current_ratio = existing_debt / monthly_income if monthly_income > 0 else 1.0

    return {
        "monthly_income": monthly_income,
        "existing_monthly_debt": existing_debt,
        "available_monthly_capacity": round(available_capacity, 2),
        "max_loan_12_months": max_loan_12m,
        "max_loan_24_months": max_loan_24m,
        "max_loan_36_months": max_loan_36m,
        "debt_ratio_current": round(current_ratio, 3),
        "debt_ratio_max_sbs": MAX_DEBT_RATIO_SBS,
        "compliant_sbs": current_ratio < MAX_DEBT_RATIO_SBS,
        "tea_assumed": TEA,
    }


def _generate_random_customer(customer_id: str) -> Dict:
    """Genera perfil aleatorio para clientes nuevos (testing)."""
    income_ranges = [3000, 5000, 8000, 12000, 15000]
    income = random.choice(income_ranges)

    return {
        "customer_id": customer_id,
        "name": f"Cliente {customer_id[-4:]}",
        "balance_soles": round(random.uniform(1000, 50000), 2),
        "balance_dolares": round(random.uniform(500, 10000), 2),
        "last_transactions": [],
        "credit_score": random.randint(550, 850),
        "monthly_income": income,
        "current_debt": round(income * random.uniform(0.1, 0.4), 2),
        "employment_type": random.choice(["dependiente", "independiente"]),
    }
```

### 2. Compliance Tools - Reglas SBS

```python
# src/tools/compliance_tools.py

from typing import Dict, List
from datetime import datetime


# Normativas vigentes Perú 2026
SBS_REGULATIONS = {
    "uif_threshold": 10000.00,  # S/ 10,000 - Reporte UIF obligatorio
    "sandbox_max_amount": 100000.00,  # S/ 100,000 - Límite sandbox
    "sandbox_max_users": 10000,  # 10,000 usuarios - Res. SBS 4142-2025
    "high_risk_threshold": 50000.00,  # S/ 50,000 - Alto riesgo
}

APPLICABLE_LAWS = {
    "fintech": "Ley Fintech 2023 - Crowdfunding, PSP, billeteras digitales",
    "ai": "Ley 31814 (2026) - Regulación IA en Perú",
    "sandbox": "Res. SBS 4142-2025 - Sandbox regulatorio expandido",
    "uif": "Normativa UIF - Reporte operaciones sospechosas",
    "open_finance": "Open Finance Roadmap SBS (Feb 2026)",
    "enia": "ENIA 2026-2030 - Estrategia Nacional IA",
}


def check_sbs_compliance(operation_type: str, amount: float) -> Dict:
    """
    Verifica cumplimiento normativo SBS para operación bancaria.

    Args:
        operation_type: Tipo de operación (transfer, loan, investment, etc.)
        amount: Monto en soles

    Returns:
        Dict con resultados de compliance
    """
    # Determinar si requiere reporte UIF
    requires_uif = amount > SBS_REGULATIONS["uif_threshold"]

    # Verificar elegibilidad sandbox
    sandbox_eligible = (
        amount <= SBS_REGULATIONS["sandbox_max_amount"] and
        operation_type in ["transfer", "loan", "investment"]
    )

    # Clasificar nivel de riesgo
    if amount < 5000:
        risk_level = "low"
    elif amount < 30000:
        risk_level = "medium"
    elif amount < SBS_REGULATIONS["high_risk_threshold"]:
        risk_level = "high"
    else:
        risk_level = "critical"

    # KYC adicional requerido
    requires_additional_kyc = amount > SBS_REGULATIONS["high_risk_threshold"]

    # Regulaciones aplicables
    applicable_regs = []
    if requires_uif:
        applicable_regs.append(APPLICABLE_LAWS["uif"])
    if sandbox_eligible:
        applicable_regs.append(APPLICABLE_LAWS["sandbox"])
    if operation_type in ["loan", "credit"]:
        applicable_regs.append(APPLICABLE_LAWS["fintech"])

    # Siempre aplicable
    applicable_regs.append(APPLICABLE_LAWS["ai"])

    return {
        "compliant": True,  # Por defecto compliant si pasa checks básicos
        "operation_type": operation_type,
        "amount": amount,
        "requires_uif_report": requires_uif,
        "requires_additional_kyc": requires_additional_kyc,
        "sandbox_eligible": sandbox_eligible,
        "risk_level": risk_level,
        "applicable_regulations": applicable_regs,
        "timestamp": datetime.now().isoformat(),
        "sbs_thresholds": {
            "uif": SBS_REGULATIONS["uif_threshold"],
            "high_risk": SBS_REGULATIONS["high_risk_threshold"],
            "sandbox_max": SBS_REGULATIONS["sandbox_max_amount"],
        },
    }
```

### 3. Fraud Detection Tools - Algoritmos

```python
# src/tools/fraud_tools.py

from typing import Dict, List
from datetime import datetime, timedelta
import random


# Configuración de detección
FRAUD_CONFIG = {
    "max_transactions_per_hour": 10,
    "max_transaction_amount_normal": 15000.00,
    "suspicious_countries": ["VE", "NG", "PK"],  # ISO códigos
    "device_change_risk_increase": 0.2,
}


def detect_fraud_patterns(
    customer_id: str,
    transaction_amount: float,
    location_country: str = "PE",
    device_fingerprint: str = "known",
    hour_of_day: int = None
) -> Dict:
    """
    Analiza patrones de fraude en transacción.

    Returns:
        Dict con scoring de riesgo y recomendación
    """
    if hour_of_day is None:
        hour_of_day = datetime.now().hour

    risk_score = 0.0
    anomalies = []
    checks = {}

    # 1. Velocity Check (frecuencia)
    # Simulamos: en producción consultaríamos DB
    transactions_last_hour = random.randint(0, 15)
    if transactions_last_hour > FRAUD_CONFIG["max_transactions_per_hour"]:
        risk_score += 0.3
        anomalies.append("velocity_spike")
        checks["velocity_check"] = "FAIL"
    else:
        checks["velocity_check"] = "PASS"

    # 2. Amount Deviation
    if transaction_amount > FRAUD_CONFIG["max_transaction_amount_normal"]:
        deviation_factor = transaction_amount / FRAUD_CONFIG["max_transaction_amount_normal"]
        risk_score += min(0.25 * deviation_factor, 0.4)
        anomalies.append("unusual_amount")
        checks["amount_deviation"] = "HIGH"
    else:
        checks["amount_deviation"] = "NORMAL"

    # 3. Geographic Check
    if location_country != "PE":
        risk_score += 0.15
        if location_country in FRAUD_CONFIG["suspicious_countries"]:
            risk_score += 0.25
            anomalies.append("high_risk_country")
        checks["geo_check"] = "FAIL"
    else:
        checks["geo_check"] = "PASS"

    # 4. Device Fingerprint
    if device_fingerprint == "unknown":
        risk_score += FRAUD_CONFIG["device_change_risk_increase"]
        anomalies.append("unknown_device")
        checks["device_fingerprint"] = "UNKNOWN"
    else:
        checks["device_fingerprint"] = "KNOWN"

    # 5. Time Pattern (horario inusual)
    if hour_of_day < 6 or hour_of_day > 23:
        risk_score += 0.1
        anomalies.append("unusual_hour")
        checks["time_pattern"] = "UNUSUAL"
    else:
        checks["time_pattern"] = "NORMAL"

    # Normalizar risk_score a 0.0-1.0
    risk_score = min(risk_score, 1.0)

    # Determinar recomendación
    if risk_score < 0.3:
        recommendation = "APPROVE"
        confidence = 0.92
    elif risk_score < 0.6:
        recommendation = "REVIEW"
        confidence = 0.75
    else:
        recommendation = "BLOCK"
        confidence = 0.88

    return {
        "customer_id": customer_id,
        "transaction_amount": transaction_amount,
        "risk_score": round(risk_score, 3),
        "anomalies_detected": anomalies,
        "checks": checks,
        "recommendation": recommendation,
        "confidence": confidence,
        "timestamp": datetime.now().isoformat(),
    }
```

## Implementation Plan

### Phase 1: Banking Tools (2-3 horas)
1. Implementar mock database en memoria
2. Actualizar `check_customer_balance()`
3. Implementar `calculate_credit_capacity()` con fórmulas reales
4. Agregar `_generate_random_customer()` para testing

### Phase 2: Compliance Tools (1-2 horas)
1. Definir constantes SBS_REGULATIONS
2. Implementar `check_sbs_compliance()` con reglas UIF
3. Agregar lógica sandbox Res. SBS 4142-2025
4. Clasificación de riesgo por monto

### Phase 3: Fraud Tools (1-2 horas)
1. Implementar velocity checking
2. Agregar geographic risk scoring
3. Device fingerprinting logic
4. Time pattern analysis
5. Risk score normalization

### Phase 4: Integration & Testing (1 hora)
1. Actualizar agents para usar nuevos tools
2. Ejecutar tests unitarios existentes
3. Validar respuestas de agentes con datos reales
4. Ajustar prompts si necesario

## Success Criteria

- [ ] Tools retornan datos calculados (no hardcoded)
- [ ] Cálculos financieros precisos (TEA, capacidad)
- [ ] Reglas SBS correctamente implementadas
- [ ] Fraud detection con scoring funcional
- [ ] Tests unitarios pasan con nuevos tools
- [ ] Agentes generan respuestas coherentes con datos reales

## Testing Strategy

Usar fixtures existentes en `tests/conftest.py`:
- Mock responses de agentes siguen funcionando
- Agregar tests para nuevas funciones de tools
- Validar cálculos matemáticos (capacidad crediticia)
- Verificar thresholds SBS

## Rollback Plan

Si implementación causa problemas:
1. Los tools originales están en git history
2. Revertir commits de esta feature
3. Mantener interfaz (signature) de funciones

## References

- SBS Res. 4142-2025: Sandbox regulatorio
- Ley 31814: Regulación IA Perú
- Normativa UIF: Operaciones sospechosas S/10,000
- TEA promedio Perú 2026: 16-22% (fuente: SBS)

---

**Next Steps**: Implementar Phase 1 (Banking Tools) en src/tools/banking_tools.py
