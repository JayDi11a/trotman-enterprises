#!/bin/bash
set -e

echo "===================================="
echo " Deploying Open WebUI to k3s cluster"
echo "===================================="
echo

# Deploy
echo "📦 Deploying Open WebUI..."
kubectl apply -f deployment.yaml

echo
echo "⏳ Waiting for pod to be ready (this may take 1-2 minutes)..."
kubectl wait --for=condition=ready pod -l app=open-webui -n open-webui --timeout=180s

echo
echo "✅ Open WebUI deployed successfully!"
echo
echo "Access at: http://192.168.1.130:30080"
echo
echo "First time setup:"
echo "  1. Open http://192.168.1.130:30080 in your browser"
echo "  2. Create an admin account (first user = admin)"
echo "  3. Login and start chatting!"
echo
echo "Models available:"
echo "  - Ollama: phi3 (auto-discovered)"
echo "  - vLLM: microsoft/Phi-3-mini-4k-instruct"
echo
echo "Useful commands:"
echo "  kubectl logs -n open-webui deployment/open-webui -f  # View logs"
echo "  kubectl get pods -n open-webui                        # Check status"
echo "  kubectl delete -f deployment.yaml                     # Uninstall"
echo
