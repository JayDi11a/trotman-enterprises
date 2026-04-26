# System Architecture

Detailed technical architecture of the Trotman Enterprises ML Lab.

## Infrastructure Stack

### Physical Layer

```
┌─────────────────────────────────────────────────────────────────┐
│ IBM System x 3650 M4                                            │
│ ├─ 2x Intel Xeon E5-2690 (8C/16T @ 2.9GHz) = 16C/32T total    │
│ ├─ 128GB DDR3 ECC RAM                                          │
│ ├─ VMware ESXi 8.0.3 (IP: 192.168.1.128)                      │
│ └─ IMM2 Remote Management (IP: 192.168.1.200)                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ IBM System x 3550 M4                                            │
│ ├─ 2x Intel Xeon E5-2690 (8C/16T @ 2.9GHz) = 16C/32T total    │
│ ├─ 336GB DDR3 ECC RAM                                          │
│ ├─ VMware ESXi 8.0.3 (IP: 192.168.1.198)                      │
│ └─ IMM2 Remote Management (IP: 192.168.1.199)                 │
└─────────────────────────────────────────────────────────────────┘
```

### Virtualization Layer

```
┌─────────────────────────────────────────────────────────────────┐
│ k8s-control VM (on 3650 M4)                                     │
│ ├─ OS: AlmaLinux 9.7 (RHEL-compatible)                         │
│ ├─ Resources: 62GB RAM, 16 vCPU, 1TB /models disk              │
│ ├─ Role: Small/medium ML models + LiteLLM orchestration        │
│ ├─ IP: 192.168.1.130                                           │
│ └─ Services: 5 llama.cpp models, LiteLLM proxy, k3s (minimal) │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ k8s-worker VM (on 3550 M4)                                      │
│ ├─ OS: AlmaLinux 9.7 (RHEL-compatible)                         │
│ ├─ Resources: 256GB RAM, 16 vCPU, 1TB /models disk             │
│ ├─ Role: Large ML model inference (70B+ parameter models)      │
│ ├─ IP: 192.168.1.131                                           │
│ └─ Services: 4 llama.cpp large models (Llama 70B, Qwen 72B...) │
└─────────────────────────────────────────────────────────────────┘
```

### Container Runtime

```
┌─────────────────────────────────────────────────────────────────┐
│ k3s v1.34.6+k3s1                                                │
│ ├─ Embedded containerd (managed by k3s)                        │
│ ├─ Default runtime: runc (io.containerd.runc.v2)               │
│ ├─ Sandbox runtime: runsc (io.containerd.runsc.v1)             │
│ ├─ CNI: Flannel (embedded)                                     │
│ ├─ Ingress: Traefik (embedded)                                 │
│ └─ Storage: local-path-provisioner (embedded)                  │
└─────────────────────────────────────────────────────────────────┘
```

## Network Architecture

### Cluster Networking

```
192.168.1.0/24 (Home Network)
├─ 192.168.1.254 (Gateway/Router)
├─ 192.168.1.128 (ESXi 3650)
│  └─ 192.168.1.130 (k8s-control VM)
├─ 192.168.1.198 (ESXi 3550)
│  └─ 192.168.1.131 (k8s-worker VM)
├─ 192.168.1.200 (IMM2 3650)
└─ 192.168.1.199 (IMM2 3550)

Pod Network: 10.42.0.0/16 (Flannel)
Service Network: 10.43.0.0/16 (k3s default)
```

### Service Exposure

