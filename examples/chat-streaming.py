#!/usr/bin/env python3
"""
Streaming chat example: See tokens as they're generated.
"""

import sys
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# Create chat client
chat = ChatOpenAI(
    base_url="http://192.168.1.130:8000/v1",
    api_key="not-needed",
    model="microsoft/Phi-3-mini-4k-instruct",
    temperature=0.7,
    streaming=True,
)

# Get user input
if len(sys.argv) > 1:
    prompt = " ".join(sys.argv[1:])
else:
    prompt = input("Ask me anything: ")

print(f"\nYou: {prompt}")
print("Assistant: ", end="", flush=True)

# Stream the response
for chunk in chat.stream([HumanMessage(content=prompt)]):
    print(chunk.content, end="", flush=True)

print("\n")
