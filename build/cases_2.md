### Case 5. Notification service

**Requirements and contract.** Deliver transactional email, SMS, or push notifications while respecting consent, preferences, priority, and provider limits. Separate 'accepted by our service', 'accepted by provider', and 'delivered to recipient'. Marketing campaigns must not starve password resets or order receipts. External delivery is not guaranteed exactly once unless the provider's contract and your workflow justify that boundary.

**Estimates.** Assume ten million notifications/day: about 116/second average, with a campaign peak of 5,000/second. If a provider permits an assumed 1,000/second and the burst lasts ten minutes, backlog grows by 2.4 million messages. At 1 KB of payload each that is 2.4 GB before broker overhead, indexes, and replicas. A queue alone cannot meet a two-minute freshness objective under that deficit.

[[FIG:case-notify-overview]]

The service accepts durable intents, checks policy, and assigns work to channel/priority queues. Provider adapters isolate vendor-specific behavior. Delivery callbacks update state asynchronously rather than holding an API request open.

**API contracts.** POST /v1/notifications accepts template_id, recipient reference, variables, channel, priority, and idempotency key. Return 202 with notification_id and a status URL after durable acceptance. GET returns accepted, suppressed, sending, provider_accepted, delivered, failed, or unknown according to defined transitions. Do not let arbitrary callers choose unrestricted template HTML or destination lists.

**Schema.** notification_intents(id, tenant_id, operation_key, template_version, recipient_ref, channel, priority, expires_at, state); attempts(id, notification_id, provider, provider_message_id, outcome, next_attempt_at); preferences(user_id, channel, purpose, consent_version); inbox(provider_event_id); outbox(event_id, payload). Separate personal recipient data from broad operational telemetry and apply retention policies.

[[FIG:case-notify-detail]]

**Step-by-step flow.** Authenticate the caller, check purpose and template permission, deduplicate intent, and store it with an outbox entry. A scheduler selects the channel queue and enforces freshness. Workers recheck relevant preference policy, acquire provider capacity, send with a stable key where supported, persist the result, and acknowledge. Callbacks are verified and deduplicated. A provider timeout creates an unknown state, resolved by provider query or controlled retry according to duplicate tolerance.

[[FIG:case-notify-sequence]]

**Failures and security.** A poison template goes to a DLQ with an owner. A provider outage opens a breaker and pauses low-priority work. Switching providers can duplicate a message if the first provider accepted it but lost its response; distinguish failover from proof of non-delivery. Protect webhook endpoints and recipient data, rate-limit callers, and prevent template variables from injecting untrusted HTML into an unsafe rendering context.

**Scaling and trade-offs.** Partition by channel and priority, with fairness across tenants. Batch only where provider semantics and freshness permit. Drop expired promotional messages under policy while preserving critical transactional intent for reconciliation. Measure age by priority, provider acceptance, final delivery where available, duplicate rate, and unit cost.

**Validation and interview probe.** Test preference changes between enqueue and send, duplicate intents, late callbacks, provider throttling, and replay after a long outage. Ask whether one message sent twice is preferable to one message lost; the correct answer can differ for a receipt, a login code, and a costly SMS campaign. Make that product choice explicit.

### Case 6. Video and content delivery

**Requirements and contract.** Accept authorized uploads, process media into supported renditions, publish manifests, and deliver content efficiently across regions. Distinguish upload completion, processing completion, and publication. Support deletion and private access where required. A partial transcode must not become a publicly valid complete asset.

**Estimates.** Assume 10,000 uploads/day averaging 500 MB: 5 TB/day of original media before renditions and retention. At 100,000 simultaneous viewers averaging 3 Mb/second, delivery is 300 Gb/second. A 95% byte hit ratio would reduce origin delivery to about 15 Gb/second under the simplified assumption; request hit ratio alone cannot provide that estimate.

[[FIG:case-video-overview]]

Clients upload directly to controlled object storage using scoped upload authorization. Processing workers create immutable renditions. The CDN serves published objects while a metadata API controls permissions and lifecycle.

**API contracts.** POST /v1/uploads creates an upload session and returns a short-lived destination constrained to the intended object and size policy. POST /v1/uploads/{id}/complete verifies the stored object and schedules processing. GET /v1/videos/{id} returns processing status or an authorized manifest. DELETE begins a documented takedown lifecycle covering origin, edge caches, and derived artifacts.

