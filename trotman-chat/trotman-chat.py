#!/usr/bin/env python3
"""
Trotman Chat - Claude Code-like CLI for your local LLMs with tool execution.
"""

import argparse
import sys
import os
import subprocess
import json
import requests
import re
from pathlib import Path
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool


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


@tool
def query_papers(question: str, complexity: str = "intermediate") -> str:
    """
    Query Ilya Sutskever's top 30 AI/ML research papers using RAG.

    Ask natural language questions about foundational AI/ML papers and get
    AI-generated answers with source citations. Papers include transformers,
    ResNets, LSTMs, scaling laws, and more.

    Args:
        question: Your question about the papers (e.g., "What are transformers?",
                 "Explain residual connections", "How do LSTMs work?")
        complexity: Response detail level - "beginner", "intermediate", "advanced",
                   or "expert" (default: "intermediate")

    Returns:
        AI-generated answer with paper citations

    Examples:
        - "What is the transformer architecture?"
        - "How do skip connections help deep networks?"
        - "Explain scaling laws for language models"
    """
    try:
        papers_api_url = "http://192.168.1.130:30092"
        response = requests.post(
            f"{papers_api_url}/query",
            json={"question": question, "complexity": complexity},
            timeout=60
        )
        response.raise_for_status()

        data = response.json()
        answer = data.get("answer", "No answer generated")
        sources = data.get("sources", [])

        # Format with sources
        if sources:
            sources_text = "\n\n📚 Sources:\n"
            for source in sources:
                sources_text += f"• {source['title']}\n"
                sources_text += f"  {source['authors']}\n"
            return f"{answer}{sources_text}"
        else:
            return answer

    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to Papers API. Is the service running? (kubectl get svc -n research-papers)"
    except requests.exceptions.Timeout:
        return "❌ Request timed out. The question may be too complex."
    except Exception as e:
        return f"❌ Error querying papers: {str(e)}"


# ============================================================================
# Chat Client Setup
# ============================================================================

def create_chat_model(provider: str, model: str = None, temperature: float = 0.7):
    """Create LangChain chat model based on provider."""
    if provider == "vllm":
        return ChatOpenAI(
            base_url="http://192.168.1.130:4000/v1",
            api_key="sk-trotman-litellm-2026",
            model=model or "qwen2.5-14b",
            temperature=temperature,
            streaming=False,
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
# Tool Call Parser for Text-Based Models
# ============================================================================

def parse_text_tool_calls(content: str):
    """
    Parse text-based tool calls from models that use <tool_call>...</tool_call> XML format
    or raw JSON tool call format.

    Returns list of dicts with 'name' and 'arguments' keys, or empty list if no tool calls found.
    """
    tool_calls = []

    # Try XML format first: <tool_call>...</tool_call>
    xml_pattern = r'<tool_call>\s*(\{.*?\})\s*</tool_call>'
    xml_matches = re.findall(xml_pattern, content, re.DOTALL)

    for match in xml_matches:
        try:
            tool_data = json.loads(match)
            if 'name' in tool_data and 'arguments' in tool_data:
                tool_calls.append({
                    'name': tool_data['name'],
                    'arguments': tool_data['arguments']
                })
        except json.JSONDecodeError:
            continue

    # If no XML format found, try raw JSON format
    if not tool_calls:
        # Look for {"name": "...", "arguments": {...}} pattern
        json_pattern = r'\{"name":\s*"([^"]+)",\s*"arguments":\s*(\{[^}]*\})\}'
        json_matches = re.findall(json_pattern, content, re.DOTALL)

        for name, args_str in json_matches:
            try:
                arguments = json.loads(args_str)
                tool_calls.append({
                    'name': name,
                    'arguments': arguments
                })
            except json.JSONDecodeError:
                continue

    return tool_calls


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
        query_papers,
    ]

    # Bind tools to the model
    # TEMP: Tool binding disabled - causes hang with langchain + LiteLLM
    # model_with_tools = chat_model.bind_tools(tools)
    model_with_tools = chat_model  # No tools for now

    # Build tool descriptions for system message
    tools_description = "\n\nAvailable tools:\n"
    for tool in tools:
        tools_description += f"- {tool.name}: {tool.description}\n"

    # Store system message
    system_message = """You are Trotman Chat, an AI assistant running on the Trotman Enterprises ML Lab.

You have access to a Kubernetes cluster with the following components:
- k3s cluster with control plane and worker node
- Kagent (agent orchestration)
- KServe (model serving)
- llama.cpp inference via LiteLLM
- Langfuse (observability)
- Knative Serving
- cert-manager
- gVisor (code sandboxing)

You also have access to Ilya Sutskever's top 30 AI/ML research papers via RAG.
Use the query_papers tool when users ask about:
- AI/ML concepts (transformers, attention, ResNets, LSTMs, etc.)
- Research papers and their contributions
- Deep learning fundamentals

When users ask you to do something:
1. Understand what they want
2. Use the appropriate tools to accomplish it
3. Explain what you're doing
4. Show the results clearly

To use a tool, respond with:
<tool_call>
{{"name": "tool_name", "arguments": {{"arg1": "value1", "arg2": "value2"}}}}
</tool_call>

Be helpful, concise, and technical. You're talking to someone who knows their way around Kubernetes and ML infrastructure.

Current working directory: {cwd}

{tools}""".format(cwd=os.getcwd(), tools=tools_description)

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

                # Check if tools were called (OpenAI format)
                if hasattr(response, 'tool_calls') and response.tool_calls:
                    # Execute OpenAI-style tool calls
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
                    # Check for text-based tool calls (e.g., <tool_call>...</tool_call>)
                    text_tool_calls = parse_text_tool_calls(response.content)

                    if text_tool_calls:
                        # Execute text-based tool calls
                        tool_results = []
                        for tool_call in text_tool_calls:
                            tool_name = tool_call["name"]
                            tool_args = tool_call["arguments"]

                            if tool_name in tools_dict:
                                result = tools_dict[tool_name].invoke(tool_args)
                                tool_results.append(f"\n**{tool_name} result:**\n{result}\n")

                        # Add tool results to context and get final response
                        tool_results_text = "\n".join(tool_results)
                        messages.append(HumanMessage(content=f"Tool execution results:\n{tool_results_text}\n\nPlease provide a summary based on these results."))

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
            "vllm": "LiteLLM (Command-R 35B)",
            "ollama": "Ollama (phi3)",
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

            # Check for OpenAI-style tool calls
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
                # Check for text-based tool calls
                text_tool_calls = parse_text_tool_calls(response.content)

                if text_tool_calls:
                    messages.append(response)

                    # Execute text-based tool calls
                    tool_results = []
                    for tool_call in text_tool_calls:
                        tool_name = tool_call["name"]
                        tool_args = tool_call["arguments"]

                        if tool_name in tools_dict:
                            result = tools_dict[tool_name].invoke(tool_args)
                            tool_results.append(f"\n**{tool_name} result:**\n{result}\n")

                    # Add tool results to context and get final response
                    tool_results_text = "\n".join(tool_results)
                    messages.append(HumanMessage(content=f"Tool execution results:\n{tool_results_text}\n\nPlease provide a summary based on these results."))

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
