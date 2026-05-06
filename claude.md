# Claude Context - PeruBank AI Agent

> **Desarrollo**: Multi-Agent Banking System powered by AMD Instinct MI300X
> **Hackathon**: AMD Developer Hackathon 2026 (May 4-10, 2026)
> **Team**: LEAD
> **Track**: AI Agents & Agentic Workflows

## Objetivo del Proyecto

Sistema multi-agente de IA para el sector bancario peruano, ejecutando Llama 3.3 70B en AMD MI300X a través de vLLM, orquestado con LangGraph.

## Contexto de Mercado

### Global
- **Ingresos Fintech 2025**: ~$650 mil millones (21% YoY)
- **Crecimiento LatAm**: 40% anual (McKinsey)
- **Agentes en producción**: 57.3% de organizaciones
- **Predicción Gartner 2028**: 33% de apps con IA agéntica (vs <1% en 2024)
- **Valor anual agentes IA**: $2.6-4.4 trillones (McKinsey)

### Perú
- **Ley Fintech**: Vigente desde 2023, sandbox regulatorio SBS
- **Res. SBS 4142-2025**: Sandbox expandido, SBS como promotor de innovación
- **Transacciones electrónicas**: 78% del total (vs 45% en 2019)
- **Startups Fintech**: +220 operando en el país
- **Open Finance**: Roadmap publicado por SBS en febrero 2026
- **Regulación IA**: Ley 31814 + ENIA 2026-2030
- **Mercado Fintech Perú**: ~USD 850 millones (2024), crecimiento 16% anual

**Insight clave**: Perú ha formalizado un marco regulatorio para IA, permitiendo innovación controlada en servicios financieros.

## Stack Tecnológico MVP

### AMD Developer Cloud
- **GPU**: AMD Instinct MI300X (192GB VRAM)
- **ROCm**: 7.2.3 (producción) / 7.12.0 (preview)
- **vLLM**: 0.17.1 (ROCm 7.2.0)
- **SGLang**: 0.5.9 (alternativa)
- **PyTorch**: 2.6.0 (ROCm 7.0.0)
- **Costo**: $1.99/GPU/hr
- **Créditos Hackathon**: $100 USD (31 días)

### Frameworks
- **LangChain**: 0.3.x (orquestación)
- **LangGraph**: 0.4.x (grafos de estado)
- **FastAPI**: 0.115+ (API)
- **Pydantic**: 2.0+ (schemas)

### Modelos Recomendados (ROCm-compatible)
- **Qwen3-Coder 235B**: Generación de código, agentes
- **Llama 3.3 70B**: Razonamiento general (actual)
- **DeepSeek-R1 671B**: Razonamiento profundo
- **Mistral Large 123B**: Multilingüe
- **Qwen-VL 72B**: Multimodal (OCR documentos)

### Presupuesto Estimado ($100 créditos)
| Actividad | Horas | Costo |
|-----------|-------|-------|
| Setup + Deploy vLLM | 2h | $3.98 |
| Desarrollo agentes | 20h | $39.80 |
| Demo y video | 3h | $5.97 |
| Buffer | 10h | $19.90 |
| **Total** | **35h** | **$69.65** |
| **Restante** | | **$30.35** |

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
   - [x] `tests/conftest.py` con fixtures completos y mocks
   - [x] `tests/unit/test_tools.py` básico
   - [x] `tests/integration/test_graph.py` básico
   - [x] `tests/unit/test_agents/` - Suite completa (59 tests)
   - [x] **Coverage: 100% en src/agents/ (97/97 statements)**
   - **Spec**: docs/features/agent-testing.md

### Pendiente / Mock

1. **Tools con Datos Reales**
   - [ ] Integración real con APIs bancarias (actualmente mock)
   - [ ] Base de datos para historial crediticio
   - [ ] Scoring real (actualmente valores hardcoded)
   - [ ] OCR para KYC (mencionado en README pero no implementado)

2. **Testing**
   - [x] Tests unitarios completos para todos los agentes (59/59 passing)
   - [ ] Tests de integración end-to-end
   - [ ] Tests de carga/performance
   - [x] Coverage objetivo: >80% (actualmente 100% en agents)

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

