## Kubernetes Services & Ingress Lab

Practice exposing workloads using ClusterIP, NodePort, and Ingress resources while reusing the same backend Deployment.

### Objectives
- Deploy an HTTP backend that serves dynamic host information.
- Explore service types (ClusterIP vs NodePort).
- Configure an Ingress to route external traffic to the backend service.

### Prerequisites
```bash
kubectl create namespace rbac-lab
kubectl config set-context --current --namespace=rbac-lab
```

---

### 1. Deploy the Backend + ClusterIP Service
`manifests/01-app-backend.yaml` creates both the Deployment and a ClusterIP Service.
```bash
kubectl apply -f manifests/01-app-backend.yaml
kubectl get deploy api-backend
kubectl get svc api-backend
kubectl get pods -l app=store -o wide
```

Check that the Pods serve unique hostnames:
```bash
POD=$(kubectl get pods -l app=store -o jsonpath='{.items[0].metadata.name}')
kubectl exec "$POD" -- curl -s localhost
```

Use a temporary Pod to hit the ClusterIP service:
```bash
kubectl run curl --rm -it --image=busybox:1.37 --restart=Never -- \
  wget -qO- http://api-backend.rbac-lab.svc.cluster.local
```

---

### 2. Add a NodePort Service for Direct Node Testing
`manifests/02-service-nodeport.yaml` exposes the backend on node port `30980`.
```bash
kubectl apply -f manifests/02-service-nodeport.yaml
kubectl get svc api-nodeport -o wide
```

From a node (or via `kubectl port-forward`), test access:
```bash
kubectl port-forward svc/api-nodeport 8080:80 &
PORT_FWD_PID=$!
curl -s http://localhost:8080
kill $PORT_FWD_PID
```

Key differences vs ClusterIP:
- NodePort reserves a port on every node IP for external clients.
- Use sparingly; often fronted by load balancers or Ingress controllers instead.

---

### 3. Configure Ingress Routing
`manifests/03-ingress.yaml` assumes an ingress controller (e.g., NGINX) is installed in the cluster.
```bash
kubectl apply -f manifests/03-ingress.yaml
kubectl get ingress store-ingress
kubectl describe ingress store-ingress
```

Update your local `/etc/hosts` or DNS to map `store.example.com` to the ingress controller address. Then test:
```bash
curl -H "Host: store.example.com" http://<INGRESS-IP>
```

Observations:
- Ingress routes by host/path instead of by port.
- Multiple services may share one ingress endpoint with distinct rules.

---

### 4. Clean Up
```bash
kubectl delete ingress store-ingress
kubectl delete svc api-nodeport
kubectl delete deploy api-backend
kubectl delete svc api-backend
```

---

### Quick Reference Q&A
- **ClusterIP vs NodePort?** ClusterIP exposes inside the cluster; NodePort allocates a port on each node for external clients.
- **Why Ingress?** Provides HTTP/S routing, TLS termination, and virtual hosting using one IP.
- **How to reach a ClusterIP from your machine?** Use `kubectl port-forward` or a helper Pod (e.g., BusyBox curl).
- **Can multiple Ingress rules target the same Service?** Yes—use host/path matches to reuse backends.
- **How to redeploy safely?** Ingress keeps routing stable while Deployments roll Pods underneath.
