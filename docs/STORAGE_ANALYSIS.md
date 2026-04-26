# Storage Analysis - Trotman Enterprises ML Lab

## Current VM Storage Allocation

### Control Plane (ruckus-unleashed / k8s-control)
```
Total VM Disk:    200GB (virtual disk from ESXi)
LVM Layout:
  - /root:        70GB  (58GB used, 13GB free)
  - /home:        109GB (0.8GB used, 108GB free) ✅
  - swap:         20GB
  - /boot:        1GB

Usable for Models: 108GB in /home
```

### Worker Node (controller / k8s-worker)
```
Total VM Disk:    ~70GB ephemeral storage
Status:          Similar to control plane
```

---

## Current Model Storage

### Ollama Models (16GB total)
- llama3.1:8b (4.9GB)
- mistral:7b (4.4GB)
- hermes3:8b (4.7GB)
- **Location:** Pod ephemeral storage (not persistent)

---

## Storage Capacity vs. Requirements

### Option C Requirements (158GB)
| Model                      | Size  | Status          |
|----------------------------|-------|-----------------|
| Llama 3.1 70B-Instruct     | 40GB  | **FITS** ✅      |
| Qwen2.5 72B-Instruct       | 43GB  | **FITS** ✅      |
| Functionary 70B            | 40GB  | **FITS** ✅      |
| Qwen2.5 32B-Instruct       | 19GB  | **FITS** ✅      |
| Existing Ollama models     | 16GB  | Already deployed |
| **TOTAL**                  | 158GB | **FITS in 109GB /home + 13GB /root = 122GB?** ❌ |

**Verdict:** Need ~36GB more space for Option C

### Option D Requirements (550GB)
All 15 function-calling models = **550GB**

**Verdict:** Need **442GB additional storage** beyond current 108GB

---

## ISSUE: VM Disk Limitation

**Problem:** Each VM was allocated only 200GB virtual disk from ESXi
- This is NOT the physical server storage
- The IBM System x bare metal servers likely have **MUCH more** (TBs?)
- ESXi datastores probably have unused capacity

---

## Solutions to Access TB Storage

### Option 1: Expand Existing VMDK (Simplest) ⭐
**Steps:**
1. Access ESXi host (vSphere client or SSH)
2. Power off VMs or use hot-add (if enabled)
3. Expand control plane VMDK from 200GB → 1TB
4. Expand worker node VMDK from 200GB → 1TB
5. Boot VMs, extend LVM partitions
6. Allocate extra space to `/home` or create `/models`

**Pros:**
- Uses existing infrastructure
- Simple LVM extension
- No new disks to manage

**Cons:**
- Requires ESXi access
- Brief downtime if not hot-add capable

---

### Option 2: Add New Virtual Disks to VMs
**Steps:**
1. Access ESXi host
2. Add new 1TB VMDK to control plane VM
3. Add new 1TB VMDK to worker VM
4. Mount as `/models` or integrate into LVM
5. Use for model storage

**Pros:**
- Keep existing system disk intact
- Dedicated model storage
- Can use different datastore

**Cons:**
- Requires ESXi access
- More disks to manage

---

### Option 3: NFS/iSCSI from ESXi or NAS
**Steps:**
1. Expose ESXi datastore via NFS
2. Or use separate NAS if available
3. Mount shared storage to both VMs
4. Store models on shared storage

**Pros:**
- Shared storage across nodes
- No VM reconfiguration
- Easy to expand

**Cons:**
- Network overhead
- NFS/iSCSI setup complexity

---

### Option 4: Longhorn Distributed Storage (Already Deployed!)
**Current Status:** Longhorn is already deployed in the cluster
**Steps:**
1. Check Longhorn datastore capacity
2. If ESXi has available space, expand Longhorn backing store
3. Create large PVC for model storage
4. Mount PVC to vLLM/Ollama pods

**Pros:**
- Already deployed infrastructure
- Kubernetes-native
- Replicated storage
- No VM-level changes needed

**Cons:**
- Limited by current VM disk space
- Still need ESXi expansion first

---

## What We Need to Check

### 1. ESXi Datastore Capacity
**Need to log into ESXi and check:**
```
- Total datastore size
- Used space
- Free space
- How much can we allocate to VMs?
```

### 2. Physical Server Disk Configuration
**IBM System x servers - what's installed?**
```
- How many physical drives?
- Drive sizes? (600GB SAS? 1TB SATA? 2TB?)
- RAID configuration?
- Total raw capacity?
```

---

## Questions for You

1. **Do you have ESXi vSphere access?**
   - IP address of ESXi host?
   - Username/password or SSH access?
   - Can we log in and check datastores?

2. **What physical drives are in the IBM servers?**
   - Do you know the drive configuration?
   - Expected total capacity?

3. **Preferred approach?**
   - **Option 1:** Expand existing VMDKs (simplest)
   - **Option 2:** Add new virtual disks
   - **Option 3:** NFS/iSCSI shared storage
   - **Option 4:** Expand Longhorn (requires Option 1 or 2 first)

---

## Temporary Workaround (Option C with current storage)

**If we can't access ESXi right now, we CAN fit Option C with optimization:**

1. **Clean up root filesystem** (58GB used → free up 10-15GB)
   - Clear logs, temp files, unused packages
   
2. **Use both /root and /home** (13GB + 108GB = 121GB available)
   - Store 2 models in /root (Qwen 32B + existing Ollama)
   - Store 3 large models in /home (Llama 70B, Qwen 72B, Functionary 70B)

3. **Deploy without Longhorn PVC overhead**
   - Use hostPath volumes instead of PVC
   - Direct filesystem access

**This gets us 158GB across both partitions = Option C viable NOW**

---

## Recommended Next Steps

### If we have ESXi access:
1. Check ESXi datastore capacity
2. Expand control plane VMDK to 1TB
3. Extend LVM `/home` to 500GB+
4. Deploy Option D (all 15 models)

### If we DON'T have ESXi access yet:
1. Use temporary workaround above
2. Deploy Option C (4 main function-calling models)
3. Test thoroughly
4. Expand later for Option D when ESXi access available

**Which approach do you want to take?**
