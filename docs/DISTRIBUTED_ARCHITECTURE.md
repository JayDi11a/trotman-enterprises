# Distributed Architecture: Control + Worker

## Overview

**Control Node (192.168.1.130) - 62GB RAM:**
- Role: Small models + LiteLLM orchestration
- Models: Hermes 8B, Qwen 14B, Granite 8B, Functionary Small, Qwen 32B
- Memory: ~40GB used, 22GB free
- Purpose: Fast response for small queries, API gateway

**Worker Node (192.168.1.131) - 256GB RAM:**
- Role: Large model inference
- Models: Llama 70B, Qwen 72B, Mixtral 8x7B, Mixtral 8x22B
- Memory: ~196GB for all large models, 60GB free
- Purpose: Maximum quality inference

## Architecture Benefits

✅ **All 15 models accessible simultaneously** (10 local + 5 cloud)  
✅ **Small models: instant response** (<100ms latency)  
✅ **Large models: always ready** (no manual start/stop)  
✅ **Single API endpoint** via LiteLLM (http://192.168.1.130:4000/v1)  
✅ **Smart routing** based on query complexity  
✅ **Cost savings** vs cloud-only ($0 local inference)  

## Model Distribution

### Control Node Models (Port 307XX)

| Model | Port | RAM | Purpose |
|-------|------|-----|---------|
| Hermes 2 Pro 8B | 30704 | 4.6GB | Fast function calling |
| Qwen 2.5 14B | 30705 | 8.4GB | General reasoning |
| Granite 3.0 8B | 30709 | 4.7GB | Enterprise tasks |
| Functionary Small | 30706 | 4.6GB | Specialized function calling |
| Qwen 2.5 32B | 30703 | 19GB | Strong reasoning |

**Total:** ~42GB RAM used

### Worker Node Models (Port 307XX)

| Model | Port | RAM | Purpose |
|-------|------|-----|---------|
| Llama 3.1 70B | 30700 | 40GB | Top-tier reasoning |
| Qwen 2.5 72B | 30701 | 43GB | State-of-the-art |
| Mixtral 8x7B | 30707 | 26GB | Efficient MoE |
| Mixtral 8x22B | 30708 | 87GB | Largest local model |

**Total:** ~196GB RAM used

## Network Architecture

```
User Request
     ↓
LiteLLM Proxy (Control:4000)
     ↓
     ├─→ Small model request → Control Node (local)
     └─→ Large model request → Worker Node (192.168.1.131:307XX)
```

## LiteLLM Configuration

**Endpoint:** http://192.168.1.130:4000/v1  
**Auth:** Bearer token required  
**Model Groups:**
- `function-calling-small` → Control node (Hermes, Granite, Functionary)
- `function-calling-medium` → Control node (Qwen 14B, Qwen 32B)
- `function-calling-large` → Worker node (Llama 70B, Qwen 72B, Mixtral)
- `cloud-premium` → Anthropic, OpenAI
- `cloud-efficient` → Claude Haiku, GPT-4o Mini, Gemini

## Deployment Steps

### 1. Expand Worker VM
- Increase RAM allocation from 62GB → 256GB in ESXi
- Reboot worker VM

### 2. Copy Models to Worker
```bash
# Run from control node
rsync -avP /models/llama-3.1-70b/ root@192.168.1.131:/models/llama-3.1-70b/
rsync -avP /models/qwen2.5-72b/ root@192.168.1.131:/models/qwen2.5-72b/
rsync -avP /models/mixtral-8x7b/ root@192.168.1.131:/models/mixtral-8x7b/
rsync -avP /models/mixtral-8x22b/ root@192.168.1.131:/models/mixtral-8x22b/
```

### 3. Deploy Systemd Services on Worker
- Create llama-cpp services for all 4 large models
- Enable and start all services
- Verify all models load successfully

### 4. Update LiteLLM Config
- Point large model endpoints to worker node (192.168.1.131)
- Restart LiteLLM proxy
- Test routing

### 5. Verify Full Stack
```bash
# Test small model (control)
curl http://192.168.1.130:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-trotman-litellm-2026" \
  -d '{"model": "hermes-2-pro-8b", "messages": [...]}'

# Test large model (worker)
curl http://192.168.1.130:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-trotman-litellm-2026" \
  -d '{"model": "llama-3.1-70b", "messages": [...]}'
```

## Memory Management

### Control Node
```
Small models:     ~42GB
LiteLLM proxy:    ~0.3GB
OS/K8s overhead:  ~10GB
---------------------------
Total used:       ~52GB / 62GB
Free:             ~10GB
```

### Worker Node
```
Llama 70B:        ~40GB
Qwen 72B:         ~43GB
Mixtral 8x7B:     ~26GB
Mixtral 8x22B:    ~87GB
---------------------------
Total models:     ~196GB
OS overhead:      ~10GB
---------------------------
Total used:       ~206GB / 256GB
Free:             ~50GB
```

## Performance Expectations

| Model Size | First Token | Tokens/sec | Use Case |
|------------|-------------|------------|----------|
| 8B | <100ms | 15-20 | Quick tasks |
| 14B | <200ms | 12-16 | General use |
| 32B | <500ms | 8-12 | Complex reasoning |
| 70B | <1s | 6-10 | Maximum quality |
| 72B | <1s | 6-10 | Maximum quality |
| 8x7B | <800ms | 10-14 | MoE efficiency |
| 8x22B | <2s | 4-8 | Largest local |

## Cost Analysis

**Hardware (one-time):**
- IBM System x3650 M4: ~$500 (used)
- Total investment: $500

**Cloud equivalent (monthly):**
- 15 models @ $0.50-$3.00/million tokens
- Estimated: $2,000-5,000/month for this workload
- **Payback period: 1-2 months**

**Ongoing costs:**
- Electricity: ~$50-80/month (both servers)
- Total: ~$600-1000/year

## Monitoring

**Check all services:**
```bash
# Control node
ssh root@192.168.1.130 "systemctl list-units 'llama-cpp-*.service'"

# Worker node
ssh root@192.168.1.131 "systemctl list-units 'llama-cpp-*.service'"
```

**Check memory:**
```bash
# Control
ssh root@192.168.1.130 "free -h"

# Worker
ssh root@192.168.1.131 "free -h"
```

**Check LiteLLM health:**
```bash
curl http://192.168.1.130:4000/health
```

## Future Expansion

**If need more capacity:**
1. Add GPU to worker node for vLLM deployment
2. Add third node for specialized workloads
3. Deploy Functionary Medium 70B on worker (42GB)

**Control node has 55GB free on ESXi host:**
- Could expand control VM to 100GB if needed
- Room for more small/medium models
