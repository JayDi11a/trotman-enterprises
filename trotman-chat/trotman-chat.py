#!/usr/bin/env python3
"""
Trotman Chat - Simple CLI for chatting with local LLMs.
"""

import argparse
import sys
import os
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


# ============================================================================
# Chat Client Setup
# ============================================================================

def create_chat_model(provider: str, model: str = None, temperature: float = 0.7):
    """Create LangChain chat model based on provider."""
    if provider == "vllm":
        return ChatOpenAI(
            base_url="http://192.168.1.130:8000/v1",
            api_key="not-needed",
            model=model or "microsoft/Phi-3-mini-4k-instruct",
            temperature=temperature,
            streaming=True,
        )
    elif provider == "ollama":
        return ChatOllama(
            base_url="http://192.168.1.130:30434",
            model=model or "phi3",
            temperature=temperature,
        )
    elif provider == "llama":
        # Llama 3.1 with function calling support
        return ChatOllama(
            base_url="http://192.168.1.130:30434",
            model=model or "llama3.1:8b",
            temperature=temperature,
            format="json",  # Enable structured output
        )
    elif provider == "mistral":
        # Mistral with function calling support
        return ChatOllama(
            base_url="http://192.168.1.130:30434",
            model=model or "mistral:7b",
            temperature=temperature,
            format="json",
        )
    elif provider == "hermes":
        # Hermes 3 with function calling support
        return ChatOllama(
            base_url="http://192.168.1.130:30434",
            model=model or "hermes3:8b",
            temperature=temperature,
            format="json",
        )
    elif provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("Warning: ANTHROPIC_API_KEY not set. Set it with:")
            print("  export ANTHROPIC_API_KEY=sk-ant-...")
            sys.exit(1)

        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model or "claude-sonnet-4-5-20250929",
            temperature=temperature,
            api_key=api_key,
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")


# ============================================================================
# Agent Setup
# ============================================================================

def create_agent_executor(chat_model):
    """Create simple tool-calling chat model."""
    tools = [
        execute_kubectl,
        execute_helm,
        read_file,
        write_file,
        list_directory,
        execute_shell,
        get_cluster_info,
    ]

    # Bind tools to the model
    model_with_tools = chat_model.bind_tools(tools)

    # Store system message
    system_message = """You are Trotman Chat, an AI assistant running on the Trotman Enterprises ML Lab.

You have access to a Kubernetes cluster with the following components:
- k3s cluster with control plane and worker node
- Kagent (agent orchestration)
- KServe (model serving)
- vLLM inference server
- Ollama (local models)
- Langfuse (observability)
- Knative Serving
- cert-manager
- gVisor (code sandboxing)

When users ask you to do something:
1. Understand what they want
2. Use the appropriate tools to accomplish it
3. Explain what you're doing
4. Show the results clearly

Be helpful, concise, and technical. You're talking to someone who knows their way around Kubernetes and ML infrastructure.

Current working directory: {cwd}""".format(cwd=os.getcwd())

    return {
        "model": model_with_tools,
        "tools": {tool.name: tool for tool in tools},
        "system_message": system_message
    }


# ============================================================================
# Interactive Chat Loop
# ============================================================================

