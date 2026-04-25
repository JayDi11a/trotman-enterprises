# Open WebUI - ChatGPT-like Interface for Local LLMs

Modern, feature-rich web interface for your local inference servers (vLLM + Ollama).

## Features

- 🎨 Beautiful ChatGPT-style interface
- 👥 Multi-user support with authentication
- 💬 Chat history and conversations
- 📄 Document upload (RAG capabilities)
- 🔧 Model management
- 🌐 Works with OpenAI-compatible APIs (vLLM) AND Ollama
- 🖼️ Image generation support
- 📱 Mobile responsive
- 🔍 Web search integration
- 🎤 Voice input/output

## Quick Start

### 1. Deploy to Kubernetes

```bash
# Deploy Open WebUI
kubectl apply -f deployment.yaml

# Wait for pod to be ready
kubectl wait --for=condition=ready pod -l app=open-webui -n open-webui --timeout=120s

# Check status
kubectl get pods -n open-webui
```

### 2. Access the UI

Open in your browser:
```
http://192.168.1.130:30080
```

**First time setup:**
1. Create an admin account (first user = admin)
2. Login with your credentials
3. Start chatting!

### 3. Configure Models

Open WebUI auto-discovers models from:
- **Ollama**: Models available at `http://ollama.ollama.svc.cluster.local:11434`
- **vLLM (OpenAI-compatible)**: Models at `http://192.168.1.130:8000/v1`

**To add vLLM model:**
1. Click Settings (gear icon) → Connections
2. Under "OpenAI API", enter:
   - API Base URL: `http://192.168.1.130:8000/v1`
   - API Key: `not-needed`
3. Click "Verify Connection"
4. Select model from dropdown: `microsoft/Phi-3-mini-4k-instruct`

## Configuration

### Environment Variables

Edit `deployment.yaml` to customize:

```yaml
env:
# Ollama connection (in-cluster)
- name: OLLAMA_BASE_URL
  value: "http://ollama.ollama.svc.cluster.local:11434"

# vLLM (OpenAI-compatible API)
- name: OPENAI_API_BASE_URLS
  value: "http://192.168.1.130:8000/v1"
- name: OPENAI_API_KEYS
  value: "not-needed"

# Default model (optional)
- name: DEFAULT_MODELS
  value: "microsoft/Phi-3-mini-4k-instruct"

# Enable/disable features
- name: ENABLE_RAG_WEB_SEARCH
  value: "true"
- name: ENABLE_IMAGE_GENERATION
  value: "false"  # Set true if you have Stable Diffusion

# Authentication (optional)
- name: WEBUI_AUTH
  value: "true"  # Require login

# Custom branding (optional)
- name: WEBUI_NAME
  value: "Trotman Enterprises ML Lab"
```

Apply changes:
```bash
kubectl apply -f deployment.yaml
kubectl rollout restart deployment/open-webui -n open-webui
```

## Usage Examples

### Basic Chat

1. Open http://192.168.1.130:30080
2. Select model (Ollama phi3 or vLLM Phi-3)
3. Type your message
4. Get instant responses from local inference!

### Document Q&A (RAG)

1. Click the paperclip icon (📎)
2. Upload a PDF, TXT, or Markdown file
3. Ask questions about the document
4. Open WebUI processes it locally and uses your LLM

### Multi-Model Comparison

1. Click "+" to add multiple chat panels
2. Select different models (Ollama vs vLLM)
3. Ask the same question to both
4. Compare responses side-by-side

### System Prompts

1. Click the profile icon
2. Go to "Settings" → "System Prompts"
3. Create custom system prompts:
   - "DevOps Expert": "You are a Kubernetes and CI/CD specialist..."
   - "Code Reviewer": "You review code for security and best practices..."
4. Select prompt before chatting

### Chat History

- All conversations automatically saved
- Search past chats by keyword
- Export chat as Markdown or JSON
- Share conversations with teammates

## Advanced Features

### Enable Web Search

Open WebUI can search the web before answering:

```yaml
env:
- name: ENABLE_RAG_WEB_SEARCH
  value: "true"
- name: RAG_WEB_SEARCH_ENGINE
  value: "duckduckgo"  # or "searxng"
```

### Enable Image Generation

If you deploy Stable Diffusion:

```yaml
env:
- name: ENABLE_IMAGE_GENERATION
  value: "true"
- name: IMAGE_GENERATION_ENGINE
  value: "automatic1111"
- name: AUTOMATIC1111_BASE_URL
  value: "http://stable-diffusion.default.svc.cluster.local:7860"
```

### Custom Models

Add more OpenAI-compatible backends:

```yaml
env:
- name: OPENAI_API_BASE_URLS
  value: "http://192.168.1.130:8000/v1;http://another-server:8001/v1"
- name: OPENAI_API_KEYS
  value: "not-needed;not-needed"
```

### Multi-User Management

1. First user created = admin
2. Admin can invite users via Settings → Users
3. Set user roles: admin, user, pending
4. Control model access per user