| Service | Type | Port | Access |
|---------|------|------|--------|
| **LiteLLM Proxy (Unified API)** | systemd | 4000/TCP | http://192.168.1.130:4000 |
| Hermes 2 Pro 8B | systemd | 30704/TCP | http://192.168.1.130:30704 |
| Qwen 2.5 14B | systemd | 30705/TCP | http://192.168.1.130:30705 |
| Granite 3.0 8B | systemd | 30709/TCP | http://192.168.1.130:30709 |
| Functionary Small | systemd | 30706/TCP | http://192.168.1.130:30706 |
| Qwen 2.5 32B | systemd | 30703/TCP | http://192.168.1.130:30703 |
| Llama 3.1 70B | systemd | 30700/TCP | http://192.168.1.131:30700 |
| Qwen 2.5 72B | systemd | 30701/TCP | http://192.168.1.131:30701 |
| Mixtral 8x7B | systemd | 30707/TCP | http://192.168.1.131:30707 |
| Mixtral 8x22B | systemd | 30708/TCP | http://192.168.1.131:30708 |
| Langfuse Web | NodePort | 30300/TCP | http://192.168.1.130:30300 |

## ML Model Serving Architecture

### Distributed llama.cpp + LiteLLM Setup

The ML inference platform uses a distributed architecture with llama.cpp-python for model serving and LiteLLM as a unified API gateway.

```
┌──────────────────────────────────────────────────────────────────────┐
│ User Applications                                                    │
└────────────────────────┬─────────────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────────┐
         │ LiteLLM Proxy (Control Node)      │
         │ http://192.168.1.130:4000/v1      │
         │ OpenAI-compatible API             │
         └───────────┬───────────────────────┘
                     │
         ┌───────────┴────────────┬─────────────────────┐
         │                        │                     │
         ▼                        ▼                     ▼
┌─────────────────┐    ┌──────────────────┐   ┌────────────────┐
│ Control Node    │    │ Worker Node      │   │ Cloud APIs     │
│ Small Models    │    │ Large Models     │   │                │
├─────────────────┤    ├──────────────────┤   ├────────────────┤
│ Hermes 8B       │    │ Llama 70B        │   │ Claude Sonnet  │
│ Qwen 14B        │    │ Qwen 72B         │   │ Claude Haiku   │
│ Granite 8B      │    │ Mixtral 8x7B     │   │ GPT-4o         │
│ Functionary     │    │ Mixtral 8x22B    │   │ GPT-4o Mini    │
│ Qwen 32B        │    │                  │   │ Gemini 2.0     │
│                 │    │                  │   │                │
│ ~42GB RAM used  │    │ ~196GB RAM used  │   │                │
└─────────────────┘    └──────────────────┘   └────────────────┘
```

### Model Distribution Strategy

**Control Node (192.168.1.130) - 62GB RAM:**
- **Purpose**: Fast-response small/medium models + API orchestration
- **Models**: 5 local models (8B-32B parameter range)
- **Memory**: ~42GB used, 20GB free
- **Response time**: <500ms first token for most queries

**Worker Node (192.168.1.131) - 256GB RAM:**
- **Purpose**: High-quality large model inference
- **Models**: 4 large models (70B+ parameter range)
- **Memory**: ~196GB when all loaded, 60GB free
- **Response time**: 1-3s first token, maximum quality

**Cloud Providers:**
- **Purpose**: Fallback, vision models, ultra-high quality
- **Models**: Claude 3.5 (Sonnet/Haiku), GPT-4o, Gemini 2.0
- **Cost**: Pay-per-token, used selectively

### Technology Stack

**Model Runtime:**
- **llama.cpp-python**: Python bindings for llama.cpp
- **GGUF Q4_K_M quantization**: 4-bit quantization, ~40GB for 70B models
- **Systemd services**: Production deployment, auto-restart on failure
- **CPU inference**: 8-15 tokens/sec on Xeon E5-2690 processors

**API Gateway:**
- **LiteLLM**: Unified OpenAI-compatible API for all models
- **Smart routing**: Route by model capability and size
- **Load balancing**: Round-robin across endpoints
- **Failover**: Automatic fallback to cloud if local fails

**Monitoring:**
- **Live dashboard**: Real-time deployment status
- **Systemd journald**: Centralized logging
- **Resource tracking**: Memory, CPU, tokens/sec metrics

See [`docs/DISTRIBUTED_ARCHITECTURE.md`](docs/DISTRIBUTED_ARCHITECTURE.md) for detailed deployment guide.

## Component Architecture

### 1. Agent Orchestration (Kagent)

