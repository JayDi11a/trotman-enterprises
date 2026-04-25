#!/usr/bin/env python3
"""
CLI chat using Open WebUI's REST API.
Use this after deploying Open WebUI to your cluster.
"""

import argparse
import requests
import sys
import json


class OpenWebUIClient:
    def __init__(self, base_url, api_key=None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers['Authorization'] = f'Bearer {api_key}'

    def chat(self, message, model=None, stream=False):
        """Send chat message to Open WebUI."""
        endpoint = f"{self.base_url}/api/chat/completions"

        payload = {
            "model": model or "microsoft/Phi-3-mini-4k-instruct",
            "messages": [{"role": "user", "content": message}],
            "stream": stream
        }

        try:
            response = self.session.post(endpoint, json=payload)
            response.raise_for_status()

            if stream:
                for line in response.iter_lines():
                    if line:
                        yield line.decode('utf-8')
            else:
                return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def list_models(self):
        """List available models."""
        endpoint = f"{self.base_url}/api/models"
        try:
            response = self.session.get(endpoint)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(
        description="Chat via Open WebUI API from command line"
    )
    parser.add_argument(
        "--url",
        default="http://192.168.1.130:30080",
        help="Open WebUI URL (default: http://192.168.1.130:30080)"
    )
    parser.add_argument(
        "--api-key",
        help="API key (if authentication enabled)"
    )
    parser.add_argument(
        "--model",
        "-m",
        help="Model name"
    )
    parser.add_argument(
        "--stream",
        "-s",
        action="store_true",
        help="Stream response"
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List available models"
    )
    parser.add_argument(
        "message",
        nargs="*",
        help="Message to send"
    )

    args = parser.parse_args()

    client = OpenWebUIClient(args.url, args.api_key)

    # List models
    if args.list_models:
        models = client.list_models()
        if "error" in models:
            print(f"Error: {models['error']}")
            return 1

        print("Available models:")
        for model in models.get("data", []):
            print(f"  - {model.get('id', 'unknown')}")
        return 0

    # Chat
    if not args.message:
        print("Error: No message provided")
        parser.print_help()
        return 1

    message = " ".join(args.message)

    if args.stream:
        print("Assistant: ", end="", flush=True)
        for chunk in client.chat(message, args.model, stream=True):
            # Parse SSE format
            if chunk.startswith("data: "):
                data = chunk[6:]
                if data != "[DONE]":
                    try:
                        obj = json.loads(data)
                        content = obj.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        print(content, end="", flush=True)
                    except json.JSONDecodeError:
                        pass
        print()
    else:
        response = client.chat(message, args.model)

        if "error" in response:
            print(f"Error: {response['error']}")
            return 1

        content = response.get("choices", [{}])[0].get("message", {}).get("content", "No response")
        print(f"Assistant: {content}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
