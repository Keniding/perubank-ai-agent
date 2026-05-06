# Feature Spec: Comprehensive Agent Testing

**Status**: In Progress
**Created**: 2026-05-06
**Author**: LEAD Team
**Branch**: feature/agents-setup

## Overview

Implementar suite completa de tests para los 4 agentes especializados del sistema PeruBank AI Agent, siguiendo metodología TDD y alcanzando >80% de cobertura.

## Motivation

Actualmente los agentes están implementados pero carecen de tests unitarios e integración robustos. Esto representa riesgos:
- Cambios futuros pueden romper funcionalidad sin detectarlo
- No hay validación de casos edge
- Dificulta el debugging y mantenimiento
- Coverage actual <50%

## Scope

### In Scope

1. **Tests Unitarios por Agente**
   - `test_compliance_agent.py`: Verificaciones SBS/BCRP
   - `test_risk_agent.py`: Scoring y análisis crediticio
   - `test_advisor_agent.py`: Recomendaciones financieras
   - `test_fraud_agent.py`: Detección de patrones sospechosos
   - `test_orchestrator.py`: Routing y state management

2. **Tests de Integración**
   - Flujo completo orchestrator → agent → END
   - State preservation entre nodos
   - Manejo de errores en el graph
   - Timeout scenarios

3. **Fixtures y Mocks**
   - Mock de vLLM responses
   - Fixtures de BankingState
   - Fixtures de customer data
   - Mock de tools layer

### Out of Scope

- Tests de performance/load (futura iteración)
- Tests E2E con vLLM real (requiere AMD Cloud)
- Tests de API endpoints (otra feature)

## Technical Design

### Test Structure

```
tests/
├── conftest.py                   # Shared fixtures
├── unit/
│   ├── test_agents/
│   │   ├── test_compliance_agent.py
│   │   ├── test_risk_agent.py
│   │   ├── test_advisor_agent.py
│   │   ├── test_fraud_agent.py
│   │   └── test_orchestrator.py
│   └── test_tools.py             # Existing
└── integration/
    ├── test_graph.py              # Existing - expand
    └── test_agent_flows.py        # New
```

### Key Test Cases

#### 1. Compliance Agent
```python
def test_compliance_agent_sbs_check():
    """Verify SBS compliance validation."""

def test_compliance_agent_uif_threshold():
    """Test UIF reporting for transactions >S/10,000."""

def test_compliance_agent_sandbox_eligibility():
    """Check sandbox regulatorio criteria."""
```

#### 2. Risk Agent
```python
def test_risk_agent_debt_ratio_calculation():
    """Verify debt/income ratio (max 30%)."""

def test_risk_agent_credit_scoring():
    """Test credit score evaluation (0-1000 scale)."""

def test_risk_agent_rejection_criteria():
    """Validate RECHAZADO recommendation."""
```

#### 3. Advisor Agent
```python
def test_advisor_agent_product_recommendation():
    """Test personalized product suggestions."""

def test_advisor_agent_risk_disclosure():
    """Ensure benefits AND risks are mentioned."""

def test_advisor_agent_currency_format():
    """Verify soles (S/) as primary currency."""
```

#### 4. Fraud Agent
```python
def test_fraud_agent_velocity_check():
    """Test transaction velocity detection."""

def test_fraud_agent_amount_deviation():
    """Verify unusual amount patterns."""

def test_fraud_agent_risk_score_calculation():
    """Validate risk score (0.0-1.0)."""
```

#### 5. Orchestrator
```python
def test_orchestrator_intent_classification():
    """Test routing to correct agent."""

def test_orchestrator_state_preservation():
    """Verify BankingState is preserved."""

def test_orchestrator_invalid_intent_fallback():
    """Test fallback to advisor for unknown intents."""
```

### Mocking Strategy

Mock vLLM responses para tests rápidos y deterministas:

