#!/bin/bash
# ============================================================
# AMD Developer Cloud - MI300X Setup Script
# PeruBank AI Agent | Team LEAD
# ============================================================

echo "Setting up PeruBank AI Agent on AMD MI300X..."

# Verify GPU
echo "Checking GPU..."
rocm-smi

# Install Python dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Download model (if not using Quick Start image)
echo "Starting vLLM server..."
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.3-70B-Instruct \
    --tensor-parallel-size 1 \
    --max-model-len 32768 \
    --port 8000 \
    --trust-remote-code &

# Wait for server to be ready
echo "Waiting for vLLM to load model..."
sleep 60

# Test endpoint
echo "Testing endpoint..."
curl -s http://localhost:8000/v1/models | python -m json.tool

echo "Setup complete! vLLM running on port 8000"
echo "Start the agent with: python -m src.main"
