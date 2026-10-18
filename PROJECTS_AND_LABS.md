# Projects and Labs

Use the thirty coding/configuration labs first, then the fifteen architecture exercises and ten incident table-tops. Solutions follow each task so you can compare a written attempt. Run only against local or explicitly authorized systems.

## Practical coding and configuration labs

### LAB01. Token bucket boundary tests (Beginner)

**Task:** Implement a bucket with capacity five and refill two/second. Use a fake monotonic clock; do not sleep in the test. Verify a weighted request and a long idle period.

**Solution walkthrough:** Admit five initial unit requests and reject the sixth. At half a second, admit exactly one more. A cost above capacity is rejected without making the balance negative. After a long idle, tokens stop at capacity. Add a lock or atomic store operation before using the algorithm concurrently.

**Associated file:** [examples/algorithms.py](examples/algorithms.py). See [setup and expected output](examples/README.md).

### LAB02. Cache expiry and key scope (Beginner)

**Task:** Add tenant and model version to a prediction-cache key and test exact TTL expiry. Decide whether None can be a cached value.

**Solution walkthrough:** A tuple of tenant, model version, preprocessing version, normalized input, and relevant parameters prevents unrelated representations sharing a key. At expiry the entry is a miss. The supplied cache uses None as a miss sentinel, so it cannot distinguish a cached None; use a private sentinel for a general cache.

**Associated file:** [examples/algorithms.py](examples/algorithms.py). See [setup and expected output](examples/README.md).

### LAB03. Circuit-breaker probe failure (Intermediate)

**Task:** Open the breaker, advance to half-open, and make the recovery probe fail. Then distinguish a user validation error from a provider timeout.

**Solution walkthrough:** The failed probe reopens the breaker with a new cooldown. A validation error should propagate without counting as a dependency-health failure. The sequential demo does not protect concurrent half-open probes; a real implementation needs atomic probe admission and a carefully selected observation window.

**Associated file:** [examples/algorithms.py](examples/algorithms.py). See [setup and expected output](examples/README.md).

### LAB04. Retry budget accounting (Intermediate)

**Task:** Implement a transient operation that fails once, succeeds once, and records the remaining deadline on each call. Test permanent failure and insufficient time for another wait.

**Solution walkthrough:** The second attempt receives less remaining time, not a fresh timeout. Permanent validation errors bypass retry. If the planned delay consumes the remaining budget, stop before another attempt. The callee must also enforce its passed timeout; passing a number alone cannot interrupt arbitrary blocking code.

**Associated file:** [examples/algorithms.py](examples/algorithms.py). See [setup and expected output](examples/README.md).

### LAB05. Transactional idempotency (Intermediate)

**Task:** Submit eight concurrent checkout calls using one tenant/key and compare order IDs, inventory, and outbox rows. Reuse the key with a changed quantity.

**Solution walkthrough:** All matching replays return one order ID, decrement stock once, and create one outbox row. A changed payload raises conflict. The unique key is scoped to tenant. SQLite serializes these writers; repeat the invariant test with PostgreSQL under the intended isolation before claiming equivalent deployment behavior.

**Associated file:** [examples/orders.py](examples/orders.py). See [setup and expected output](examples/README.md).

### LAB06. Crash before local commit (Intermediate)

**Task:** Inject a failure after inventory modification but before commit. Inspect all related tables and then retry the original operation.

**Solution walkthrough:** The transaction rollback restores inventory and removes order, operation, and outbox changes together. A later retry can succeed. This proves local atomicity only; if a real provider had already charged outside the transaction, local rollback would not undo it and reconciliation would be required.

**Associated file:** [examples/orders.py](examples/orders.py). See [setup and expected output](examples/README.md).

### LAB07. Inbox and duplicate delivery (Intermediate)

**Task:** Deliver the same event twice to the notification consumer and verify one local notification row. Explain the remaining email boundary.

