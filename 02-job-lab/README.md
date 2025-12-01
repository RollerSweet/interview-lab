## Kubernetes Job Lab

Learn how to run batch-style workloads by creating Jobs, handling failures, and scaling work in parallel.

### Objectives
- Understand what distinguishes a Job from a long-running Deployment.
- Package scripts with ConfigMaps and execute them through Jobs.
- Observe retry behavior with `backoffLimit` and `restartPolicy`.
- Explore `completions` and `parallelism` for parallel processing.

### Prerequisites
```bash
kubectl create namespace rbac-lab    # skip if it already exists
kubectl config set-context --current --namespace=rbac-lab
```

---

### 1. Create the Script ConfigMap
The script in `manifests/01-process-script-configmap.yaml` prints progress for a short workload and sleeps between steps.
```bash
kubectl apply -f manifests/01-process-script-configmap.yaml
kubectl get configmap process-script
kubectl describe configmap process-script
```

Why a ConfigMap? Bundling the script outside of the image keeps the Job manifest clean and lets us iterate on the script with a simple re-apply.

---

### 2. Run the Script with a Job
`manifests/02-job-run-script.yaml` mounts the ConfigMap at `/scripts` and executes `process.sh`.
```bash
kubectl apply -f manifests/02-job-run-script.yaml
kubectl get jobs
kubectl get pods -l job-name=run-script-job
kubectl logs job/run-script-job
```

Key fields:
- `restartPolicy: Never` (inside the Pod spec) prevents Kubernetes from restarting the same Pod. Instead, the Job Controller creates a new Pod on failure.
- `backoffLimit: 2` controls how many retries happen before the Job is marked failed.

When the logs show `Processing completed successfully!`, the Job status should read `1/1` completions.

---

### 3. Observe Failure and Backoff Behavior
`manifests/03-job-failing-script.yaml` intentionally exits with status 1.
```bash
kubectl apply -f manifests/03-job-failing-script.yaml
kubectl describe job fail-script-job
kubectl get pods -l job-name=fail-script-job
kubectl logs <failing-pod-name>
```

Watch for:
- Events showing retries up to `backoffLimit: 3`.
- `Failed` status once Kubernetes exhausts retries.
- Pods created sequentially (check their `restartCount`, which remains zero because Pods are never restarted—new Pods are created instead).

Clean up the failed Job once you finish inspecting it:
```bash
kubectl delete job fail-script-job
```

---

### 4. Run Work in Parallel
`manifests/04-job-parallel.yaml` demonstrates `completions` vs. `parallelism`.
```bash
kubectl apply -f manifests/04-job-parallel.yaml
kubectl get jobs parallel-job -w
kubectl get pods -l job-name=parallel-job -o wide
```

- `completions: 10` requires ten successful Pods.
- `parallelism: 3` allows up to three Pods to run simultaneously for faster completion.
- Each Pod logs its hostname so you can see which worker processed which task.

View logs from all Pods:
```bash
for pod in $(kubectl get pods -l job-name=parallel-job -o name); do
  kubectl logs "$pod"
done
```

---

### 5. Review and Clean Up
```bash
kubectl get jobs
kubectl get pods

kubectl delete job run-script-job
kubectl delete job parallel-job
kubectl delete configmap process-script
```

---

### Quick Reference Q&A
- **What is a Job?** A controller that runs Pods to completion; once the required `completions` succeed, the Job is marked `Completed`.
- **How does retrying work?** The Job Controller creates new Pods when failures happen, up to `backoffLimit`.
- **How do I run a script?** Put the script in a ConfigMap, mount it as a volume, and run it with `command: ["/bin/sh", "/path/script.sh"]`.
- **Why use `restartPolicy: Never`?** Jobs expect Pods to exit; Kubernetes handles retries by creating new Pods.
- **Difference between `completions` and `parallelism`?**
  - `completions`: total successful runs required.
  - `parallelism`: how many Pods may run at once to satisfy those completions faster.
