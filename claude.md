# Claude Context - PeruBank AI Agent

> **Desarrollo**: Multi-Agent Banking System powered by AMD Instinct MI300X
> **Hackathon**: AMD Developer Hackathon 2026 (May 4-10, 2026)
> **Team**: LEAD

## Objetivo del Proyecto

Sistema multi-agente de IA para el sector bancario peruano, ejecutando Llama 3.3 70B en AMD MI300X a través de vLLM, orquestado con LangGraph.

## Estado Actual

### Implementado

1. **Infraestructura Base**
   - [x] Python 3.13 con `uv` package manager
   - [x] pre-commit hooks v6.0.0 (ruff, mypy)
   - [x] CI/CD con GitHub Actions (Python 3.12 + 3.13)
   - [x] pyproject.toml configurado
   - [x] Estructura de carpetas completa

2. **Configuración**
   - [x] `src/config/settings.py` con pydantic-settings
   - [x] Variables de entorno para vLLM/AMD MI300X
   - [x] Settings: VLLM_BASE_URL, VLLM_MODEL, timeouts, temperature

3. **Orquestador LangGraph**
   - [x] `src/agents/orchestrator.py` con StateGraph
   - [x] BankingState TypedDict definido
   - [x] Routing condicional a 4 agentes especializados
   - [x] Flujo: orchestrator → {compliance, risk, advisor, fraud} → END

4. **Agentes Especializados**
   - [x] `compliance_agent`: Verificaciones SBS/BCRP, normativas
   - [x] `risk_agent`: Scoring crediticio, análisis de capacidad
   - [x] `advisor_agent`: Recomendaciones financieras personalizadas
   - [x] `fraud_agent`: Detección de patrones sospechosos

5. **Tools Layer**
   - [x] `banking_tools.py`: Balance, capacidad crediticia
   - [x] `compliance_tools.py`: Checks regulatorios SBS
   - [x] `fraud_tools.py`: Detección de patrones de fraude
   - **NOTA**: Tools implementados con datos mock (hardcoded)

6. **System Prompts**
   - [x] Prompts en español peruano para todos los agentes
   - [x] Contexto regulatorio: Ley 31814, SBS, BCRP, Fintech
   - [x] Definición clara de responsabilidades por agente

7. **API FastAPI**
   - [x] `src/api/app.py` con CORS configurado
   - [x] Routes: `/api/v1/health`, `/api/v1/chat`
   - [x] Schemas con Pydantic: ChatRequest, ChatResponse, HealthResponse
   - [x] OpenAPI docs en `/docs`

8. **CLI Interactivo**
   - [x] `src/main.py` con Rich para UI en terminal
   - [x] Modo interactivo con asyncio
   - [x] Banner y display de estado

9. **Tests**
   - [x] `tests/conftest.py` configurado
   - [x] `tests/unit/test_tools.py` básico
   - [x] `tests/integration/test_graph.py` básico
   - **NOTA**: Cobertura aún limitada

### Pendiente / Mock

1. **Tools con Datos Reales**
   - [ ] Integración real con APIs bancarias (actualmente mock)
   - [ ] Base de datos para historial crediticio
   - [ ] Scoring real (actualmente valores hardcoded)
   - [ ] OCR para KYC (mencionado en README pero no implementado)

2. **Testing**
   - [ ] Tests unitarios completos para todos los agentes
   - [ ] Tests de integración end-to-end
   - [ ] Tests de carga/performance
   - [ ] Coverage objetivo: >80%

3. **Documentación**
   - [ ] `docs/api/` está vacío
   - [ ] Swagger/OpenAPI docs extendidos
   - [ ] Guías de uso para desarrolladores
   - [x] `docs/architecture/README.md` básico

4. **Deployment**
   - [ ] Docker/Kubernetes configs
   - [ ] Scripts de deployment a AMD Cloud
   - [x] `scripts/test_vllm.sh` para testing

5. **Features Avanzadas**
   - [ ] Persistencia de conversaciones
   - [ ] Multi-sesión con session_id
   - [ ] Logging estructurado completo
   - [ ] Métricas y observabilidad

## Arquitectura

```
┌──────────────────────────────────────────────────┐
│         AMD Developer Cloud (MI300X)             │
│  vLLM 0.17.1 + ROCm 7.2 + Llama 3.3 70B         │
└────────────────┬─────────────────────────────────┘
                 │ OpenAI-compatible API
┌────────────────▼─────────────────────────────────┐
│           LangGraph Orchestrator                 │
│  ┌──────────────────────────────────────────┐   │
│  │  BankingState (TypedDict)                │   │
│  │  - messages: list                        │   │
│  │  - customer_id: str                      │   │
│  │  - intent: str                           │   │
│  │  - risk_score: float                     │   │
│  │  - compliance_check: dict                │   │
│  │  - current_agent: str                    │   │
│  └──────────────────────────────────────────┘   │
│                                                   │
│  ┌─────────┬─────────┬─────────┬─────────┐      │
│  │Complian│  Risk   │ Advisor │  Fraud  │      │
│  │   ce   │         │         │         │      │
│  └─────────┴─────────┴─────────┴─────────┘      │
└──────────────────────────────────────────────────┘
                 │
┌────────────────▼─────────────────────────────────┐
│                Tools Layer                       │
│  - banking_tools (balance, credit capacity)     │
│  - compliance_tools (SBS checks)                │
│  - fraud_tools (pattern detection)              │
└──────────────────────────────────────────────────┘
```

