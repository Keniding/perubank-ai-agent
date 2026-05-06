# Feature Spec: Agent Enhancements

**Status**: In Progress
**Created**: 2026-05-06
**Author**: LEAD Team
**Branch**: feature/agents-setup
**Priority**: HIGH (antes de integración vLLM)

## Overview

Mejorar agentes existentes para aprovechar los tools reales implementados, agregar error handling, y preparar estructura para persistencia MongoDB (sin conectar aún).

## Motivation

Actualmente los agentes:
- No aprovechan todos los campos de los tools reales
- Tienen bugs (ej: `existing_debt` hardcoded en risk_agent)
- No tienen manejo de errores robusto
- Pasan contexto limitado al LLM
- No están preparados para persistencia

## Scope

### In Scope

1. **Bugfixes en Agentes**
   - risk_agent: usar `current_debt` de customer_data (no hardcoded)
   - Todos: usar datos reales de tools

2. **Enriquecimiento de Contexto**
   - Pasar más información relevante al LLM
   - Usar nuevos campos de tools (tea_assumed, risk_category, etc.)
   - Formatear mejor los datos para el LLM

3. **Error Handling**
   - Try-catch en llamadas a tools
   - Manejo de customer_id inexistente
   - Fallback responses si LLM falla
   - Logging de errores

4. **Preparación MongoDB**
   - Modelos Pydantic para Customer, Transaction, Conversation
   - Estructura de schemas sin conectar
   - Interface para futuro motor de persistencia

### Out of Scope

- Conexión real a MongoDB (equipo trabajando en vLLM primero)
- Cambios en BankingState (mantener compatibilidad)
- Tests nuevos (los 59 existentes deben seguir pasando)

## Technical Design

### 1. Risk Agent - Mejoras

**Bugs a corregir:**
```python
# ANTES (bug)
credit_capacity = calculate_credit_capacity(
    monthly_income=customer_data["monthly_income"],
    existing_debt=1200.0,  # ❌ Hardcoded
)

# DESPUÉS (correcto)
credit_capacity = calculate_credit_capacity(
    monthly_income=customer_data["monthly_income"],
    existing_debt=customer_data["current_debt"],  # ✅ Del customer
)
```

**Enriquecimiento de contexto:**
```python
# Construir contexto más rico para el LLM
context = f"""
PERFIL DEL CLIENTE:
- Nombre: {customer_data['name']}
- Score crediticio: {customer_data['credit_score']}/1000
- Ingreso mensual: S/ {customer_data['monthly_income']:,.2f}
- Deuda mensual actual: S/ {customer_data['current_debt']:,.2f}
- Tipo de empleo: {customer_data['employment_type']}
- Antigüedad laboral: {customer_data['years_employed']} años
- Sector: {customer_data['sector']}

ANÁLISIS DE CAPACIDAD CREDITICIA:
- Ratio deuda/ingreso actual: {credit_capacity['debt_ratio_current']:.1%}
- Ratio máximo SBS: {credit_capacity['debt_ratio_max_sbs']:.0%}
- Capacidad mensual disponible: S/ {credit_capacity['available_monthly_capacity']:,.2f}
- Préstamo máximo 12 meses: S/ {credit_capacity['max_loan_12_months']:,.2f}
- Préstamo máximo 24 meses: S/ {credit_capacity['max_loan_24_months']:,.2f}
- Préstamo máximo 36 meses: S/ {credit_capacity['max_loan_36_months']:,.2f}
- TEA asumida: {credit_capacity['tea_assumed']:.0%}
- Cumple SBS: {'SÍ' if credit_capacity['compliant_sbs'] else 'NO'}

CONSULTA DEL CLIENTE:
{state['messages'][-1].content}
"""
```

### 2. Compliance Agent - Mejoras