**Solution walkthrough:** Insert the event ID and local effect in one transaction. The duplicate ID causes the second delivery to become a no-op. A real email send is outside that database transaction, so provider idempotency or a documented duplicate/loss trade-off is still needed. Do not rename this test exactly-once email delivery.

**Associated file:** [examples/orders.py](examples/orders.py). See [setup and expected output](examples/README.md).

### LAB08. Poison message and redrive (Intermediate)

**Task:** Mix a successful job, its duplicate, and a poison message. Move the poison job after three attempts and propose a controlled replay procedure.

**Solution walkthrough:** The local effect count is one and the poison job records three attempts in DLQ. Repair the schema or handler, preserve the original event ID, throttle replay, and observe terminal outcomes. The in-memory demo loses state on process exit; production attempts and progress need durable storage.

**Associated file:** [examples/messaging.py](examples/messaging.py). See [setup and expected output](examples/README.md).

### LAB09. Saga unknown payment (Advanced)

**Task:** Compare confirmed, declined, and unknown provider outcomes. Fail inventory-release compensation once and recover it later.

**Solution walkthrough:** Confirmed advances the order; declined compensates; unknown retains a reconciliation state rather than guessing failure. Failed compensation remains pending with its reservation intact. Retry the compensation idempotently after the cause is resolved, and alert on excessive state age. Persist workflow state before relying on restart recovery.

**Associated file:** [examples/messaging.py](examples/messaging.py). See [setup and expected output](examples/README.md).

### LAB10. Pool cleanup and saturation (Intermediate)

**Task:** Raise an exception while holding the only pool token, then acquire it again. Attempt a nested acquisition with a short deadline.

**Solution walkthrough:** The finally block returns the token despite the exception. The nested acquisition times out rather than waiting forever. A real pool must additionally roll back/reset connection state and handle stale sockets. Use aggregate pool limits across replicas, not a size chosen independently for each process.

**Associated file:** [examples/concurrency.py](examples/concurrency.py). See [setup and expected output](examples/README.md).

### LAB11. Fencing a paused owner (Advanced)

**Task:** Write with token nine, then simulate an old worker resuming with token eight. Explain who must generate and enforce tokens.

**Solution walkthrough:** The resource rejects token eight and retains the new owner's value. A safe coordination authority must issue increasing tokens; the storage target must enforce them. The toy ledger only demonstrates enforcement and is not a distributed lock service. An external API without token support needs another correctness strategy.

**Associated file:** [examples/concurrency.py](examples/concurrency.py). See [setup and expected output](examples/README.md).

### LAB12. Deterministic race reproduction (Beginner)

**Task:** Reproduce two buyers reading stock one before either writes. Compare final stock with the number of accepted sales.

**Solution walkthrough:** Both can write zero, leaving an apparently valid stock value but two accepted sales. Protect admission and decrement in one conditional database update or correct critical section. A final nonnegative stock assertion alone is insufficient; assert accepted sales plus remaining stock equals the original stock.

**Associated file:** [examples/concurrency.py](examples/concurrency.py). See [setup and expected output](examples/README.md).

### LAB13. Wait-for graph (Intermediate)

**Task:** Represent transactions as nodes and waits as directed edges. Detect a two-node cycle and a longer acyclic chain.

**Solution walkthrough:** Depth-first traversal tracks active and completed nodes. Revisiting an active node finds a cycle; revisiting a completed node does not. In a real database, recover by aborting and retrying the entire victim transaction under a bounded policy. Distinguish deadlock from a long but progressing wait.

**Associated file:** [examples/concurrency.py](examples/concurrency.py). See [setup and expected output](examples/README.md).

### LAB14. Bounded queue conservation (Intermediate)

**Task:** Run arrivals at 120/second, service at 100/second, capacity 1,000, for sixty discrete ticks. Verify no work silently disappears.

