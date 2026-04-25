# Trotman Chat - Claude Code-like CLI

Interactive CLI assistant with tool execution for your Kubernetes ML lab.

## Quick Start

```bash
# Install (one-time setup)
cd /Users/geraldtrotman/Virtualenvs/trotman-enterprises
pip3 install langchain-anthropic  # Only missing package
chmod +x trotman-chat/trotman-chat.py

# Run with vLLM (local, $0 cost)
./trotman-chat/trotman-chat.py

# Run with Ollama (local, $0 cost)
./trotman-chat/trotman-chat.py --provider ollama

# Run with Anthropic (cloud, costs money)
export ANTHROPIC_API_KEY=sk-ant-...
./trotman-chat/trotman-chat.py --provider anthropic
```

## Features

✅ Interactive chat like Claude Code  
✅ Execute kubectl, helm, shell commands  
✅ Read/write files  
✅ Multi-turn conversations  
✅ Uses your local models (zero cost)  

## Available Tools

- `execute_kubectl` - Run kubectl commands
- `execute_helm` - Run helm commands  
- `read_file` - Read file contents
- `write_file` - Create/update files
- `list_directory` - List files
- `execute_shell` - Run shell commands
- `get_cluster_info` - Show cluster overview

## Commands

- `/exit` - Quit
- `/clear` - Clear history
- `/help` - Show tools
- `/cluster` - Cluster info

## Examples

```
You: List all pods in kagent namespace
Assistant: [Runs kubectl get pods -n kagent]
...

You: Show me the README file  
Assistant: [Runs read_file README.md]
...

You: Create a test deployment
Assistant: [Creates deployment.yaml]
...
```

## Cost

- vLLM: $0/month (local CPU)
- Ollama: $0/month (local)
- Anthropic: ~$0.015/1K tokens

Recommended: Use vLLM or Ollama for zero-cost operation.
