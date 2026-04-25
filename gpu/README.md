# GPU Acceleration Guide

Complete guide for adding GPU compute to the Trotman Enterprises ML Lab.

## Overview

This guide covers adding NVIDIA GPUs to your IBM System x M4 servers for 5-10x inference performance improvement while maintaining zero or near-zero operating costs.

**Expected results:**
- Current (CPU): ~8 tokens/sec
- With GPU: ~40-80 tokens/sec (depending on GPU model)
- Power cost: $8-27/month (vs $500+/month cloud GPU instances)

## Hardware Compatibility

### Supported GPUs

Your IBM System x M4 servers support PCIe Gen 3 with ESXi 8.0.3 GPU passthrough (vDGA).

#### Recommended Options

| GPU | VRAM | Cost (Used) | Performance | Power | Best For |
|-----|------|-------------|-------------|-------|----------|
| **Tesla P40** | 24GB | $200-400 | 40-60 tok/s | 250W | **Large models (Llama 3 70B)** |
| **Tesla P4** | 8GB | $100-200 | 30-40 tok/s | 75W | **Budget, low power** |
| **RTX A4000** | 16GB | $800-1000 | 60-80 tok/s | 140W | **Modern, efficient** |
| **Tesla K80** | 24GB | $100-200 | 20-30 tok/s | 300W | **Cheapest, high VRAM** |

#### Detailed Comparison

**1. NVIDIA Tesla P40 (24GB) - RECOMMENDED**
```
Architecture: Pascal (2016)
CUDA Cores: 3840
Memory: 24GB GDDR5
Bandwidth: 346 GB/s
TDP: 250W (requires 8-pin PCIe power)
Form Factor: Dual-slot, passive cooling

Performance (Phi-3 Mini 4K):
├─ First token: ~200ms (vs 800ms CPU)
├─ Throughput: 40-60 tok/s (vs 8 tok/s CPU)
└─ 5-7x improvement

Model Capacity:
├─ Phi-3 Mini (3.8B): ✅ FP16 full precision
├─ Llama 3 8B: ✅ FP16 full precision
├─ Llama 3 70B: ✅ INT8 quantized
└─ Multiple models: Can serve 2-3 models simultaneously

Pros:
✅ Excellent VRAM/cost ratio
✅ Data center reliability (designed for 24/7)
✅ ESXi certified hardware
✅ Can run large models (70B with quantization)
✅ Already planned in architecture docs

Cons:
⚠️ Passive cooling (requires good server airflow)
⚠️ 250W power draw (check PSU capacity)
⚠️ Older architecture (no Tensor cores)

Cost Analysis:
├─ Purchase: $300 (average used price)
├─ Power (24/7): ~$27/month
├─ Power (8hrs/day): ~$9/month
└─ vs Cloud (V100): ~$1,500/month
```

**2. NVIDIA Tesla P4 (8GB) - BUDGET OPTION**
```
Architecture: Pascal (2016)
CUDA Cores: 2560
Memory: 8GB GDDR5
Bandwidth: 192 GB/s
TDP: 75W (no external power needed!)
Form Factor: Single-slot, passive cooling

Performance (Phi-3 Mini 4K):
├─ First token: ~250ms
├─ Throughput: 30-40 tok/s
└─ 4-5x improvement

Model Capacity:
├─ Phi-3 Mini (3.8B): ✅ FP16
├─ Llama 3 8B: ✅ FP16
├─ Llama 3 13B: ✅ INT8 quantized
└─ Llama 3 70B: ❌ Too large

Pros:
✅ No external power connector required
✅ Low power consumption (75W)
✅ Single-slot design
✅ Budget-friendly
✅ Good for smaller models (<13B)

Cons:
⚠️ Limited VRAM (8GB)
⚠️ Cannot run large models (70B+)

Cost Analysis:
├─ Purchase: $150 (average used price)
├─ Power (24/7): ~$8/month
├─ Power (8hrs/day): ~$3/month
└─ Near-zero cost for dev sessions
```

