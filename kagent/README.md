# Kagent - Kubernetes-Native AI Agents

Kagent v0.9.0 deployment with 3 model providers and 17 pre-configured agents.

## Installation

```bash
# Add Kagent Helm repository
helm repo add kagent https://langfuse.github.io/langfuse-k8s
helm repo update

# Install Kagent CRDs
helm install kagent-crds oci://ghcr.io/kagent-dev/kagent/helm/kagent-crds \
  --namespace kagent \
  --create-namespace

# Install Kagent with Ollama as default provider
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
helm install kagent oci://ghcr.io/kagent-dev/kagent/helm/kagent \
  --namespace kagent \
  --set providers.default=ollama \
  --set providers.ollama.host=http://ollama.ollama.svc.cluster.local:11434
```

## Model Configurations

### 1. Ollama (Local)

```yaml
apiVersion: kagent.dev/v1alpha2
kind: ModelConfig
metadata:
  name: ollama-phi3
  namespace: kagent
spec:
  model: phi3
  provider: Ollama
  ollama:
    host: http://ollama.ollama.svc.cluster.local:11434
```

### 2. vLLM (Local, OpenAI-compatible)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: vllm-api-key
  namespace: kagent
type: Opaque
stringData:
  VLLM_API_KEY: "not-needed"
---
apiVersion: kagent.dev/v1alpha2
kind: ModelConfig
metadata:
  name: vllm-phi3
  namespace: kagent
spec:
  apiKeySecret: vllm-api-key
  apiKeySecretKey: VLLM_API_KEY
  model: /models/phi-3-mini-4k-instruct.Q4_K_M.gguf
  provider: OpenAI
  openAI:
    baseUrl: "http://192.168.1.130:8000/v1"
```

### 3. Anthropic (Cloud)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: anthropic-api-key
  namespace: kagent
type: Opaque
stringData:
  apiKey: "sk-ant-api03-YOUR-KEY-HERE"
---
apiVersion: kagent.dev/v1alpha2
kind: ModelConfig
metadata:
  name: anthropic-claude
  namespace: kagent
spec:
  apiKeySecret: anthropic-api-key
  apiKeySecretKey: apiKey
  model: claude-sonnet-4-5-20250929
  provider: Anthropic
```

## Deployed Agents

```bash
$ kubectl get agents -n kagent

NAME                             READY   MODEL
argo-rollouts-conversion-agent   1/1     llama3.2
cilium-debug-agent               1/1     llama3.2
cilium-manager-agent             1/1     llama3.2
cilium-policy-agent              1/1     llama3.2
helm-agent                       1/1     llama3.2
istio-agent                      1/1     llama3.2
k8s-agent                        1/1     llama3.2
kgateway-agent                   1/1     llama3.2
observability-agent              1/1     llama3.2
promql-agent                     1/1     llama3.2
```

## Access Kagent UI

```bash
# Port-forward the UI service
kubectl -n kagent port-forward service/kagent-ui 8080:8080

# Open in browser
open http://localhost:8080
```

## Usage Examples

### Query Kubernetes cluster

```bash
# Using kagent CLI or UI
Agent: k8s-agent
Query: "How many pods are running in the kagent namespace?"

# Agent will use kubectl via MCP tools to answer
```

### Deploy application with helm-agent

```bash
Agent: helm-agent
Query: "Install nginx with Helm in the default namespace"

# Agent will execute helm install with proper values
```

## MCP Servers

Kagent includes MCP (Model Context Protocol) servers for tool integration:

- **kagent-tools**: Built-in tools (kubectl, filesystem, etc.)
- **grafana-mcp**: Grafana dashboard queries
- **querydoc**: Documentation search

## Troubleshooting

### Check pod status
```bash
kubectl get pods -n kagent
```

### View agent logs
```bash
kubectl logs -n kagent -l app.kubernetes.io/component=agent -f
```

### Describe ModelConfig
```bash
kubectl describe modelconfig -n kagent ollama-phi3
```

## Resources

- [Kagent Documentation](https://kagent.dev)
- [Kagent GitHub](https://github.com/kagent-dev/kagent)
- [CNCF Sandbox Project](https://www.cncf.io/projects/kagent/)