**Solution walkthrough:** Accepted work equals completed plus remaining backlog. Total arrivals equal completed plus backlog plus explicit rejection. The discrete model admits then serves within each tick, so its exact maximum backlog differs from a continuous fluid approximation. State that convention before comparing arithmetic or simulation output.

**Associated file:** [examples/concurrency.py](examples/concurrency.py). See [setup and expected output](examples/README.md).

### LAB15. Memory-retention experiment (Intermediate)

**Task:** Allocate a retained collection, observe traced memory, then clear references. Explain why this is not a production leak diagnosis by itself.

**Solution walkthrough:** The lab shows reachability-driven retention and release for Python allocations. It does not measure all native allocations, resident memory, fragmentation, or GPU memory. A real investigation needs repeated snapshots under a steady workload, retainer analysis, and a soak test after the fix.

**Associated file:** [examples/concurrency.py](examples/concurrency.py). See [setup and expected output](examples/README.md).

### LAB16. Percentile aggregation (Intermediate)

**Task:** Compute mean and P99 for 980 samples at 20 ms and twenty at 2,000 ms. Then combine two unequal instance populations.

**Solution walkthrough:** Mean is 59.6 ms and nearest-rank P99 is 2,000 ms. Combine samples or compatible histogram counts before calculating the fleet percentile. Averaging local P99 values weights neither population nor rank correctly. Report timed-out requests and sample size so the result is interpretable.

**Associated file:** [examples/performance.py](examples/performance.py). See [setup and expected output](examples/README.md).

### LAB17. Error-budget policy (Intermediate)

**Task:** Compute burn for 9,900 good requests out of 10,000 at a 99.9% target, and write a release decision rule.

**Solution walkthrough:** The bad fraction is 1%, ten times the allowed 0.1%. The observed population has consumed more than its allowed bad-event allocation. A policy can pause risky features while permitting reviewed mitigations, but it must use the actual SLO window and distinguish short spikes from sustained burn.

**Associated file:** [examples/performance.py](examples/performance.py). See [setup and expected output](examples/README.md).

### LAB18. Trace critical path (Intermediate)

**Task:** Compare summing all spans with taking the longest required branch in a parallel trace. Add explicit pool-acquisition timing.

**Solution walkthrough:** Parallel branch durations overlap; summing them overstates wall-clock time. Add parent work to the maximum required branch under the toy DAG model. Pool wait deserves its own span because database execution can remain fast while connections are unavailable. Real traces also require careful handling of nested overlap and clock skew.

**Associated file:** [examples/performance.py](examples/performance.py). See [setup and expected output](examples/README.md).

### LAB19. Bound SQL values safely (Beginner)

**Task:** Search for a legitimate apostrophe-containing name and a harmless SQL-looking string in the isolated SQLite database.

**Solution walkthrough:** Parameter binding returns the exact apostrophe-containing row and no rows for the unrelated SQL-looking value. The input remains data. For dynamic sort direction or identifiers, use an explicit allowlist; value placeholders do not substitute arbitrary SQL structure. PostgreSQL driver placeholder syntax differs from this SQLite example.

**Associated file:** [examples/security.py](examples/security.py). See [setup and expected output](examples/README.md).

### LAB20. Authorization and browser controls (Intermediate)

**Task:** Deny a cross-tenant write, reject a lookalike CORS origin, and reject a missing CSRF token. Explain why these are three separate tests.

**Solution walkthrough:** Object authorization prevents access to another tenant's data. CORS controls browser reading by origin and does not authenticate arbitrary API clients. CSRF protects cookie-authenticated mutations from unwanted cross-site actions. A successful result in one test proves nothing about the other two boundaries.

**Associated file:** [examples/security.py](examples/security.py). See [setup and expected output](examples/README.md).

### LAB21. Webhook tampering and replay (Intermediate)

**Task:** Verify an HMAC over raw bytes, change one byte, and test an expired timestamp. Add durable event-ID deduplication as a design step.

