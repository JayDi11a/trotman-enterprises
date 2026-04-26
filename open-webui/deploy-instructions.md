# Deploy Open WebUI from k3s Control Plane

Run these commands on your k3s control plane node (192.168.1.130):

```bash
# SSH to control plane
ssh almalinux@192.168.1.130

# Clone the repo (if not already there)
cd ~
git clone https://github.com/JayDi11a/trotman-enterprises.git

# Or if already cloned, just pull latest
cd ~/trotman-enterprises
git pull

# Deploy Open WebUI
cd open-webui
chmod +x deploy.sh
./deploy.sh

# Wait for deployment to complete (about 2 minutes)
# Then access at: http://192.168.1.130:30080
```

## After Deployment

1. Open browser: http://192.168.1.130:30080
2. Create admin account (first user = admin)
3. Login
4. Select model:
   - Ollama: `phi3`
   - vLLM: `microsoft/Phi-3-mini-4k-instruct`
5. Start chatting!

## Verify Deployment

```bash
# Check pod status
kubectl get pods -n open-webui

# Check service
kubectl get svc -n open-webui

# View logs
kubectl logs -n open-webui deployment/open-webui -f
```