**Enriquecimiento:**
```python
# Ejecutar check real
compliance_result = check_sbs_compliance(
    operation_type="loan",  # Detectar del mensaje
    amount=_extract_amount_from_message(state['messages'][-1].content)
)

context = f"""
VERIFICACIÓN DE CUMPLIMIENTO SBS:

Tipo de operación: {compliance_result['operation_type']}
Monto: S/ {compliance_result['amount']:,.2f}

RESULTADOS:
- Cumplimiento: {'✓ COMPLIANT' if compliance_result['compliant'] else '✗ NON-COMPLIANT'}
- Nivel de riesgo: {compliance_result['risk_level'].upper()}
- Requiere reporte UIF: {'SÍ' if compliance_result['requires_uif_report'] else 'NO'}
- Requiere KYC adicional: {'SÍ' if compliance_result['requires_additional_kyc'] else 'NO'}
- Elegible para sandbox: {'SÍ' if compliance_result['sandbox_eligible'] else 'NO'}

UMBRALES SBS:
- UIF: S/ {compliance_result['sbs_thresholds']['uif']:,.2f}
- KYC reforzado: S/ {compliance_result['sbs_thresholds']['kyc_enhanced']:,.2f}
- Alto riesgo: S/ {compliance_result['sbs_thresholds']['high_risk']:,.2f}

NORMATIVAS APLICABLES:
{chr(10).join('- ' + reg for reg in compliance_result['applicable_regulations'])}

CONSULTA:
{state['messages'][-1].content}
"""
```

### 3. Fraud Agent - Mejoras

**Usar parámetros opcionales:**
```python
# Extraer información del contexto si está disponible
location = _extract_location(state.get('metadata', {}))
device = state.get('device_fingerprint', 'known')
hour = datetime.now().hour

fraud_result = detect_fraud_patterns(
    customer_id=state["customer_id"],
    transaction_amount=_extract_amount_from_message(state['messages'][-1].content),
    location_country=location,
    device_fingerprint=device,
    hour_of_day=hour,
)

context = f"""
ANÁLISIS ANTI-FRAUDE:

Cliente: {fraud_result['customer_id']}
Monto transacción: S/ {fraud_result['transaction_amount']:,.2f}

SCORING DE RIESGO:
- Risk Score: {fraud_result['risk_score']:.3f}
- Categoría: {fraud_result['risk_category'].upper()}
- Confianza: {fraud_result['confidence']:.0%}

ANOMALÍAS DETECTADAS ({fraud_result['anomaly_count']}):
{chr(10).join('- ' + anomaly for anomaly in fraud_result['anomalies_detected']) if fraud_result['anomalies_detected'] else '- Ninguna'}

CHECKS REALIZADOS:
- Velocity: {fraud_result['checks']['velocity_check']}
- Geo: {fraud_result['checks']['geo_check']}
- Dispositivo: {fraud_result['checks']['device_fingerprint']}
- Monto: {fraud_result['checks']['amount_deviation']}
- Horario: {fraud_result['checks']['time_pattern']}

RECOMENDACIÓN: {fraud_result['recommendation']}
Acción requerida: {fraud_result['action_required']}

CONSULTA:
{state['messages'][-1].content}
"""
```

### 4. Error Handling Pattern

Todos los agentes deben seguir este patrón:

```python
def agent_name(state: dict) -> dict:
    """Agent description."""
    try:
        # Initialize LLM
        llm = ChatOpenAI(...)

        # Execute tools with error handling
        try:
            data = tool_function(state["customer_id"])
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            # Return graceful error response
            return {
                **state,
                "messages": state["messages"] + [
                    AIMessage(content=f"[{agent_name}] Lo siento, ocurrió un error "
                                     f"al procesar tu consulta. Por favor intenta de nuevo.")
                ],
                "current_agent": agent_name,
            }

        # Build context and invoke LLM
        messages = [SystemMessage(content=PROMPT), HumanMessage(content=context)]

        try:
            response = llm.invoke(messages)
        except Exception as e:
            logger.error(f"LLM invocation failed: {e}")
            # Fallback response
            return {
                **state,
                "messages": state["messages"] + [
                    AIMessage(content=f"[{agent_name}] El servicio está temporalmente "
                                     f"no disponible. Por favor intenta más tarde.")
                ],
                "current_agent": agent_name,
            }

        # Return successful response
        return {
            **state,
            # ... agent-specific state updates
            "messages": state["messages"] + [AIMessage(content=f"[{agent_name}] {response.content}")],
            "current_agent": agent_name,
        }

    except Exception as e:
        logger.error(f"Unexpected error in {agent_name}: {e}")
        # Ultimate fallback
        return {
            **state,
            "messages": state["messages"] + [
                AIMessage(content=f"[Sistema] Error interno. Contacta soporte.")
            ],
            "current_agent": agent_name,
        }
```

