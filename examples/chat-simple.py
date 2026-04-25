#!/usr/bin/env python3
"""
Minimal example: Single query to vLLM server using LangChain.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# Create chat client
chat = ChatOpenAI(
    base_url="http://192.168.1.130:8000/v1",
    api_key="not-needed",
    model="microsoft/Phi-3-mini-4k-instruct",
    temperature=0.7,
)

# Send a message
response = chat.invoke([
    HumanMessage(content="Explain Kubernetes in one sentence.")
])

print(f"Assistant: {response.content}")