```mermaid
graph TB
    subgraph "Kagent Namespace"
        UI["kagent-ui<br/>Web Interface"]
        CTRL["kagent-controller<br/>K8s Operator"]
        ENGINE["kagent-engine<br/>Agent Runtime"]
        KMCP["kagent-kmcp-manager<br/>MCP Controller"]
        
        AGENTS["17 Agent Pods<br/>k8s, helm, istio, etc."]
        TOOLS["Tool Servers<br/>grafana-mcp, querydoc"]
        
        UI --> CTRL
        CTRL --> ENGINE
        ENGINE --> AGENTS
        KMCP --> TOOLS
        AGENTS --> TOOLS
    end
    
    subgraph "Model Configs"
        MC1["ollama-phi3<br/>Ollama Provider"]
        MC2["vllm-phi3<br/>OpenAI Provider"]
        MC3["anthropic-claude<br/>Anthropic Provider"]
    end
    
    subgraph "External Services"
        OLLAMA["Ollama Pod<br/>ollama namespace"]
        VLLM["vLLM Server<br/>Host: 192.168.1.130:8000"]
        ANTHROPIC["Anthropic API<br/>claude.ai"]
    end
    
    AGENTS --> MC1 --> OLLAMA
    AGENTS --> MC2 --> VLLM
    AGENTS --> MC3 --> ANTHROPIC
```

**Key Components:**
- **kagent-controller**: Reconciles Agent, ModelConfig, ToolServer CRDs
- **kagent-engine**: Executes agent logic, manages tool calls
- **kagent-ui**: Web dashboard for agent management
- **kagent-kmcp-manager**: MCP (Model Context Protocol) server lifecycle
- **Built-in agents**: 17 pre-configured agents for k8s operations

### 2. Model Serving (KServe + vLLM)

```mermaid
graph LR
    subgraph "Client Layer"
        API_CLIENTS["API Clients<br/>curl, SDKs"]
    end
    
    subgraph "KServe Namespace"
        KSERVE_CTRL["kserve-controller<br/>InferenceService Reconciler"]
        KSERVE_LOCAL["kserve-localmodel-controller<br/>Local Model Management"]
    end
    
    subgraph "Knative Serving"
        ACTIVATOR["activator<br/>Scale-from-zero"]
        AUTOSCALER["autoscaler<br/>Request-based HPA"]
        CONTROLLER["controller<br/>Revision management"]
    end
    
    subgraph "Inference Backends"
        VLLM["vLLM Server<br/>Phi-3 Mini Q4<br/>8 tok/s"]
    end
    
    API_CLIENTS --> KSERVE_CTRL
    KSERVE_CTRL --> ACTIVATOR
    ACTIVATOR --> AUTOSCALER
    AUTOSCALER --> VLLM
    CONTROLLER --> VLLM
```

**vLLM Configuration:**
```bash
python3 -m llama_cpp.server \
  --model /models/phi-3-mini-4k-instruct.Q4_K_M.gguf \
  --host 0.0.0.0 \
  --port 8000 \
  --n_ctx 4096 \
  --n_gpu_layers 0  # CPU-only
```

### 3. Observability (Langfuse)

```mermaid
graph TB
    subgraph "Application Layer"
        LANGCHAIN["LangChain Apps<br/>Auto-instrumented"]
        KAGENT["Kagent Agents<br/>Manual traces"]
    end
    
    subgraph "Langfuse Namespace"
        WEB["langfuse-web<br/>NodePort :30300"]
        WORKER["langfuse-worker<br/>Async processing"]
        
        PG["PostgreSQL<br/>Metadata, users, projects"]
        CH_SHARD0["ClickHouse Shard 0<br/>3 replicas"]
        CH_SHARD1["ClickHouse Shard 1<br/>3 replicas (optional)"]
        REDIS["Redis<br/>Cache, queues"]
        ZK["Zookeeper<br/>3 nodes"]
        S3["S3 (MinIO)<br/>Artifacts"]
        
        WEB --> PG
        WEB --> CH_SHARD0
        WEB --> REDIS
        WORKER --> PG
        WORKER --> CH_SHARD0
        WORKER --> S3
        
        CH_SHARD0 --> ZK
    end
    
    LANGCHAIN -->|"OTLP/HTTP"| WEB
    KAGENT -->|"OTLP/HTTP"| WEB
```