**Schema.** videos(id, owner_id, state, source_object, checksum, duration, visibility, version); renditions(video_id, profile, object_prefix, checksum, status); processing_jobs(id, video_id, artifact_version, state, attempts); publication(video_id, manifest_object, generation). Object names include immutable content or generation identity. Metadata commits publication only after all required artifacts pass validation.

[[FIG:case-video-detail]]

**Step-by-step flow.** Validate the upload session, ingest bounded media, verify checksum and type in an isolated processor, enqueue transcode jobs, produce renditions, validate outputs, write a versioned manifest, then atomically mark that manifest published in metadata. Playback authorization yields a scoped URL or cookie policy. The edge serves cached segments and fetches missing immutable objects from a protected origin.

[[FIG:case-video-sequence]]

**Failures and security.** Workers can retry a deterministic rendition key without publishing duplicate versions. A crash leaves incomplete objects unreferenced until cleanup. Media parsers process untrusted content and need isolation, resource limits, and maintained libraries. A public origin bypasses private CDN access controls. Signed links have expiry and revocation trade-offs, and cache policy must not leak private content across viewers.

**Scaling and trade-offs.** Separate upload, processing, and playback capacity. Use priority and checkpointing for expensive transcodes. Add origin shielding and staged warmup for popular releases. Adaptive bitrate improves playback under changing networks but adds storage and encoding cost. Multi-CDN improves some resilience while complicating authorization, cache policy, and telemetry.

**Validation and interview probe.** Test incomplete uploads, corrupt media, duplicate completion callbacks, worker interruption, manifest publication races, and takedown propagation. Measure startup delay, rebuffering, playback failures, and delivered bytes, not merely API latency. Ask how deletion interacts with already downloaded content: server-side removal cannot erase copies users already possess.

### Case 7. Scalable AI inference API

**Requirements and contract.** Serve a versioned model through an authenticated API with bounded input, cost-aware quotas, predictable overload behavior, and observable latency. Support synchronous small requests and asynchronous long jobs. Define quality evaluation separately from service availability. Assume no GPU requirement until measurements show a benefit; a small CPU model is a legitimate production choice.

**Estimates.** Suppose peak demand is 200 requests/second and measured service time on one worker is 100 ms at concurrency one. The ideal single-worker rate is ten/second, so twenty workers only match arrivals. At a target utilization of 70%, the arithmetic suggests ceil(200/(10*0.7))=29 workers before failure headroom and nonlinearity. For generative models, requests are not equal: estimate input/output tokens, sequence lengths, memory, and time to first token. These are illustrative assumptions, not GPU benchmarks.

[[FIG:case-ai-overview]]

The gateway authenticates and reserves budget, then routes to a bounded interactive queue or durable job path. Model workers load immutable artifacts from a registry/object store. Telemetry captures serving phases; an evaluation pipeline independently measures quality.

**API contracts.** POST /v1/predict accepts a model alias or explicit supported version and a bounded schema. It returns prediction, model_version, preprocessing_version, and request_id. POST /v1/jobs accepts longer work with an idempotency key and returns 202; GET /v1/jobs/{id} requires tenant ownership. Streaming endpoints define partial-result and cancellation behavior, including how usage is charged after a client disconnects.

**Schema.** model_versions(id, artifact_uri, checksum, feature_schema_version, preprocessing_version, status); deployments(alias, version, cohort_policy, rollback_version); inference_jobs(id, tenant_id, operation_key, input_ref, model_version, state, deadline, output_ref); usage_ledger(operation_id, reserved_units, actual_units, outcome); evaluations(model_version, dataset_version, metric_definition, result). Protect input/output references and avoid raw private prompts in logs or metric labels.

[[FIG:case-ai-detail]]

**Step-by-step flow.** Authenticate, validate input size and shape, choose a stable model/preprocessing pair, reserve estimated cost, and check a tenant-scoped versioned cache only if reuse is semantically permitted. Admit within queue and concurrency bounds. Optionally batch compatible requests up to a maximum size and wait time. Execute preprocessing and model inference, validate output shape, persist asynchronous results if applicable, return or stream, and reconcile actual usage. Release resources and propagate cancellation where supported.

[[FIG:case-ai-sequence]]

**Failures and security.** A model artifact can be missing, corrupted, incompatible, or malicious. Verify provenance/checksum, use trusted formats and loaders, and isolate untrusted processing. Cold starts require startup/readiness separation. Retries can duplicate expensive jobs; provider idempotency or durable job identity prevents double billing where the contract permits. Prompt safety, access to retrieval data, and model-quality controls are separate from ordinary TLS and authentication. An authorized user must still be prevented from retrieving another tenant's documents.

