# Function Calling / Tool Calling Models

## Current Setup
- **Storage:** 
  - Root (/): 70GB total, 13GB available, 58GB used
  - Home (/home): 109GB total, **108GB available** (optimal for large models)
  - Current Ollama models: 16GB (llama3.1:8b, mistral:7b, hermes3:8b)
- **Issue:** Existing Ollama models output JSON but don't execute tools properly through LangChain
- **Solution:** Deploy vLLM with proper function-calling models OR use cloud APIs

---

## FREE Local Models (100% self-hosted via vLLM)

### Tier 1: Production-Ready Function Calling (Recommended)

#### 1. **Llama 3.1 70B-Instruct** ⭐ BEST OVERALL
- **Size:** ~40GB
- **Function Calling:** Excellent (native OpenAI-compatible)
- **Performance:** 2-4 tokens/sec on CPU (acceptable for tools)
- **Use Case:** Primary recommendation - best balance of size/quality
- **Download:** `meta-llama/Llama-3.1-70B-Instruct`

#### 2. **Qwen2.5 72B-Instruct** ⭐ STRONG ALTERNATIVE
- **Size:** ~43GB
- **Function Calling:** Excellent (purpose-built for it)
- **Performance:** 2-4 tokens/sec on CPU
- **Use Case:** Alternative to Llama 70B, some prefer for tool use
- **Download:** `Qwen/Qwen2.5-72B-Instruct`

#### 3. **Functionary 70B v2.5** ⭐ PURPOSE-BUILT
- **Size:** ~40GB
- **Function Calling:** Excellent (specifically trained for function calling)
- **Performance:** 2-4 tokens/sec on CPU
- **Use Case:** Best for complex multi-tool scenarios
- **Download:** `meetkai/functionary-medium-v2.5`

---

### Tier 2: Smaller Efficient Models

#### 4. **Qwen2.5 32B-Instruct**
- **Size:** ~19GB
- **Function Calling:** Very Good
- **Performance:** 4-8 tokens/sec on CPU
- **Use Case:** Good balance for limited resources
- **Download:** `Qwen/Qwen2.5-32B-Instruct`

#### 5. **Hermes 2 Pro Llama 3 8B** (replacement for current hermes3:8b)
- **Size:** ~4.9GB
- **Function Calling:** Good (better than vanilla Llama 3)
- **Performance:** 8-12 tokens/sec on CPU
- **Use Case:** Lightweight tool calling
- **Download:** `NousResearch/Hermes-2-Pro-Llama-3-8B`

#### 6. **Qwen2.5 14B-Instruct**
- **Size:** ~8.7GB
- **Function Calling:** Very Good
- **Performance:** 6-10 tokens/sec on CPU
- **Use Case:** Good middle ground
- **Download:** `Qwen/Qwen2.5-14B-Instruct`

#### 7. **Functionary 7B v3.1**
- **Size:** ~4.4GB
- **Function Calling:** Good
- **Performance:** 8-12 tokens/sec on CPU
- **Use Case:** Smallest dedicated function calling model
- **Download:** `meetkai/functionary-small-v3.1`

---

### Tier 3: Advanced / Experimental

#### 8. **Llama 3.1 405B-Instruct** (if you have LOTS of storage)
- **Size:** ~231GB
- **Function Calling:** Best in class
- **Performance:** 0.5-1 token/sec on CPU (SLOW but accurate)
- **Use Case:** Ultimate quality, research, benchmarking
- **Download:** `meta-llama/Llama-3.1-405B-Instruct`

#### 9. **Mixtral 8x7B-Instruct**
- **Size:** ~26GB
- **Function Calling:** Good
- **Performance:** 3-6 tokens/sec on CPU
- **Use Case:** MoE architecture, efficient inference
- **Download:** `mistralai/Mixtral-8x7B-Instruct-v0.1`

#### 10. **Mixtral 8x22B-Instruct**
- **Size:** ~87GB
- **Function Calling:** Very Good
- **Performance:** 1-2 tokens/sec on CPU
- **Use Case:** Larger MoE for better quality
- **Download:** `mistralai/Mixtral-8x22B-Instruct-v0.1`