**Data Flow:**
1. LangChain SDK auto-instruments all LLM calls
2. Traces sent to Langfuse via OTLP
3. Metadata stored in PostgreSQL (users, projects, prompts)
4. Trace data stored in ClickHouse (high-volume time-series)
5. Redis caches recent queries
6. S3 stores large artifacts (datasets, fine-tuning data)

### 4. Code Sandboxing (gVisor)

```mermaid
graph TB
    subgraph "Container Runtime"
        CONTAINERD["containerd"]
        
        subgraph "Runtime Handlers"
            RUNC["runc<br/>Default runtime"]
            RUNSC["runsc<br/>gVisor runtime"]
        end
        
        CONTAINERD --> RUNC
        CONTAINERD --> RUNSC
    end
    
    subgraph "Pods"
        NORMAL_POD["Normal Pod<br/>runtimeClassName: default"]
        SANDBOX_POD["Sandboxed Pod<br/>runtimeClassName: gvisor"]
    end
    
    RUNC --> NORMAL_POD
    RUNSC --> SANDBOX_POD
    
    subgraph "Kernel"
        LINUX_KERNEL["Linux Kernel"]
        GVISOR_KERNEL["gVisor Application Kernel<br/>User-space syscall intercept"]
    end
    
    NORMAL_POD --> LINUX_KERNEL
    SANDBOX_POD --> GVISOR_KERNEL
    GVISOR_KERNEL -.->|"Limited syscalls"| LINUX_KERNEL
```

**gVisor RuntimeClass:**
```yaml
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: gvisor
handler: runsc
```

**Usage:**
```yaml
spec:
  runtimeClassName: gvisor  # Adds application kernel isolation
```

## Data Persistence

### Storage Classes

```
┌─────────────────────────────────────────────────────────────────┐
│ local-path (k3s default)                                        │
│ ├─ Type: hostPath with dynamic provisioning                    │
│ ├─ Location: /var/lib/rancher/k3s/storage/                    │
│ ├─ Used by: PostgreSQL, ClickHouse, Redis, models             │
│ └─ Limitations: Node-affinity (not portable across nodes)     │
└─────────────────────────────────────────────────────────────────┘
```

### Persistent Volumes

| Component | PVC Name | Size | Mount Path |
|-----------|----------|------|------------|
| PostgreSQL | langfuse-postgresql | 8Gi | /bitnami/postgresql |
| ClickHouse Shard 0-0 | data-langfuse-clickhouse-shard0-0 | 8Gi | /bitnami/clickhouse |
| ClickHouse Shard 0-1 | data-langfuse-clickhouse-shard0-1 | 8Gi | /bitnami/clickhouse |
| ClickHouse Shard 0-2 | data-langfuse-clickhouse-shard0-2 | 8Gi | /bitnami/clickhouse |
| Redis | redis-data-langfuse-redis-primary-0 | 8Gi | /data |
| Zookeeper 0 | data-langfuse-zookeeper-0 | 8Gi | /bitnami/zookeeper |
| Zookeeper 1 | data-langfuse-zookeeper-1 | 8Gi | /bitnami/zookeeper |
| Zookeeper 2 | data-langfuse-zookeeper-2 | 8Gi | /bitnami/zookeeper |

## Security Architecture

### Authentication & Authorization

```
┌─────────────────────────────────────────────────────────────────┐
│ Kubernetes RBAC                                                 │
│ ├─ ServiceAccounts per namespace                               │
│ ├─ Kagent: scoped RBAC (read cluster, write kagent ns)        │
│ ├─ KServe: cluster-admin for CRD management                   │
│ └─ Langfuse: namespace-scoped (langfuse only)                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ API Authentication                                              │
│ ├─ vLLM: No auth (internal network only)                      │
│ ├─ Ollama: No auth (cluster-internal only)                    │
│ ├─ Anthropic: API key in Kubernetes Secret                    │
│ └─ Langfuse: NextAuth.js (email/password, OAuth)              │
└─────────────────────────────────────────────────────────────────┘
```