### 5. MongoDB Models (preparación sin conexión)

```python
# src/models/database.py

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Customer(BaseModel):
    """Customer profile model."""
    customer_id: str = Field(..., description="Unique customer ID")
    name: str
    dni: str
    monthly_income: float
    current_debt: float
    credit_score: int
    account_soles: float
    account_dolares: float
    employment_type: str
    years_employed: int
    sector: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Transaction(BaseModel):
    """Transaction record model."""
    transaction_id: str = Field(..., description="Unique transaction ID")
    customer_id: str
    amount: float
    type: str  # deposito, pago, transferencia, compra
    description: str
    date: datetime
    location_country: str = "PE"
    device_fingerprint: str = "known"
    fraud_check: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.now)


class Conversation(BaseModel):
    """Conversation history model."""
    conversation_id: str = Field(..., description="Unique conversation ID")
    customer_id: str
    session_id: str
    messages: List[dict]  # LangChain messages serialized
    started_at: datetime
    last_message_at: datetime
    agents_used: List[str]
    metadata: dict = Field(default_factory=dict)


class ComplianceCheck(BaseModel):
    """Compliance check record."""
    check_id: str = Field(..., description="Unique check ID")
    customer_id: str
    operation_type: str
    amount: float
    result: dict
    created_at: datetime = Field(default_factory=datetime.now)
```

### 6. Helper Functions

```python
# src/utils/helpers.py

import re
from typing import Optional


def extract_amount_from_message(message: str) -> float:
    """
    Extrae monto de un mensaje.

    Ejemplos:
    - "Quiero un préstamo de S/20,000" → 20000.0
    - "Transferir 5000 soles" → 5000.0
    - "¿Puedo pedir S/ 15,500?" → 15500.0
    """
    # Patterns comunes en español peruano
    patterns = [
        r'S/\s*([0-9,]+(?:\.[0-9]{2})?)',  # S/ 20,000 o S/20000.00
        r'soles?\s+([0-9,]+)',               # 5000 soles
        r'([0-9,]+)\s+soles?',               # soles 5000
    ]

    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(',', '')
            try:
                return float(amount_str)
            except ValueError:
                continue

    # Default: monto promedio para análisis
    return 15000.0


def extract_location(metadata: dict) -> str:
    """Extrae país de metadata."""
    return metadata.get('location_country', 'PE')
```

## Implementation Plan

### Phase 1: Bugfixes y Helpers (30 min)
1. Crear src/utils/helpers.py con extract_amount_from_message
2. Corregir bug en risk_agent (usar current_debt real)
3. Agregar logging básico

### Phase 2: Enriquecer Agentes (1-2 horas)
1. risk_agent: contexto rico + error handling
2. compliance_agent: contexto rico + detectar tipo operación
3. fraud_agent: usar parámetros opcionales
4. advisor_agent: contexto más completo

### Phase 3: MongoDB Models (30 min)
1. Crear src/models/database.py con modelos Pydantic
2. No conectar aún (equipo trabajando en vLLM)
3. Documentar estructura para futura integración

### Phase 4: Testing (30 min)
1. Verificar que los 59 tests existentes sigan pasando
2. Ajustar mocks si necesario
3. Validar que agentes usan datos reales

## Success Criteria

- [ ] Bug de risk_agent corregido
- [ ] Todos los agentes usan datos reales de tools
- [ ] Contexto enriquecido pasado al LLM
- [ ] Error handling implementado en todos los agentes
- [ ] Helper functions creadas y testeadas
- [ ] MongoDB models definidos (sin conexión)
- [ ] 59 tests existentes siguen pasando
- [ ] Sin degradación de performance

## Testing Strategy

Los tests existentes deben seguir funcionando:
- Mocks de LLM siguen siendo válidos
- Mocks de tools se ajustan si necesario
- Verificar que error handling no rompe flujo

## Rollback Plan

Si hay problemas:
1. Revertir commits de esta feature
2. Los agentes originales están en git history
3. Tests garantizan funcionalidad básica

## References

- Tools reales: src/tools/*.py
- Tests existentes: tests/unit/test_agents/
- MongoDB URI: mongodb+srv://develop-user:***@cluster0.j3c0b.mongodb.net/agroplus

---

**Next Steps**: Implementar Phase 1 (bugfixes y helpers)
