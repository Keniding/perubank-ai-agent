#!/bin/bash
# ============================================================
# Quick test script for the vLLM endpoint
# AMD Developer Cloud - MI300X
# ============================================================

VLLM_URL=""

echo "============================================"
echo "Testing vLLM endpoint on AMD MI300X..."
echo "URL: $VLLM_URL"
echo "============================================"

# 1. Check available models
echo ""
echo "[1/3] Checking available models..."
curl -s $VLLM_URL/v1/models | python3 -m json.tool

# 2. Simple completion test
echo ""
echo "[2/3] Testing chat completion..."
curl -s -X POST $VLLM_URL/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"meta-llama/Llama-3.3-70B-Instruct\",
    \"messages\": [{\"role\": \"user\", \"content\": \"Hola, soy un cliente de PeruBank. Responde en una sola frase.\"}],
    \"max_tokens\": 64,
    \"temperature\": 0.1
  }" | python3 -m json.tool

# 3. Latency test
echo ""
echo "[3/3] Latency test..."
time curl -s -X POST $VLLM_URL/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"meta-llama/Llama-3.3-70B-Instruct\",
    \"messages\": [{\"role\": \"user\", \"content\": \"Di solo: OK\"}],
    \"max_tokens\": 5,
    \"temperature\": 0.0
  }" > /dev/null

echo ""
echo "Done! vLLM is ready for PeruBank AI Agent."