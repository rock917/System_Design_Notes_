# Runnable examples and environment guide

The executable labs use Python 3.11+ and only its standard library. They were executed here with the bundled Python 3.12.14 runtime. No package installation, account, GPU, or cloud credential is needed. The inference score is deterministic teaching arithmetic, not a trained model. SQLite examples demonstrate local transactions; PostgreSQL behavior is taught separately in database.sql.

## Quick start

Open a terminal in this examples directory. On Windows, `py -3` can replace `python` if that is how Python is installed.

```text
python -m unittest -v
python algorithms.py
python orders.py
python messaging.py
python concurrency.py
python performance.py
python security.py
python protocols.py
python incident_drill.py
```

The default suite executes algorithm, transaction, security, protocol, and in-process HTTP-handler tests. Real loopback socket tests are opt-in: set RUN_SOCKET_TESTS=1 and rerun. In this authoring sandbox, outgoing loopback connections were denied; those four tests were skipped, while the same HTTP handlers were tested in memory. If your managed temporary directory has restrictive cleanup permissions, set TMP and TEMP to a writable local scratch directory before running.

## What each module teaches

### algorithms.py

Fake-time token refill, bounded TTL cache, circuit-breaker transitions, jitter, retry budget, round-robin routing, hash partitioning, stable feature cohorts, versioned projection updates, and quorum arithmetic. These are single-process models, not distributed implementations.

Run `python algorithms.py`. Important lines are documented in the module; the behavior tests name the intended invariants. Actual captured output:

```text
initial admission: [True, True, True, True, True, False]
after 0.5s: True
cache hit: book
expired: None
breaker after failures: open
probe: recovered closed
jitter seconds: [0.0324, 0.0302, 0.2604, 0.0579]
routing: ['A', 'B', 'C', 'A', 'B', 'C']
projection: {'product': (3, 'value-3')}
five-node quorum, reachable 2/3: False True
```

### orders.py

Concurrent idempotency keys, payload conflict, guarded stock decrement, atomic outbox creation, local inbox deduplication, and SQLite backup/restore. Temporary demo data is removed after execution. No real payment or email is sent.

Run `python orders.py`. Important lines are documented in the module; the behavior tests name the intended invariants. Actual captured output:

```text
concurrent replay order IDs: [1, 1, 1, 1]
first event: True
duplicate event: False
row counts: {'orders': 1, 'operations': 1, 'outbox': 1, 'inbox': 1, 'notifications': 1}
backup restores same counts: True
```

### messaging.py

Duplicate delivery, poison-message attempts, DLQ, Saga confirmation/decline/unknown outcomes, compensation retry, and logical scheduled-period deduplication. State is in memory and is not restart-durable.

Run `python messaging.py`. Important lines are documented in the module; the behavior tests name the intended invariants. Actual captured output:

```text
effects: 1 completed: ['a']
DLQ: [('b', 3)]
Saga confirmed : new -> reserved -> confirmed reserved: True
Saga declined : new -> reserved -> compensating -> rejected reserved: False
Saga unknown : new -> reserved -> reconcile-payment reserved: True
same scheduled period: True False
```

### concurrency.py

Guaranteed pool-token release, stale-owner fencing, queue conservation, autoscaling arithmetic, a forced lost-update schedule, wait-for cycle detection, and traced memory retention. Pool tokens are not actual database connections.

Run `python concurrency.py`. Important lines are documented in the module; the behavior tests name the intended invariants. Actual captured output:

```text
pool token returned: True
fencing: stale fencing token
bounded queue: {'backlog': 900, 'rejected': 300, 'completed': 6000}
workers at 70% target: 9
lost update: {'sales': 2, 'final_stock': 0}
deadlock cycle: True
retention: {'grew': True, 'released': True}
```

### performance.py

Nearest-rank percentiles, error budgets, independent fanout probability, Little's Law, and a simplified DAG critical path. Outputs are arithmetic, not measured vendor benchmarks.

