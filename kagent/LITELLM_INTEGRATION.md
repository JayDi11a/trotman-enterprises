# Kagent LiteLLM Integration

Kagent has been successfully configured to use LiteLLM as a model provider.

## ModelConfigs Created

| Name | Provider | Model | Endpoint |
|------|----------|-------|----------|
| **litellm-hermes-8b** | OpenAI | hermes-2-pro-8b | http://192.168.1.130:4000/v1 |
| **litellm-llama-70b** | OpenAI | llama-3.1-70b | http://192.168.1.130:4000/v1 |
| anthropic-claude | Anthropic | claude-sonnet-4-5 | api.anthropic.com |
| default-model-config | Ollama | llama3.2 | ollama.ollama.svc |
| ollama-phi3 | Ollama | phi3 | ollama.ollama.svc |
| ~~vllm-phi3~~ | OpenAI | *(deprecated)* | ~~:8000~~ |

## Available Agents (17 total)

All agents are **READY** and **ACCEPTED**:

- **argo-rollouts-conversion-agent** - GitOps deployment automation
- **cilium-debug-agent** - Network debugging
- **cilium-manager-agent** - CNI management
- **cilium-policy-agent** - Network policy enforcement
- **helm-agent** - Helm chart operations
- **istio-agent** - Service mesh management
- **k8s-agent** - Kubernetes resource management
- **kgateway-agent** - API gateway operations
- **observability-agent** - Monitoring and logging
- *...and 8 more*

## Access Points

**Kagent UI:** http://192.168.1.130:30090

**API Endpoint:** Via kubectl or Kagent API

## Usage Example

### Create an Agent Task

```yaml
apiVersion: kagent.dev/v1alpha1
kind: AgentTask
metadata:
  name: list-pods-with-llama
  namespace: kagent
spec:
  agentName: k8s-agent
  modelConfigRef: litellm-llama-70b  # Use Llama 70B via LiteLLM
  prompt: "List all pods in the langfuse namespace and summarize their status"
```

### Test with kubectl

```bash
# Create task
kubectl apply -f task.yaml

# Watch status
kubectl get agenttask list-pods-with-llama -n kagent -w

# Get result
kubectl get agenttask list-pods-with-llama -n kagent -o yaml
```

## All 15 LiteLLM Models Available

Via `litellm-hermes-8b` or `litellm-llama-70b` ModelConfig, Kagent can access:

**Local (10 models):**
- hermes-2-pro-8b, qwen2.5-14b, granite-3.0-8b, functionary-small
- qwen2.5-32b, command-r-35b, mixtral-8x7b
- llama-3.1-70b, qwen2.5-72b, mixtral-8x22b

**Cloud (5 models):**
- claude-3-5-sonnet, claude-3-5-haiku
- gpt-4o, gpt-4o-mini
- gemini-2.0-flash

## Next Steps

1. **Update old vllm-phi3 ModelConfig** to use LiteLLM (currently points to :8000)
2. **Create AgentTasks** using new ModelConfigs
3. **Test agent execution** with both small (Hermes 8B) and large (Llama 70B) models
4. **Consider removing Ollama** if all agents work well with LiteLLM

## Architecture

```
Kagent Agents → ModelConfig (litellm-*) → LiteLLM (:4000) → llama.cpp models
                     ↓
              LiteLLM routes to:
              - Hermes 8B (control node)
              - Llama 70B (worker node)
              - 13 other models
```

## Benefits

- **Single integration point**: One ModelConfig can access 15 different models
- **Smart routing**: LiteLLM handles load balancing and fallback
- **Cost optimization**: Use small models for simple tasks, large for complex
- **Model groups**: Can use `function-calling-small`, `-medium`, `-large` aliases