**3. NVIDIA RTX A4000 (16GB) - MODERN CHOICE**
```
Architecture: Ampere (2021)
CUDA Cores: 6144
Tensor Cores: 192 (3rd gen)
Memory: 16GB GDDR6
Bandwidth: 448 GB/s
TDP: 140W
Form Factor: Dual-slot, active cooling

Performance (Phi-3 Mini 4K):
├─ First token: ~150ms
├─ Throughput: 60-80 tok/s
└─ 7-10x improvement

Model Capacity:
├─ Phi-3 Mini (3.8B): ✅ FP16
├─ Llama 3 8B: ✅ FP16
├─ Llama 3 13B: ✅ FP16
├─ Llama 3 70B: ✅ FP8/INT8 quantized
└─ Newer features: FP8 precision for larger models

Pros:
✅ Modern architecture (Tensor cores, FP8)
✅ Energy efficient (better perf/watt)
✅ Active cooling (quieter operation)
✅ Great balance of VRAM and performance

Cons:
⚠️ More expensive ($800-1000 used)
⚠️ Less VRAM than P40 (16GB vs 24GB)

Cost Analysis:
├─ Purchase: $900 (average used price)
├─ Power (24/7): ~$15/month
├─ Power (8hrs/day): ~$5/month
└─ vs Cloud (A10): ~$800/month
```

**4. NVIDIA Tesla K80 (24GB) - CHEAPEST**
```
Architecture: Kepler (2014)
CUDA Cores: 4992 (dual GPU: 2496 x 2)
Memory: 24GB GDDR5 (12GB per GPU)
Bandwidth: 240 GB/s
TDP: 300W (requires 8-pin + 6-pin PCIe power)
Form Factor: Dual-slot, passive cooling

Performance (Phi-3 Mini 4K):
├─ First token: ~400ms
├─ Throughput: 20-30 tok/s
└─ 3-4x improvement

Model Capacity:
├─ Phi-3 Mini (3.8B): ✅ FP16
├─ Llama 3 8B: ✅ FP16
├─ Llama 3 70B: ✅ INT8 (distributed across GPUs)
└─ Dual GPU (requires special configuration)

Pros:
✅ Very cheap ($100-200)
✅ High VRAM (24GB total)
✅ Widely available (common in surplus market)

Cons:
⚠️ Old architecture (2014, Kepler)
⚠️ Power hungry (300W TDP)
⚠️ Dual GPU complicates setup
⚠️ Slower than newer cards

Cost Analysis:
├─ Purchase: $150 (average used price)
├─ Power (24/7): ~$32/month
├─ Power (8hrs/day): ~$11/month
└─ Good for learning/testing before P40
```

### Server Compatibility Check

**IBM System x 3650 M4 / 3550 M4 Requirements:**

```
PCIe Slots:
├─ Type: PCIe Gen 3 x16
├─ Quantity: 3-5 slots (model dependent)
├─ Height: Full-height cards supported
└─ Length: Up to 312mm (standard length GPUs fit)

Power Supply:
├─ Typical: 750W - 900W
├─ Available for GPU: ~400-600W
├─ Connectors needed: 8-pin PCIe (for P40/K80)
└─ P4 requires no external power ✅

Cooling:
├─ Airflow: Front-to-back
├─ Passive GPUs: Work with good airflow
├─ Active GPUs: Preferred for quieter operation
└─ Ensure adequate case ventilation

BIOS Support:
├─ VT-d (Intel Virtualization for Directed I/O): Required
├─ Above 4G Decoding: May be required
└─ Check BIOS version: Update to latest if needed
```

### Pre-Purchase Checklist

Run these commands before buying a GPU:

```bash
# SSH to ESXi host
ssh root@192.168.1.128  # or 192.168.1.198

# 1. Check available PCIe slots
esxcli hardware pci list | grep -i "Class.*VGA\|Class.*Display\|Slot"

# 2. Check power supply capacity
esxcli hardware power get

# 3. Check ESXi version (should be 8.0.3+)
vmware -v

# 4. Check VT-d support in BIOS
esxcli hardware platform get | grep -i VT

# 5. List current PCI devices
lspci | grep -i nvidia  # Should show nothing initially
```

**Expected output:**
```
# PCIe slots should show available x16 slots
# Power budget should have 250W+ headroom for P40
# VT-d should be enabled in BIOS
```

## Installation Guide

### Phase 1: Physical Installation

**Time estimate:** 30 minutes

**Tools needed:**
- Phillips screwdriver
- Anti-static wrist strap (recommended)
- Flashlight

**Steps:**