def chat_loop(agent_config, provider_name):
    """Interactive chat loop with tool execution."""
    print(f"\n{'='*70}")
    print(f"  🤖 Trotman Chat - Claude Code-like CLI ({provider_name})")
    print(f"{'='*70}")
    print("I can execute kubectl, helm, and shell commands to help you!")
    print("\nCommands:")
    print("  /exit, /quit     - Exit the chat")
    print("  /clear           - Clear conversation history")
    print("  /help            - Show available tools")
    print("  /cluster         - Show cluster info")
    print(f"{'='*70}\n")

    model = agent_config["model"]
    tools_dict = agent_config["tools"]
    system_msg = agent_config["system_message"]

    messages = [SystemMessage(content=system_msg)]

    while True:
        try:
            # Get user input
            user_input = input("\n🧑 You: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() in ['/exit', '/quit']:
                print("\n👋 Goodbye!")
                break

            if user_input.lower() == '/clear':
                messages = [SystemMessage(content=system_msg)]
                print("\n[Conversation history cleared]\n")
                continue

            if user_input.lower() == '/help':
                print("\n📚 Available Tools:")
                print("  • execute_kubectl - Run kubectl commands")
                print("  • execute_helm - Run helm commands")
                print("  • read_file - Read file contents")
                print("  • write_file - Create/update files")
                print("  • list_directory - List directory contents")
                print("  • execute_shell - Run shell commands")
                print("  • get_cluster_info - Get cluster overview")
                continue

            if user_input.lower() == '/cluster':
                user_input = "Show me comprehensive cluster information including nodes, namespaces, and key deployments"

            # Add user message
            messages.append(HumanMessage(content=user_input))

            # Execute with tool calling
            print("\n🤖 Assistant: ", end="", flush=True)

            try:
                # Get response from model
                response = model.invoke(messages)
                messages.append(response)

                # Check if tools were called
                if hasattr(response, 'tool_calls') and response.tool_calls:
                    # Execute tools
                    for tool_call in response.tool_calls:
                        tool_name = tool_call["name"]
                        tool_args = tool_call["args"]

                        if tool_name in tools_dict:
                            tool_result = tools_dict[tool_name].invoke(tool_args)
                            messages.append(ToolMessage(
                                content=str(tool_result),
                                tool_call_id=tool_call["id"]
                            ))

                    # Get final response after tool execution
                    final_response = model.invoke(messages)
                    messages.append(final_response)
                    print(final_response.content)
                else:
                    # No tools called, just print response
                    print(response.content)

            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("Try rephrasing your request or use /help to see available tools.")
                # Remove failed message
                if messages and isinstance(messages[-1], HumanMessage):
                    messages.pop()

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except EOFError:
            print("\n\n👋 Goodbye!")
            break


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Trotman Chat - Claude Code-like CLI with tool execution"
    )
    parser.add_argument(
        "--provider",
        "-p",
        choices=["vllm", "ollama", "llama", "mistral", "hermes", "anthropic"],
        default="llama",
        help="Model provider (default: llama)"
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
    parser.add_argument(
        "--query",
        "-q",
        help="Single query mode (non-interactive)"
    )

    args = parser.parse_args()

    # Create chat model
    try:
        chat_model = create_chat_model(args.provider, args.model, args.temperature)
        provider_name = {
            "vllm": "vLLM (Phi-3 Mini)",
            "ollama": "Ollama (phi3)",
            "llama": "Llama 3.1 8B (Function Calling)",
            "mistral": "Mistral 7B (Function Calling)",
            "hermes": "Hermes 3 8B (Function Calling)",
            "anthropic": "Anthropic (Claude Sonnet 4.5)"
        }[args.provider]
    except Exception as e:
        print(f"Error creating chat model: {e}")
        return 1

    # Create agent config
    agent_config = create_agent_executor(chat_model)

    # Single query mode
    if args.query:
        print(f"\n🧑 You: {args.query}")
        print("\n🤖 Assistant: ", end="", flush=True)

        try:
            model = agent_config["model"]
            tools_dict = agent_config["tools"]
            system_msg = agent_config["system_message"]

            messages = [
                SystemMessage(content=system_msg),
                HumanMessage(content=args.query)
            ]

            # Get response
            response = model.invoke(messages)

            # Check for tool calls
            if hasattr(response, 'tool_calls') and response.tool_calls:
                messages.append(response)

                # Execute tools
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]

                    if tool_name in tools_dict:
                        tool_result = tools_dict[tool_name].invoke(tool_args)
                        messages.append(ToolMessage(
                            content=str(tool_result),
                            tool_call_id=tool_call["id"]
                        ))

                # Get final response
                final_response = model.invoke(messages)
                print(final_response.content)
            else:
                print(response.content)

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            return 1

        return 0

    # Interactive mode
    chat_loop(agent_config, provider_name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
