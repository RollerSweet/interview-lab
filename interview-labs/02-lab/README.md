Lab 1 – Kubernetes Deployment with Config, Secret, Ingress & Health Checks

Scenario:
You’re given a simple web app (can be nginx or any demo app) and asked to deploy it “production-style”.

Requirements

Namespace & basic app

Create a namespace: interview-app.

Create a Deployment of a web app (e.g. nginx:1.27) with:

replicas: 3

Resource requests/limits (e.g. 100m CPU, 128Mi RAM).

Expose it with a ClusterIP Service.

Configuration & secrets

Create a ConfigMap with:

APP_ENV=production

APP_MESSAGE="Hello from K8s interview lab"

Create a Secret with:

DB_PASSWORD (any fake value).

Mount them into the pod:

As environment variables.

And at least one key as a file (via volume).

Liveness & readiness probes

Add HTTP liveness & readiness probes:

e.g. httpGet on / at port 80.

Reasonable initialDelaySeconds, periodSeconds.

Ingress

Create an Ingress (with your ingress controller) that:

Exposes the app at app.interview.local (or any host).

Path / -> your Service.

Test from your machine with /etc/hosts entry pointing app.interview.local to your cluster IP / LB.

What to “show” in an interview

kubectl get deploy,po,svc,ing -n interview-app

kubectl describe deploy ... showing env from ConfigMap/Secret.

kubectl exec into a pod and:

env | grep APP_

cat the mounted file for the secret/config.

Show that when you scale from 3 → 5 replicas:

kubectl scale deploy <name> --replicas=5 – pods roll out without downtime.

Stretch goals

Add canary deployment: 90% traffic to v1, 10% to v2 using two Deployments + one Service and Ingress annotations / paths.

Use podAntiAffinity so replicas don’t sit on the same node.