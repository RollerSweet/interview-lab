## RBAC Lab: Namespace Viewer

Walk through the steps below to create a namespace-scoped, read-only service account and verify its privileges.

### 1. Prepare the Namespace Context
```bash
kubectl create namespace rbac-lab
kubectl get ns rbac-lab

kubectl config set-context --current --namespace=rbac-lab
kubectl config view --minify | grep namespace
```

### 2. Create a Service Account
```bash
kubectl create serviceaccount viewer -n rbac-lab
kubectl get sa -n rbac-lab
```

### 3. Apply a Read-Only Role
```bash
kubectl apply -f role-namespace-viewer.yaml
kubectl get role -n rbac-lab
```

### 4. Bind the Role to the Service Account
```bash
kubectl apply -f rolebinding-namespace-viewer.yaml
kubectl get rolebinding -n rbac-lab
```

### 5. Verify Permissions with `kubectl auth can-i`
```bash
# Allowed: get pods in rbac-lab
kubectl auth can-i get pods \
  --as system:serviceaccount:rbac-lab:viewer \
  -n rbac-lab

# Denied: delete pods in rbac-lab
kubectl auth can-i delete pods \
  --as system:serviceaccount:rbac-lab:viewer \
  -n rbac-lab

# Denied: view pods in other namespaces
kubectl auth can-i get pods \
  --as system:serviceaccount:rbac-lab:viewer \
  -n default
```

### 6. Create a Demo Deployment for Testing
```bash
kubectl create deployment demo --image=nginx:1.27 -n rbac-lab
kubectl get deploy -n rbac-lab
```

Validate the viewer role:
```bash
# Allowed operations
kubectl get deploy \
  --as system:serviceaccount:rbac-lab:viewer \
  -n rbac-lab

kubectl describe deploy demo \
  --as system:serviceaccount:rbac-lab:viewer \
  -n rbac-lab

# Denied operations
kubectl delete deploy demo \
  --as system:serviceaccount:rbac-lab:viewer \
  -n rbac-lab

kubectl apply -f role-namespace-viewer.yaml \
  --as system:serviceaccount:rbac-lab:viewer
```

### 7. Generate a Standalone Kubeconfig for the Viewer
```bash
TOKEN=$(kubectl create token viewer -n rbac-lab)
CLUSTER_NAME=$(kubectl config view --minify -o jsonpath='{.clusters[0].name}')
CLUSTER_SERVER=$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')
CLUSTER_CA=$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.certificate-authority-data}')

cat > rbac-lab-viewer.kubeconfig <<EOF
apiVersion: v1
kind: Config
clusters:
- name: ${CLUSTER_NAME}
  cluster:
    server: ${CLUSTER_SERVER}
    certificate-authority-data: ${CLUSTER_CA}

users:
- name: rbac-lab-viewer
  user:
    token: ${TOKEN}

contexts:
- name: rbac-lab-viewer@${CLUSTER_NAME}
  context:
    cluster: ${CLUSTER_NAME}
    user: rbac-lab-viewer
    namespace: rbac-lab

current-context: rbac-lab-viewer@${CLUSTER_NAME}
EOF
```

Test with the generated config:
```bash
KUBECONFIG=./rbac-lab-viewer.kubeconfig kubectl get pods
KUBECONFIG=./rbac-lab-viewer.kubeconfig kubectl get deploy
KUBECONFIG=./rbac-lab-viewer.kubeconfig kubectl describe deploy demo
```