1. **Prepare the server:**
   ```bash
   # Gracefully shut down VMs
   ssh root@192.168.1.198  # Worker node (recommended for GPU)
   vim-cmd vmsvc/getallvms  # Note VM IDs
   vim-cmd vmsvc/power.shutdown <k8s-worker-vm-id>
   
   # Wait for shutdown
   sleep 60
   
   # Power off ESXi host
   esxcli system shutdown poweroff -d 15 -r "Installing GPU hardware"
   ```

2. **Physical installation:**
   ```
   ⚠️ SAFETY: Disconnect power cable from server
   ⚠️ Wait 30 seconds for capacitors to discharge
   ⚠️ Use anti-static wrist strap
   
   1. Remove server cover
   2. Locate available PCIe x16 slot (usually blue)
   3. Remove slot cover plate
   4. Insert GPU firmly into PCIe slot
   5. Secure with screw
   6. Connect PCIe power cables:
      - P40: 1x 8-pin PCIe power
      - P4: No external power needed
      - K80: 1x 8-pin + 1x 6-pin PCIe power
   7. Verify card is fully seated
   8. Replace server cover
   9. Reconnect power cable
   ```

3. **Power on and verify:**
   ```bash
   # Power on server (use IMM2 or press power button)
   
   # SSH back to ESXi
   ssh root@192.168.1.198
   
   # Verify GPU detected
   lspci | grep -i nvidia
   
   # Expected output:
   # 0000:04:00.0 3D controller: NVIDIA Corporation GP102GL [Tesla P40]
   ```

### Phase 2: ESXi Configuration

**Time estimate:** 30 minutes

**1. Enable VT-d in BIOS (if not already enabled):**

```bash
# Access IMM2
# Navigate to: http://192.168.1.199
# Login → Remote Control → Launch Console
# Restart server → Press F1 for BIOS setup
# Advanced → Processors → Enable VT-d
# Save and exit
```

**2. Configure GPU passthrough in ESXi:**

```bash
# SSH to ESXi host
ssh root@192.168.1.198

# List PCI devices to find GPU ID
esxcli hardware pci list | grep -i nvidia

# Example output:
# 0000:04:00.0 3D controller: NVIDIA Corporation GP102GL [Tesla P40] [10de:1b38]

# Enable passthrough for the GPU (use your device ID)
esxcli hardware pci pcidevice set -d 0000:04:00.0 -e true

# Verify passthrough enabled
esxcli hardware pci pcidevice list | grep -A 5 -i nvidia

# Should show: "Passthrough Enabled: true"

# Reboot ESXi host for changes to take effect
esxcli system shutdown reboot -d 15 -r "Enabling GPU passthrough"
```

**3. Verify passthrough after reboot:**

```bash
# SSH back after reboot
ssh root@192.168.1.198

# Check passthrough status
esxcli hardware pci pcidevice list | grep -B 2 -A 5 "Passthrough Enabled: true"

# List available passthrough devices
esxcli hardware pci pcidevice list | grep -i "Passthrough.*true" | wc -l
# Should show at least 1
```

### Phase 3: VM Configuration

**Time estimate:** 15 minutes

**1. Power off k8s-worker VM:**

```bash
# Find k8s-worker VM ID
vim-cmd vmsvc/getallvms | grep -i worker

# Power off the VM (use your VM ID)
vim-cmd vmsvc/power.off <vm-id>

# Verify powered off
vim-cmd vmsvc/power.getstate <vm-id>
```

**2. Add PCI device to VM:**

```bash
# Method 1: Via vim-cmd (command line)

# Get PCI device ID from earlier step (e.g., 0000:04:00.0)
# Add GPU to VM configuration
vim-cmd vmsvc/device.pcipassthru.add <vm-id> 0000:04:00.0

# Verify device added
vim-cmd vmsvc/get.config <vm-id> | grep -i pci

# Method 2: Manual edit of VMX file (alternative)

# Find VM VMX file
find /vmfs/volumes -name "*worker*.vmx"

# Edit VMX file
vi /vmfs/volumes/datastore1/k8s-worker/k8s-worker.vmx

# Add these lines at the end:
# pciPassthru0.present = "TRUE"
# pciPassthru0.id = "0000:04:00.0"
# pciPassthru0.deviceId = "0x1b38"  # P40 device ID, adjust for your GPU
# pciPassthru0.vendorId = "0x10de"  # NVIDIA vendor ID
# hypervisor.cpuid.v0 = "FALSE"      # Hide VM from guest OS
```