**Solution walkthrough:** The valid signature passes, changed bytes fail, and an old timestamp fails the normal freshness window. Timestamp checks do not prevent replay within that window; durable event IDs suppress repeated effects. Long-outage redelivery needs an explicit authenticated recovery policy rather than silently disabling all replay checks.

**Associated file:** [examples/security.py](examples/security.py). See [setup and expected output](examples/README.md).

### LAB22. Safe URL-fetch boundary (Advanced)

**Task:** Allow one exact HTTPS partner host and reject a suffix lookalike, credentials in the URL, a wrong port, and a loopback address. Describe missing defenses.

**Solution walkthrough:** Parsing and exact allowlisting reject these input shapes. A general fetcher additionally needs actual connected-IP validation, DNS-rebinding defense, redirect validation, restricted egress, no ambient credentials, and bounded response/time. The lab performs no network fetch and must not be represented as a complete arbitrary-URL SSRF defense.

**Associated file:** [examples/security.py](examples/security.py). See [setup and expected output](examples/README.md).

### LAB23. Stream framing and reconnect (Intermediate)

**Task:** Split a length-prefixed byte stream mid-message and recover two complete messages after the remaining bytes arrive. Format an SSE event with an ID.

**Solution walkthrough:** Retain incomplete bytes until the declared length is available; TCP reads do not preserve application messages. Reject oversized declared frames. SSE uses text/event-stream and blank-line termination; a durable cursor and retained history recover gaps after reconnect. Socket delivery alone does not establish business processing.

**Associated file:** [examples/protocols.py](examples/protocols.py). See [setup and expected output](examples/README.md).

### LAB24. Schema compatibility adapter (Intermediate)

**Task:** Read a historical INR-only record into a new explicit-currency representation. Explain why the default is conditional.

**Solution walkthrough:** The adapter may add INR only because the historical contract states all v1 records used INR. If old data contains mixed currencies, that default invents information and is unsafe. Test unknown schema versions, missing required values, units, and old-reader/new-writer compatibility separately.

**Associated file:** [examples/protocols.py](examples/protocols.py). See [setup and expected output](examples/README.md).

### LAB25. Inference API boundary (Intermediate)

**Task:** Start the local API, send valid and invalid feature arrays, repeat a request, inspect metrics, and test an incorrect API key.

**Solution walkthrough:** A valid zero-valued input returns score 0.5 with toy-linear-v1; the repeat reports a cache hit. Booleans, empty arrays, nonfinite values, and oversized inputs are rejected. Incorrect credentials return 401. This is a local standard-library teaching server with per-process limits, not a production multi-tenant serving stack.

**Associated file:** [examples/inference_api.py](examples/inference_api.py). See [setup and expected output](examples/README.md).

### LAB26. PostgreSQL plan comparison (Intermediate)

**Task:** Run database.sql in a disposable PostgreSQL database, compare plans before and after the composite index, and inspect partition pruning.

**Solution walkthrough:** Evaluate actual rows, loops, buffer work, sort behavior, and elapsed time without requiring one universal plan or speedup. Data size and caching influence planner choices. The script creates an isolated schema and intentionally fails on a second run rather than dropping existing work. EXPLAIN ANALYZE executes its statement.

**Associated file:** [examples/database.sql](examples/database.sql). See [setup and expected output](examples/README.md).

### LAB27. Container packaging and limits (Intermediate)

**Task:** Build the image, run it with a runtime-only demo key, inspect the user, and test readiness. Compare startup with a cold versus locally available image.

**Solution walkthrough:** The image runs as UID 10001, copies only required modules, and receives its key at runtime. Multi-stage verification checks syntax but does not replace behavioral tests. A production release should use a reviewed base digest and maintained server, plus explicit signal/draining behavior and external TLS policy.

**Associated file:** [examples/Dockerfile](examples/Dockerfile). See [setup and expected output](examples/README.md).

### LAB28. Kubernetes labels and probes (Advanced)

**Task:** In a local cluster, create the required Secret, load the local image, apply k8s.yaml, and observe readiness and rollout. Inspect the HPA's metric dependency.