**Scaling and trade-offs.** Scale on queue age, useful throughput, saturation, and memory constraints, accounting for loading time. Large batches improve some throughput but increase latency and may exceed memory. Separate interactive and batch pools, share model weights safely where supported, and test multiple input shapes. Prediction caching requires model, preprocessing, tenant, and generation settings in the key. Multi-region serving must align artifact availability, data residency, and external-provider quotas.

**Validation and interview probe.** Run the included toy API to study mechanics; its sigmoid score is not a trained model and has no accuracy claim. Test overload, invalid numeric values, authorization, cache versioning, model-load failure, queue expiry, and cancellation. Canary a real model using latency, cost, quality, and safety guardrails. Ask why GPU utilization can rise while useful throughput falls: queueing, oversized sequences, retries, memory pressure, or poor batching can all be involved, and evidence must discriminate among them.

### Case 8. Distributed job-processing system

**Requirements and contract.** Accept durable jobs, schedule eligible work, distribute it to workers, expose progress, retry transient failures, and isolate poison jobs. Support cancellation and expiry with explicit semantics. A job marked completed must have a durable result under the promised storage guarantees. Worker process health does not prove job progress.

**Estimates.** Assume arrival at 1,000 jobs/second, mean execution two seconds, and 10 KB metadata/input references per job. Stable average concurrent execution is about 2,000 jobs before headroom. If 100 workers each support twenty useful concurrent I/O tasks, they merely match that average under ideal assumptions. CPU-bound tasks require a different execution model. One hour of unprocessed arrivals produces 3.6 million jobs and about 36 GB of logical metadata at the stated size.

[[FIG:case-jobs-overview]]

The API persists job intent and outbox metadata. A broker dispatches references to workers. Results live outside worker-local storage. A scheduler/reconciler recovers expired leases and monitors deadlines; a DLQ holds work needing repair.

**API contracts.** POST /v1/jobs accepts type, schema_version, input_ref, priority, deadline, and idempotency key. Return 202 with job_id only after durable acceptance. GET /v1/jobs/{id} returns queued, running, completed, failed, cancel_requested, cancelled, or reconciliation_required. DELETE or a cancel command requests cancellation; it must not claim an irreversible external effect was undone.

**Schema.** jobs(id, tenant_id, operation_key, type, schema_version, state, attempt, lease_owner, lease_expiry, fencing_token, deadline, result_ref); attempts(job_id, number, started_at, finished_at, error_class); outbox(event_id, job_id); result_objects(job_id, checksum, generation). Enforce unique logical operation identity and guarded state transitions. Store large payloads separately with access-controlled references and retention.

[[FIG:case-jobs-detail]]

**Step-by-step flow.** Validate and persist the job, publish its reference through an outbox relay, claim work with bounded lease/visibility, verify the current ownership token, execute with checkpoints, commit the result and terminal state under the applicable consistency boundary, then acknowledge. If execution exceeds the lease, renew only while healthy. On crash, another worker can retry; local or external effects must remain idempotent. Old owners must be fenced from overwriting newer results.

[[FIG:case-jobs-sequence]]

**Failures and security.** Acknowledgment loss causes redelivery. A paused worker can resume after lease expiry. A malformed payload enters DLQ after a bounded policy. Authorize input/result objects and job status by tenant, sandbox untrusted code if the product executes it, and never give arbitrary jobs the platform's administrative credentials. Separate compute pools by trust and resource class where necessary.

**Scaling and trade-offs.** Measure oldest age and completion rate by priority, not only depth. Scale consumers against downstream capacity and reserve interactive capacity. Fair scheduling prevents one tenant's huge batch from starving others. Checkpointing reduces restart cost but adds state and compatibility requirements. Exactly-once local result publication may be achievable with a transaction or conditional object generation; that does not imply exactly-once arbitrary external effects.

**Validation and interview probe.** Kill workers before and after result commit, delay acknowledgments, expire leases, replay old schemas, cancel mid-execution, and restore the job database. Verify one authoritative terminal result and account for every accepted job. Ask how to drain a million-job backlog without harming live traffic; use excess capacity, priority, deadline expiry, and rate-limited recovery rather than simply maximizing worker count.
