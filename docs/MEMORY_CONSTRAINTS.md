# Memory Constraints & Deployment Strategy

## Critical Discovery

**Cannot run all 10 local models simultaneously on 62GB RAM.**

### Memory Requirements Analysis

Current hardware: **62GB RAM per VM** (k8s-control, k8s-worker)

#### Model Memory Footprints (Q4_K_M quantization)

**Small Models (< 15GB):**
- Hermes 2 Pro 8B: ~4.6GB
- Granite 3.0 8B: ~4.7GB  
- Qwen2.5 14B: ~8.4GB
- Qwen2.5 32B: ~19GB
- Functionary 7B: ~4GB (estimated)

**Large Models (> 20GB):**
- Mixtral 8x7B: ~26GB
- Llama 3.1 70B: ~40GB
- Qwen2.5 72B: ~43GB
- Functionary 70B: ~40GB (estimated)
- Mixtral 8x22B: ~87GB

**Total if all loaded: ~290GB+ (4.6x available RAM!)**

### Observed Issue

When attempting to run 4 models simultaneously:
- Qwen 14B (8.7GB) + Hermes 8B (4.8GB) + Granite 8B (4.8GB) + Llama 70B (40GB loading)
- System exhausted: 308MB free RAM, 19GB swap fully used
- Llama 70B killed by OOM (Out Of Memory) killer repeatedly
- Service restart loop: 21 failures before manual intervention

## Solution: Hybrid Deployment Architecture

### Phase 1: Persistent Small Model Services ✅

**Deploy models < 15GB as systemd services** (always loaded)

```
llama-cpp-hermes-2-pro-8b.service   → port 30704
llama-cpp-qwen2.5-14b.service       → port 30705  
llama-cpp-granite-3.0-8b.service    → port 30709
llama-cpp-qwen2.5-32b.service       → port 30703 (when download completes)
```

**Memory footprint: ~37GB** - Fits comfortably in 62GB with OS overhead

**Configuration adjustments:**
- Reduced `n_ctx` from 4096 to 2048 (30% memory reduction)
- Reduced `n_threads` from 16 to 8 (lower CPU contention)

### Phase 2: LiteLLM Orchestration for All Models ⏳

**LiteLLM proxy manages on-demand loading:**
- All 15 models (10 local + 5 cloud) configured
- Small models: immediate response (already loaded)
- Large models: load on first request, unload after idle timeout
- Smart routing based on model capabilities
- OpenAI-compatible API (drop-in replacement)

**Benefits:**
- Full access to all 15 function-calling models
- Memory-efficient: only 2-3 large models loaded at once
- Automatic load balancing
- Graceful degradation if model fails to load

### Phase 3: Optional Multi-VM Distribution

**If LiteLLM on-demand loading proves insufficient:**

Distribute models across both VMs:

**k8s-control (192.168.1.130):**
- Small models (Hermes 8B, Qwen 14B, Granite 8B, Qwen 32B)
- LiteLLM proxy (orchestrator)
- Total: ~37GB

**k8s-worker (192.168.1.131):**
- Large models (Llama 70B, Qwen 72B, Mixtral 8x7B, Mixtral 8x22B)
- Managed by LiteLLM on k8s-control
- On-demand loading: 1-2 models at a time

## Configuration Changes

### Systemd Service Template (Small Models)

```ini
[Service]
ExecStart=/usr/bin/python3.11 -m llama_cpp.server \
    --model /models/MODEL_DIR/MODEL_FILE.gguf \
    --host 0.0.0.0 \
    --port PORT \
    --n_ctx 2048 \        # Reduced from 4096
    --n_threads 8         # Reduced from 16
```

**Memory savings:** ~30% per model via context reduction

### LiteLLM Config (Prepared)

See `/Users/geraldtrotman/Virtualenvs/trotman-enterprises/litellm/config-15-models.yaml`

## Current Status

**Deployed (4/10 local models):**
- ✅ Hermes 2 Pro 8B (port 30704)
- ✅ Qwen 2.5 14B (port 30705)
- ✅ Granite 3.0 8B (port 30709)
- ⏳ Qwen 2.5 32B (downloading: 12GB/19GB, will auto-deploy when complete)

**Downloading (3 large models):**
- Qwen 2.5 72B: 22GB/43GB (51%)
- Mixtral 8x7B: 14GB/26GB (54%)
- Mixtral 8x22B: 20GB/87GB (23%)

**Not Started:**
- Functionary 7B (need correct HuggingFace repo)
- Functionary 70B (need correct HuggingFace repo)

**Disabled (memory constraints):**
- ❌ Llama 3.1 70B systemd service (killed by OOM 21 times, now disabled)
- Will be managed by LiteLLM instead

## Next Steps

1. ✅ Continue downloading remaining models
2. ⏳ Auto-deploy Qwen 32B when download completes
3. 📝 Deploy LiteLLM proxy with all 15 models configured
4. 🧪 Test on-demand loading and smart routing
5. 📊 Monitor memory usage under load
6. 🔍 Locate Functionary model repos and complete deployment

## Lessons Learned

- **Q4_K_M quantization is aggressive but not magic**: 70B models still need ~40GB RAM
- **Bare metal memory limits are hard constraints**: Can't just scale horizontally like cloud
- **Orchestration is mandatory at scale**: Running all models as persistent services doesn't work
- **Context window vs memory trade-off**: Reducing n_ctx from 4096 to 2048 saves ~30% RAM with acceptable UX impact for most use cases
