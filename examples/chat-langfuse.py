#!/usr/bin/env python3
"""
Chat with automatic Langfuse tracing enabled.
All conversations will appear in Langfuse UI at http://192.168.1.130:30300
"""

import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langfuse.callback import CallbackHandler

# Initialize Langfuse callback
langfuse_handler = CallbackHandler(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY", "your-public-key"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY", "your-secret-key"),
    host="http://192.168.1.130:30300"
)

# Create chat client
chat = ChatOpenAI(
    base_url="http://192.168.1.130:8000/v1",
    api_key="not-needed",
    model="microsoft/Phi-3-mini-4k-instruct",
    temperature=0.7,
)

# Simple conversation with tracing
messages = [
    HumanMessage(content="What is Kubernetes?")
]

print("Sending query to vLLM (with Langfuse tracing)...")
response = chat.invoke(messages, config={"callbacks": [langfuse_handler]})

print(f"\nAssistant: {response.content}")
print(f"\n✅ Trace captured in Langfuse: http://192.168.1.130:30300")
