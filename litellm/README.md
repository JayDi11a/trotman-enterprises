# LiteLLM Deployment Guide

## Overview

LiteLLM provides a unified OpenAI-compatible API gateway to all 15 function-calling models (10 local + 5 cloud).

**Architecture:**
- **Small models (< 15GB):** Run as persistent systemd services (always loaded)
- **Large models (> 20GB):** Systemd services exist but are disabled - start manually as needed
- **Cloud models:** Always available via API keys
- **LiteLLM proxy:** Routes requests to appropriate endpoints with smart load balancing

## Quick Start

### 1. Install LiteLLM

```bash
ssh root@192.168.1.130
pip3.11 install 'litellm[proxy]'
```

### 2. Set Environment Variables

```bash
cat > /etc/environment.d/litellm.conf << 'EOF'
LITELLM_MASTER_KEY=your-master-key-here
ANTHROPIC_API_KEY=your-anthropic-key
OPENAI_API_KEY=your-openai-key
GEMINI_API_KEY=your-gemini-key
EOF
```

### 3. Deploy LiteLLM as Systemd Service

```bash
cat > /etc/systemd/system/litellm-proxy.service << 'EOF'
[Unit]
Description=LiteLLM Proxy Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root
EnvironmentFile=/etc/environment.d/litellm.conf
ExecStart=/usr/local/bin/litellm --config /root/litellm-config.yaml --port 4000 --host 0.0.0.0
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Copy config to server
scp config-15-models.yaml root@192.168.1.130:/root/litellm-config.yaml

# Start service
systemctl daemon-reload
systemctl enable litellm-proxy.service
systemctl start litellm-proxy.service
```

### 4. Verify Deployment

```bash
# Check LiteLLM status
curl http://192.168.1.130:4000/health

# List available models
curl http://192.168.1.130:4000/v1/models \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY"

# Test inference (will use small persistent model)
curl http://192.168.1.130:4000/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "hermes-2-pro-8b",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Managing Large Models

Large models are **not running by default** to conserve memory. Start them manually when needed.

### Start a Large Model

```bash
# Start Llama 3.1 70B
systemctl start llama-cpp-llama-70b.service

# Verify it's running
systemctl status llama-cpp-llama-70b.service

# Test via LiteLLM
curl http://192.168.1.130:4000/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.1-70b",
    "messages": [{"role": "user", "content": "What is 2+2?"}]
  }'
```

### Stop a Large Model

```bash
# Stop to free memory
systemctl stop llama-cpp-llama-70b.service

# Verify memory freed
free -h
```

### Available Large Model Services

```bash
llama-cpp-llama-70b.service       # Meta Llama 3.1 70B (~40GB RAM)
llama-cpp-qwen2.5-72b.service     # Qwen2.5 72B (~43GB RAM)
llama-cpp-mixtral-8x7b.service    # Mixtral 8x7B (~26GB RAM)
llama-cpp-mixtral-8x22b.service   # Mixtral 8x22B (~87GB RAM)
```

## Model Selection Guide

### For Quick Tasks (< 1 second response)
```
Use: hermes-2-pro-8b, granite-3.0-8b
- Already loaded, instant response
- Good for simple function calling
```

### For Complex Reasoning (< 5 second response)
```
Use: qwen2.5-14b, qwen2.5-32b
- Already loaded (14B) or quick to load (32B)
- Strong reasoning capabilities
```

### For Maximum Quality (10-30 second response)
```
Start: llama-3.1-70b or qwen2.5-72b
- Best local model quality
- Requires manual service start
- Use when quality > speed
```

### For Massive Context or Complexity
```
Use: claude-3-5-sonnet, gpt-4o
- Cloud models, always available
- Best for production use cases
- Cost per request
```

## Smart Routing via Model Groups

LiteLLM config includes model group aliases for easy routing:

```bash
# Route to any small model (load balanced)
curl http://192.168.1.130:4000/v1/chat/completions \
  -d '{"model": "function-calling-small", "messages": [...]}'

# Route to any medium model
curl http://192.168.1.130:4000/v1/chat/completions \
  -d '{"model": "function-calling-medium", "messages": [...]}'

# Route to any large model (must be running)
curl http://192.168.1.130:4000/v1/chat/completions \
  -d '{"model": "function-calling-large", "messages": [...]}'

# Route to cloud premium models
curl http://192.168.1.130:4000/v1/chat/completions \
  -d '{"model": "cloud-premium", "messages": [...]}'
```

## Memory Management Best Practices

### Current Memory Usage (Small Models Only)

```
Hermes 8B:  ~4.6GB
Qwen 14B:   ~8.4GB
Granite 8B: ~4.7GB
Qwen 32B:   ~19GB
OS/Other:   ~10GB
-----------------------
Total:      ~47GB / 62GB available
Free:       ~15GB
```

### Running 1 Large Model

```
Small models:  ~37GB
Llama 70B:     ~40GB
OS/Other:      ~10GB
-----------------------
Total:         ~87GB (will use swap, but workable)
```

### Running 2 Large Models Simultaneously

```
⚠️  NOT RECOMMENDED - will thrash swap and be very slow
```

### Optimal Strategy

1. **Keep small models running 24/7** (instant access)
2. **Load 1 large model at a time** when needed
3. **Stop large model when done** to free memory
4. **Use cloud models for production** critical paths

## Monitoring

### Check LiteLLM Logs
```bash
journalctl -u litellm-proxy.service -f
```

### Check Model Service Status
```bash
systemctl status llama-cpp-*.service
```

### Check Memory Usage
```bash
watch -n 1 free -h
```

### Check Active Models
```bash
ps aux | grep llama_cpp.server | grep -v grep
```

## Troubleshooting

### LiteLLM Can't Reach Model

```bash
# Verify model service is running
systemctl status llama-cpp-MODELNAME.service

# Test model endpoint directly
curl http://192.168.1.130:30XXX/v1/models

# Check firewall (should be disabled on k8s-control)
systemctl status firewalld
```

### Model OOM Killed

```bash
# Stop other large models first
systemctl stop llama-cpp-*.service

# Verify memory available
free -h

# Try starting just one large model
systemctl start llama-cpp-MODELNAME.service
```

### LiteLLM Not Starting

```bash
# Check environment variables
systemctl show litellm-proxy.service --property=Environment

# Check config syntax
litellm --config /root/litellm-config.yaml --test

# Check logs
journalctl -u litellm-proxy.service -n 50
```

## Integration with trotman-chat.py

Update `trotman-chat.py` to use LiteLLM:

```python
import openai

# Point to LiteLLM proxy instead of individual model endpoints
client = openai.OpenAI(
    base_url="http://192.168.1.130:4000/v1",
    api_key=os.environ["LITELLM_MASTER_KEY"]
)

# Use any model from config
response = client.chat.completions.create(
    model="qwen2.5-14b",  # or any other model
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## Next Steps

1. ✅ Deploy LiteLLM proxy service
2. ✅ Test small model inference (should work immediately)
3. 📝 Create large model service files (when downloads complete)
4. 🧪 Test large model on-demand loading
5. 🔄 Update trotman-chat.py to use LiteLLM endpoint
6. 📊 Monitor memory usage under realistic workload
