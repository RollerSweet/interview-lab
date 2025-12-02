## Kubernetes CronJob Lab

Practice scheduled batch processing in Kubernetes by combining CronJobs, Jobs, ConfigMaps, and scripts.

### Objectives
- Understand how CronJobs wrap Jobs with schedules.
- Package reusable scripts with ConfigMaps.
- Observe history limits, concurrency controls, and deadline behavior.
- Practice inspecting the Jobs and Pods that CronJobs create.

### Prerequisites
```bash
kubectl create namespace rbac-lab
kubectl config set-context --current --namespace=rbac-lab
```

---

### 1. Provide the Scheduled Script
`manifests/01-report-script-configmap.yaml` stores a shell script that prints timestamps and simulates a reporting task.
```bash
kubectl apply -f manifests/01-report-script-configmap.yaml
kubectl get configmap cron-report-script
kubectl describe configmap cron-report-script
```

The script checks the optional `REPORT_TARGET` env variable and writes details out so you can confirm the CronJob picked it up.

---

### 2. Schedule the Script Every Five Minutes
`manifests/02-cronjob-run-script.yaml` defines a CronJob that runs the script on `*/5 * * * *`.
```bash
kubectl apply -f manifests/02-cronjob-run-script.yaml
kubectl get cronjob cronjob-run-script
kubectl describe cronjob cronjob-run-script
```

Key spec fields:
- `schedule`: standard cron expression (every five minutes).
- `successfulJobsHistoryLimit` / `failedJobsHistoryLimit`: keep recent status without cluttering resources.
- `jobTemplate.spec.template.spec.restartPolicy: Never`: each Pod runs once; retries create new Pods.
- ConfigMap volume mount so `/scripts/report.sh` is executable.

Watch the CronJob create Jobs and Pods (wait for the next schedule window):
```bash
kubectl get jobs --watch
kubectl get pods -l job-name | grep cronjob-run-script
kubectl logs job/$(kubectl get jobs -l cronjob-name=cronjob-run-script -o jsonpath='{.items[0].metadata.name}')
```

You can manually trigger the CronJob without waiting:
```bash
kubectl create job --from=cronjob/cronjob-run-script manual-run-script
kubectl logs job/manual-run-script
kubectl delete job manual-run-script
```

---

### 3. Explore Concurrency Control
`manifests/03-cronjob-forbid-overlap.yaml` demonstrates how to prevent overlapping runs.
```bash
kubectl apply -f manifests/03-cronjob-forbid-overlap.yaml
kubectl describe cronjob cronjob-forbid-overlap
```

Important fields:
- `concurrencyPolicy: Forbid` ensures a new Job will not start until the previous Job finishes.
- `startingDeadlineSeconds: 60` prevents running jobs that missed their window for more than 60 seconds.
- The script sleeps for 90 seconds so you can see skipped schedules in the CronJob events.

Inspect the Jobs it creates:
```bash
kubectl get jobs -l cronjob-name=cronjob-forbid-overlap
kubectl describe job -l cronjob-name=cronjob-forbid-overlap
kubectl logs job/<job-name>
```

Suspend the CronJob after observing a few runs:
```bash
kubectl patch cronjob cronjob-forbid-overlap -p '{"spec":{"suspend":true}}'
```

Resume when you want to continue:
```bash
kubectl patch cronjob cronjob-forbid-overlap -p '{"spec":{"suspend":false}}'
```

---

### 4. Review and Clean Up
```bash
kubectl get cronjobs
kubectl get jobs
kubectl get pods

kubectl delete cronjob cronjob-run-script
kubectl delete cronjob cronjob-forbid-overlap
kubectl delete configmap cron-report-script
```

---

### Quick Reference Q&A
- **CronJob vs Job?** CronJobs create Jobs on a schedule; each Job then creates Pods.
- **How do scripts fit in?** Store the script in a ConfigMap, mount it, and run it from the container image.
- **What if a schedule is missed?** `startingDeadlineSeconds` decides whether Kubernetes should still try; otherwise the run is skipped.
- **Can runs overlap?** Use `concurrencyPolicy` (`Allow`, `Forbid`, or `Replace`) to control overlap.
- **How to trigger immediately?** `kubectl create job --from=cronjob/<name> <manual-name>` reuses the CronJob template on demand.
