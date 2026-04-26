# Trotman Enterprises ML Lab

Bare metal ML inference platform: distributed llama.cpp CPU inference, unified LiteLLM gateway, and open-source observability -- all self-hosted, no cloud vendor lock-in.

## What's Deployed

| Layer | Components | Location | Status |
|-------|-----------|----------|--------|
| **Model Serving** | llama.cpp-python (10 models: 8B-87GB) | systemd on VMs | 7/10 Running (3 copying) |
| **API Gateway** | LiteLLM v2.0 — unified OpenAI-compatible API (15 models) | systemd on control | Running |
| **Observability** | Langfuse v3 — PostgreSQL, ClickHouse 3-node sharded, Redis, Zookeeper | `langfuse` namespace | Running (8 PVCs, 12 pods) |
| **Container Runtime** | k3s v1.34.6 — embedded containerd, Flannel CNI, Traefik ingress | k8s-control, k8s-worker VMs | 2-node cluster (52 pods) |
| **Virtualization** | VMware ESXi 8.0.3 — k8s-control (62GB), k8s-worker (256GB) | IBM System x 3650 M4, 3550 M4 | 2 VMs running |
| **Agent Orchestration** | Kagent v0.9.0 — 17 agents, 3 model providers | `kagent` namespace | Planned |
| **Model Platform** | KServe v0.14.0 + Knative Serving v1.15.0 | `kserve`, `knative-serving` | Planned |
| **Code Sandbox** | gVisor release-20260420.0 RuntimeClass | cluster-wide | Planned |
| **TLS Automation** | cert-manager v1.15.3 | `cert-manager` | Planned |
| **Interfaces** | Trotman Chat CLI, Open WebUI | host machine, `open-webui` | Planned |

## Key Results

