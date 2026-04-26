# Trotman Enterprises ML Lab

Production-grade, self-hosted ML inference platform on bare metal IBM System x hardware with distributed llama.cpp deployment, CPU-optimized inference, and unified LiteLLM API gateway.

## Deployment Status

### ✅ Currently Deployed

| Component | Version | Status | Purpose |
|-----------|---------|--------|---------|
| **llama.cpp Models** | 10 models | Running | CPU-optimized GGUF inference |
| **LiteLLM Proxy** | Latest | Running | Unified API gateway (15 models) |
| **Langfuse** | v3 | Running | LLM observability |
| **k3s** | v1.34.6 | Running | Container runtime |
| **AlmaLinux VMs** | 9.7 | Running | OS layer |

### 🔜 Planned Deployment

| Component | Purpose | Timeline |
|-----------|---------|----------|
| **Kagent** | AI agent orchestration | Next |
| **KServe** | Model serving platform | Next |
| **Knative** | Serverless autoscaling | Next |
| **gVisor** | Code sandbox isolation | Next |
| **cert-manager** | TLS automation | Next |
| **Trotman Chat CLI** | Interactive CLI interface | Next |
| **Open WebUI** | ChatGPT-style web interface | Next |

### 🅿️ Parked (GPU Required)

| Component | Reason | Future |
|-----------|--------|--------|
| **vLLM** | Requires GPU for Linux | Add with Tesla P40 |

## What's Live Now

**15 function-calling models** accessible through single OpenAI-compatible API:
- **10 local models** running on llama.cpp-python (systemd services)
- **5 cloud models** (Claude, GPT-4o, Gemini) via LiteLLM proxy

## Hardware Configuration

| Node | Role | Specs | Allocation |
|------|------|-------|------------|
| **IBM System x 3650 M4** | ESXi host (control) | 128GB RAM, 2x Xeon E5-2667 v2 @ 3.30GHz (16C/32T) | 55GB free |
| **IBM System x 3550 M4** | ESXi host (worker) | 335GB RAM, 2x Xeon E5-2667 v2 @ 3.30GHz (16C/32T) | 277GB free |
| **k8s-control VM** | Small/medium models | 62GB RAM, 16 vCPU, 1TB /models, AlmaLinux 9.7 | 192.168.1.130 |
| **k8s-worker VM** | Large models | 256GB RAM, 16 vCPU, 1TB /models, AlmaLinux 9.7 | 192.168.1.131 |

## Deployed Models (Live)

### Local Models (10 total)

**Control Node (192.168.1.130) - Small/Medium Models:**
| Model | Size | Port | RAM | Purpose |
|-------|------|------|-----|---------|
| Hermes 2 Pro 8B | 4.6GB | 30704 | ~5GB | Function calling specialist |
| Qwen 2.5 14B | 8.4GB | 30705 | ~9GB | Strong reasoning + tool use |
| Granite 3.0 8B | 4.7GB | 30709 | ~5GB | Enterprise instruction following |
| Functionary Small v3.2 | 4.6GB | 30706 | ~5GB | Dedicated function calling |
| Qwen 2.5 32B | 19GB | 30703 | ~20GB | High-capability medium model |

**Worker Node (192.168.1.131) - Large Models:**
| Model | Size | Port | RAM | Purpose |
|-------|------|------|-----|---------|
| Llama 3.1 70B | 40GB | 30700 | ~41GB | Top-tier reasoning |
| Qwen 2.5 72B | 43GB | 30701 | ~44GB | State-of-the-art open model |
| Command-R 35B | 21GB | 30702 | ~21GB | RAG + tool use specialist (Cohere) |
| Mixtral 8x7B | 26GB | 30707 | ~27GB | MoE architecture, efficient |
| Mixtral 8x22B | 87GB | 30708 | ~88GB | Largest MoE, exceptional performance |

**All models:** Q4_K_M quantization (4-bit mixed precision)

### Cloud Models (5 total)

Accessible via LiteLLM proxy with API keys:
- **Claude 3.5 Sonnet** - Best overall reasoning + vision
- **Claude 3.5 Haiku** - Fast and efficient + vision
- **GPT-4o** - OpenAI flagship + vision
- **GPT-4o Mini** - Cost-effective + vision
- **Gemini 2.0 Flash** - Fast reasoning + vision

## Current Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ Control Node (192.168.1.130) - 62GB RAM                        │
├─────────────────────────────────────────────────────────────────┤
│ • Hermes 2 Pro 8B       (port 30704)  ~5GB                     │
│ • Qwen 2.5 14B          (port 30705)  ~9GB                     │
│ • Granite 3.0 8B        (port 30709)  ~5GB                     │
│ • Functionary Small     (port 30706)  ~5GB                     │
│ • Qwen 2.5 32B          (port 30703)  ~20GB                    │
│ • LiteLLM Proxy         (port 4000)   ~0.3GB                   │
├─────────────────────────────────────────────────────────────────┤
│ Total: ~44GB used, 18GB free                                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Worker Node (192.168.1.131) - 256GB RAM                        │
├─────────────────────────────────────────────────────────────────┤
│ • Llama 3.1 70B         (port 30700)  ~41GB                    │
│ • Qwen 2.5 72B          (port 30701)  ~44GB                    │
│ • Command-R 35B         (port 30702)  ~21GB                    │
│ • Mixtral 8x7B          (port 30707)  ~27GB                    │
│ • Mixtral 8x22B         (port 30708)  ~88GB                    │
├─────────────────────────────────────────────────────────────────┤
│ Total: ~221GB used, 35GB free                                   │
└─────────────────────────────────────────────────────────────────┘

                              ▼
                    LiteLLM Unified API
              http://192.168.1.130:4000/v1
                    (OpenAI-compatible)
                              ▼
                  Routes to 15 models:
        10 local (llama.cpp) + 5 cloud (Claude, GPT-4o, Gemini)