## Diferenciadores Competitivos

| Aspecto | Ventaja |
|---------|---------|
| **Contexto local** | Regulación SBS peruana, Open Finance, ENIA 2026-2030 |
| **Multi-agente real** | No es chatbot simple, son agentes especializados coordinados |
| **AMD-native** | vLLM optimizado para MI300X con ROCm 7.2 |
| **Business value** | Caso de uso bancario real con métricas de compliance |
| **Escalabilidad** | Arquitectura lista para producción con LangGraph |
| **Open Source** | Todo el código disponible en GitHub |

## Roadmap de Implementación Real

### Prioridad 1: Tools con Lógica Real
1. **banking_tools.py**
   - Integrar cálculo real de capacidad crediticia
   - Implementar scoring con reglas SBS (ratio deuda/ingreso 30%)
   - Conectar con mock database para transacciones

2. **compliance_tools.py**
   - Implementar verificación UIF (>S/10,000)
   - Reglas sandbox SBS Res. 4142-2025
   - Validación contra normativas vigentes

3. **fraud_tools.py**
   - Algoritmo de velocity checking
   - Detección de patrones sospechosos
   - Scoring de riesgo basado en reglas

### Prioridad 2: Integración vLLM Real
- [ ] Configurar endpoint AMD MI300X
- [ ] Optimizar prompts para Llama 3.3 70B
- [ ] Implementar fallback si vLLM no disponible
- [ ] Métricas de latencia y tokens

### Prioridad 3: Features Avanzadas
- [ ] OCR de DNI peruano (Qwen-VL)
- [ ] Persistencia con SQLite/PostgreSQL
- [ ] Dashboard de métricas
- [ ] Rate limiting por cliente

### Prioridad 4: Deployment
- [ ] Dockerizar aplicación
- [ ] Scripts de deploy a AMD Cloud
- [ ] CI/CD pipeline completo
- [ ] Monitoring y logging

## Issues Conocidos

- Tools con datos hardcoded (PRIORIDAD ALTA - siguiente feature)
- Falta manejo de errores robusto en agents
- Sin persistencia de conversaciones aún
- Sin rate limiting en API
- Warnings de Pydantic (Settings class-based config deprecation)
- No hay integración real con vLLM en AMD MI300X

## Cronograma Hackathon (May 4-10, 2026)

| Día | Actividad | Estado |
|-----|-----------|--------|
| **May 5** | Setup AMD Cloud, deploy vLLM, test conexión | Pendiente |
| **May 6** | Implementar tools reales (Compliance + Risk) | En progreso |
| **May 7** | Implementar tools (Advisor + Fraud) + OCR | Planeado |
| **May 8** | Integración, testing E2E, UI básica | Planeado |
| **May 9** | Pulir demo, grabar video, submission | Planeado |
| **May 10** | Submit antes 2:00 PM (hora Perú) | Deadline |

## Submission Checklist

- [ ] Título: "PeruBank AI Agent — Multi-Agent Banking System on AMD"
- [ ] Repositorio GitHub público
- [ ] Video demo (3-5 min)
- [ ] Hugging Face Space publicado
- [ ] 2 posts técnicos (X: @lablabai + @AIatAMD)
- [ ] Feedback AMD Developer Experience

## Logros Recientes

- [x] Pre-commit hooks actualizados a v6.0.0
- [x] CI funcionando en Python 3.12 y 3.13
- [x] Estructura completa del proyecto
- [x] Orchestrator con LangGraph funcionando
- [x] 4 agentes especializados implementados
- [x] API FastAPI lista
- [x] CLI interactivo con Rich
- [x] Suite completa de tests (59 tests, 100% coverage en agents)
- [x] Feature spec: agent-testing.md
- [x] Metodología spec-driven design implementada
- [x] Documento MVP completo integrado

---

**Última actualización**: 2026-05-06 23:30
**Branch actual**: feature/agents-setup
**Día del Hackathon**: 2/6 (May 6)
**Siguiente milestone**: Implementar tools con lógica real
