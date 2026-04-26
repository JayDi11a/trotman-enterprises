# vLLM + GPU Deployment (Future)

**Status:** Parked until GPU hardware acquired

## Why vLLM is parked
- vLLM **does not support CPU inference on Linux** (only macOS for testing)
- Platform detection requires GPU-specific builds
- Designed for A100/H100/MI250 GPU deployments

## Current CPU Solution
- **llama.cpp-python** with systemd services (ports 30700-30714)
- Works perfectly on CPU (Xeon E5-2690)
- OpenAI-compatible API
- Proven reliable for 15 function-calling models

## GPU Hardware Options (Future)
- NVIDIA Tesla P40 (24GB) - Good for single large model
- NVIDIA A40 (48GB) - Better multi-model support
- AMD MI250 (128GB) - Best value for multiple 70B models

## When GPU acquired:
1. Enable GPU passthrough in ESXi (vDGA)
2. Install CUDA drivers in k8s-control VM
3. Deploy vLLM with GPU support
4. Migrate high-throughput models from llama.cpp to vLLM
5. Keep llama.cpp for CPU overflow/redundancy

## vLLM Performance Benefits (with GPU)
- 10-50x faster inference than CPU
- PagedAttention for better memory efficiency
- Continuous batching for higher throughput
- Multiple LoRA adapters simultaneously

## References
- vLLM GitHub: https://github.com/vllm-project/vllm
- ESXi GPU Passthrough: https://docs.vmware.com/en/VMware-vSphere/8.0/vsphere-resource-management/GUID-58B9FED9-C31F-4AD6-A302-09D5B1F5DB95.html