### Network Policies

Currently: **Open** (all pods can communicate)

Future considerations:
- Restrict Ollama to kagent namespace only
- Isolate Langfuse data plane from public access
- Implement NetworkPolicies for zero-trust

### Secrets Management

```yaml
kagent/anthropic-api-key:
  apiKey: sk-ant-api03-...

kagent/vllm-api-key:
  VLLM_API_KEY: not-needed

langfuse/langfuse-secrets:
  NEXTAUTH_SECRET: <auto-generated>
  SALT: <auto-generated>
```

## Performance Characteristics

### Resource Utilization (Idle)

| Node | CPU Usage | Memory Usage | Pods |
|------|-----------|--------------|------|
| k8s-control | ~2 cores (12.5%) | ~18GB (28%) | 35 |
| k8s-worker | ~1 core (6.25%) | ~12GB (18%) | 17 |

### vLLM Performance (Phi-3 Mini Q4 on Xeon E5-2690)

```
Model: Phi-3 Mini 4K Instruct Q4
Size: 2.3GB
Context: 4096 tokens
Quantization: Q4_K_M

Metrics:
├─ First token latency: 800ms
├─ Throughput: ~8 tokens/sec
├─ Memory footprint: ~4GB
└─ CPU utilization: 100% (1 core)
```

### Langfuse Data Volume

```
Expected trace volume: ~100/day (development)
├─ PostgreSQL: <100MB/month (metadata)
├─ ClickHouse: ~500MB/month (traces)
└─ Redis: ~50MB (cache)

Production estimate: ~10K traces/day
├─ PostgreSQL: ~1GB/month
├─ ClickHouse: ~50GB/month
└─ Retention: 400 days (configurable)
```

## Scaling Strategy

### Horizontal Scaling

**Current:** Single replica for all services

**Future:** Scale-out targets
- vLLM: Add replicas on k8s-worker (load-balanced)
- Ollama: Add model-specific deployments (llama3, mistral, etc.)
- Langfuse workers: 3-5 replicas for async processing
- ClickHouse: Add shard 1 for >100K traces/day

### Vertical Scaling

**Current:** Fixed VM resources (64GB/16vCPU)

**Options:**
- Increase VM RAM to 128GB (3650 M4 has capacity)
- Increase worker VM to 256GB (3550 M4 has capacity)
- Reduce control plane workloads (offload to worker)

### GPU Acceleration

**Future:** Pass-through NVIDIA Tesla P40 (12GB VRAM)
- ESXi supports GPU passthrough (vDGA)
- Target: 40-60 tokens/sec with FP16 models
- Requires: PCIe slot, power budget, driver setup

## Disaster Recovery

### Backup Strategy

**Not yet implemented**

Recommended:
```bash
# PostgreSQL (Langfuse metadata)
pg_dump -h langfuse-postgresql -U postgres langfuse > langfuse-backup.sql

# ClickHouse (trace data)
clickhouse-client --query "BACKUP DATABASE default TO Disk('backups', 'backup.zip')"

# Kubernetes manifests
kubectl get all --all-namespaces -o yaml > cluster-backup.yaml

# Model files
rsync -av /models/ backup-server:/models-backup/
```

### Recovery Plan

1. **VM failure:** Rebuild from AlmaLinux ISO + k3s install script
2. **k3s failure:** `systemctl restart k3s`
3. **Database corruption:** Restore from pg_dump/ClickHouse backup
4. **Model loss:** Re-download from Hugging Face
5. **Config loss:** Re-apply from Git repository

## Monitoring & Alerting

### Current State

**No infrastructure monitoring** (Prometheus/Grafana not deployed)

### Available Metrics

