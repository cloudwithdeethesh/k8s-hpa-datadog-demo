# Kubernetes HPA with Datadog External Metrics - Calculator Demo

A **Flask calculator app** instrumented with **Datadog APM** and scaled with Kubernetes **Horizontal Pod Autoscaler (HPA)** using **external metrics** from the Datadog Cluster Agent.

---

## 📂 Project Structure
- `app/` → Flask app (`calculator.py`, `requirements.txt`, `templates/calculator.html`)
- `k8s/` → Kubernetes manifests (Deployment, Service, HPA, DatadogMetric)
- `ops/` → Load testing script (`loadtest.js`)
- `Dockerfile` → Container build
- `datadog-values.example.yaml` → Safe sample values (no secrets)

---

## ⚡ Quickstart (two ways to run)

You can either **use the prebuilt image** for a fast deploy, or **build your own image** locally and swap it in.

---

### 0) Prereqs & Base Setup
- Namespace: this repo uses **`app-ns`**.
- Datadog: Cluster Agent with **External Metrics** enabled (and APM if you want traces).
- **DD APM annotations/env**: ensure your Deployment has Datadog log/trace annotations and env vars.
- **DD Agent host**: point your app to the agent. Example:
  ```yaml
  DD_AGENT_HOST=datadog-agent.datadog-monitoring.svc.cluster.local
  ```
- **Secrets**: Do **not** hardcode keys. Create a secret once:
  ```bash
  kubectl create ns datadog-monitoring || true
  kubectl -n datadog-monitoring create secret generic datadog-secret     --from-literal api-key='<REDACTED>'     --from-literal app-key='<REDACTED>'
  ```

---

### 1A) Quick Deploy (prebuilt image)
Deploy using the published image: **`cloudwithdeethesh/calculator-app:v4`**

```bash
kubectl create ns app-ns || true

# (Optional) Inspect or tweak k8s/deployment.yaml to confirm:
# - image: cloudwithdeethesh/calculator-app:v4
# - DD_AGENT_HOST, DD_* envs, and Datadog annotations are set for your setup.

# Apply manifests (DatadogMetric → Deployment → Service → HPA)
kubectl apply -f k8s/datadogmetric.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
```

---

### 1B) Build Your Own Image
If you want to bake in code changes:

```bash
docker build -t cloudwithdeethesh/calculator-app:local .
docker push cloudwithdeethesh/calculator-app:local

# Update k8s/deployment.yaml to use the :local tag
kubectl apply -f k8s/deployment.yaml
```

---

### 2) Deploy Datadog Metric CRD
> Note: the **DatadogMetric CRD** is installed with the Datadog Cluster Agent.  
This repo includes a sample metric mapping for HPA.

```bash
kubectl apply -f k8s/datadogmetric.yaml
```

The metric used in this demo:
```text
sum:trace.flask.request.hits{env:mycalc,service:calculator-app}.as_rate().rollup(10).fill(0)
```

---

### 3) Deploy HPA (External Metrics)
Review `k8s/hpa.yaml`:
- `metric.name: datadogmetric@app-ns:calculator-latency-metrics`
- `target.averageValue: "200m"`

Apply it:
```bash
kubectl apply -f k8s/hpa.yaml
```

---

### 4) Verify Setup
```bash
# External metrics API should list your metric
kubectl get --raw "/apis/external.metrics.k8s.io/v1beta1" | jq '.'

# HPA should show current values and scaling decisions
kubectl -n app-ns describe hpa calculator-app-hpa

# App service reachable (port-forward)
kubectl -n app-ns port-forward svc/calculator-app 8000:8000
# Now open http://localhost:8000
```

---

### 5) Load Testing with k6
A minimal k6 script is included at `ops/loadtest.js`.

```bash
# Install k6 (macOS)
brew install k6

# Run the test
k6 run ops/loadtest.js
```

This will generate load, push the external metric above your target, and let the HPA scale your pods.

---

## ✅ Notes
- If you briefly see `unknown` metric values, that’s expected while Datadog → Cluster Agent → External Metrics API syncs.  
- Make sure **DD_ENV** and **DD_SERVICE** match what’s in your DatadogMetric query.  
- Keep `datadog-values.yaml` local (gitignored). Only commit `datadog-values.example.yaml`.  
