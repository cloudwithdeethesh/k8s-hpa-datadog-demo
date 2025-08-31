# Kubernetes HPA with Datadog External Metrics — Calculator Demo

A **Flask calculator app** instrumented with **Datadog APM** and scaled with Kubernetes **Horizontal Pod Autoscaler (HPA)** using **external metrics** from the Datadog Cluster Agent.

---

## 📂 Project Structure
- `app/` → Flask app (`calculator.py`, `requirements.txt`, `templates/calculator.html`)
- `k8s/` → Kubernetes manifests (Deployment, Service, HPA, DatadogMetric)
- `ops/` → Load testing script (`loadtest.js`)
- `Dockerfile` → Container build
- `datadog-values.example.yaml` → Safe sample values 

---

## ⚡ Quickstart (two ways to run)

You can either **use the prebuilt image** for a fast deploy, or **build your own image** locally and swap it in.

### 0) Prereqs & base setup
- Namespace: this repo uses **`app-ns`**.
- Datadog: Cluster Agent with **External Metrics** enabled (and APM if you want traces).
- **DD APM annotations/env**: ensure your Deployment has Datadog log/trace annotations and env vars.
- **DD Agent host**: point your app to the agent. Here we use **service discovery**:
  - `DD_AGENT_HOST=datadog-agent.datadog-monitoring.svc.cluster.local`
- **Secrets**: Do **not** hardcode keys. Create a secret once:
  ```bash
  kubectl create ns datadog-monitoring || true
  kubectl -n datadog-monitoring create secret generic datadog-secret \
    --from-literal api-key='<REDACTED>' \
    --from-literal app-key='<REDACTED>'


kubectl create ns app-ns || true

# (Optional) Inspect or tweak k8s/deployment.yaml to confirm:
# - image: cloudwithdeethesh/calculator-app:v4
# - DD_AGENT_HOST, DD_* envs, and Datadog annotations are set for your setup.

# Apply manifests (DatadogMetric → Deployment → Service → HPA)
kubectl apply -f k8s/datadogmetric.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml

docker build -t cloudwithdeethesh/calculator-app:local .
docker push cloudwithdeethesh/calculator-app:local

# Update k8s/deployment.yaml:
#   image: cloudwithdeethesh/calculator-app:local
kubectl apply -f k8s/deployment.yaml

kubectl apply -f k8s/datadogmetric.yaml


sum:trace.flask.request.hits{env:mycalc,service:calculator-app}.as_rate().rollup(10).fill(0)

kubectl apply -f k8s/hpa.yaml

# External metrics API should list your metric
kubectl get --raw "/apis/external.metrics.k8s.io/v1beta1" | jq '.'

# HPA should show current values and scaling decisions
kubectl -n app-ns describe hpa calculator-app-hpa

# App service reachable (port-forward)
kubectl -n app-ns port-forward svc/calculator-app 8000:8000
# http://localhost:8000

# Install k6 first (brew install k6 on macOS)
k6 run ops/loadtest.js