Run `python performance.py`. Important lines are documented in the module; the behavior tests name the intended invariants. Actual captured output:

```text
mean ms: 59.6
P50/P95/P99 ms: 20 20 2000
100-branch slow chance: 0.634
in-flight at 500/s and 0.2s: 100.0
SLO: {'success_ratio': 0.99, 'allowed_bad': 10.0, 'remaining_bad': -90.0, 'burn_rate': 10.0}
parallel critical path ms: 110
```

### security.py

Parameterized SQL, HTML text-context escaping, exact origin and partner allowlists, CSRF comparison, cross-tenant authorization, raw-body HMAC verification, and allowlisted structured logging. URL validation does not fetch anything and is not a complete arbitrary-destination SSRF defense.

Run `python security.py`. Important lines are documented in the module; the behavior tests name the intended invariants. Actual captured output:

```text
bound apostrophe query: [("O'Reilly",)]
SQL-looking text returns: []
HTML text encoding: &lt;b&gt;review&lt;/b&gt;
valid/tampered webhook: True False
partner/lookalike: True False
cross-tenant authorization: False
safe log: {"event": "order.accepted", "order_id": 1}
```

### protocols.py

Length-prefixed framing under partial reads, SSE formatting, retained-cursor replay, and an explicitly justified historical schema adapter. It does not implement TCP, QUIC, OAuth, or gRPC.

Run `python protocols.py`. Important lines are documented in the module; the behavior tests name the intended invariants. Actual captured output:

```text
partial read messages: []
completed messages: [{'message': 'one'}, {'message': 'two'}] remaining bytes: 0
SSE frame: 'id: 42\ndata: {"status": "shipped"}\n\n'
reconnect after 1: [{'id': 2}]
old schema adapter: {'amount_minor': 19900, 'currency': 'INR'}
```

### incident_drill.py

A timed offline response exercise showing why unknown payment outcomes remain part of recovery after HTTP metrics improve.

Run `python incident_drill.py`. Important lines are documented in the module; the behavior tests name the intended invariants. Actual captured output:

```text
09:00 Release B reaches 25% of checkout traffic.
09:04 B P99 rises; database CPU remains low; pool acquisition wait rises.
09:06 Traces show B holds a DB connection while awaiting the payment provider.
09:08 Feature flag disables the new path; no schema contraction occurred.
09:12 Success and latency recover; 14 payment outcomes remain unknown.
09:20 Provider operation-ID reconciliation resolves all 14 outcomes.
At 09:12 complete: False
At 09:20 complete: True
Action: add a test proving DB connections are released before provider I/O.
Owner: checkout team. Verification: failure-injected integration test plus rollout telemetry.
```

## Local inference API

The server validates bounded finite feature arrays, authenticates a single demo key, limits requests, bounds in-flight model work, caches by model version and normalized input, and exposes /live, /ready, and /metrics. It uses ThreadingHTTPServer for teaching, which is not a hardened production server and does not itself bound all incoming connection threads. A production service needs a maintained server/runtime, transport security, tenant identity, global quotas if required, durable usage, robust shutdown/draining, privacy review, and realistic load tests.

PowerShell:

```powershell
$env:DEMO_API_KEY = 'local-demo-key-change-me'
python inference_api.py
```

In another local terminal:

```powershell
$headers = @{ 'X-API-Key' = 'local-demo-key-change-me' }
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/v1/predict' -Method Post -Headers $headers -ContentType 'application/json' -Body '{"features":[0,0]}'
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/ready'
```

Bash:

```bash
export DEMO_API_KEY=local-demo-key-change-me
python inference_api.py
# In another terminal:
curl -H 'X-API-Key: local-demo-key-change-me' -H 'Content-Type: application/json' --data '{"features":[0,0]}' http://127.0.0.1:8000/v1/predict
```