- Langfuse UI: Trace latency, token usage, cost
- Kagent UI: Agent execution logs
- kubectl top: CPU/memory per pod
- vLLM: OpenAI-compatible `/metrics` endpoint

### Future Integration

```
Prometheus → Grafana
├─ Node metrics (node-exporter)
├─ Pod metrics (kubelet cAdvisor)
├─ vLLM metrics (/metrics endpoint)
└─ Langfuse metrics (custom exporter)

Alerting:
├─ vLLM down (>5min)
├─ Langfuse PostgreSQL storage >80%
├─ Node CPU >90% (sustained)
└─ Pod OOMKilled events
```

## Cost Analysis

### Hardware (One-time)

| Item | Cost | Notes |
|------|------|-------|
| IBM System x 3650 M4 | $500 | Used server market |
| IBM System x 3550 M4 | $400 | Used server market |
| RAM upgrades | $200 | 256GB DDR3 ECC |
| Network switch | $50 | Gigabit switch |
| **Total** | **$1,150** | One-time investment |

### Operating Costs (Monthly)

| Item | Cost | Notes |
|------|------|-------|
| Electricity (~400W @ $0.15/kWh) | $43 | 24/7 operation |
| Internet | $0 | Home network |
| Anthropic API (minimal) | $5 | ~1M tokens/month |
| **Total** | **$48/month** | **$576/year** |

### Cloud Comparison (Equivalent)

| Provider | Monthly Cost | Notes |
|----------|--------------|-------|
| AWS EKS (2x m5.4xlarge) | ~$500 | 16 vCPU, 64GB RAM each |
| LangSmith Cloud (10K traces) | $39 | Self-hosted = $0 |
| GPU instances (optional) | +$500 | Self-hosted = future investment |
| **Total** | **$1,000+/month** | **vs $48/month** |

**Break-even:** ~14 months of self-hosting = cloud costs

## Technology Choices

### Why k3s over k8s?

- **Simplicity:** Single binary, no external dependencies
- **Resource efficiency:** Lower memory footprint (~500MB vs 2GB)
- **Built-in components:** Traefik, local-path-provisioner, CoreDNS
- **Production-ready:** CNCF certified Kubernetes distribution

### Why vLLM over llama.cpp?

- **Performance:** 2-3x faster on CPU (PagedAttention, continuous batching)
- **OpenAI API:** Drop-in replacement for OpenAI SDK
- **Scalability:** Supports distributed inference (future GPU)
- **Ecosystem:** Native KServe integration

### Why Langfuse over LangSmith?

- **Cost:** $0 vs $2,500+/month at scale
- **Data ownership:** Full SQL access, no vendor lock-in
- **Open source:** MIT license, active community
- **Framework-agnostic:** Works with any LLM framework

### Why Kagent over custom agents?

- **Kubernetes-native:** CRDs, RBAC, declarative manifests
- **Multi-provider:** Ollama, vLLM, Anthropic in single platform
- **MCP support:** Integrates with Model Context Protocol servers
- **CNCF project:** Accepted to CNCF Sandbox (May 2025)

## Future Architecture Evolution

### Phase 2: GPU Acceleration (Q3 2026)

```
Add: NVIDIA Tesla P40 (12GB VRAM)
├─ ESXi GPU passthrough to k8s-worker VM
├─ vLLM with CUDA support
├─ Expected: 40-60 tok/s (5-7x improvement)
└─ Larger models: Llama 3 70B (quantized to FP8)
```

### Phase 3: Multi-Cluster (Q4 2026)

```
Add: 3rd node (edge cluster)
├─ Federated learning across sites
├─ KServe multi-cluster routing
└─ Disaster recovery (geo-redundancy)
```

### Phase 4: Production Hardening (2027)

```
Add:
├─ Istio service mesh (mTLS, traffic policies)
├─ ArgoCD for GitOps (declarative deployments)
├─ Prometheus + Grafana (full observability)
├─ Velero backups (automated snapshots)
└─ NetworkPolicies (zero-trust networking)
```
