## Kubernetes Workloads Lab (Deployments, StatefulSets, DaemonSets)

Practice core workload controllers to understand when to pick each object and how to observe their behavior.

### Objectives
- Deploy stateless web replicas with a Deployment and practice rolling updates.
- Launch ordered, persistent Pods with a StatefulSet and headless Service.
- Ensure a Pod runs on every node with a DaemonSet for cluster-wide agents.

### Prerequisites
```bash
kubectl create namespace rbac-lab
kubectl config set-context --current --namespace=rbac-lab
```

---

### 1. Rolling Deployment
Manifest: `manifests/01-deployment-rolling.yaml`
```bash
kubectl apply -f manifests/01-deployment-rolling.yaml
kubectl get deploy web-frontend
kubectl get pods -l app=web-lab -o wide
kubectl rollout status deployment/web-frontend
kubectl rollout history deployment/web-frontend
```

Key fields:
- `replicas: 3` for availability across nodes.
- `strategy.rollingUpdate` configured for 1 max surge/unavailable.
- `liveness` + `readiness` probes to keep traffic on healthy Pods only.

Simulate an update:
```bash
kubectl set image deployment/web-frontend nginx=nginx:1.27.1
kubectl rollout status deployment/web-frontend
kubectl rollout undo deployment/web-frontend
```

---

### 2. StatefulSet with Persistent Volumes
Manifest: `manifests/02-statefulset-queue.yaml` (includes a headless Service).
```bash
kubectl apply -f manifests/02-statefulset-queue.yaml
kubectl get statefulset queue-broker
kubectl get pods -l app=queue-lab -o wide
kubectl get pvc -l app=queue-lab
```

Concepts to observe:
- Stable Pod names (`queue-broker-0`, `-1`, `-2`).
- Per-Pod PVCs provisioned from `volumeClaimTemplates`.
- Headless Service (`clusterIP: None`) enabling DNS records like `queue-broker-0.queue-broker`.

Perform a rolling restart and inspect volumes:
```bash
kubectl rollout restart statefulset/queue-broker
kubectl describe pvc data-queue-broker-0
```

Cleanup if needed (deletes PVCs too):
```bash
kubectl delete statefulset queue-broker
kubectl delete pvc -l app=queue-lab
kubectl delete svc queue-broker
```

---

### 3. DaemonSet for Node Agents
Manifest: `manifests/03-daemonset-logs.yaml`
```bash
kubectl apply -f manifests/03-daemonset-logs.yaml
kubectl get daemonset node-log-agent
kubectl get pods -l app=node-observer -o wide
```

Important bits:
- DaemonSets ensure one Pod per node (including tainted nodes due to `tolerations`).
- `hostPath` mounts `/var/log` to inspect host logs.
- Minimal resource requests keep the agent lightweight.

Check logs from multiple nodes:
```bash
for pod in $(kubectl get pods -l app=node-observer -o name); do
  echo "Logs from $pod"
  kubectl logs "$pod" --tail=5
done
```

Remove when finished:
```bash
kubectl delete daemonset node-log-agent
```

---

### Quick Reference Q&A
- **Deployment vs StatefulSet?** Deployment suits stateless replicas; StatefulSet keeps stable IDs and storage.
- **Why headless Service for StatefulSet?** Provides predictable DNS per Pod for ordered apps.
- **When to use a DaemonSet?** For node-scoped services like logging, monitoring, or networking agents.
- **How to roll back a Deployment?** `kubectl rollout undo deployment/<name>` uses stored revisions.
- **Can StatefulSets scale down safely?** Yes, but pods are removed highest ordinal first; data may persist via PVCs.