**Solution walkthrough:** Service selectors must match Pod labels and the named target port. Startup permits initialization before other probes. Readiness changes routing eligibility; liveness triggers restart for appropriate local failure. HPA needs a working metrics API and resource requests. A configured object is not proof that traffic or autoscaling works.

**Associated file:** [examples/k8s.yaml](examples/k8s.yaml). See [setup and expected output](examples/README.md).

### LAB29. Terraform and Helm review (Advanced)

**Task:** Run Terraform format/validate/plan for the local terraform_data resource. Render the Helm chart with one and three replicas and inspect output.

**Solution walkthrough:** The Terraform example creates no cloud resource; its state still demonstrates mapping and lifecycle. Helm rendering should preserve matching labels, secret references, ports, and probes. Static rendering does not validate runtime image availability or cluster admission. Never apply an unexpected destructive plan merely because validation passed.

**Associated file:** [examples/main.tf](examples/main.tf). See [setup and expected output](examples/README.md).

### LAB30. Incident and postmortem tabletop (Advanced)

**Task:** Read the timed incident evidence and decide when the service is recovered. Write one preventive test and one detection improvement.

**Solution walkthrough:** Restored HTTP success at 09:12 is insufficient while fourteen payment outcomes remain unknown. Reconciliation completes at 09:20. A preventive test verifies DB connections are released before remote calls; detection separately measures pool wait. Assign owners and measurable acceptance criteria instead of asking engineers to be more careful.

**Associated file:** [examples/incident_drill.py](examples/incident_drill.py). See [setup and expected output](examples/README.md).

## Architecture-design exercises

### DESIGN01. URL shortener with urgent takedown (Advanced)

**Task:** Extend Case 1 so an abusive link must stop resolving within a stated short bound, while ordinary edits tolerate stale caches.

**Solution walkthrough:** Separate urgent deny policy from ordinary cached mapping freshness. Distribute a versioned deny signal, protect origin bypass, define edge purge and failure behavior, and test stale clients. State the remaining propagation bound and whether an unavailable policy source blocks redirects. Measure both removal latency and legitimate redirect availability.

### DESIGN02. Global quota with regional leases (Advanced)

**Task:** Extend Case 2 to three regions without a central network call on every request.

**Solution walkthrough:** Allocate bounded regional token leases from a durable global authority. Define lease expiry, unspent reservation, replenishment, and reconciliation. Bound outstanding allocation and account for uncertain usage after partition. Use small local concurrency limits and an explicit paid-work outage policy. Trade coordination frequency against utilization and possible overshoot.

### DESIGN03. Inventory reservation expiry (Advanced)

**Task:** Extend Case 3 to handle payment confirmation arriving after a reservation expires.

**Solution walkthrough:** Persist reservation and payment state with versions. Reconcile unknown provider operations before treating them as decline. If stock was reassigned and payment later confirms, apply an explicit business policy: reacquire stock, offer substitution, or initiate a refund with tracked completion. Test the race instead of assuming expiry cancels payment.

### DESIGN04. Large-room chat (Advanced)

**Task:** Extend Case 4 to a room with 100,000 members while preserving conversation order.

**Solution walkthrough:** Separate one logical sequencing authority from distributed fanout. Persist once, publish batches/references to connection partitions, and let clients recover from history. Bound per-client buffers and use coarse presence. Explain the sequencer's failover and throughput ceiling; sharding fanout alone does not remove ordered-write ownership.

### DESIGN05. Notification priority fairness (Advanced)

**Task:** Extend Case 5 so campaigns cannot starve account-security messages without permanently starving campaigns.

**Solution walkthrough:** Use separate priority queues or weighted fair scheduling, reserve provider capacity for critical work, and allocate residual capacity with aging or shares. Apply tenant quotas and expiry. Monitor oldest age per class and provider limits. A single strict-priority queue can starve low-priority work indefinitely.