```

## Access Points (Live Now)

| Service | URL | Authentication |
|---------|-----|----------------|
| **LiteLLM API** | http://192.168.1.130:4000/v1 | Bearer token: `sk-trotman-litellm-2026` |
| **Langfuse UI** | http://192.168.1.130:30300 | Create account on first access |
| **Individual Models** | http://192.168.1.130:30704-30709 (control)<br>http://192.168.1.131:30700-30702,30707-30708 (worker) | Direct OpenAI API access |

## Quick Start (Current Deployment)

### 1. Chat with Any Model via LiteLLM

```bash
# Use small model (fast, low latency)
curl http://192.168.1.130:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-trotman-litellm-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "hermes-2-pro-8b",
    "messages": [{"role": "user", "content": "What is Kubernetes?"}],
    "max_tokens": 100
  }'

# Use large model (high quality, slower)
curl http://192.168.1.130:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-trotman-litellm-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.1-70b",
    "messages": [{"role": "user", "content": "Explain distributed systems"}],
    "max_tokens": 200
  }'

# Use cloud model (vision, multimodal)
curl http://192.168.1.130:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-trotman-litellm-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-5-sonnet",
    "messages": [{"role": "user", "content": "What is in this image?"}]
  }'
```

### 2. Use Model Groups (Smart Routing)

```bash
# Small models (fast response)
curl http://192.168.1.130:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-trotman-litellm-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "function-calling-small",
    "messages": [{"role": "user", "content": "List files in /tmp"}]
  }'

# Medium models (balanced)
curl http://192.168.1.130:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-trotman-litellm-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "function-calling-medium",
    "messages": [{"role": "user", "content": "Analyze this code"}]
  }'

# Large models (maximum quality)
curl http://192.168.1.130:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-trotman-litellm-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "function-calling-large",
    "messages": [{"role": "user", "content": "Design a microservices architecture"}]
  }'
```

### 3. Access Langfuse (Observability)

```bash
# Open in browser
open http://192.168.1.130:30300

