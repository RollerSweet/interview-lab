# Kubernetes Helper Commands

Quick reference for creating Kubernetes objects, exploring their schemas, and validating manifests from the command line.

## 1. Generate YAML for Kubernetes Objects

Use `kubectl create` with `--dry-run=client -o yaml` to scaffold resources without applying them:

```bash
kubectl create <object> <object_name> --image=<image_name> --dry-run=client -o yaml
```

Common one-liners:

```bash
kubectl create deployment myapp --image=nginx --dry-run=client -o yaml
kubectl create job test --image=nginx --dry-run=client -o yaml
kubectl create cronjob backup --image=busybox --schedule="*/5 * * * *" --dry-run=client -o yaml
kubectl run mypod --image=nginx --dry-run=client -o yaml
kubectl create service clusterip myservice --tcp=80:80 --dry-run=client -o yaml
kubectl create namespace dev --dry-run=client -o yaml
```

## 2. Explore Object Documentation

Use `kubectl explain` to navigate object schemas:

- Top level: `kubectl explain deployment`, `kubectl explain job`, `kubectl explain pod`
- Spec fields: `kubectl explain deployment.spec`, `kubectl explain job.spec`
- Pod template: `kubectl explain deployment.spec.template.spec`, `kubectl explain job.spec.template.spec`
- Containers: `kubectl explain pod.spec.containers`

You can drill into any field, e.g.:

```bash
kubectl explain pod.spec.containers.resources
kubectl explain pod.spec.containers.livenessProbe
kubectl explain <object> --recursive
```

## 3. View the Manifest Running in the Cluster

Inspect live resources to see exactly what Kubernetes stored:

```bash
kubectl get deployment myapp -o yaml
kubectl get pod mypod -o yaml
kubectl get svc myservice -o yaml
```

## 4. Validate and Debug YAML

- Client-side validation: `kubectl apply --dry-run=client -f file.yaml`
- Server-side validation (schema + admission): `kubectl apply --dry-run=server -f file.yaml`

## 5. Useful Shortcuts

- List all API resources: `kubectl api-resources`
- Find versions for a resource: `kubectl api-resources | grep job`
- View fully expanded schema: `kubectl explain job --recursive`

## 6. Create Common Resources Quickly

```bash
kubectl create configmap app-config --from-literal=env=prod --dry-run=client -o yaml
kubectl create secret generic mysecret --from-literal=password=1234 --dry-run=client -o yaml
kubectl create ingress mying \
  --class=nginx \
  --rule="app.local/=myservice:80" \
  --dry-run=client -o yaml
```

## 7. Editing and Applying Changes

```bash
kubectl edit deployment myapp
kubectl patch deployment myapp -p '{"spec":{"replicas":3}}'
kubectl delete job test
```