**3. Increase VM memory reservation:**

```bash
# GPU passthrough requires memory reservation
# Edit VM settings to reserve all allocated RAM

vim-cmd vmsvc/get.config <vm-id> | grep -i memoryReservationLockedToMax
# If FALSE, need to set to TRUE

# Alternatively, ensure VM has enough RAM allocated
# P40 requires at least 8GB host RAM + 24GB for VRAM mapping
# Recommended: Keep VM at 64GB with full reservation
```

**4. Power on VM:**

```bash
# Start the VM
vim-cmd vmsvc/power.on <vm-id>

# Monitor boot
tail -f /var/log/vmware.log | grep -i nvidia

# Check VM console for any PCI errors
vim-cmd vmsvc/get.summary <vm-id>
```

**5. Verify GPU visible in VM:**

```bash
# SSH to k8s-worker VM
ssh almalinux@192.168.1.131

# Check if GPU is visible
lspci | grep -i nvidia

# Expected output:
# 03:00.0 3D controller: NVIDIA Corporation GP102GL [Tesla P40] (rev a1)

# Verify device files
ls -la /dev/nvidia*
# If no /dev/nvidia*, drivers not installed yet (next phase)
```

### Phase 4: Driver Installation

**Time estimate:** 30 minutes

**1. Install kernel headers and development tools:**

```bash
# SSH to k8s-worker VM
ssh almalinux@192.168.1.131

# Update system
sudo dnf update -y

# Install required packages
sudo dnf install -y \
  kernel-devel-$(uname -r) \
  kernel-headers-$(uname -r) \
  gcc \
  make \
  elfutils-libelf-devel \
  tar \
  wget

# Install EPEL repository (for DKMS)
sudo dnf install -y epel-release
sudo dnf install -y dkms
```

**2. Download and install NVIDIA driver:**

```bash
# Check CUDA compatibility for your GPU
# P40: CUDA 12.x compatible, driver >= 525.x

# Download NVIDIA driver (adjust version as needed)
wget https://us.download.nvidia.com/tesla/550.127.05/NVIDIA-Linux-x86_64-550.127.05.run

# Make executable
chmod +x NVIDIA-Linux-x86_64-550.127.05.run

# Run installer
sudo ./NVIDIA-Linux-x86_64-550.127.05.run \
  --silent \
  --dkms \
  --disable-nouveau \
  --no-x-check \
  --no-nouveau-check

# If installation fails due to nouveau driver:
# 1. Blacklist nouveau
sudo bash -c "cat > /etc/modprobe.d/blacklist-nouveau.conf" << EOF
blacklist nouveau
options nouveau modeset=0
EOF

# 2. Rebuild initramfs
sudo dracut --force

# 3. Reboot
sudo reboot

# After reboot, re-run NVIDIA installer
```

**3. Verify driver installation:**

```bash
# Check NVIDIA driver loaded
lsmod | grep nvidia

# Should show:
# nvidia_drm
# nvidia_modeset
# nvidia
# nvidia_uvm

# Run nvidia-smi
nvidia-smi

# Expected output:
# +-----------------------------------------------------------------------------+
# | NVIDIA-SMI 550.127.05   Driver Version: 550.127.05   CUDA Version: 12.4     |
# |-------------------------------+----------------------+----------------------+
# | GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
# | Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
# |===============================+======================+======================|
# |   0  Tesla P40           Off  | 00000000:03:00.0 Off |                    0 |
# | N/A   32C    P0    48W / 250W |      0MiB / 24576MiB |      0%      Default |
# +-------------------------------+----------------------+----------------------+
```

**4. Install CUDA toolkit (for development):**

```bash
# Download CUDA installer
wget https://developer.download.nvidia.com/compute/cuda/12.4.0/local_installers/cuda_12.4.0_550.54.14_linux.run

# Install CUDA
sudo sh cuda_12.4.0_550.54.14_linux.run --silent --toolkit --override

# Add to PATH
echo 'export PATH=/usr/local/cuda-12.4/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.4/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# Verify CUDA installation
nvcc --version

# Expected output:
# nvcc: NVIDIA (R) Cuda compiler driver
# Cuda compilation tools, release 12.4, V12.4.XX
```

### Phase 5: vLLM GPU Configuration

**Time estimate:** 15 minutes

**1. Install GPU-enabled vLLM:**

