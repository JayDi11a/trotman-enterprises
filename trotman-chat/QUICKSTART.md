# Trotman Chat - Quick Start

## ✅ Installation Complete!

Trotman Chat is installed and ready to use. It's a Claude Code-like CLI that can execute kubectl, helm, and shell commands using your local LLMs.

## 🚀 Start Using It

### Option 1: Interactive Chat (Recommended)

```bash
# Make sure vLLM server is running first
# (Check: curl http://192.168.1.130:8000/v1/models)

# Start chatting
trotman-chat
```

Then type naturally:
- "List all pods in kagent namespace"
- "Show me cluster information"
- "Read the README.md file"
- "What namespaces exist?"

### Option 2: Single Query

```bash
# One-off questions
trotman-chat -q "List all namespaces in my cluster"
```

### Option 3: Different Providers

```bash
# Ollama (if available in cluster)
trotman-chat --provider ollama

# Anthropic (requires API key)
export ANTHROPIC_API_KEY=sk-ant-...
trotman-chat --provider anthropic
```

## 📋 Available Commands (while chatting)

- `/exit` - Quit
- `/clear` - Clear conversation history
- `/help` - Show available tools
- `/cluster` - Show cluster information

## 🛠️ What Can It Do?

Execute any kubectl/helm command:
```
You: Get all pods in kagent namespace
Assistant: [Runs: kubectl get pods -n kagent]
          Shows results...
```

Read/write files:
```
You: Show me the README
Assistant: [Reads: README.md]
          Shows content...
```

Run shell commands:
```
You: What's the disk usage?
Assistant: [Runs: df -h]
          Shows disk space...
```

## ⚠️ Before First Use

**Make sure vLLM is running:**
```bash
curl http://192.168.1.130:8000/v1/models
```

If you get an error, vLLM server needs to be started on your cluster.

## 💰 Cost

- vLLM: $0/month (local CPU inference)
- Ollama: $0/month (in-cluster)
- Anthropic: ~$0.015/1K tokens (only if you use it)

**Recommended: Stick with vLLM for zero-cost operation!**

## 🆘 Troubleshooting

**"Connection refused" error:**
```bash
# Check if vLLM is running
curl http://192.168.1.130:8000/v1/models

# If not, start your vLLM server
# (see vllm/README.md for instructions)
```

**"Command not found: trotman-chat":**
```bash
# Reload your shell
source ~/.zshrc

# Or use full path
/Users/geraldtrotman/bin/trotman-chat
```

## 📚 Full Documentation

See [README.md](README.md) for complete documentation.

## 🎉 You're Ready!

Try it now:
```bash
trotman-chat -q "What tools do you have access to?"
```