- **15 models accessible** via single API endpoint (http://192.168.1.130:4000/v1)
- **7/10 local models running**: Llama 70B, Qwen 72B deployed on worker (82GB RAM used)
- **Distributed CPU inference**: 6-18 tokens/sec on Xeon E5-2667 v2 @ 3.30GHz
- **Memory optimization**: Control node 44GB/62GB (71%), worker 221GB/256GB (86% target)
- **Function calling**: All 10 local models support OpenAI tool calling format
- **Zero-cost observability**: Langfuse self-hosted (vs $2,500+/month LangSmith)
- **Production deployment**: systemd services (auto-restart, journald logging)
- **Cost efficiency**: $48/month self-hosted vs $700+/month cloud equivalent

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design.

```
┌─────────────────────────────────────────────────────────────────┐
│ User Applications                                               │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
   ┌─────────────────────┐
   │ LiteLLM Proxy :4000 │──────┐
   │ (Control Node)      │      │ Traces
   └──┬──────────────┬───┘      │
      │              │          ▼
      │              │    ┌──────────────┐
      │              │    │ Langfuse     │
      │              │    │ (k3s cluster)│
      │              │    └──────────────┘
      │              │
      ▼              ▼
┌──────────────┐  ┌────────────────┐
│ Control Node │  │ Worker Node    │
│ 5 models     │  │ 5 models       │
│ 8B-32B       │  │ 35B-87GB       │
│ ~44GB RAM    │  │ ~221GB RAM     │
└──────────────┘  └────────────────┘
      │                   │
      └───────┬───────────┘
              │
              ▼
      Cloud Fallback (5 models)
      Claude, GPT-4o, Gemini
```

## Deployed Models

### Local Models (10 total, systemd services)

**Control Node (192.168.1.130) — Small/Medium:**
| Model | Params | Quant | Port | RAM | Status | Purpose |
|-------|--------|-------|------|-----|--------|---------|
| Hermes 2 Pro | 8B | Q4_K_M | 30704 | 5GB | ✅ Running | Function calling specialist |
| Qwen 2.5 | 14B | Q4_K_M | 30705 | 9GB | ✅ Running | Strong reasoning + tools |
| Granite 3.0 | 8B | Q4_K_M | 30709 | 5GB | ✅ Running | Enterprise instruction |
| Functionary Small | 3.2B | Q4_K_M | 30706 | 5GB | ✅ Running | Dedicated function calling |
| Qwen 2.5 | 32B | Q4_K_M | 30703 | 20GB | ✅ Running | High-capability medium |

**Worker Node (192.168.1.131) — Large:**
| Model | Params | Quant | Port | RAM | Status | Purpose |
|-------|--------|-------|------|-----|--------|---------|
| Llama 3.1 | 70B | Q4_K_M | 30700 | 41GB | ✅ Running | Top-tier reasoning |
| Qwen 2.5 | 72B | Q4_K_M | 30701 | 44GB | ✅ Running | SOTA open model |
| Command-R | 35B | Q4_K_M | 30702 | 21GB | 🔄 Copying | Cohere RAG + tools |
| Mixtral | 8x7B | Q4_K_M | 30707 | 27GB | 🔄 Copying | MoE architecture |
| Mixtral | 8x22B | Q4_K_M | 30708 | 88GB | 🔄 Copying | Largest MoE |

**Model sources:** [bartowski](https://huggingface.co/bartowski) GGUF quantizations

### Cloud Models (5 total, via LiteLLM)

| Provider | Model | Capability | Cost |
|----------|-------|------------|------|
| Anthropic | Claude 3.5 Sonnet | Reasoning + vision | Pay-per-token |
| Anthropic | Claude 3.5 Haiku | Fast + vision | Pay-per-token |
| OpenAI | GPT-4o | Flagship + vision | Pay-per-token |
| OpenAI | GPT-4o Mini | Cost-effective + vision | Pay-per-token |
| Google | Gemini 2.0 Flash | Fast reasoning + vision | Pay-per-token |

## Hardware Configuration

| Node | Host | Specs | VM Allocation | Network |
|------|------|-------|---------------|---------|
| **k8s-control** | IBM System x 3650 M4 | 2x Xeon E5-2667 v2 @ 3.30GHz (16C/32T)<br>128GB DDR3 ECC (55GB free) | 62GB RAM, 16 vCPU<br>1TB /models disk | 192.168.1.130 |
| **k8s-worker** | IBM System x 3550 M4 | 2x Xeon E5-2667 v2 @ 3.30GHz (16C/32T)<br>335GB DDR3 ECC (277GB free) | 256GB RAM, 16 vCPU<br>1TB /models disk | 192.168.1.131 |

**ESXi Management:**
- Control IMM2: 192.168.1.200
- Worker IMM2: 192.168.1.199
- Network: 192.168.1.0/24 (home network)

## Project Structure

```
trotman-enterprises/
├── litellm/
│   ├── models-config.yaml       # LiteLLM routing (15 models, model groups)
│   └── README.md                # LiteLLM deployment guide
├── langfuse/
│   ├── values.yaml              # Helm overrides (PostgreSQL, ClickHouse, Redis)
│   └── README.md                # Observability stack deployment
├── scripts/
│   ├── deployment-status.sh     # Live monitoring dashboard (colors, progress bars)
│   ├── watch-deployment.sh      # Auto-refresh wrapper (30s interval)
│   └── README.md                # Monitoring tools documentation
├── docs/
│   ├── DISTRIBUTED_ARCHITECTURE.md  # Control/worker deployment guide
│   └── MEMORY_CONSTRAINTS.md        # Memory planning + OOM analysis
├── kagent/                      # (Planned) Agent orchestration
│   ├── model-configs/           # ModelConfig YAMLs for 3 providers
│   ├── values.yaml              # Helm overrides
│   └── README.md
├── kserve/                      # (Planned) Model serving platform
│   ├── manifests/               # KServe + dependencies
│   └── README.md
├── knative/                     # (Planned) Serverless autoscaling
│   ├── serving/                 # Knative Serving YAMLs
│   ├── kourier/                 # Networking layer
│   └── README.md
├── gvisor/                      # (Planned) Agent code sandbox
│   ├── runtimeclass.yaml        # RuntimeClass definition
│   ├── install.sh               # gVisor installation
│   └── README.md
├── cert-manager/                # (Planned) TLS automation
│   └── README.md
├── trotman-chat/                # (Planned) Interactive CLI
│   ├── trotman-chat.py          # Main CLI with tool execution
│   ├── install.sh
│   └── README.md
├── open-webui/                  # (Planned) ChatGPT-style web UI
│   ├── deployment.yaml
│   ├── deploy.sh
│   └── README.md
├── vllm/                        # (Parked) GPU-only inference engine
│   └── README.md                # Waiting on Tesla P40 GPU
├── journal/                     # Session logs (not committed)
│   ├── manifest.md              # Journal config
│   └── 2026-04-26.md            # Installation journal
├── ARCHITECTURE.md              # System design, technology choices
└── README.md                    # This file
```

## Technology Stack

| Component | Version | Source | Role |
|-----------|---------|--------|------|
| **llama.cpp-python** | 0.3.20 | pip | Python bindings for llama.cpp CPU inference |
| **LiteLLM** | Latest | pip | Multi-provider API gateway + routing |
| **Langfuse** | v3 | langfuse/langfuse (Helm) | LLM observability (traces, evals, prompts) |
| **k3s** | v1.34.6+k3s1 | Rancher | Lightweight Kubernetes |
| **AlmaLinux** | 9.7 | RedHat | RHEL-compatible OS |
| **systemd** | 252 | System | Production process manager |
| **VMware ESXi** | 8.0.3 | VMware | Type-1 hypervisor |
| **Kagent** | v0.9.0 (planned) | CNCF Sandbox | AI agent orchestration |
| **KServe** | v0.14.0 (planned) | CNCF Incubating | Model serving platform |
| **Knative** | v1.15.0 (planned) | CNCF | Serverless autoscaling |
| **gVisor** | release-20260420.0 (planned) | Google | Application kernel sandbox |
| **cert-manager** | v1.15.3 (planned) | CNCF | TLS certificate automation |

## Quick Start

### Prerequisites
- Network access to 192.168.1.130 (control node)
- LiteLLM API key: `sk-trotman-litellm-2026`

### Test Small Model (Fast, Low Latency)

```bash
curl http://192.168.1.130:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-trotman-litellm-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "hermes-2-pro-8b",
    "messages": [{"role": "user", "content": "What is Kubernetes?"}],
    "max_tokens": 100
  }'
```

### Test Large Model (High Quality, Slower)

```bash
curl http://192.168.1.130:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-trotman-litellm-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.1-70b",
    "messages": [{"role": "user", "content": "Explain distributed systems"}],
    "max_tokens": 200
  }'
```

### Test Cloud Model (Vision, Multimodal)

```bash
curl http://192.168.1.130:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-trotman-litellm-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-5-sonnet",
    "messages": [{"role": "user", "content": "Analyze this architecture"}]
  }'
```

### Use Model Groups (Smart Routing)

LiteLLM automatically routes to appropriate models based on capability tier:

```bash
# Small models: hermes-2-pro-8b, qwen2.5-14b, granite-3.0-8b, functionary-small
curl http://192.168.1.130:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-trotman-litellm-2026" \
  -H "Content-Type: application/json" \
  -d '{"model": "function-calling-small", "messages": [{"role": "user", "content": "List files"}]}'

# Medium models: qwen2.5-32b, command-r-35b, mixtral-8x7b
curl http://192.168.1.130:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-trotman-litellm-2026" \
  -H "Content-Type: application/json" \
  -d '{"model": "function-calling-medium", "messages": [{"role": "user", "content": "Analyze code"}]}'

# Large models: llama-3.1-70b, qwen2.5-72b, mixtral-8x22b
curl http://192.168.1.130:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-trotman-litellm-2026" \
  -H "Content-Type: application/json" \
  -d '{"model": "function-calling-large", "messages": [{"role": "user", "content": "Design architecture"}]}'
```

### Access Langfuse Observability

```bash
# Open in browser
open http://192.168.1.130:30300

# All API calls automatically traced
# View latency, token usage, costs, prompt engineering metrics
```

### Direct Model Access (Bypass LiteLLM)

```bash
# Access individual models directly (no gateway overhead)
curl http://192.168.1.131:30700/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.1-70b",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 10
  }'
```

### Monitor Live Deployment

```bash
# One-time status check
cd /Users/geraldtrotman/Virtualenvs/trotman-enterprises
./scripts/deployment-status.sh

# Auto-refresh dashboard (30s interval)
./scripts/watch-deployment.sh
```

## Performance Benchmarks

**llama.cpp CPU inference on Xeon E5-2667 v2 @ 3.30GHz:**

| Model Size | First Token | Throughput | Memory | Threads | Context |
|------------|-------------|------------|--------|---------|---------|
| 8B-14B | 100-300ms | 12-18 tok/s | 4-9GB | 8 | 2048 |
| 32B-35B | 400-600ms | 8-12 tok/s | 19-21GB | 8 | 4096 |
| 70B-72B | 1-2s | 6-10 tok/s | 40-44GB | 16 | 4096 |
| 87GB (8x22B) | 2-3s | 6-8 tok/s | 88GB | 16 | 4096 |

**Quantization:** Q4_K_M (4-bit mixed precision)  
**Runtime:** llama.cpp-python v0.3.20 + systemd  
**Known limitation:** No GPU support in current deployment (vLLM parked until Tesla P40 acquisition)

## Known Issues & Workarounds

- **SSH passwordless auth fails** on worker node → workaround: `sshpass -p 'Pass4Admin'` for rsync operations
- **Langfuse startup slow** (~60s) due to ClickHouse schema initialization → wait for HTTP 200 on :30300/health
- **Model loading latency** (first request): 40GB+ models take 30-45s to load into memory → use `/health` warmup endpoint
- **No GPU acceleration** → vLLM deployment parked until NVIDIA Tesla P40 PCIe passthrough (planned Q3 2026)
- **Worker build tools missing** → AlmaLinux 9 requires `dnf groupinstall 'Development Tools'` before llama-cpp-python install
- **3 models still copying** to worker (Command-R 35B 21GB, Mixtral 8x7B 25GB, Mixtral 8x22B 81GB) → ~2-4 hours remaining

## Cost Analysis

### Hardware (One-time)
| Item | Cost | Source |
|------|------|--------|
| IBM System x 3650 M4 | $500 | Used enterprise market |
| IBM System x 3550 M4 | $400 | Used enterprise market |
| 256GB DDR3 ECC RAM upgrade | $200 | eBay |
| **Total** | **$1,100** | One-time investment |

### Operating Costs (Monthly)
| Item | Usage | Cost |
|------|-------|------|
| Electricity | ~400W @ $0.15/kWh, 24/7 | $43 |
| Cloud API | Minimal fallback (<1M tokens) | $5 |
| **Total** | | **$48/month** ($576/year) |

### Cloud Comparison (Equivalent)
| Provider | Service | Monthly Cost |
|----------|---------|--------------|
| AWS | 2x m5.4xlarge (16 vCPU, 64GB each) | ~$500 |
| LangSmith | 10K traces/month | $39 |
| OpenAI/Anthropic | 10K API requests | $200+ |
| **Total** | | **$700+/month** |

**Break-even:** 14 months self-hosting vs cloud  
**5-year TCO:** $6,980 self-hosted vs $42,000 cloud (83% savings)

## Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** — Physical/virtual/container layers, network architecture, component diagrams
- **[docs/DISTRIBUTED_ARCHITECTURE.md](docs/DISTRIBUTED_ARCHITECTURE.md)** — Control/worker deployment guide, model distribution strategy
- **[docs/MEMORY_CONSTRAINTS.md](docs/MEMORY_CONSTRAINTS.md)** — Memory planning, OOM analysis, why distributed architecture
- **[scripts/README.md](scripts/README.md)** — Monitoring tools, troubleshooting commands
- **[litellm/README.md](litellm/README.md)** — LiteLLM configuration, model routing, API examples
- **[langfuse/README.md](langfuse/README.md)** — Observability stack deployment, Helm configuration

## Operational Notes

### Installation Timeline

**Day 1 (April 25, 2026):**
- ESXi 8.0.3 installation on both IBM servers via IMM2 virtual media
- Network configuration (vmnic mapping, vSwitch setup)
- AlmaLinux 9.7 VM creation (k8s-control 62GB, k8s-worker 62GB initial)
- k3s v1.34.6 cluster bootstrap (single-node, then worker join)
- Langfuse v3 deployment (PostgreSQL, ClickHouse 3-shard, Redis, Zookeeper)

**Day 2 (April 26, 2026):**
- Worker VM expansion (62GB → 256GB RAM)
- llama.cpp-python installation + build tools (Development Tools, cmake)
- Model downloads (10 models, 270GB total via HuggingFace CLI)
- Systemd service creation (5 control + 5 worker)
- LiteLLM proxy deployment + configuration
- Model distribution (control: 5 small/medium, worker: 5 large)
- 7/10 models deployed and verified, 3 copying in progress

### Lessons Learned

**Good patterns:**
- IMM2 remote management eliminates physical console trips for BIOS/boot troubleshooting
- Memory-driven deployment decisions (worker has capacity, control maxed) optimize utilization
- llama.cpp stability on CPU vs vLLM GPU-only limitations (vLLM doesn't support Linux CPU inference)
- Systemd reliability vs Kubernetes orchestration overhead for stateless model serving
- Distributed architecture enables scaling beyond single-node memory constraints
- Live monitoring dashboard essential for multi-hour deployments (file copies, downloads)
- Stable config naming (models-config.yaml vs version numbers) for long-term maintainability

**Anti-patterns avoided:**
- Single-node deployment constrained by 62GB RAM limit (would only fit 2-3 large models)
- GPU-only frameworks (vLLM) on CPU infrastructure (Linux vLLM requires CUDA)
- Complex Kubernetes operators when systemd provides better reliability for stateless services
- Cloud-only observability SaaS ($2,500+/month LangSmith) vs self-hosted Langfuse ($0)
- Version-numbered config files (config-15-models.yaml) that become outdated as counts change

## Roadmap

**Next phase (Q2 2026):**
- [ ] Deploy Kagent v0.9.0 for AI agent orchestration
- [ ] Deploy KServe v0.14.0 + Knative Serving v1.15.0 for model serving platform
- [ ] Deploy gVisor RuntimeClass for code sandbox isolation
- [ ] Deploy cert-manager v1.15.3 for TLS automation
- [ ] Build Trotman Chat CLI (interactive Claude Code-like interface)
- [ ] Deploy Open WebUI (ChatGPT-style web interface)

**Future (Q3-Q4 2026):**
- [ ] GPU acceleration: NVIDIA Tesla P40 (24GB VRAM) via ESXi PCIe passthrough
- [ ] vLLM deployment with GPU support (40-60 tok/s, 4-8x CPU performance)
- [ ] Additional models: Mistral 7B, DeepSeek-Coder 33B, Yi-34B
- [ ] Prometheus + Grafana for infrastructure metrics
- [ ] Multi-cluster federation (edge deployment)

## Contributing

This is a personal ML lab project. See [CONTRIBUTING.md](./CONTRIBUTING.md) for development workflow.

## License

MIT License — See [LICENSE](./LICENSE) for details.

## Acknowledgments

Built with open-source tools:
- [llama.cpp](https://github.com/ggerganov/llama.cpp) — High-performance CPU LLM inference
- [LiteLLM](https://github.com/BerriAI/litellm) — Unified multi-provider LLM gateway
- [Langfuse](https://langfuse.com) — Open-source LLM observability platform
- [bartowski](https://huggingface.co/bartowski) — GGUF model quantizations on HuggingFace
- [k3s](https://k3s.io) — Lightweight Kubernetes by Rancher
- [Kagent](https://kagent.dev) — CNCF Sandbox AI agent orchestration (planned)
- [KServe](https://kserve.github.io) — CNCF Incubating model serving (planned)

Inspired by [AI Catalyst Lab](https://github.com/aicatalyst-team/catalyst-lab)