## Estructura del Proyecto

```
perubank-ai-agent/
├── src/
│   ├── agents/           # 4 agentes + orchestrator
│   │   ├── orchestrator.py   # LangGraph StateGraph
│   │   ├── compliance.py
│   │   ├── risk.py
│   │   ├── advisor.py
│   │   └── fraud.py
│   ├── tools/            # LangChain tools (actualmente mock)
│   │   ├── banking_tools.py
│   │   ├── compliance_tools.py
│   │   └── fraud_tools.py
│   ├── api/
│   │   ├── app.py
│   │   └── routes/
│   │       ├── chat.py
│   │       └── health.py
│   ├── models/
│   │   └── schemas.py    # Pydantic models
│   ├── prompts/
│   │   └── system_prompts.py  # Prompts en español
│   ├── config/
│   │   └── settings.py   # pydantic-settings
│   ├── utils/
│   │   └── logger.py
│   └── main.py           # CLI interactivo
├── tests/
│   ├── unit/
│   │   └── test_tools.py
│   ├── integration/
│   │   └── test_graph.py
│   └── conftest.py
├── docs/
│   └── architecture/
│       └── README.md
├── data/
│   ├── regulations/
│   └── sample/
├── scripts/
│   └── test_vllm.sh
├── deployment/
├── notebooks/
├── pyproject.toml
├── .pre-commit-config.yaml
└── .env.example
```

## Metodología: Spec-Driven Design

Para nuevas features, seguir:

1. **Spec First**: Escribir la especificación en `docs/` antes de codificar
2. **Test-Driven**: Escribir tests antes de implementación
3. **Implementación**: Código mínimo que pase los tests
4. **Documentación**: Actualizar docs y claude.md

### Ejemplo de workflow:

```bash
# 1. Crear spec
docs/features/feature-name.md

# 2. Escribir tests
tests/unit/test_feature.py
tests/integration/test_feature_integration.py

# 3. Implementar
src/agents/new_agent.py  # o donde corresponda

# 4. Verificar
uv run pytest tests/ -v --cov=src

# 5. Commit
git add .
git commit -m "feat(agents): implement feature-name

- Add feature-name agent
- Implement spec from docs/features/feature-name.md
- Tests passing with 90% coverage"
```

## Tecnologías Clave

- **LLM**: Llama 3.3 70B Instruct (via vLLM)
- **GPU**: AMD Instinct MI300X (192GB VRAM)
- **Framework**: LangGraph 0.4 + LangChain
- **API**: FastAPI + uvicorn
- **Schemas**: Pydantic v2
- **Testing**: pytest + coverage
- **Linting**: ruff + mypy (pre-commit)
- **Package Manager**: uv (Astral)
- **Python**: 3.13 (minimum 3.12)

## Contexto Regulatorio Peruano

El sistema debe cumplir con:

- **Ley 31814** (2026): Regulación de IA en Perú
- **Res. SBS 4142-2025**: Sandbox regulatorio expandido
- **Normativa UIF**: Reporte de operaciones sospechosas (>S/10,000)
- **Open Finance Roadmap SBS** (Febrero 2026)
- **ENIA 2026-2030**: Estrategia Nacional de IA
- **Ley Fintech 2023**: Crowdfunding, billeteras digitales, PSP

## Comandos Útiles

```bash
# Desarrollo
uv sync                                  # Instalar deps
uv run python -m src.main                # CLI interactivo
uv run uvicorn src.api.app:app --reload  # API server

# Testing
uv run pytest tests/ -v                  # Run tests
uv run pytest tests/ --cov=src           # With coverage

# Linting
uv run ruff check .                      # Check code
uv run ruff check . --fix                # Auto-fix
uv run mypy src/                         # Type checking

# Pre-commit
pre-commit install                       # Instalar hooks
pre-commit run --all-files              # Run manualmente
```

## Siguiente Feature

Al implementar una nueva feature:

1. **Definir la spec** en `docs/features/`
2. **Escribir tests** que fallen inicialmente
3. **Implementar** el código mínimo
4. **Actualizar claude.md** con el estado
5. **Documentar** en `docs/api/` si es endpoint nuevo

## Notas de Desarrollo

- **LangGraph State**: Siempre retornar `{**state, ...}` para preservar el estado
- **Agentes**: Cada agente recibe `state: dict` y retorna `dict`
- **Tools**: Implementar como funciones normales de Python, LangChain las envuelve
- **Prompts**: Mantener en español peruano, ser específico con normativa
- **Testing**: Mock vLLM responses para tests unitarios rápidos
- **Logging**: Usar `src/utils/logger.py` para logs estructurados

## Issues Conocidos

- Tools con datos hardcoded (prioridad alta para próxima iteración)
- Coverage de tests bajo (<50% actualmente)
- Falta manejo de errores robusto en agents
- Sin persistencia de conversaciones aún
- Sin rate limiting en API

## Logros Recientes

- [x] Pre-commit hooks actualizados a v6.0.0
- [x] CI funcionando en Python 3.12 y 3.13
- [x] Estructura completa del proyecto
- [x] Orchestrator con LangGraph funcionando
- [x] 4 agentes especializados implementados
- [x] API FastAPI lista
- [x] CLI interactivo con Rich

---

**Última actualización**: 2026-05-06
**Branch actual**: develop → feature/agents-setup (próximo)