## Performance Tuning

### Resource Limits

For production, adjust resources:

```yaml
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "4Gi"
    cpu: "2000m"
```

### Persistent Storage

Increase storage for more chat history:

```yaml
spec:
  resources:
    requests:
      storage: 50Gi  # Increase from 10Gi
```

## Troubleshooting

### Can't connect to vLLM

**Check vLLM is running:**
```bash
curl http://192.168.1.130:8000/v1/models
```

**Test from Open WebUI pod:**
```bash
kubectl exec -it -n open-webui deployment/open-webui -- sh
curl http://192.168.1.130:8000/v1/models
```

If fails, vLLM server is not accessible from cluster.

### Can't connect to Ollama

**Check Ollama service:**
```bash
kubectl get svc -n ollama
kubectl get pods -n ollama
```

**Test connectivity:**
```bash
kubectl exec -it -n open-webui deployment/open-webui -- sh
curl http://ollama.ollama.svc.cluster.local:11434/api/tags
```

### Login page not loading

**Check pod status:**
```bash
kubectl get pods -n open-webui
kubectl logs -n open-webui deployment/open-webui
```

**Check service:**
```bash
kubectl get svc -n open-webui
```

Access should be at: `http://192.168.1.130:30080`

### Slow responses

- **Normal for CPU inference**: 8 tokens/sec expected
- **Add GPU**: See [GPU Guide](../gpu/README.md) for 5-10x speedup
- **Reduce model size**: Use smaller models or higher quantization

### Out of disk space

**Check PVC usage:**
```bash
kubectl exec -it -n open-webui deployment/open-webui -- df -h
```

**Increase PVC size:**
```bash
# Edit PVC
kubectl edit pvc open-webui-data -n open-webui
# Change storage: 10Gi → 50Gi
```

## Uninstall

```bash
# Delete all resources
kubectl delete -f deployment.yaml

# Delete PVC (removes all chat history!)
kubectl delete pvc open-webui-data -n open-webui

# Delete namespace
kubectl delete namespace open-webui
```

## Comparison with Alternatives

| Feature | Open WebUI | LibreChat | Chatbot UI |
|---------|-----------|-----------|------------|
| **Ollama Support** | ✅ Native | ❌ Via proxy | ✅ Native |
| **OpenAI Compatible** | ✅ | ✅ | ✅ |
| **Document Upload** | ✅ | ✅ | ❌ |
| **Multi-user** | ✅ | ✅ | ❌ |
| **Image Generation** | ✅ | ❌ | ❌ |
| **Voice I/O** | ✅ | ❌ | ❌ |
| **Mobile App** | ✅ PWA | ❌ | ✅ PWA |
| **Self-hosted** | ✅ | ✅ | ✅ |
| **Complexity** | Low | Medium | Low |
| **Resource Usage** | Light | Medium | Light |

## Screenshots

**Chat Interface:**
```
┌─────────────────────────────────────────────────────────┐
│ Trotman Enterprises ML Lab                    [Settings]│
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 📝 New Chat    📁 Documents    🔍 Models                │
│                                                         │
│ Model: Phi-3 Mini (vLLM) ▼         [Clear]  [Export]   │
│                                                         │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ You: What is Kubernetes?                           │ │
│ │                                                     │ │
│ │ 🤖 Assistant: Kubernetes is an open-source        │ │
│ │ container orchestration platform that automates   │ │
│ │ deploying, scaling, and managing containerized    │ │
│ │ applications...                                    │ │
│ │                                                     │ │
│ │ You: How does it compare to Docker?               │ │
│ │                                                     │ │
│ │ 🤖 Assistant: While Docker focuses on...          │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ [📎]  Type your message...              [Send ▶]       │
└─────────────────────────────────────────────────────────┘
```

## Integration with Langfuse

Open WebUI doesn't natively support Langfuse tracing, but you can:

1. Use LangChain examples for traced conversations
2. Build custom API wrapper that logs to Langfuse
3. Use Langfuse's proxy mode (coming soon)

For now, use [examples/chat-langfuse.py](../examples/chat-langfuse.py) for traced CLI chats.

## Cost

- **Open WebUI**: $0 (open source)
- **Hosting**: Already running on your cluster
- **Storage**: 10Gi PVC (negligible cost)
- **Total**: $0/month

Compare to:
- ChatGPT Plus: $20/month
- Claude Pro: $20/month
- Perplexity Pro: $20/month

## Resources

- **Official Docs**: https://docs.openwebui.com/
- **GitHub**: https://github.com/open-webui/open-webui
- **Discord**: https://discord.gg/5rJgQTnV4s
- **Demo**: https://openwebui.com/ (cloud version)

## Next Steps

1. Deploy Open WebUI to your cluster
2. Create your admin account
3. Add both vLLM and Ollama models
4. Start chatting with your local LLMs!
5. Explore RAG with document upload
6. Add GPU for faster responses ([GPU Guide](../gpu/README.md))
