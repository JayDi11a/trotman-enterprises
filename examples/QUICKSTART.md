# Quick Start: Chat with Your Local LLMs

## 1. Install Dependencies

```bash
cd examples
pip3 install -r requirements.txt
```

## 2. Test Connection to vLLM

```bash
# Quick test - make sure vLLM is responding
curl http://192.168.1.130:8000/v1/models
```

If you get a response with model info, you're ready!

## 3. Run Your First Chat

### Option A: Interactive Chat (Recommended)

```bash
./chat-cli.py
```

Then type your questions:
```
You: What is Kubernetes?
Assistant: [AI response here]

You: /exit
Goodbye!
```

### Option B: Simple Single Question

```bash
./chat-simple.py
```

### Option C: Streaming (See Tokens Generate)

```bash
./chat-streaming.py "Explain Docker in simple terms"
```

## Commands in Interactive Chat

- Type normally to chat
- `/exit` or `/quit` - Exit the chat
- `/clear` - Clear conversation history  
- `/system <message>` - Set a system prompt

## Examples

```bash
# Chat with vLLM (default)
./chat-cli.py

# Chat with Ollama instead
./chat-cli.py --provider ollama

# More creative responses (higher temperature)
./chat-cli.py --temperature 0.9

# More focused responses (lower temperature)
./chat-cli.py --temperature 0.3
```

## Troubleshooting

**Can't connect to vLLM?**
```bash
# Check if vLLM is running
curl http://192.168.1.130:8000/v1/models
```

**Module not found?**
```bash
pip3 install -r requirements.txt
```

See [README.md](README.md) for full documentation.
