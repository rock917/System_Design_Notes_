## Part XIII. AI/ML Systems Engineering

### A model is one component in a service

Training produces an artifact and evidence about predictive behavior. Serving turns that artifact into a product with authentication, input contracts, bounded resources, deployment, monitoring, and recovery. A perfect model in an unavailable API has no practical value. A perfectly available API returning poor predictions is also a product failure. Keep these two dimensions visible rather than using HTTP success as a proxy for model quality.

Start with the simplest serving architecture that meets requirements: one process, one model loaded at startup, a typed input contract, bounded concurrency, and a reproducible artifact. Many models work well on CPUs. Introduce GPUs, microservices, or Kubernetes only when measured workload, deployment needs, or operational ownership justify them. The included standard-library HTTP API intentionally uses a deterministic toy score so you can study serving behavior without downloading a model or requiring a GPU.

### Artifact and feature contracts

A deployable model version includes weights, tokenizer where applicable, preprocessing code, feature schema, runtime dependencies, and configuration. Record checksums and provenance. A rollback must restore a compatible set. Loading weights from one version with a tokenizer or feature transformation from another can produce incorrect outputs while every health check passes.

An online feature store serves features under a freshness and point-in-time contract. Training data must reflect what would have been available at prediction time to avoid leakage. Online serving needs missing-feature defaults that were evaluated, not ad hoc replacements. Cache keys must include entity, feature version, relevant time window, and tenant scope. A stale feature may be tolerable for recommendations but unacceptable for a time-sensitive fraud decision.

[[FIG:arch-feature-store]]

The offline path prepares historically correct training features. The online path materializes current features for inference. The arrows do not imply identical latency or consistency. A versioned transformation and validation step connects the paths and helps detect training-serving skew.

### Admission, batching, and memory

Before expensive computation, authenticate, validate input shape and size, estimate cost, and acquire bounded admission. For text generation, input and maximum output length influence memory and runtime far more than request count alone. Reject unsupported shapes and nonfinite numeric values. Keep per-tenant fairness and global capacity as separate controls.

Batching amortizes fixed overhead and can improve hardware utilization. It also adds queue delay and may pad short inputs to match long ones. Group compatible shapes or lengths where useful, set maximum batch size and wait time, and measure useful outputs per second at the latency target. A larger batch that causes out-of-memory retries can reduce useful throughput despite high utilization. For generative serving, specialized continuous batching has different behavior from batching a fixed-size classifier; do not assume one model applies to both.

[[FIG:ill-batching]]

The illustration separates waiting time from execution time. A request arriving just after a batch launches waits for another scheduling opportunity. The optimization target is a measured combination of latency, quality, throughput, and cost, not filling every possible batch slot.

### Interactive and asynchronous inference

Interactive requests need an end-to-end deadline and a bounded queue. Return a clear overload response when useful completion is no longer plausible. Long jobs should use durable acceptance plus a status endpoint, authenticated result access, expiry, and cancellation semantics. A client disconnect does not automatically stop a GPU kernel or undo a provider request; account for completed work and unknown outcomes.

Streaming improves time to first visible output, but partial output can be followed by failure. Once HTTP headers are sent, later failure needs an in-stream error contract or a terminal status record. Track time to first token, inter-token delay, total time, input/output size, cancellation, and completion. Do not merge all these into one unexplained 'latency' number.

### Caching and privacy

Prediction caching is appropriate only when repeating an answer is acceptable and all relevant inputs are represented. Include model/preprocessing versions, tenant, feature snapshot, parameters, and any authorization-dependent retrieval context. Hashing input text can shorten keys but does not automatically anonymize sensitive content or make retention acceptable. A cache may need encryption, access controls, and deletion propagation.

Generative outputs may be nondeterministic. Reusing a cached output changes that behavior and can preserve an outdated answer. Retrieval-augmented systems must also track document permissions and freshness. Never let a shared cache return one tenant's retrieved context or answer to another tenant because their visible prompt text matches.

### Deploying and evaluating a model

Package an immutable artifact and dependency set. Load and validate it before readiness, then run a known input to detect gross incompatibility. That health example verifies serving mechanics, not broad accuracy. Use a held-out, versioned evaluation dataset and appropriate metrics for quality. For classification, inspect relevant precision/recall and calibration, not just aggregate accuracy; for ranking or generation, define task-specific evaluation and human review where needed.

Shadow traffic evaluates a candidate without using its output for the user, but it still consumes compute and may expose data to a new destination. Canary traffic actually changes user-visible behavior and needs eligibility, stable cohorts, and guardrails. Compare workload mix and delayed outcomes. A rollback policy should name both service failures and quality regressions and preserve the full model/preprocessing compatibility set.

[[FIG:arch-ai-quality]]

The serving path and quality-evaluation path meet at versioned evidence and release decisions. A low HTTP error rate cannot substitute for quality evaluation, and a high offline score cannot substitute for latency and operational safety checks. Keep data access and retention policy explicit in both paths.

### Operating the service

Measure queue age, accepted/rejected work, model-load failures, memory, device utilization where applicable, useful throughput, and cost per useful result. Segment by bounded model version and workload class. Avoid raw prompts in logs and user IDs in metric labels. Correlate request IDs to restricted audit records when deeper investigation is necessary.

Autoscaling must include artifact transfer and initialization time. Reserve enough warm capacity for predictable bursts and failures. Scaling to zero can suit delay-tolerant jobs but may violate an interactive first-request objective. External model providers introduce their own quotas, credentials, retention policies, outages, and unknown outcomes. Use timeouts, budgets, circuit breakers, and a documented fallback whose quality and privacy implications are understood.

For multi-region inference, distribute verified artifacts and configuration, consider data residency and cross-region transfer, and test whether the surviving region has enough hardware and quota. Regionally available HTTP infrastructure does not guarantee a large model is already loaded there. The complete design in Case 7 joins these serving concerns with an API, schema, failure plan, and scaling calculation.