#### 11. **Granite 3.0 8B-Instruct** (IBM, recent)
- **Size:** ~4.9GB
- **Function Calling:** Good (new model, Feb 2024)
- **Performance:** 8-12 tokens/sec on CPU
- **Use Case:** Enterprise-friendly license
- **Download:** `ibm-granite/granite-3.0-8b-instruct`

---

## PAID Cloud Models (API-based, no storage needed)

### 12. **Anthropic Claude Sonnet 4.5** ⭐ ALREADY CONFIGURED
- **Cost:** ~$1-2/month light usage
- **Function Calling:** Excellent
- **Latency:** ~500ms first token
- **Use Case:** Production-ready, low maintenance
- **Status:** Already in trotman-chat.py

### 13. **Anthropic Claude Opus 4.7**
- **Cost:** ~$3-5/month light usage
- **Function Calling:** Best in class
- **Latency:** ~500ms first token
- **Use Case:** Most complex tool scenarios
- **Status:** Can enable in trotman-chat.py

### 14. **OpenAI GPT-4o**
- **Cost:** ~$2-4/month light usage
- **Function Calling:** Excellent
- **Latency:** ~300ms first token
- **Use Case:** Fast, reliable
- **Status:** Need to add to trotman-chat.py

### 15. **OpenAI GPT-4o-mini**
- **Cost:** ~$0.50/month light usage
- **Function Calling:** Very Good
- **Latency:** ~200ms first token
- **Use Case:** Cheapest quality option
- **Status:** Need to add to trotman-chat.py

---

## Recommended Deployment Strategy

### Option A: Single Best Model (Recommended for starting)
**Deploy:** Llama 3.1 70B-Instruct via vLLM
- **Why:** Best balance of quality/size, proven function calling
- **Storage:** 40GB (fits comfortably in 108GB available)
- **Cost:** $0
- **Setup Time:** 30 minutes

### Option B: Tiered Deployment (Recommended for production)
**Deploy 3 models:**
1. **Llama 3.1 70B-Instruct** (40GB) - Primary tool calling
2. **Qwen2.5 14B-Instruct** (8.7GB) - Fast lightweight tools
3. **Claude Sonnet 4.5** (API) - Fallback for complex scenarios

**Total Storage:** 48.7GB (fits in 108GB available)
**Total Cost:** ~$1-2/month (Claude only)

### Option C: Maximum Coverage (Everything!)
**Deploy locally:**
1. Llama 3.1 70B-Instruct (40GB)
2. Qwen2.5 72B-Instruct (43GB)
3. Functionary 70B (40GB)
4. Qwen2.5 32B-Instruct (19GB)
5. Keep existing 3 Ollama models (16GB)

**Total Storage:** 158GB (need to optimize storage first - see below)
**Total Cost:** $0

### Option D: Research Lab (All sizes)
**All local models above** = ~550GB
**Requires:** Storage expansion to /home or additional drive

---

## Storage Optimization Required

Current Ollama models are stored in pod ephemeral storage (root filesystem).
For large model deployment, we need to:

1. **Create PVC backed by /home partition (108GB available)**
2. **Or mount /home into vLLM deployment**
3. **Or add Longhorn StorageClass for distributed storage**

**Next Steps:**
1. Choose deployment strategy (A, B, C, or D)
2. Optimize storage (I'll create the manifests)
3. Deploy vLLM with selected models
4. Test function calling with kubectl/helm tools
5. Update trotman-chat.py to use vLLM endpoint

---

## Model Testing Priority

Once deployed, test in this order:
1. **Llama 3.1 70B** - Most likely to work perfectly
2. **Qwen2.5 72B** - Strong alternative
3. **Functionary 70B** - Purpose-built, should be excellent
4. **Smaller models** - For performance comparison

---

## What I Need From You

**Question 1:** Which deployment strategy?
- **Option A:** Single best model (Llama 3.1 70B) - safest start
- **Option B:** Tiered (70B + 14B + Claude) - production ready
- **Option C:** Maximum coverage (all 70B+ models) - need storage optimization first
- **Option D:** Everything (all models) - need significant storage work

**Question 2:** Storage preference?
- **Option 1:** Create PVC using /home partition (108GB, simple)
- **Option 2:** Add external drive to cluster (requires hardware)
- **Option 3:** Use Longhorn for distributed storage (more complex)

Let me know and I'll deploy immediately!
