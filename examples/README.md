# LangChain Chat Examples

Simple command-line examples for chatting with your local inference servers using LangChain.

## Prerequisites

Install required packages:

```bash
pip install langchain langchain-openai langchain-ollama langfuse
```

## Quick Start

### 1. Simple Single Query

```bash
python3 chat-simple.py
```

**What it does:**
- Sends one question to vLLM server
- Prints the response
- Exits

### 2. Interactive Chat (Recommended)

```bash
# Chat with vLLM (default)
python3 chat-cli.py

# Chat with Ollama
python3 chat-cli.py --provider ollama

# Adjust temperature
python3 chat-cli.py --temperature 0.3
```

**Features:**
- Interactive conversation loop
- Maintains chat history
- Commands: `/exit`, `/clear`, `/system <msg>`
- Works with both vLLM and Ollama

**Example session:**
```
You: What is Kubernetes?
Assistant: Kubernetes is an open-source container orchestration platform...

You: How does it differ from Docker?
Assistant: While Docker is primarily a containerization platform...

You: /exit
Goodbye!
```

### 3. Streaming Responses

```bash
# Interactive prompt
python3 chat-streaming.py

# Direct query
python3 chat-streaming.py "Explain machine learning"
```

**What it does:**
- Shows tokens as they're generated (like ChatGPT)
- Great for long responses
- See inference speed in real-time

### 4. Chat with Langfuse Tracing

```bash
# Set Langfuse credentials (get from http://192.168.1.130:30300)
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."

python3 chat-langfuse.py
```

**What it does:**
- Sends chat to vLLM
- Automatically traces conversation in Langfuse
- View traces at http://192.168.1.130:30300

## Usage Examples

### Basic Chat

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

chat = ChatOpenAI(
    base_url="http://192.168.1.130:8000/v1",
    api_key="not-needed",
    model="microsoft/Phi-3-mini-4k-instruct",
)

response = chat.invoke([HumanMessage(content="Hello!")])
print(response.content)
```

### Multi-turn Conversation

```python
from langchain_core.messages import HumanMessage, AIMessage

messages = [
    HumanMessage(content="What is Kubernetes?"),
]

response = chat.invoke(messages)
messages.append(AIMessage(content=response.content))

# Follow-up question
messages.append(HumanMessage(content="What are its main benefits?"))
response = chat.invoke(messages)
print(response.content)
```

### With System Message

```python
from langchain_core.messages import SystemMessage, HumanMessage

messages = [
    SystemMessage(content="You are a helpful DevOps expert. Be concise."),
    HumanMessage(content="How do I deploy an app to Kubernetes?"),
]

response = chat.invoke(messages)
print(response.content)
```

### Streaming

```python
for chunk in chat.stream([HumanMessage(content="Explain Docker")]):
    print(chunk.content, end="", flush=True)
```

### Using Ollama

```python
from langchain_ollama import ChatOllama

chat = ChatOllama(
    base_url="http://ollama.ollama.svc.cluster.local:11434",
    model="phi3",
)

response = chat.invoke([HumanMessage(content="Hello!")])
print(response.content)
```

## Configuration Options

### vLLM Options

```python
chat = ChatOpenAI(
    base_url="http://192.168.1.130:8000/v1",
    api_key="not-needed",
    model="microsoft/Phi-3-mini-4k-instruct",
    
    # Generation parameters
    temperature=0.7,        # 0.0 = deterministic, 1.0 = creative
    max_tokens=512,         # Max response length
    top_p=0.9,             # Nucleus sampling
    frequency_penalty=0.0,  # Penalize repetition
    presence_penalty=0.0,   # Penalize topic repetition
    
    # Streaming
    streaming=True,         # Enable token streaming
)
```

### Ollama Options

```python
chat = ChatOllama(
    base_url="http://ollama.ollama.svc.cluster.local:11434",
    model="phi3",
    
    # Generation parameters
    temperature=0.7,
    num_predict=512,        # Max tokens
    top_p=0.9,
    top_k=40,
    repeat_penalty=1.1,
    
    # Context
    num_ctx=4096,          # Context window
)
```

## Troubleshooting

### vLLM Connection Error

```bash
# Check if vLLM is running
curl http://192.168.1.130:8000/v1/models

# Should return:
# {"object":"list","data":[{"id":"microsoft/Phi-3-mini-4k-instruct",...}]}
```

If not running, start vLLM:
```bash
ssh almalinux@192.168.1.130
sudo systemctl start vllm-server  # Or however you start it
```

### Ollama Connection Error

```bash
# Check if Ollama is running in cluster
kubectl get pods -n ollama

# Port-forward Ollama to local machine
kubectl port-forward -n ollama svc/ollama 11434:11434

# Then update base_url in script:
# base_url="http://localhost:11434"
```

### Slow Responses

- **CPU inference**: ~8 tokens/sec is normal (800-1000ms first token)
- **Increase performance**: Add GPU (see [GPU Guide](../gpu/README.md))
- **Reduce context**: Lower `num_ctx` or `max_model_len`

### Import Errors

```bash
# Install missing packages
pip install langchain langchain-openai langchain-ollama

# For Langfuse tracing
pip install langfuse
```

## Advanced: LangChain Agents

Create an agent that can use tools:

```python
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import tool

@tool
def get_cluster_info() -> str:
    """Get Kubernetes cluster information."""
    import subprocess
    result = subprocess.run(
        ["kubectl", "cluster-info"],
        capture_output=True,
        text=True
    )
    return result.stdout

tools = [get_cluster_info]

# Create agent (requires function-calling model)
agent = create_tool_calling_agent(chat, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)

response = agent_executor.invoke({
    "input": "What's the status of my Kubernetes cluster?"
})
```

## Cost Tracking

All examples use **local inference** with zero API costs:

- **vLLM**: $0/month (local)
- **Ollama**: $0/month (local)
- **Electricity**: ~$2-5/month for dev sessions only

Compare to:
- OpenAI GPT-4: $0.03/1K tokens (~$30-300/month typical usage)
- Anthropic Claude: $0.015/1K tokens (~$15-150/month typical usage)

## Next Steps

- Try different models with Ollama: `ollama pull llama3`, `ollama pull mistral`
- Build agents with Kagent (see [kagent/README.md](../kagent/README.md))
- Monitor conversations in Langfuse at http://192.168.1.130:30300
- Add GPU for 5-10x faster responses (see [GPU Guide](../gpu/README.md))

## Resources

- [LangChain Documentation](https://python.langchain.com/)
- [vLLM OpenAI API](https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html)
- [Ollama Documentation](https://ollama.ai/docs)
- [Langfuse Tracing](https://langfuse.com/docs/integrations/langchain)
