# Architecture Documentation

## System Overview

PeruBank AI Agent uses a **multi-agent architecture** orchestrated by LangGraph,
running inference on AMD Instinct MI300X via vLLM.

## Components

### 1. Inference Layer (AMD MI300X)
- vLLM 0.17.1 with ROCm 7.2
- Llama 3.3 70B Instruct
- OpenAI-compatible API endpoint

### 2. Orchestration Layer (LangGraph)
- State machine-based routing
- Conditional edges for agent selection
- Async execution support

### 3. Agent Layer
- Compliance Agent (SBS/BCRP)
- Risk Agent (Credit Scoring)
- Advisor Agent (Financial Recommendations)
- Fraud Agent (Transaction Analysis)

### 4. Tools Layer
- Banking tools (balance, credit capacity)
- Compliance tools (SBS checks)
- Fraud tools (pattern detection)

## Data Flow

1. User sends query via API/CLI
2. Orchestrator classifies intent
3. Specialized agent processes with tools
4. Response returned to user