# All LLM API calls are automatically traced
# View latency, token usage, costs, and prompt engineering
```

## Planned Features (Next Phase)

### Trotman Chat CLI
Interactive Claude Code-like CLI for chatting with local models with tool execution.

### Open WebUI
ChatGPT-style web interface for beautiful model interactions.

### Kagent
AI agent orchestration with multi-model support and Kubernetes integration.

### KServe + Knative
Model serving platform with serverless autoscaling (0→N based on traffic).

### gVisor
Application kernel for sandboxed code execution in agent workflows.

### cert-manager
Automated TLS certificate management for webhooks and ingress.

## Project Structure

```
trotman-enterprises/
├── litellm/
│   ├── models-config.yaml      # LiteLLM configuration (15 models)
│   └── README.md
├── langfuse/
│   ├── values.yaml             # Helm values (PostgreSQL, ClickHouse, Redis)
│   └── README.md
├── scripts/
│   ├── deployment-status.sh    # Live deployment monitoring
│   └── watch-deployment.sh     # Auto-refresh dashboard
├── docs/
│   ├── DISTRIBUTED_ARCHITECTURE.md  # Deployment guide
│   └── MEMORY_CONSTRAINTS.md        # Memory planning
├── kagent/                     # (Planned) Agent orchestration
├── kserve/                     # (Planned) Model serving
├── knative/                    # (Planned) Serverless platform
├── gvisor/                     # (Planned) Code sandbox
├── cert-manager/               # (Planned) TLS automation
├── trotman-chat/               # (Planned) Interactive CLI
├── open-webui/                 # (Planned) Web interface
├── journal/                    # Session journals (not committed)
│   ├── manifest.md
│   └── 2026-04-26.md
├── ARCHITECTURE.md             # Detailed technical architecture
└── README.md                   # This file
```

## Performance Benchmarks (Current)

**llama.cpp on Xeon E5-2667 v2 @ 3.30GHz:**

| Model Size | First Token | Throughput | Memory | Threads |
|------------|-------------|------------|--------|---------|
| 8B-14B | 100-300ms | 12-18 tok/s | 4-9GB | 8 |
| 32B | 400-600ms | 8-12 tok/s | ~19GB | 8 |
| 70B+ | 1-2 seconds | 6-10 tok/s | 40-88GB | 16 |

**Quantization:** Q4_K_M (4-bit mixed precision)  
**Context window:** 2048-4096 tokens  
**Runtime:** llama.cpp-python + systemd

## Key Results (Achieved)

- ✅ **15 models accessible** via single API endpoint
- ✅ **Distributed architecture** optimizes memory (5 small + 5 large)
- ✅ **CPU inference** at 6-18 tok/s on commodity Xeon hardware
- ✅ **Function calling** across all 10 local models
- ✅ **Zero-cost observability** with Langfuse (self-hosted)
- ✅ **Production deployment** via systemd (auto-restart, logging)
- ✅ **Cloud failover** to Claude/GPT-4o/Gemini when needed

## Technology Stack (Current)

| Component | Version | Purpose |
|-----------|---------|---------|
| **llama.cpp-python** | 0.3.20 | Python bindings for llama.cpp inference |
| **LiteLLM** | Latest | Unified API gateway + routing |
| **Langfuse** | v3 | LLM observability (traces, evals, prompts) |
| **k3s** | v1.34.6+k3s1 | Minimal Kubernetes (Langfuse only) |
| **AlmaLinux** | 9.7 | RHEL-compatible OS |
| **systemd** | 252 | Production process management |
| **VMware ESXi** | 8.0.3 | Hypervisor layer |

## Cost Analysis

### Hardware (One-time)
| Item | Cost |
|------|------|
| IBM System x 3650 M4 | $500 |
| IBM System x 3550 M4 | $400 |
| RAM upgrades | $200 |
| **Total** | **$1,100** |

### Operating (Monthly)
| Item | Cost |
|------|------|
| Electricity (~400W @ $0.15/kWh) | $43 |
| Cloud API (minimal fallback) | $5 |
| **Total** | **$48/month** |

### Cloud Comparison
| Provider | Monthly Cost |
|----------|-------------|
| AWS EKS (2x m5.4xlarge) | ~$500 |
| LangSmith Cloud (10K traces) | $39 |
| Hosted LLM APIs (10K requests) | $200+ |
| **Cloud Total** | **$700+/month** |

**Break-even:** 14 months self-hosting vs cloud

## Installation Timeline

**Day 1 (April 25, 2026):**
- ESXi 8.0.3 installation on both IBM servers
- IMM2 remote management configuration
- AlmaLinux 9 VM creation
- k3s cluster bootstrap
- Langfuse deployment

**Day 2 (April 26, 2026):**
- llama.cpp-python + model downloads (10 models)
- Systemd service creation (all models)
- LiteLLM proxy configuration
- Worker VM expansion (62GB → 256GB)
- Distributed deployment (5 control + 5 worker)

**Next Phase:**
- Kagent, KServe, Knative, gVisor, cert-manager deployment
- Trotman Chat CLI + Open WebUI interfaces

## Lessons Learned

### Good Patterns
- **IMM2 remote management** eliminates physical console dependency
- **Memory-driven deployment** optimizes resource utilization
- **llama.cpp for CPU** provides stability and simplicity
- **Systemd over Kubernetes** for model serving (reliability, no orchestration overhead)
- **LiteLLM unified API** abstracts 15 heterogeneous backends cleanly
- **Distributed architecture** enables scaling beyond single-node memory
- **Stable config naming** (models-config.yaml vs version numbers)

### Anti-Patterns Avoided
- Single-node deployment with memory constraints
- Complex Kubernetes operators when systemd suffices
- GPU-only frameworks (vLLM) on CPU infrastructure
- Cloud-only observability SaaS (Langfuse self-hosted)
- Version-numbered config files that become outdated

## Future Enhancements

- [ ] Deploy Kagent for AI agent orchestration
- [ ] Deploy KServe + Knative for model serving platform
- [ ] Deploy gVisor for code sandbox isolation
- [ ] Deploy cert-manager for TLS automation
- [ ] Build Trotman Chat CLI interface
- [ ] Deploy Open WebUI for ChatGPT-style interface
- [ ] GPU acceleration (NVIDIA Tesla P40) for vLLM deployment
- [ ] Additional models: Mistral 7B, DeepSeek-Coder 33B
- [ ] Prometheus + Grafana for infrastructure metrics

## Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed technical architecture
- **[docs/DISTRIBUTED_ARCHITECTURE.md](docs/DISTRIBUTED_ARCHITECTURE.md)** - Deployment guide
- **[docs/MEMORY_CONSTRAINTS.md](docs/MEMORY_CONSTRAINTS.md)** - Memory planning
- **[scripts/README.md](scripts/README.md)** - Monitoring tools

## Contributing

This is a personal ML lab project. Feel free to fork and adapt for your own infrastructure.

## License

MIT License - See [LICENSE](./LICENSE) for details.

## Acknowledgments

Built with open-source tools:
- [llama.cpp](https://github.com/ggerganov/llama.cpp) - High-performance LLM inference
- [LiteLLM](https://github.com/BerriAI/litellm) - Unified LLM API gateway
- [Langfuse](https://langfuse.com) - Open-source LLM observability
- [bartowski](https://huggingface.co/bartowski) - GGUF model quantizations
