#!/usr/bin/env python3
"""
Simple CLI chat interface for local LLM inference servers.
Supports vLLM (OpenAI-compatible) and Ollama providers.
"""

import argparse
import sys
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


def create_vllm_chat():
    """Create LangChain chat client for vLLM server."""
    return ChatOpenAI(
        base_url="http://192.168.1.130:8000/v1",
        api_key="not-needed",  # vLLM doesn't require API key
        model="microsoft/Phi-3-mini-4k-instruct",  # Or your model path
        temperature=0.7,
        max_tokens=512,
    )


def create_ollama_chat():
    """Create LangChain chat client for Ollama server."""
    return ChatOllama(
        base_url="http://ollama.ollama.svc.cluster.local:11434",
        model="phi3",
        temperature=0.7,
        num_predict=512,
    )


def chat_loop(chat_model, provider_name):
    """Interactive chat loop."""
    print(f"\n{'='*60}")
    print(f"  Trotman Enterprises ML Lab - Chat CLI ({provider_name})")
    print(f"{'='*60}")
    print("Commands:")
    print("  /exit, /quit - Exit the chat")
    print("  /clear - Clear conversation history")
    print("  /system <msg> - Set system message")
    print(f"{'='*60}\n")

    messages = []
    system_message = None

    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() in ['/exit', '/quit']:
                print("\nGoodbye!")
                break

            if user_input.lower() == '/clear':
                messages = []
                print("\n[Conversation history cleared]\n")
                continue

            if user_input.lower().startswith('/system '):
                system_msg = user_input[8:].strip()
                system_message = SystemMessage(content=system_msg)
                print(f"\n[System message set: {system_msg}]\n")
                continue

            # Add user message
            messages.append(HumanMessage(content=user_input))

            # Build message list with optional system message
            chat_messages = []
            if system_message:
                chat_messages.append(system_message)
            chat_messages.extend(messages)

            # Get AI response
            print("Assistant: ", end="", flush=True)

            try:
                response = chat_model.invoke(chat_messages)
                print(response.content)

                # Add AI response to history
                messages.append(AIMessage(content=response.content))

            except Exception as e:
                print(f"\n[Error: {e}]")
                # Remove the failed user message
                messages.pop()

            print()  # Blank line for readability

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except EOFError:
            print("\n\nGoodbye!")
            break


def main():
    parser = argparse.ArgumentParser(
        description="Chat with local LLM inference servers using LangChain"
    )
    parser.add_argument(
        "--provider",
        "-p",
        choices=["vllm", "ollama"],
        default="vllm",
        help="Inference provider (default: vllm)"
    )
    parser.add_argument(
        "--model",
        "-m",
        help="Model name (overrides default)"
    )
    parser.add_argument(
        "--temperature",
        "-t",
        type=float,
        default=0.7,
        help="Temperature (0.0-1.0, default: 0.7)"
    )

    args = parser.parse_args()

    # Create chat model based on provider
    if args.provider == "vllm":
        chat_model = create_vllm_chat()
        provider_name = "vLLM (Phi-3 Mini)"
    else:
        chat_model = create_ollama_chat()
        provider_name = "Ollama (phi3)"

    # Override defaults if specified
    if args.model:
        chat_model.model = args.model
    if args.temperature != 0.7:
        chat_model.temperature = args.temperature

    # Start chat loop
    chat_loop(chat_model, provider_name)


if __name__ == "__main__":
    main()