```bash
# SSH to k8s-control VM (where vLLM runs)
ssh almalinux@192.168.1.130

# Uninstall CPU-only vLLM
pip3 uninstall -y vllm

# Install GPU-enabled vLLM with CUDA support
pip3 install vllm[cuda] --extra-index-url https://download.pytorch.org/whl/cu124

# Verify installation
python3 -c "import vllm; print(vllm.__version__)"

# Check CUDA availability
python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

**2. Update vLLM startup script:**

```bash
# Edit vLLM startup script
vi /path/to/vllm/startup.sh

# Update to:
#!/bin/bash

# GPU-accelerated vLLM server
python3 -m llama_cpp.server \
  --model /models/phi-3-mini-4k-instruct.Q4_K_M.gguf \
  --host 0.0.0.0 \
  --port 8000 \
  --n_ctx 4096 \
  --n_gpu_layers -1 \
  --tensor_split 0 \
  --n_threads 8

# Explanation of flags:
# --n_gpu_layers -1     : Offload ALL layers to GPU
# --tensor_split 0      : Use first GPU (for multi-GPU setups)
# --n_threads 8         : CPU threads for preprocessing (reduce CPU usage)
```

**Alternative: Use pure vLLM (not llama-cpp-python):**

```bash
# Create new startup script for pure vLLM
cat > ~/vllm-gpu-server.sh << 'EOF'
#!/bin/bash

# vLLM GPU server with OpenAI-compatible API
python3 -m vllm.entrypoints.openai.api_server \
  --model microsoft/Phi-3-mini-4k-instruct \
  --host 0.0.0.0 \
  --port 8000 \
  --tensor-parallel-size 1 \
  --dtype auto \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.9 \
  --trust-remote-code

# Flags explained:
# --tensor-parallel-size 1           : Single GPU
# --dtype auto                       : Auto-detect best precision (FP16)
# --max-model-len 4096              : Context window size
# --gpu-memory-utilization 0.9      : Use 90% of GPU VRAM
# --trust-remote-code               : Required for Phi-3
EOF

chmod +x ~/vllm-gpu-server.sh

# Run vLLM server
~/vllm-gpu-server.sh
```

**3. Create systemd service for vLLM:**

```bash
# Create service file
sudo tee /etc/systemd/system/vllm-gpu.service > /dev/null << 'EOF'
[Unit]
Description=vLLM GPU Inference Server
After=network.target

[Service]
Type=simple
User=almalinux
WorkingDirectory=/home/almalinux
ExecStart=/home/almalinux/vllm-gpu-server.sh
Restart=always
RestartSec=10
Environment="CUDA_VISIBLE_DEVICES=0"

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable vllm-gpu.service
sudo systemctl start vllm-gpu.service

# Check status
sudo systemctl status vllm-gpu.service

# View logs
sudo journalctl -u vllm-gpu.service -f
```

### Phase 6: Performance Testing

**Time estimate:** 15 minutes

**1. Test GPU inference:**

```bash
# Simple completion test
curl http://192.168.1.130:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "microsoft/Phi-3-mini-4k-instruct",
    "messages": [{"role": "user", "content": "Explain Kubernetes in one sentence."}],
    "max_tokens": 100,
    "stream": false
  }'

# Monitor GPU utilization during inference
ssh almalinux@192.168.1.131
watch -n 1 nvidia-smi

# Expected GPU utilization during inference: 80-100%
```

**2. Benchmark performance:**

```bash
# Install benchmarking tool
pip3 install openai

# Create benchmark script
cat > benchmark-gpu.py << 'EOF'
import time
import openai

openai.api_base = "http://192.168.1.130:8000/v1"
openai.api_key = "not-needed"

# Warmup
print("Warming up...")
response = openai.ChatCompletion.create(
    model="microsoft/Phi-3-mini-4k-instruct",
    messages=[{"role": "user", "content": "Hello"}],
    max_tokens=10
)

# Benchmark
print("\nBenchmarking...")
prompts = [
    "Explain machine learning",
    "What is Kubernetes?",
    "Describe neural networks",
    "How does Docker work?",
    "Explain distributed systems"
]

total_tokens = 0
total_time = 0