### DESIGN06. Private video distribution (Advanced)

**Task:** Extend Case 6 to paid videos with fast subscription revocation.

**Solution walkthrough:** Authorize manifest access, scope signed delivery credentials, restrict origin access, and define credential lifetime. Short lifetimes improve revocation but increase authorization dependency. Protect cache keys and avoid sharing private responses incorrectly. Acknowledge that already downloaded content cannot be recalled by revoking a server-side URL.

### DESIGN07. Interactive and batch inference (Advanced)

**Task:** Extend Case 7 to serve interactive predictions and nightly bulk processing on shared accelerators.

**Solution walkthrough:** Separate admission queues and reserve interactive headroom. Batch compatible bulk work with checkpoints and preemption where supported. Measure interactive P99 and batch freshness, memory, useful throughput, and cost. Pause bulk work under overload rather than letting it consume every slot. Model artifact compatibility applies to both paths.

### DESIGN08. Job cancellation and external effects (Advanced)

**Task:** Extend Case 8 with cancellation while a worker is calling an external provider.

**Solution walkthrough:** Represent cancel_requested separately from cancelled. Stop future work where safe, but reconcile an in-flight provider operation before claiming no effect occurred. Guard terminal transitions and use fencing for local result publication. Return the final known business outcome, including too-late-to-cancel, rather than hiding an already committed action.

### DESIGN09. Feature-store freshness (Advanced)

**Task:** Design online and offline features for a recommendation system with a ten-minute freshness objective.

**Solution walkthrough:** Version transformations, record event time and availability time, materialize online features idempotently, and monitor lag from source event to serving availability. Train with point-in-time joins to avoid future leakage. Define evaluated missing/stale defaults and include feature version in prediction-cache identity. Test late events and replay.

### DESIGN10. Expand-and-contract migration (Advanced)

**Task:** Rename a required customer field while old mobile clients and old API Pods remain active.

**Solution walkthrough:** Add the new field, accept both contracts with explicit precedence, dual-write compatible data, backfill in bounded batches, and measure old-client usage. Switch reads only after validation. Remove the old representation in a separate release after client and rollback support expire. Test every supported reader/writer combination.

### DESIGN11. Regional disaster recovery (Advanced)

**Task:** Recover checkout within one hour with an explicitly chosen data-loss target after total primary-region loss.

**Solution walkthrough:** Budget detection, authority transfer, data readiness, routing, startup, and validation separately. Preposition artifacts, keys, configuration, and capacity. Fence old writers and compare replica progress to the RPO. Drill the full user journey and payment reconciliation. If measurements exceed an hour, revise architecture or target honestly.

### DESIGN12. Observability under privacy constraints (Advanced)

**Task:** Diagnose tenant-specific inference failures without retaining raw prompts in general telemetry.

**Solution walkthrough:** Use bounded workload-class metrics, trace and operation IDs, model/preprocessing version, input length buckets, and sanitized error categories. Keep any necessary sensitive audit record separately access-controlled with narrow retention. Connect evidence by opaque IDs. Test redaction and document sampling gaps instead of claiming complete visibility.

### DESIGN13. Webhook platform (Advanced)

**Task:** Deliver merchant webhooks with retries, signing-key rotation, and customer-configured destinations.

**Solution walkthrough:** Persist event IDs and attempts, sign exact bytes, define timestamps and replay, and rotate secrets with overlap. Isolate outbound fetching with egress restrictions and redirect/IP controls. Apply per-merchant fairness, deadlines, and DLQ ownership. Acknowledge that merchants need idempotent consumers and that destination failure is independent of platform acceptance.

### DESIGN14. Cost-aware model canary (Advanced)

**Task:** Release a model that improves quality but doubles average output length and may raise latency and cost.

**Solution walkthrough:** Compare representative cohorts with versioned evaluation data and delayed outcome review. Measure time to first token, completion time, useful throughput, output length, and cost per quality-qualified result. Set guardrails and a rollback-compatible artifact set. Consider product-level output limits or selective routing instead of a blanket deployment.

