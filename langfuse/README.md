# Langfuse - Open Source LLM Observability

Self-hosted Langfuse v3 for tracing, evaluation, and prompt management.

## Architecture

```
Langfuse Namespace
├── langfuse-web (NodePort :30300)
├── langfuse-worker (async processing)
├── PostgreSQL (metadata, users, projects)
├── ClickHouse Shard 0 (3 replicas for trace data)
├── Redis (caching, queues)
├── Zookeeper (3 nodes for ClickHouse coordination)
└── S3 (MinIO for artifacts)
```

## Installation

```bash
# Add Langfuse Helm repository
helm repo add langfuse https://langfuse.github.io/langfuse-k8s
helm repo update

# Create values file
cat > langfuse-values.yaml << EOF
postgresql:
  auth:
    password: "YOUR-POSTGRES-PASSWORD"

clickhouse:
  auth:
    password: "YOUR-CLICKHOUSE-PASSWORD"

langfuse:
  nextauth:
    secret:
      value: "$(openssl rand -base64 32)"
  salt:
    value: "$(openssl rand -base64 32)"
  
  service:
    type: NodePort
    port: 3000
    nodePort: 30300
EOF

# Install Langfuse
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
helm install langfuse langfuse/langfuse \
  --namespace langfuse \
  --create-namespace \
  -f langfuse-values.yaml

# Patch service to NodePort (if needed)
kubectl patch svc langfuse-web -n langfuse \
  -p '{"spec":{"type":"NodePort","ports":[{"port":3000,"nodePort":30300}]}}'
```

## Access

**Web UI:** http://192.168.1.130:30300

**First-time setup:**
1. Open http://192.168.1.130:30300
2. Create admin account
3. Create first project
4. Copy API keys

## Integration with LangChain

### Environment Variables

```bash
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."
export LANGFUSE_HOST="http://192.168.1.130:30300"
```

### Python SDK

```python
from langfuse import Langfuse

# Initialize Langfuse
langfuse = Langfuse(
    public_key="pk-lf-...",
    secret_key="sk-lf-...",
    host="http://192.168.1.130:30300"
)

# LangChain auto-instrumentation
from langfuse.callback import CallbackHandler
langfuse_handler = CallbackHandler()

# Use with LangChain
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    base_url="http://192.168.1.130:8000/v1",
    api_key="not-needed",
    callbacks=[langfuse_handler]
)

response = llm.invoke("What is Kubernetes?")
# Trace automatically sent to Langfuse
```

## Components

### PostgreSQL
- **Purpose:** User accounts, projects, prompts, metadata
- **Storage:** 8Gi PVC
- **Access:** Internal only

### ClickHouse
- **Purpose:** High-volume trace data storage
- **Shards:** 1 shard with 3 replicas
- **Storage:** 3x 8Gi PVCs (one per replica)
- **Retention:** Configurable (default: 400 days)

### Redis
- **Purpose:** Caching, job queues
- **Storage:** 8Gi PVC
- **Mode:** Primary-only (no replicas yet)

### Zookeeper
- **Purpose:** ClickHouse cluster coordination
- **Nodes:** 3 (quorum for HA)
- **Storage:** 3x 8Gi PVCs

### S3 (MinIO)
- **Purpose:** Large artifacts (datasets, fine-tuning data)
- **Storage:** Ephemeral (in-pod)
- **Access:** Internal S3-compatible API

## Monitoring

### Check pod status
```bash
kubectl get pods -n langfuse
```

### View web logs
```bash
kubectl logs -n langfuse -l app.kubernetes.io/component=web -f
```

### Check database connections
```bash
# PostgreSQL
kubectl exec -n langfuse langfuse-postgresql-0 -- psql -U postgres -c "\l"

# ClickHouse
kubectl exec -n langfuse langfuse-clickhouse-shard0-0 -- clickhouse-client -q "SELECT count() FROM system.tables"
```

## Data Persistence

All data is stored in PersistentVolumeClaims using the `local-path` storage class:

```bash
$ kubectl get pvc -n langfuse

NAME                                    STATUS   VOLUME          CAPACITY
langfuse-postgresql                     Bound    pvc-xxx         8Gi
data-langfuse-clickhouse-shard0-0       Bound    pvc-yyy         8Gi
data-langfuse-clickhouse-shard0-1       Bound    pvc-zzz         8Gi
data-langfuse-clickhouse-shard0-2       Bound    pvc-aaa         8Gi
redis-data-langfuse-redis-primary-0     Bound    pvc-bbb         8Gi
data-langfuse-zookeeper-0               Bound    pvc-ccc         8Gi
data-langfuse-zookeeper-1               Bound    pvc-ddd         8Gi
data-langfuse-zookeeper-2               Bound    pvc-eee         8Gi
```

## Backup & Recovery

### PostgreSQL Backup

```bash
# Backup
kubectl exec -n langfuse langfuse-postgresql-0 -- \
  pg_dump -U postgres langfuse > langfuse-backup-$(date +%Y%m%d).sql

# Restore
kubectl exec -i -n langfuse langfuse-postgresql-0 -- \
  psql -U postgres langfuse < langfuse-backup-20260425.sql
```

### ClickHouse Backup

```bash
# Backup (requires ClickHouse backup disk configuration)
kubectl exec -n langfuse langfuse-clickhouse-shard0-0 -- \
  clickhouse-client --query "BACKUP DATABASE default TO Disk('backups', 'backup-$(date +%Y%m%d).zip')"
```

## Scaling

### Horizontal Scaling

```bash
# Scale workers for async processing
kubectl scale deployment -n langfuse langfuse-worker --replicas=3

# Add ClickHouse shard 1 (requires Helm values update)
# Not needed until >100K traces/day
```

### Vertical Scaling

```bash
# Increase PostgreSQL resources
kubectl edit statefulset -n langfuse langfuse-postgresql
# Update resources.requests and resources.limits
```

## Troubleshooting

### Web UI not accessible

```bash
# Check service
kubectl get svc -n langfuse langfuse-web

# Check pod logs
kubectl logs -n langfuse -l app.kubernetes.io/component=web --tail=100
```

### Worker crashing

```bash
# Check worker logs
kubectl logs -n langfuse -l app.kubernetes.io/component=worker --tail=100

# Common issues:
# - Database connection failed (check PostgreSQL/ClickHouse)
# - Redis connection failed
# - S3 credentials missing
```

### Database connection issues

```bash
# Test PostgreSQL
kubectl exec -n langfuse langfuse-postgresql-0 -- psql -U postgres -c "SELECT version()"

# Test ClickHouse
kubectl exec -n langfuse langfuse-clickhouse-shard0-0 -- clickhouse-client -q "SELECT version()"
```

## Resources

- [Langfuse Documentation](https://langfuse.com)
- [Langfuse GitHub](https://github.com/langfuse/langfuse)
- [Self-Hosting Guide](https://langfuse.com/self-hosting)
- [Kubernetes Deployment](https://langfuse.com/self-hosting/deployment/kubernetes-helm)