for prompt in prompts:
    start = time.time()
    response = openai.ChatCompletion.create(
        model="microsoft/Phi-3-mini-4k-instruct",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100
    )
    elapsed = time.time() - start
    
    tokens = response['usage']['completion_tokens']
    total_tokens += tokens
    total_time += elapsed
    
    tok_per_sec = tokens / elapsed
    print(f"Prompt: {prompt[:30]}... | {tokens} tokens in {elapsed:.2f}s | {tok_per_sec:.1f} tok/s")

avg_tok_per_sec = total_tokens / total_time
print(f"\nAverage: {avg_tok_per_sec:.1f} tokens/sec")
print(f"Total tokens: {total_tokens}")
print(f"Total time: {total_time:.2f}s")
EOF

python3 benchmark-gpu.py
```

**Expected results:**
```
# CPU baseline (before GPU):
Average: ~8 tokens/sec

# With Tesla P40:
Average: ~50 tokens/sec (6x improvement)

# With RTX A4000:
Average: ~70 tokens/sec (9x improvement)
```

**3. Monitor GPU metrics:**

```bash
# Real-time GPU monitoring
nvidia-smi dmon -s pucvmet -d 1

# GPU memory usage
nvidia-smi --query-gpu=memory.used,memory.total --format=csv -l 1

# GPU temperature and power
nvidia-smi --query-gpu=temperature.gpu,power.draw,power.limit --format=csv -l 1
```

## Troubleshooting

### Issue: GPU not visible in lspci

**Symptoms:** `lspci | grep -i nvidia` shows nothing

**Solutions:**
1. Verify physical installation (card seated properly, power connected)
2. Check BIOS settings (Above 4G Decoding may be needed)
3. Try different PCIe slot
4. Reseat the card

```bash
# Check ESXi sees the device
esxcli hardware pci list | grep -i display

# Check for errors in ESXi logs
tail -f /var/log/vmkernel.log | grep -i pci
```

### Issue: Passthrough fails with "device not available"

**Symptoms:** VM fails to start with PCI passthrough error

**Solutions:**
1. Verify passthrough enabled: `esxcli hardware pci pcidevice list`
2. Check VM memory reservation (must be 100% or locked)
3. Ensure no other VM using the GPU
4. Reboot ESXi host after enabling passthrough

```bash
# Check passthrough status
esxcli hardware pci pcidevice list | grep -A 10 "0000:04:00.0"

# Verify only one VM has the device
vim-cmd vmsvc/getallvms | while read vmid rest; do
  vim-cmd vmsvc/get.config $vmid | grep -i pciPassthru && echo "VM $vmid"
done
```

### Issue: NVIDIA driver installation fails

**Symptoms:** Driver installer errors or kernel module not loading

**Solutions:**
1. Blacklist nouveau driver (conflicts with NVIDIA)
2. Ensure kernel-devel matches running kernel
3. Disable secure boot in BIOS

```bash
# Check kernel version match
uname -r
rpm -q kernel-devel

# If mismatch:
sudo dnf install -y kernel-devel-$(uname -r)

# Blacklist nouveau
sudo bash -c "cat > /etc/modprobe.d/blacklist-nouveau.conf" << EOF
blacklist nouveau
options nouveau modeset=0
EOF

sudo dracut --force
sudo reboot

# After reboot, reinstall NVIDIA driver
```

### Issue: nvidia-smi shows "No devices found"

**Symptoms:** Driver installed but GPU not detected

**Solutions:**
1. Verify GPU visible in `lspci`
2. Check nvidia kernel modules loaded: `lsmod | grep nvidia`
3. Check dmesg for errors: `dmesg | grep -i nvidia`

```bash
# Manual module load
sudo modprobe nvidia
sudo modprobe nvidia_uvm

# Check for errors
dmesg | tail -50

# Reinstall driver if needed
sudo dkms remove nvidia/550.127.05 --all
sudo ./NVIDIA-Linux-x86_64-550.127.05.run --uninstall
# Then reinstall
```

### Issue: vLLM not using GPU

**Symptoms:** vLLM running but nvidia-smi shows 0% GPU utilization

**Solutions:**
1. Verify CUDA available in Python: `python3 -c "import torch; print(torch.cuda.is_available())"`
2. Check vLLM installed with CUDA support: `pip3 list | grep vllm`
3. Ensure `--n_gpu_layers -1` flag set in startup script

```bash
# Verify PyTorch CUDA
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, Devices: {torch.cuda.device_count()}')"

# Should output: CUDA: True, Devices: 1

