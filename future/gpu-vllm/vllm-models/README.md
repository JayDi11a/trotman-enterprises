# vLLM Function-Calling Models Deployment

## Overview

This directory contains Kubernetes manifests for deploying **all 15 function-calling capable models** identified in [docs/FUNCTION_CALLING_MODELS.md](../docs/FUNCTION_CALLING_MODELS.md).

## Storage Setup

✅ **Completed:** Both k8s-control and k8s-worker have 1TB disks mounted at `/models`
- Total available: ~1.9TB across cluster
- Sufficient for all 15 models (~550GB) plus room to grow

## Deployment Strategy

### Phase 1: Production Models (Priority 1)
Deploy the 3 best function-calling models first:

1. **Llama 3.1 70B-Instruct** (40GB) - Port 30700
   - Best overall balance of quality/size
   - Native OpenAI-compatible function calling
   - 2-4 tokens/sec on CPU

2. **Qwen2.5 72B-Instruct** (43GB) - Port 30701
   - Strong alternative to Llama
   - Purpose-built for function calling
   - 2-4 tokens/sec on CPU

3. **Functionary 70B v2.5** (40GB) - Port 30702
   - Specifically trained for function calling
   - Best for complex multi-tool scenarios
   - 2-4 tokens/sec on CPU

### Phase 2: Efficient Models (Priority 2)
Deploy smaller, faster models:

4. **Qwen2.5 32B-Instruct** (19GB) - Port 30703
5. **Qwen2.5 14B-Instruct** (8.7GB) - Port 30704
6. **Functionary 7B v3.1** (4.4GB) - Port 30705
7. **Hermes 2 Pro Llama 3 8B** (4.9GB) - Port 30706

### Phase 3: Advanced Models (Priority 3)
Deploy larger experimental models:

8. **Llama 3.1 405B-Instruct** (231GB) - Port 30707 (if storage permits)
9. **Mixtral 8x22B-Instruct** (87GB) - Port 30708
10. **Mixtral 8x7B-Instruct** (26GB) - Port 30709
11. **Granite 3.0 8B-Instruct** (4.9GB) - Port 30710

### Existing Ollama Models (Chat Only)
Keep for comparison:
- llama3.1:8b (4.9GB)
- mistral:7b (4.4GB)
- hermes3:8b (4.7GB)

## Quick Start

### Deploy Phase 1 (Production Models)

```bash
# Create namespace and storage
kubectl apply -f namespace.yaml
kubectl apply -f pvc-models.yaml

# Deploy Llama 3.1 70B (first and best)
kubectl apply -f vllm-llama-70b.yaml

# Wait for model download (may take 30-60 minutes for 40GB)
kubectl logs -f -n vllm-models deployment/vllm-llama-70b

# Test the endpoint
curl http://192.168.1.130:30700/v1/models

# Deploy remaining Phase 1 models
kubectl apply -f vllm-qwen-72b.yaml
kubectl apply -f vllm-functionary-70b.yaml
```

### Access Points

| Model | Endpoint | Port | Size |
|-------|----------|------|------|
| Llama 3.1 70B | http://192.168.1.130:30700 | 30700 | 40GB |
| Qwen2.5 72B | http://192.168.1.130:30701 | 30701 | 43GB |
| Functionary 70B | http://192.168.1.130:30702 | 30702 | 40GB |

## Testing Function Calling

Once deployed, test with trotman-chat:

```bash
# Test Llama 3.1 70B
trotman-chat --provider vllm --model meta-llama/Llama-3.1-70B-Instruct

# Ask it to execute kubectl commands
You: List all pods in the kagent namespace
```

The model should properly execute the `execute_kubectl` tool and return results.

## Resource Requirements

### Per Model (70B class):
- **Memory:** 48-64GB RAM
- **CPU:** 8-16 cores
- **Disk:** 40-43GB
- **Inference Speed:** 2-4 tokens/sec on CPU

### Current Cluster Capacity:
- **k8s-control:** 64GB RAM, 16 CPU cores
- **k8s-worker:** 64GB RAM, 16 CPU cores
- **Total:** 128GB RAM, 32 CPU cores

**Strategy:** Deploy 1-2 large models at a time, can run multiple smaller models simultaneously.

## Model Download Times

HuggingFace download speeds vary, but expect:
- **70B models (40GB):** 30-60 minutes
- **14B models (8GB):** 5-15 minutes
- **7B models (4GB):** 3-10 minutes

## Next Steps

1. ✅ Storage configured (1TB per node)
2. 🔄 Deploy Llama 3.1 70B (in progress)
3. ⏳ Test function calling
4. ⏳ Deploy remaining Phase 1 models
5. ⏳ Update trotman-chat.py with vLLM providers
6. ⏳ Deploy Phase 2 and 3 models

## Troubleshooting

### Model won't download
```bash
# Check pod logs
kubectl logs -n vllm-models deployment/vllm-llama-70b

# Check internet connectivity
kubectl exec -n vllm-models deployment/vllm-llama-70b -- curl -I https://huggingface.co

# Manually download (if needed)
kubectl exec -n vllm-models deployment/vllm-llama-70b -- bash
huggingface-cli download meta-llama/Llama-3.1-70B-Instruct
```

### Out of memory
```bash
# Check node resources
kubectl describe node k8s-control
kubectl describe node k8s-worker

# Reduce max-model-len in deployment
# Edit vllm-llama-70b.yaml and change --max-model-len to 4096 or 2048
```

### Slow inference
- Expected on CPU: 2-4 tokens/sec for 70B models
- Use smaller models (14B, 7B) for faster responses
- GPU would be 10-50x faster (future upgrade)

## Cost Analysis

**Current Setup (Option D - All Models):**
- Total Cost: $0
- Power: ~$30-50/month (two servers running 24/7)
- Performance: Acceptable for development/testing (2-4 tok/sec)

**vs Cloud Alternative:**
- OpenAI GPT-4: ~$3-5/month light usage
- Anthropic Claude: ~$1-2/month light usage
- But you own the infrastructure and data!
