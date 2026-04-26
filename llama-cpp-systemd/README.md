# llama.cpp Systemd Services

**Current Production Solution** for CPU-based inference

## Architecture
- **15 function-calling models** deployed as individual systemd services
- Each model = dedicated port (30700-30714)
- OpenAI-compatible API endpoints
- No orchestration layer - pure systemd reliability

## Models Deployed
| Model | Port | Size | Status |
|-------|------|------|--------|
| Llama 3.1 70B | 30700 | 40GB | ✅ Running |
| Qwen2.5 72B | 30701 | 43GB | ⏳ Deploying |
| Functionary 70B | 30702 | 40GB | ⏳ Deploying |
| Qwen2.5 32B | 30703 | 19GB | ⏳ Deploying |
| Hermes 2 Pro 8B | 30704 | 4.9GB | ✅ Running |
| Qwen2.5 14B | 30705 | 8.7GB | ✅ Running |
| Functionary 7B | 30706 | 4.4GB | ⏳ Deploying |
| Mixtral 8x7B | 30707 | 26GB | ⏳ Deploying |
| Mixtral 8x22B | 30708 | 87GB | ⏳ Deploying |
| Granite 3.0 8B | 30709 | 4.9GB | ⏳ Deploying |

## Service Template
```ini
[Unit]
Description=llama.cpp - Model Name
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/models/model-dir
Environment="HF_HOME=/models/huggingface"
ExecStart=/usr/bin/python3.11 -m llama_cpp.server \
    --model /models/model-dir/model-file.gguf \
    --host 0.0.0.0 \
    --port 307XX \
    --n_ctx 4096 \
    --n_threads 16
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

## Management Commands
```bash
# List all services
systemctl list-units 'llama-cpp-*'

# Check service status
systemctl status llama-cpp-llama-70b

# View logs
journalctl -u llama-cpp-llama-70b -f

# Restart service
systemctl restart llama-cpp-llama-70b

# Test API
curl http://192.168.1.130:30700/v1/models
```

## Why This Works
- ✅ **Reliable**: systemd process management is battle-tested
- ✅ **Simple**: No orchestration complexity
- ✅ **Performant**: llama.cpp is industry standard for CPU inference
- ✅ **Compatible**: OpenAI API format works with existing tools
- ✅ **Proven**: All 3 deployed models working perfectly