### DESIGN15. Dependency-independent recovery (Advanced)

**Task:** Redesign a multi-region service whose two regions share one identity/configuration dependency.

**Solution walkthrough:** Map transitive dependencies, distinguish cached validation from live privileged operations, and define bounded stale-config use. Preposition verified keys and nonsecret configuration with revocation policies. Keep emergency access scoped and audited. Test failure of the shared dependency itself; two application regions alone do not prove independence.

## Production incident scenarios

### INCIDENT01. Tenfold traffic surge (Advanced)

**Task:** Checkout latency rises after traffic jumps tenfold. CPU is high on API Pods, but the database is near its connection cap.

**Solution walkthrough:** Establish user impact and stop optional work. Inspect arrival/completion rates, pool wait, database saturation, cache misses, and retry amplification. Apply tenant-aware admission and bounded concurrency before blindly adding Pods, since extra pools can exceed the database cap. Scale only the measured bottleneck with headroom and verify successful checkout rate, P99, and backlog age. Preserve a timeline and review whether the surge was legitimate demand or abuse.

### INCIDENT02. Low database CPU, slow requests (Advanced)

**Task:** Queries appear slow while database CPU remains low and disk throughput is ordinary.

**Solution walkthrough:** Separate pool acquisition from server execution, inspect lock waits and long transactions, and compare query plans and wait events. A remote call inside a transaction can hold connections and locks while consuming little CPU. Mitigate the specific blocker or revert the responsible path under a controlled plan. Do not increase CPU merely because the symptom is latency. Verify transaction age, pool occupancy, and user recovery.

### INCIDENT03. Duplicate payment charges (Advanced)

**Task:** Clients retried after timeouts and some orders now have two provider charges.

**Solution walkthrough:** Stop the unsafe retry path and preserve provider operation IDs. Reconcile all uncertain orders against the provider before issuing refunds or retrying again. Add tenant-scoped durable idempotency with request fingerprints and stable provider keys; define retention and unknown states. A local mutex or in-memory cache is insufficient across replicas and restarts. Validate with response-loss and concurrent-replay tests, then monitor duplicate financial effects.

### INCIDENT04. Stale catalog prices (Advanced)

**Task:** Most reads are fast, but some users see an old price after a confirmed update.

**Solution walkthrough:** Compare source and cache versions, TTL/stale-serving policy, invalidation delivery, and region-specific keys. Reproduce the delayed-reader stale-repopulation race. Keep authoritative checkout price validation while repairing browsing freshness. Use version-aware updates or immutable versioned keys as appropriate, and bound origin load during invalidation. A high cache-hit ratio says nothing by itself about correctness.

### INCIDENT05. Running Pods, unreachable service (Advanced)

**Task:** Kubernetes shows running Pods, but users receive gateway errors.

**Solution walkthrough:** Trace DNS, ingress, TLS, Service port, selector, EndpointSlice readiness, network policy, application bind address, and dependency credentials. Running is not ready, and ready is not end-to-end healthy. Compare direct local Pod behavior with Service and ingress paths in a controlled environment. Fix the broken boundary and verify from the user side; restarting every Pod can hide evidence and trigger cold-start overload.

### INCIDENT06. Gradual P99 regression after release (Advanced)

**Task:** Mean latency barely changes while P99 worsens over an hour.

**Solution walkthrough:** Segment by release, route, region, workload size, and cache state. Compare queue wait, allocation/GC, connection age, lock contention, and slow traces. A retained-object leak or slowly growing pool occupancy can explain gradual degradation. Halt rollout or revert a compatible change if user impact warrants it, then reproduce under a soak test. Exclude neither timeouts nor large requests merely to improve the percentile.

### INCIDENT07. Half-completed cross-service order (Advanced)

**Task:** Inventory is reserved, the payment call timed out, and the order remains pending.

