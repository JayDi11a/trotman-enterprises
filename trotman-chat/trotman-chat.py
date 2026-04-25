#!/usr/bin/env python3
"""
Trotman Chat - Claude Code-like CLI for your local LLMs with tool execution.
"""

import argparse
import sys
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain.agents import create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


# ============================================================================
# Tool Definitions
# ============================================================================

@tool
def execute_kubectl(command: str) -> str:
    """
    Execute kubectl commands to interact with Kubernetes cluster.

    Args:
        command: The kubectl command to run (without 'kubectl' prefix).
                 Example: "get pods -n kagent" or "describe pod my-pod"

    Returns:
        Command output or error message.
    """
    try:
        full_command = f"kubectl {command}"
        result = subprocess.run(
            full_command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return result.stdout if result.stdout else "Command executed successfully (no output)"
        else:
            return f"Error: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds"
    except Exception as e:
        return f"Error executing kubectl: {str(e)}"


@tool
def execute_helm(command: str) -> str:
    """
    Execute helm commands to manage Helm charts.

    Args:
        command: The helm command to run (without 'helm' prefix).
                 Example: "list -A" or "status kagent -n kagent"

    Returns:
        Command output or error message.
    """
    try:
        full_command = f"helm {command}"
        result = subprocess.run(
            full_command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return result.stdout if result.stdout else "Command executed successfully (no output)"
        else:
            return f"Error: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds"
    except Exception as e:
        return f"Error executing helm: {str(e)}"


@tool
def read_file(file_path: str) -> str:
    """
    Read the contents of a file.

    Args:
        file_path: Absolute or relative path to the file.

    Returns:
        File contents or error message.
    """
    try:
        path = Path(file_path).expanduser()
        with open(path, 'r') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return f"Error: File not found: {file_path}"
    except PermissionError:
        return f"Error: Permission denied: {file_path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool
def write_file(file_path: str, content: str) -> str:
    """
    Write content to a file. Creates parent directories if needed.

    Args:
        file_path: Absolute or relative path to the file.
        content: Content to write to the file.

    Returns:
        Success message or error message.
    """
    try:
        path = Path(file_path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except PermissionError:
        return f"Error: Permission denied: {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


@tool
def list_directory(directory: str = ".") -> str:
    """
    List files and directories in the specified path.

    Args:
        directory: Path to list (default: current directory).

    Returns:
        Directory listing or error message.
    """
    try:
        path = Path(directory).expanduser()
        if not path.exists():
            return f"Error: Directory not found: {directory}"

        if not path.is_dir():
            return f"Error: Not a directory: {directory}"

        items = []
        for item in sorted(path.iterdir()):
            if item.is_dir():
                items.append(f"📁 {item.name}/")
            else:
                size = item.stat().st_size
                items.append(f"📄 {item.name} ({size} bytes)")

        return "\n".join(items) if items else "Empty directory"
    except PermissionError:
        return f"Error: Permission denied: {directory}"
    except Exception as e:
        return f"Error listing directory: {str(e)}"


@tool
def execute_shell(command: str) -> str:
    """
    Execute a shell command. Use with caution!

    Args:
        command: Shell command to execute.

    Returns:
        Command output or error message.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )

        output = result.stdout if result.stdout else ""
        error = result.stderr if result.stderr else ""

        if result.returncode == 0:
            return output if output else "Command executed successfully (no output)"
        else:
            return f"Exit code {result.returncode}\n{error}\n{output}"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds"
    except Exception as e:
        return f"Error executing shell command: {str(e)}"


@tool
def get_cluster_info() -> str:
    """
    Get comprehensive Kubernetes cluster information.

    Returns:
        Cluster status, nodes, and resource summary.
    """
    try:
        # Get cluster info
        cluster_info = subprocess.run(
            "kubectl cluster-info",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        ).stdout

        # Get nodes
        nodes = subprocess.run(
            "kubectl get nodes -o wide",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        ).stdout

        # Get namespaces
        namespaces = subprocess.run(
            "kubectl get namespaces",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        ).stdout

        return f"=== Cluster Info ===\n{cluster_info}\n\n=== Nodes ===\n{nodes}\n\n=== Namespaces ===\n{namespaces}"
    except Exception as e:
        return f"Error getting cluster info: {str(e)}"


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
            base_url="http://ollama.ollama.svc.cluster.local:11434",
            model=model or "phi3",
            temperature=temperature,
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
    """Create LangChain agent with tools."""
    tools = [
        execute_kubectl,
        execute_helm,
        read_file,
        write_file,
        list_directory,
        execute_shell,
        get_cluster_info,
    ]

    # Create system prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are Trotman Chat, an AI assistant running on the Trotman Enterprises ML Lab.

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

Current working directory: {cwd}""".format(cwd=os.getcwd())),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    # Create react agent
    agent = create_react_agent(chat_model, tools, prompt)

    # Return agent executor wrapper for compatibility
    from langchain.agents import AgentExecutor
    return AgentExecutor(agent=agent, tools=tools, verbose=False, handle_parsing_errors=True)


# ============================================================================
# Interactive Chat Loop
# ============================================================================

def chat_loop(agent_executor, provider_name):
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

    chat_history = []

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
                chat_history = []
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

            # Execute agent
            print("\n🤖 Assistant: ", end="", flush=True)

            try:
                response = agent_executor.invoke({
                    "input": user_input,
                    "chat_history": chat_history
                })

                output = response.get("output", "No response")
                print(output)

                # Update chat history
                chat_history.append(HumanMessage(content=user_input))
                chat_history.append(AIMessage(content=output))

            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("Try rephrasing your request or use /help to see available tools.")

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
        choices=["vllm", "ollama", "anthropic"],
        default="vllm",
        help="Model provider (default: vllm)"
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
            "anthropic": "Anthropic (Claude Sonnet 4.5)"
        }[args.provider]
    except Exception as e:
        print(f"Error creating chat model: {e}")
        return 1

    # Create agent executor
    agent_executor = create_agent_executor(chat_model)

    # Single query mode
    if args.query:
        print(f"\n🧑 You: {args.query}")
        print("\n🤖 Assistant: ", end="", flush=True)

        try:
            response = agent_executor.invoke({
                "input": args.query,
                "chat_history": []
            })
            print(response.get("output", "No response"))
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            return 1

        return 0

    # Interactive mode
    chat_loop(agent_executor, provider_name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