```python
@pytest.fixture
def mock_llm_response():
    """Mock ChatOpenAI responses."""
    with patch('src.agents.orchestrator.ChatOpenAI') as mock:
        mock_instance = mock.return_value
        mock_instance.invoke.return_value = AIMessage(content="compliance")
        yield mock_instance
```

### Fixtures Comunes

```python
@pytest.fixture
def banking_state():
    """Sample BankingState for testing."""
    return {
        "messages": [HumanMessage(content="¿Es legal esta transacción?")],
        "customer_id": "TEST-001",
        "intent": "",
        "risk_score": 0.0,
        "compliance_check": {},
        "recommendation": "",
        "current_agent": ""
    }

@pytest.fixture
def customer_profile():
    """Sample customer data."""
    return {
        "id": "TEST-001",
        "monthly_income": 5000.0,
        "current_debt": 1200.0,
        "credit_score": 750,
        "employment_type": "dependiente"
    }
```

## Success Criteria

- [ ] Test coverage >80% en src/agents/
- [ ] Todos los tests pasan en CI (Python 3.12 + 3.13)
- [ ] Cada agente tiene >5 test cases
- [ ] Tests de integración cubren flujos principales
- [ ] Tiempo de ejecución total <30s
- [ ] Pre-commit hooks pasan

## Implementation Plan

### Phase 1: Setup (30 min)
1. Crear estructura de carpetas tests/unit/test_agents/
2. Configurar fixtures comunes en conftest.py
3. Setup mocks para vLLM

### Phase 2: Unit Tests (2h)
1. test_orchestrator.py (intent routing, state management)
2. test_compliance_agent.py (SBS, UIF, sandbox)
3. test_risk_agent.py (scoring, ratios, recommendations)
4. test_advisor_agent.py (products, risks, currency)
5. test_fraud_agent.py (patterns, velocity, scores)

### Phase 3: Integration Tests (1h)
1. Expandir test_graph.py con más flujos
2. test_agent_flows.py para scenarios end-to-end
3. Error handling tests

### Phase 4: Validation (30 min)
1. Run pytest con coverage
2. Ajustar implementación si tests fallan
3. Verificar CI pasa
4. Actualizar claude.md

## Testing Guidelines

- **Arrange-Act-Assert** pattern
- Un concepto por test
- Nombres descriptivos: `test_<component>_<scenario>_<expected>`
- Mock external dependencies (vLLM, tools)
- Use fixtures para setup repetido
- Parametrize tests similares con `@pytest.mark.parametrize`

## Example Test

```python
import pytest
from langchain_core.messages import HumanMessage, AIMessage
from unittest.mock import patch

from src.agents.compliance import compliance_agent


@pytest.mark.parametrize(
    "amount,expected_uif",
    [
        (8000.0, False),   # Below threshold
        (10001.0, True),   # Above threshold
        (10000.0, False),  # Exactly at threshold
    ]
)
def test_compliance_agent_uif_reporting(
    banking_state,
    mock_llm_response,
    amount,
    expected_uif
):
    """Verify UIF reporting for transactions >S/10,000."""
    # Arrange
    state = {
        **banking_state,
        "messages": [HumanMessage(content=f"Transferencia de S/{amount}")]
    }

    # Act
    result = compliance_agent(state)

    # Assert
    assert "current_agent" in result
    assert result["current_agent"] == "compliance"
    # Additional assertions on UIF reporting logic
```

## Dependencies

- pytest ^9.0.3
- pytest-cov
- pytest-asyncio (for async graph tests)
- pytest-mock
- existing: langchain, langgraph

## Rollback Plan

Si tests revelan bugs críticos:
1. Documentar issues en GitHub
2. Crear branch hotfix/agent-fixes
3. Fix implementation
4. Re-run tests
5. Merge cuando todos pasen

## References

- [pytest documentation](https://docs.pytest.org/)
- [LangGraph testing guide](https://langchain-ai.github.io/langgraph/how-tos/testing/)
- claude.md - Metodología Spec-Driven Design

---

**Next Steps**: Implement Phase 1 (setup) en tests/conftest.py