**Solution walkthrough:** Treat payment as unknown, query the original provider operation ID, and guard order transitions against racing callbacks. If declined, release inventory idempotently; if confirmed, complete or apply an explicit repair policy. Persist compensation progress and alert on workflow age. Blindly rolling back local rows can create an untracked successful charge. Recovery requires business reconciliation, not just healthy services.

### INCIDENT08. GPU busy, inference queue growing (Advanced)

**Task:** GPU utilization is near full while queue age and useful completion latency rise.

**Solution walkthrough:** Inspect input/output lengths, batch composition, memory pressure, retries, model version, and actual useful tokens or predictions per second. Enforce cost-aware admission and separate bulk from interactive work. Test a smaller or length-aware batch policy and available replica headroom. High utilization alone does not show efficient useful work. Verify quality and cost alongside latency after mitigation.

### INCIDENT09. One region unavailable (Advanced)

**Task:** The same service works in region A but fails for users in region B.

**Solution walkthrough:** Compare regional DNS answers, certificates, routes, policy, artifacts, secrets, downstream reachability, and data replication. Determine whether the failure is local compute, an entry path, or a shared dependency observed differently. Shift traffic only if the destination has capacity and data/ownership semantics permit it. Verify user-region measurements and avoid promoting a second writer solely because one observer timed out.

### INCIDENT10. Migration breaks old Pods (Advanced)

**Task:** New Pods work after a schema migration, but old Pods fail during a rolling deployment.

**Solution walkthrough:** Stop the rollout and identify the incompatible schema change. Restore compatibility or roll forward safely if the previous binary cannot read current data. Do not assume an image rollback undoes DDL. Reintroduce the old representation if feasible, then use expand-and-contract with a backfill and mixed-version matrix. The postmortem should add a concrete compatibility gate and ownership policy, not merely a reminder to coordinate.

## Final integrated assessment

Design ShopStream for an assumed 2,000 peak API requests/second, 100 checkout requests/second, and 200 inference requests/second. A region can fail, a payment response can disappear, an old app version can remain during rollout, and one tenant can submit a large batch. Choose explicit freshness, availability, RPO, RTO, latency, and cost objectives. State what is excluded and identify assumptions needing measurement.

**Required submission:** Produce requirements, estimates with units, three architecture views, API contracts, schemas and invariants, cache policy, admission/retry/deadline policy, order Saga, inference scheduling, migration and rollout plan, security boundaries, telemetry, recovery plan, and one incident runbook. Include a test that falsifies each critical correctness claim.

**Model solution outline:** Begin with a modular transactional order core. Use an idempotent provider operation and reconciliation for ambiguous payment outcomes. Cache only permitted catalog/prediction representations with versioned scoped keys. Bound API and inference work independently, reserving interactive capacity. Use a durable outbox and idempotent consumers for notifications and jobs. Keep schema changes additive through mixed-version operation. Put identity and object authorization at explicit boundaries, rotate secrets, and protect every required transport hop. Measure pool wait, queue age, P99, user success, model quality, and cost separately. Select a regional ownership model with fencing and enough failover capacity, then demonstrate restoration and reconciliation against the chosen RPO/RTO.

**Scoring rubric (100 points):** Requirements and assumptions 10; capacity arithmetic 10; data invariants and transaction boundaries 15; failure handling and recovery 15; security and privacy 10; performance and backpressure 10; deployment compatibility 10; observability and operations 10; trade-offs and test evidence 10. A design that claims exactly-once arbitrary external effects, uses a cache as the sole payment authority, or omits cross-tenant authorization must be corrected before it can pass, regardless of the diagram quality.

**Expert follow-up:** Remove one of your assumptions: clocks are less accurate, one region has stale data, the provider shortens idempotency retention, or the new model doubles output length. Revisit the affected contract, arithmetic, and mitigation. A strong answer changes the design or states the weaker guarantee; it does not repeat the original component list.