# Reinstall vLLM with CUDA
pip3 uninstall -y vllm torch
pip3 install vllm[cuda] --extra-index-url https://download.pytorch.org/whl/cu124

# Test CUDA in vLLM
python3 -c "from vllm import LLM; print('vLLM GPU ready')"
```

### Issue: Out of memory errors

**Symptoms:** "CUDA out of memory" or model fails to load

**Solutions:**
1. Reduce model size (use smaller quantization: Q4 → Q3)
2. Decrease `--gpu-memory-utilization` from 0.9 to 0.7
3. Reduce `--max-model-len` context window
4. Use model with smaller parameter count

```bash
# Check GPU memory usage
nvidia-smi

# Adjust vLLM parameters
python3 -m vllm.entrypoints.openai.api_server \
  --model microsoft/Phi-3-mini-4k-instruct \
  --gpu-memory-utilization 0.7 \
  --max-model-len 2048 \
  ...
```

### Issue: Performance not improving

**Symptoms:** GPU installed but tokens/sec same as CPU

**Solutions:**
1. Verify GPU actually in use (check nvidia-smi during inference)
2. Check CPU offloading: `--n_gpu_layers -1` (all layers on GPU)
3. Monitor PCIe bandwidth (may be limited in some slots)
4. Verify using correct model format (GGUF vs safetensors)

```bash
# Monitor during inference
watch -n 0.1 nvidia-smi

# Check PCIe bandwidth
nvidia-smi -q -d PERFORMANCE

# Expected for PCIe Gen 3 x16: ~16 GB/s
```

## Cost Analysis

### Purchase Costs

| GPU | Used Price | Where to Buy |
|-----|------------|--------------|
| Tesla P40 | $200-400 | eBay, ServerMonkey, LabGopher |
| Tesla P4 | $100-200 | eBay, Amazon |
| RTX A4000 | $800-1000 | eBay, Newegg |
| Tesla K80 | $100-200 | eBay (very common) |

**Recommended vendors:**
- eBay (search "Tesla P40 24GB")
- ServerMonkey (https://www.servermonkey.com/)
- LabGopher (https://labgopher.com/)
- Amazon (search "refurbished Tesla P40")

### Operating Costs

**Tesla P40 (250W):**
```
24/7 operation:
├─ Power: 250W × 24hr × 30 days = 180 kWh
├─ Cost: 180 kWh × $0.15 = $27/month
└─ Annual: $324/year

8 hours/day (dev sessions):
├─ Power: 250W × 8hr × 30 days = 60 kWh
├─ Cost: 60 kWh × $0.15 = $9/month
└─ Annual: $108/year

vs Cloud GPU (NVIDIA V100):
├─ AWS p3.2xlarge: $3.06/hour
├─ 8 hours/day: $734/month
└─ Annual: $8,808/year

Savings: $8,700/year (vs 8hr/day cloud usage)
```

**Tesla P4 (75W):**
```
24/7 operation:
├─ Power: 75W × 24hr × 30 days = 54 kWh
├─ Cost: 54 kWh × $0.15 = $8/month
└─ Annual: $96/year

8 hours/day:
├─ Cost: ~$3/month
└─ Annual: $36/year

Near-zero cost for occasional dev sessions
```

### Break-Even Analysis

**Tesla P40 scenario:**
```
Initial investment:
├─ GPU: $300
├─ Power cables (if needed): $20
└─ Total: $320

Monthly cost (8hr/day): $9
Cloud equivalent (8hr/day): $734

Monthly savings: $725
Break-even: 0.44 months (~13 days!)

After 1 year:
├─ Total cost: $320 + ($9 × 12) = $428
├─ Cloud cost: $734 × 12 = $8,808
└─ Savings: $8,380
```

**Tesla P4 scenario:**
```
Initial investment: $150
Monthly cost (8hr/day): $3
Cloud equivalent (T4): $300/month

Monthly savings: $297
Break-even: 0.5 months (~15 days)

