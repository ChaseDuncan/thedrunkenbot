#!/bin/bash
export HF_HUB_OFFLINE=1
export HF_HUB_DISABLE_TELEMETRY=1

source .venv/bin/activate
vllm serve Qwen/Qwen3-0.6B \
    --host 0.0.0.0 \
    --port 8000 \
    --enforce-eager \
    --gpu-memory-utilization 0.7 \
    --max-model-len 2048