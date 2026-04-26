# Deployment Monitoring Scripts

## Quick Start

### Live Dashboard (Auto-refresh every 30 seconds)
```bash
cd /Users/geraldtrotman/Virtualenvs/trotman-enterprises
./scripts/watch-deployment.sh
```
Press `Ctrl+C` to exit

### One-time Status Check
```bash
./scripts/deployment-status.sh
```

## What You'll See

### Control Node Section
- **Memory Status**: RAM and swap usage on control node
- **Running Model Services**: All small/medium models (Hermes 8B, Qwen 14B, Granite 8B, Functionary, Qwen 32B)
- **LiteLLM Proxy**: API gateway status and health
- **Active Downloads**: Progress bars for models downloading from HuggingFace

### Worker Node Section
- **Memory Status**: RAM usage on 251GB worker node
- **Running Model Services**: Large models (Llama 70B, Qwen 72B, Mixtral 8x7B, Mixtral 8x22B)
- **Active File Transfers**: Rsync progress for copying models from control to worker

### Deployment Summary
- **Model Count**: Running models on each node
- **Target Architecture**: What the final setup should look like
- **Next Steps**: Automated list of what's happening next

## Current Deployment Status

**Control Node (192.168.1.130):**
- ✅ 5 small/medium models running
- ✅ LiteLLM proxy active on port 4000
- 🔄 3 large models still downloading (Qwen 72B, Mixtral 8x7B, Mixtral 8x22B)

**Worker Node (192.168.1.131):**
- ✅ Expanded to 251GB RAM
- 🔄 Llama 70B copying (8% complete, ~50 min remaining)
- ⏳ Ready to deploy large models when copies complete

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│ Control Node (192.168.1.130) - 62GB RAM                        │
├─────────────────────────────────────────────────────────────────┤
│ • Hermes 2 Pro 8B       (port 30704)  ~4.6GB                   │
│ • Qwen 2.5 14B          (port 30705)  ~8.4GB                   │
│ • Granite 3.0 8B        (port 30709)  ~4.7GB                   │
│ • Functionary Small     (port 30706)  ~4.6GB                   │
│ • Qwen 2.5 32B          (port 30703)  ~19GB                    │
│ • LiteLLM Proxy         (port 4000)   ~0.3GB                   │
├─────────────────────────────────────────────────────────────────┤
│ Total: ~42GB used, 20GB free                                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Worker Node (192.168.1.131) - 251GB RAM                        │
├─────────────────────────────────────────────────────────────────┤
│ • Llama 3.1 70B         (port 30700)  ~40GB  [copying...]      │
│ • Qwen 2.5 72B          (port 30701)  ~43GB  [downloading...]  │
│ • Mixtral 8x7B          (port 30707)  ~26GB  [downloading...]  │
│ • Mixtral 8x22B         (port 30708)  ~87GB  [downloading...]  │
├─────────────────────────────────────────────────────────────────┤
│ Total: ~196GB when all loaded, 55GB free                        │
└─────────────────────────────────────────────────────────────────┘

                              ▼
                    LiteLLM Unified API
              http://192.168.1.130:4000/v1
                              ▼
                         User Apps
```

## Timeline Estimates

**Downloads on Control:**
- Qwen 72B: ~5GB remaining, ~30 min
- Mixtral 8x7B: ~4GB remaining, ~25 min
- Mixtral 8x22B: ~32GB remaining, ~3 hours

**Llama 70B Copy to Worker:**
- ~37GB remaining, ~50 min at current speed

**Total time to full deployment:** ~3-4 hours (limited by Mixtral 8x22B download)

## Troubleshooting

### Dashboard not updating?
```bash
# Check if control node is reachable
ping -c 3 192.168.1.130

# Check if worker node is reachable
sshpass -p 'Pass4Admin' ssh root@192.168.1.131 'hostname'
```

### Want to check a specific service?
```bash
# Control node
ssh root@192.168.1.130 "systemctl status llama-cpp-qwen2.5-14b.service"

# Worker node
sshpass -p 'Pass4Admin' ssh root@192.168.1.131 "systemctl status llama-cpp-llama-70b.service"
```

### Check LiteLLM logs
```bash
ssh root@192.168.1.130 "journalctl -u litellm-proxy.service -f"
```

### Check model download progress
```bash
ssh root@192.168.1.130 "ps aux | grep 'hf download' | grep -v grep"
```

### Check rsync progress
```bash
ssh root@192.168.1.130 "tail -f /tmp/rsync-llama70b.log"
```

## Manual Operations

### Test a specific model via LiteLLM
```bash
curl http://192.168.1.130:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-trotman-litellm-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5-14b",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 50
  }'
```

### Stop all downloads (if needed)
```bash
ssh root@192.168.1.130 "pkill -f 'hf download'"
```

### Stop rsync transfer (if needed)
```bash
ssh root@192.168.1.130 "pkill -f 'rsync.*llama'"
```

## Files Location

- Dashboard script: `scripts/deployment-status.sh`
- Watch script: `scripts/watch-deployment.sh`
- LiteLLM config: `litellm/config-15-models.yaml`
- Architecture docs: `docs/DISTRIBUTED_ARCHITECTURE.md`
- Memory constraints: `docs/MEMORY_CONSTRAINTS.md`