Expected response: score 0.5, model_version toy-linear-v1, cached false on the first permitted request and true on a repeat within TTL. Incorrect credentials return 401, invalid inputs 400, quota exhaustion 429, and occupied inference slots 503. The cache and limiter are per process. Health/metrics endpoints are local demonstration endpoints; restrict exposure in a real deployment.

## PostgreSQL lab

Install a supported PostgreSQL runtime and psql, create a disposable empty database, and set DATABASE_URL to its connection URI without committing credentials. Run `psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f database.sql` in Bash, or `psql $env:DATABASE_URL -v ON_ERROR_STOP=1 -f database.sql` in PowerShell. Expect 100,000 orders, two different plan observations, one successful version-guarded update followed by zero affected rows, and partition-pruning evidence. Exact plan choice and timings vary. The script creates handbook_lab and does not delete existing schemas. It was not executed here because no PostgreSQL server was available.

## Container and local Kubernetes

With a running Docker engine, run `docker build -t shopstream-inference:local .`, then `docker run --rm -p 127.0.0.1:8000:8000 -e DEMO_API_KEY=local-demo-key-change-me shopstream-inference:local`. The key is a disposable local example, not a production credential. Docker was installed here but its Linux engine was not running, so no image build is claimed.

For a local Kubernetes cluster, first confirm `kubectl config current-context` names that intended local cluster and load the built image using the cluster's supported mechanism. Create the local secret with `kubectl create secret generic shopstream-demo-key --from-literal=api-key=local-demo-key-change-me`, then `kubectl apply -f k8s.yaml`. Inspect `kubectl rollout status deployment/shopstream-inference`, `kubectl get pods`, `kubectl get endpointslices`, and `kubectl describe hpa shopstream-inference`. Use `kubectl port-forward service/shopstream-inference 8000:80` for a local call. Do not point these teaching commands at an unrelated production cluster.

HPA requires the metrics API. The local image tag must exist in the cluster runtime. The manifest references a Secret rather than embedding one, uses non-root and read-only-root settings, and has different startup/readiness/liveness roles. It does not supply a public Ingress, TLS certificate, cloud load balancer, full network policy, or durable application database. Those choices require the real deployment environment. Server-side admission and live probe behavior were not tested here.

## Terraform, Helm, proxy, and CI examples

`terraform fmt -check`, `terraform init`, `terraform validate`, and `terraform plan` inspect the built-in terraform_data example. Optional `terraform apply` creates local Terraform state and no cloud resource; review the plan first. Terraform was unavailable here. Keep state and plan files private and out of source control when they contain sensitive values.

`helm lint helm` and `helm template shopstream helm` render the local chart. Inspect labels, secret references, ports, resource settings, and probes. A local installation uses `helm upgrade --install shopstream helm` only after the image and Secret are ready in the intended context. Helm was unavailable here; rendered chart output and cluster execution remain verification tasks.

`nginx -t -c <absolute-path-to-nginx.conf>` validates the supplied isolated local proxy configuration when Nginx is installed. It listens only on 127.0.0.1:8080 and forwards to the local API. It deliberately provides no fake certificate or pretend production TLS configuration. For real TLS, use valid issued certificates, verified hostnames, current maintained server guidance, and an explicit upstream transport policy.

Copy ci.yml into .github/workflows/labs.yml in a repository whose examples directory matches its working-directory. It runs tests and builds a local image but does not publish or deploy. Review and pin third-party action commits for a real privileged release pipeline. service.proto is a contract example: install a compatible protobuf/gRPC toolchain and language plugin before generating stubs; no server implementation or compiler execution is claimed here.

## Test boundary and next experiments

See [../VERIFICATION_REPORT.md](../VERIFICATION_REPORT.md) for exact results. Passing deterministic tests does not prove cloud quotas, broker delivery, database replication, TLS configuration, distributed coordination, or production capacity. Extend the labs using the thirty tasks in [../PROJECTS_AND_LABS.md](../PROJECTS_AND_LABS.md), and record each added experiment with runtime, input, fault, expected invariant, and actual outcome.