After 1 year savings: $3,414
```

## Performance Benchmarks

### Expected Performance Improvements

**Phi-3 Mini 4K (3.8B parameters):**

| Hardware | Tokens/sec | First Token | Latency | Throughput Gain |
|----------|------------|-------------|---------|-----------------|
| CPU (Xeon E5-2690) | 8 | 800ms | High | Baseline |
| Tesla P4 (8GB) | 35 | 250ms | Medium | 4.4x |
| Tesla P40 (24GB) | 50 | 200ms | Low | 6.3x |
| RTX A4000 (16GB) | 70 | 150ms | Very Low | 8.8x |

**Llama 3 8B:**

| Hardware | Tokens/sec | VRAM Used | Precision |
|----------|------------|-----------|-----------|
| CPU | 2-3 | System RAM | Q4 |
| Tesla P4 | 15-20 | 6GB | FP16 |
| Tesla P40 | 25-30 | 16GB | FP16 |
| RTX A4000 | 35-40 | 14GB | FP16 |

**Llama 3 70B (quantized):**

| Hardware | Tokens/sec | VRAM Used | Precision | Fits? |
|----------|------------|-----------|-----------|-------|
| Tesla P4 (8GB) | N/A | N/A | N/A | ❌ Too large |
| Tesla P40 (24GB) | 8-12 | 22GB | INT8 | ✅ Tight fit |
| RTX A4000 (16GB) | 10-15 | 15GB | FP8 | ✅ With optimization |

### Real-World Use Cases

**1. Development workflow (8 hours/day, 5 days/week):**
```
Use case: Interactive agent development with local models
Model: Phi-3 Mini 4K
GPU: Tesla P40

Performance:
├─ Instant feedback (<200ms first token)
├─ 50 tok/s sustained throughput
├─ Can test 100+ agent interactions/hour
└─ No API costs, unlimited usage

Monthly cost: ~$5 electricity
Cloud equivalent: $1,000+ (V100 instance)
Savings: $995/month
```

**2. Batch processing (overnight jobs):**
```
Use case: Process 10,000 documents with LLM summarization
Model: Llama 3 8B
GPU: Tesla P40

Performance:
├─ 30 tok/s × 100 tokens/doc = 3.3 sec/doc
├─ 10,000 docs = 9.2 hours total
└─ Single overnight job

Cost: $1 electricity (9 hours × 250W)
Cloud: $28 (9 hours × $3.06/hour p3.2xlarge)
Savings: $27 per batch
```

**3. Production serving (24/7 API):**
```
Use case: Internal API serving 1,000 requests/day
Model: Phi-3 Mini 4K
GPU: Tesla P40

Performance:
├─ 50 tok/s throughput
├─ Can handle 10+ concurrent requests
├─ 99.9% uptime (local control)
└─ No rate limits

Monthly cost: $27 electricity
Cloud: $2,200 (24/7 p3.2xlarge)
Savings: $2,173/month
```

## Next Steps

After successful GPU installation:

1. **Update documentation:**
   - Add GPU specs to [README.md](../README.md)
   - Update [ARCHITECTURE.md](../ARCHITECTURE.md) with GPU architecture
   - Document performance benchmarks

2. **Update Kagent model configs:**
   - Create GPU-accelerated ModelConfigs
   - Test agents with GPU-backed models
   - Compare performance vs CPU models

3. **Enable KServe GPU scheduling:**
   - Configure KServe to use GPU nodes
   - Deploy InferenceServices with GPU requests
   - Test autoscaling with GPU workloads

4. **Optimize for cost:**
   - Create power management scripts
   - Schedule heavy workloads during low-rate hours
   - Monitor GPU utilization and right-size

5. **Scale up:**
   - Consider second GPU in 3650 M4
   - Explore multi-GPU inference (tensor parallelism)
   - Deploy larger models (Llama 3 70B)

## Resources

**Documentation:**
- NVIDIA Tesla P40 Datasheet: https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/tesla-p40/nvidia-tesla-p40-datasheet.pdf
- ESXi GPU Passthrough Guide: https://docs.vmware.com/en/VMware-vSphere/8.0/vsphere-resource-management/GUID-2C6C0A3C-5F3B-4C3C-B6F0-2C6C0A3C5F3B.html
- vLLM GPU Installation: https://docs.vllm.ai/en/latest/getting_started/installation.html

**Community:**
- r/homelab - GPU in home servers
- ServeTheHome forums - Enterprise GPU discussions
- vLLM Discord - GPU inference optimization

**Tools:**
- GPU-Z: Verify GPU specifications
- nvidia-smi: Monitor GPU utilization
- nvtop: htop-like GPU monitor

---

**Guide Version:** 1.0  
**Last Updated:** 2026-04-25  
**Next Review:** After first GPU installation
