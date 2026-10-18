# Quick Revision

Use after studying the full topic. These notes intentionally omit the depth, diagrams, and exercises in the textbook.

## 1. Rate Limiting

Rate limiting decides how much work one caller may submit during a period.

**Mechanism:** Identify an authenticated tenant and operation, not an easily spoofed header.

**Trade-off:** Fixed windows are cheap but allow boundary bursts.

**Trap:** Keying every user by proxy IP unfairly groups them.

**Recall test:** Simulate a burst at t=0 and another at t=0.5; expect 5 then 1 accepted.

**Full topic:** [1. Rate Limiting](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-001).

## 2. Caching

A cache keeps a reusable copy near the reader.

**Mechanism:** Construct keys from every input that changes the result: tenant, product, locale, permissions where necessary, and model version for predictions.

**Trade-off:** Local caches are fast but diverge across processes.

**Trap:** A cache outage can send all traffic to an origin sized for misses.

**Recall test:** Run the TTL demo, advance its fake clock, and count origin calls.

**Full topic:** [2. Caching](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-002).

## 3. Load Balancing

A load balancer distributes incoming work among eligible servers.

**Mechanism:** Discover backends, evaluate health, select one, establish or reuse a connection, and forward traffic.

**Trade-off:** Sticky sessions reduce movement but concentrate load and complicate failover.

**Trap:** Retrying a POST blindly after backend timeout can duplicate an order.

**Recall test:** Route twelve requests round robin across three servers; expect four each.

**Full topic:** [3. Load Balancing](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-003).

## 4. Reverse Proxies

A reverse proxy accepts requests on behalf of an application server.

**Mechanism:** Accept the client connection, validate HTTP framing and size, terminate TLS if configured, choose an upstream, and forward a normalized request.

**Trade-off:** A forward proxy represents clients; a reverse proxy represents servers.

**Trap:** Mismatched parsers and ambiguous message framing can create request-smuggling risks.

**Recall test:** Draw the two independent TCP connections.

**Full topic:** [4. Reverse Proxies](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-004).

## 5. API Gateways

An API gateway applies shared API policies at a service boundary.

**Mechanism:** Authenticate credentials, validate their issuer and audience, derive a trusted principal, apply tenant quotas, route by a stable contract, and propagate a deadline and trace context.

**Trade-off:** A reverse proxy primarily mediates traffic; a gateway adds API policy and management.

**Trap:** Trusting unsigned identity headers lets direct callers impersonate users.

**Recall test:** Trace authentication and ownership as separate decisions.

**Full topic:** [5. API Gateways](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-005).

## 6. CI/CD

Continuous integration repeatedly combines changes and checks them.

**Mechanism:** Check out a fixed revision, resolve locked dependencies, run unit and integration tests, scan source and artifacts, build an image, record its digest and provenance, deploy to a test environment, verify behavior, then promote.

**Trade-off:** More gates catch more classes of defects but lengthen feedback.

**Trap:** Rebuilding after testing ships different bytes.

**Recall test:** Run tests against a fixed commit and record an artifact hash.

**Full topic:** [6. CI/CD](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-006).

## 7. Docker

A container packages an application's user-space dependencies and runs an isolated process.

**Mechanism:** Docker builds layered filesystem snapshots from a Dockerfile.

**Trade-off:** Virtual machines isolate kernels and support different guest operating systems; containers generally start with less overhead but share the host kernel.

**Trap:** Putting secrets in a build argument or copied file can leave them in image layers.

**Recall test:** Build and inspect the supplied Dockerfile.

**Full topic:** [7. Docker](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-007).

## 8. Kubernetes

Kubernetes continually tries to make running workloads match declared desired state.

**Mechanism:** The API server stores accepted objects through the control plane.

**Trade-off:** A simple VM or managed application platform can be easier for a small service.

**Trap:** Omitting requests distorts scheduling.

**Recall test:** Render the supplied Deployment and Service, match labels by hand, and inspect resource budgets.

**Full topic:** [8. Kubernetes](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-008).

## 9. Service Discovery

Service discovery maps a logical service name to current reachable instances.

**Mechanism:** Instances register or controllers publish membership.

**Trade-off:** Server-side discovery centralizes routing in a proxy.

**Trap:** Treating DNS TTL as an exact global cutover timer ignores application and resolver caches.

**Recall test:** Replace one logical endpoint and trace which caches retain it.

**Full topic:** [9. Service Discovery](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-009).

## 10. Circuit Breakers

A circuit breaker stops repeatedly calling a dependency that is likely to fail.

**Mechanism:** In closed state, forward calls and record eligible failures.

**Trade-off:** Retries seek success by repeating attempts; breakers reduce attempts when failure is sustained.

**Trap:** Counting user validation errors as provider failures opens the breaker unnecessarily.

**Recall test:** Run the fake-clock state transition demo.

**Full topic:** [10. Circuit Breakers](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-010).

## 11. Timeouts

A timeout limits how long a caller waits.

**Mechanism:** Establish an end-to-end deadline using a monotonic clock.

**Trade-off:** Short timeouts reduce resource occupancy but increase false failures.

**Trap:** A read timeout that resets after every byte permits an arbitrarily long total transfer.

**Recall test:** Allocate a 1-second deadline across three sequential calls.

**Full topic:** [11. Timeouts](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-011).

## 12. Retries

A retry repeats an operation after a failure that might be temporary.

**Mechanism:** Classify the failure, establish whether replay is safe, check total deadline and attempt budget, wait with jitter, then repeat using the same logical operation ID.

**Trade-off:** Retries improve availability for independent transient failures but amplify sustained overload.

**Trap:** Infinite retries make outages self-sustaining.

**Recall test:** Simulate one transient failure followed by success and verify two attempts.

**Full topic:** [12. Retries](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-012).

## 13. Exponential Backoff

Exponential backoff increases the delay between repeated attempts.

**Mechanism:** For retry index k starting at zero, calculate cap_k=min(max_delay,base*2**k).

**Trade-off:** Fixed delay is simple and useful for predictable polling but can synchronize clients.

**Trap:** Adding tiny random noise to a huge common delay may leave a retry herd.

**Recall test:** Print seeded retry delays and verify each lies within its window.

**Full topic:** [13. Exponential Backoff](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-013).

## 14. Idempotency

An idempotent operation has the same intended effect when repeated as when performed once.

**Mechanism:** Accept a client-generated operation key scoped to tenant and endpoint.

**Trade-off:** Idempotency differs from deduplication by time or payload similarity.

**Trap:** Checking then inserting without a uniqueness constraint races.

**Recall test:** Run concurrent attempts with the same key and assert one order row.

**Full topic:** [14. Idempotency](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-014).

## 15. Message Queues

A message queue stores work until a consumer can process it.

**Mechanism:** Publish durably according to broker guarantees, deliver to a consumer, reserve or hide it for a visibility interval, process the side effect, then acknowledge.

**Trade-off:** At-most-once avoids redelivery but can lose work.

**Trap:** Acknowledging before committing loses work on crash.

**Recall test:** Simulate acknowledgment loss and verify local deduplication.

**Full topic:** [15. Message Queues](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-015).

## 16. Pub/Sub

Publish/subscribe sends an event to multiple independently interested subscribers.

**Mechanism:** Publish an event to a topic, route it to subscriptions, retain it according to policy, and let each subscriber track its own progress.

**Trade-off:** A work queue typically assigns one job to one consumer in a group.

**Trap:** Assuming all subscribers are atomic creates false business guarantees.

**Recall test:** Deliver one event to two subscriptions and assert two independent outcomes.

**Full topic:** [16. Pub/Sub](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-016).

## 17. Event-Driven Architecture

An event-driven system reacts to recorded facts instead of coordinating every action through direct calls.

**Mechanism:** Commit domain state and an outbox row in the same local transaction.

**Trade-off:** Events support asynchronous fanout and independent scaling.

**Trap:** Writing the database then publishing without an outbox loses events between the two steps.

**Recall test:** Crash a relay after publish and verify one inventory change.

**Full topic:** [17. Event-Driven Architecture](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-017).

## 18. Distributed Transactions

A distributed transaction coordinates changes across multiple transactional participants.

**Mechanism:** In two-phase commit, a coordinator asks participants to prepare.

**Trade-off:** A single-database transaction is usually simpler and should be preferred where the data boundary permits it.

**Trap:** Calling two REST APIs inside a local SQL transaction does not create a distributed transaction.

**Recall test:** Write a prepare/commit timeline for two participants.

**Full topic:** [18. Distributed Transactions](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-018).

## 19. Saga Pattern

A Saga implements a business workflow as local transactions with compensating actions.

**Mechanism:** Persist a workflow ID and current state.

**Trade-off:** Sagas avoid long cross-service locks and accommodate heterogeneous APIs.

**Trap:** Treating compensation as guaranteed success leaves stuck workflows.

**Recall test:** Simulate payment decline and assert inventory is released once.

**Full topic:** [19. Saga Pattern](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-019).

## 20. Dead Letter Queues

A dead letter queue isolates messages that cannot be processed under the normal retry policy.

**Mechanism:** Classify permanent and transient errors, record attempts, and move exhausted messages with their original IDs, timestamps, payload version, and sanitized error metadata.

**Trade-off:** Immediate rejection is suitable for invalid synchronous requests.

**Trap:** A DLQ without an owner becomes a hidden data-loss sink.

**Recall test:** Fail a job three times and inspect its terminal metadata.

**Full topic:** [20. Dead Letter Queues](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-020).

## 21. Cron Jobs

Cron-style scheduling starts work according to time rules.

**Mechanism:** Evaluate the schedule in an explicit timezone, create a run identity from job and business interval, acquire bounded ownership, and record completion.

**Trade-off:** Fixed-interval timers are useful for local maintenance; durable schedulers recover missed runs.

**Trap:** Local daylight-saving changes can skip or repeat wall-clock times.

**Recall test:** Simulate two triggers for one date and assert one result.

**Full topic:** [21. Cron Jobs](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-021).

## 22. WebSockets

WebSockets provide a long-lived bidirectional message channel.

**Mechanism:** Establish an authenticated HTTP upgrade where applicable, then exchange framed messages.

**Trade-off:** SSE suits server-to-browser streams with simpler HTTP semantics.

**Trap:** Unbounded buffers let a slow client exhaust memory.

**Recall test:** Specify message IDs and acknowledgments for chat.

**Full topic:** [22. WebSockets](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-022).

## 23. Long Polling

Long polling holds an HTTP request until an update arrives or a server timeout ends it.

**Mechanism:** Send a last-seen cursor, register a bounded waiter, check for newer events without a race, and return events or an empty timeout response.

**Trade-off:** Short polling is simpler but adds latency or excessive requests.

**Trap:** Keeping only ephemeral notifications loses updates in the reconnect gap.

**Recall test:** Deliver an event between successive requests and verify the cursor recovers it.

**Full topic:** [23. Long Polling](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-023).

## 24. Server-Sent Events

Server-sent events stream text events from a server to a browser over HTTP.

**Mechanism:** Return text/event-stream, format events with data fields and optional IDs, terminate each event with a blank line, and flush intentionally.

**Trade-off:** SSE is convenient for one-way status and token streams.

**Trap:** Writing bytes without correct blank-line framing leaves the browser waiting.

**Recall test:** Parse the supplied event stream and verify IDs and multiline data.

**Full topic:** [24. Server-Sent Events](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-024).

## 25. Database Indexing

An index is a searchable structure that helps a database find rows without examining every row.

**Mechanism:** B-tree indexes organize sorted keys in balanced pages, supporting equality, ranges, and ordering.

**Trade-off:** More indexes improve selected reads but increase writes, storage, vacuum work, and cache pressure.

**Trap:** Indexing every column wastes resources.

**Recall test:** Run the PostgreSQL query-plan lab on generated orders.

**Full topic:** [25. Database Indexing](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-025).

## 26. Query Optimization

Query optimization reduces the work needed to produce a correct database result.

**Mechanism:** Capture a representative slow query and parameters.

**Trade-off:** Optimizing one query may increase write cost or memory use.

**Trap:** EXPLAIN costs are not milliseconds.

**Recall test:** Compare estimated and actual rows in the SQL lab.

**Full topic:** [26. Query Optimization](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-026).

## 27. N+1 Queries

N+1 occurs when one query fetches a list and another query runs for each list item.

**Mechanism:** Instrument query count per request.

**Trade-off:** Joins let the database optimize relationships.

**Trap:** Caching masks N+1 in warm tests but leaves cold requests slow.

**Recall test:** Count queries for 1, 10, and 100 parent rows; linear growth reveals the pattern.

**Full topic:** [27. N+1 Queries](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-027).

## 28. Connection Pooling

A connection pool reuses a bounded set of database connections.

**Mechanism:** Acquire a connection with a timeout, execute a short transaction, commit or roll back, and release in a guaranteed cleanup path.

**Trade-off:** Session pooling preserves connection-specific state.

**Trap:** Leaked connections eventually block every caller.

**Recall test:** Calculate the maximum aggregate connection count during a 25% rollout surge.

**Full topic:** [28. Connection Pooling](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-028).

## 29. Read Replicas

A read replica serves a copy of database data to offload reads.

**Mechanism:** The primary writes a replication log.

**Trade-off:** Replicas scale some reads and support recovery but do not generally increase primary write throughput.

**Trap:** Round-robin reads can make a user see data go backward.

**Recall test:** Write then immediately read from a delayed replica simulation.

**Full topic:** [29. Read Replicas](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-029).

## 30. Sharding

Sharding splits a dataset across independently hosted partitions.

**Mechanism:** Choose a key aligned with common transactions, map keys to shards through ranges, hashes, or a directory, and route requests accordingly.

**Trade-off:** Replication copies the same data; sharding divides it.

**Trap:** A timestamp key concentrates new writes in the newest range.

**Recall test:** Distribute sample tenant keys and measure skew.

**Full topic:** [30. Sharding](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-030).

## 31. Partitioning

Partitioning divides a logical table or dataset into smaller pieces using a rule.

**Mechanism:** Define range, list, or hash bounds, route inserts, and let queries prune irrelevant partitions when predicates expose the partition key.

**Trade-off:** Partitioning improves manageability and some query patterns.

**Trap:** Missing the next month's partition can reject inserts.

**Recall test:** Create monthly partitions in the SQL lab and inspect pruning.

**Full topic:** [31. Partitioning](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-031).

## 32. Replication

Replication maintains copies of data on multiple machines.

**Mechanism:** Capture committed changes in a log, transmit them, apply them in order within the guaranteed domain, and track durable progress.

**Trade-off:** Synchronous and asynchronous replication trade acknowledgment latency, availability, and possible data loss.

**Trap:** Assuming every copy is current creates stale reads.

**Recall test:** Pause replication, commit a write, and inspect divergence in a simulation.

**Full topic:** [32. Replication](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-032).

## 33. Leader Election

Leader election chooses a coordinator among replicas.

**Mechanism:** In a quorum-based consensus protocol, nodes use election timeouts, increasing terms, durable votes, and log freshness checks.

**Trade-off:** A coordination service can provide election primitives, but a simplistic lock is not a complete consensus algorithm.

**Trap:** Electing the node with the fastest clock is unsafe.

**Recall test:** Enumerate all majorities of three nodes and show intersection.

**Full topic:** [33. Leader Election](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-033).

## 34. CAP Theorem

CAP explains a limit during a network partition: a distributed service cannot guarantee both linearizable behavior and a response for every request to a nonfailed node under the theorem's assumptions.

**Mechanism:** Model a register with reads and writes.

**Trade-off:** CAP consistency means linearizability, not every possible meaning of consistency or ACID's C.

**Trap:** Saying a system is CA because partitions are rare ignores the failure case.

**Recall test:** Draw a two-region partition and place one write on A.

**Full topic:** [34. CAP Theorem](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-034).

## 35. Eventual Consistency

Eventual consistency allows replicas to differ temporarily but requires convergence under appropriate delivery and update assumptions.

**Mechanism:** Propagate changes through logs or events, identify entities and versions, apply a defined merge rule, and repair missed updates.

**Trade-off:** Stronger consistency simplifies some reasoning but may add coordination latency or reduce availability under partition.

**Trap:** Last-write-wins based on unsynchronized wall clocks can lose a valid update.

**Recall test:** Deliver versions 1, 3, 2 and verify the projection ends at 3.

**Full topic:** [35. Eventual Consistency](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-035).

## 36. Optimistic Locking

Optimistic locking lets concurrent readers proceed, then checks whether data changed before accepting a write.

**Mechanism:** Read a row and version, compute the proposed change, then atomically UPDATE with WHERE id=?

**Trade-off:** Optimistic checks work well with infrequent conflicts and short write operations.

**Trap:** Reading then writing the version in separate unguarded operations races.

**Recall test:** Run two updates against the same version and assert one success.

**Full topic:** [36. Optimistic Locking](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-036).

## 37. Pessimistic Locking

Pessimistic locking reserves access before changing shared data.

**Mechanism:** Start a transaction, acquire the required row locks such as SELECT FOR UPDATE, inspect current values, perform changes, and commit promptly.

**Trade-off:** Locking prevents certain concurrent interference but adds waiting and deadlock risk.

**Trap:** Calling a payment provider while holding inventory locks creates long contention chains.

**Recall test:** Use two SQL sessions to reserve the last unit.

**Full topic:** [37. Pessimistic Locking](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-037).

## 38. Distributed Locks

A distributed lock coordinates exclusive work across processes or machines.

**Mechanism:** Acquire ownership atomically with a unique owner ID and expiry.

**Trade-off:** A database transaction or unique constraint often protects an invariant more directly.

**Trap:** Unconditionally deleting a lock can remove another worker's renewed ownership.

**Recall test:** Simulate A pausing past lease expiry and B taking over.

**Full topic:** [38. Distributed Locks](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-038).

## 39. Race Conditions

A race condition occurs when correctness depends on the timing of concurrent operations.

**Mechanism:** Identify shared mutable state and the invariant.

**Trade-off:** Data races refer more narrowly to unsynchronized memory access under a language's memory model.

**Trap:** Testing only sequentially misses the bug.

**Recall test:** Force two readers to observe the same initial stock with a barrier.

**Full topic:** [39. Race Conditions](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-039).

## 40. Deadlocks

A deadlock is a cycle of operations waiting for resources held by one another.

**Mechanism:** Build a wait-for graph: an edge points from a waiting transaction to the holder it needs.

**Trade-off:** A long lock wait is not necessarily a deadlock; its holder may eventually finish.

**Trap:** Retrying only the last SQL statement after transaction abort is incorrect.

**Recall test:** Construct the two-row cycle in an isolated database.

**Full topic:** [40. Deadlocks](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-040).

## 41. Memory Leaks

A memory leak is retained memory that the program no longer needs.

**Mechanism:** Establish a steady workload and track heap, process resident memory, allocation rate, and object counts over time.

**Trade-off:** A leak differs from a legitimate large working set, allocator fragmentation, or a temporary spike.

**Trap:** Watching only language heap misses native buffers and GPU allocations.

**Recall test:** Run the bounded-versus-unbounded retention demo and compare traced allocations.

**Full topic:** [41. Memory Leaks](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-041).

## 42. Garbage Collection

Garbage collection reclaims memory that a program can no longer reach.

**Mechanism:** A tracing collector starts from roots such as stacks and globals, marks reachable objects, and reclaims unmarked ones.

**Trade-off:** Automatic collection improves safety but consumes CPU and may introduce pauses.

**Trap:** Calling collect on every request can worsen latency.

**Recall test:** Create a reference cycle and inspect reclamation in the Python lab.

**Full topic:** [42. Garbage Collection](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-042).

## 43. Thread Safety

Thread-safe code preserves its contract when several threads call it concurrently.

**Mechanism:** Define shared state and its invariant.

**Trade-off:** Threads share memory and suit some I/O workloads.

**Trap:** Holding a lock during slow network I/O serializes unrelated requests.

**Recall test:** Protect a compound cache initialization and count actual constructions.

**Full topic:** [43. Thread Safety](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-043).

## 44. Backpressure

Backpressure makes a slow downstream stage constrain upstream production.

**Mechanism:** Bound queue length, in-flight requests, and per-client buffers.

**Trade-off:** Rate limits bound arrivals over time; backpressure reacts to current capacity.

**Trap:** Unbounded asyncio tasks move the queue into memory.

**Recall test:** Run the queue-growth simulation and calculate time to fill.

**Full topic:** [44. Backpressure](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-044).

## 45. Autoscaling

Autoscaling changes capacity in response to demand or schedules.

**Mechanism:** Choose a workload-related signal, target utilization or backlog per worker, calculate desired capacity, respect minimum/maximum bounds, and stabilize scale-down.

**Trade-off:** Reactive scaling follows observed demand; scheduled scaling anticipates known peaks.

**Trap:** Scaling on high latency alone can worsen an overloaded database.

**Recall test:** Calculate replicas from arrival rate and measured service rate, then add failure headroom.

**Full topic:** [45. Autoscaling](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-045).

## 46. Horizontal Scaling

Horizontal scaling adds machines or process instances.

**Mechanism:** Externalize durable state, make requests safely repeatable, distribute traffic, partition or coordinate background work, and cap aggregate dependency usage.

**Trade-off:** Horizontal scaling offers fault isolation and incremental capacity but adds distributed coordination.

**Trap:** Local file uploads disappear from requests routed to another replica.

**Recall test:** Model throughput with a shared database ceiling.

**Full topic:** [46. Horizontal Scaling](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-046).

## 47. Vertical Scaling

Vertical scaling gives one machine more CPU, memory, storage performance, or accelerator capacity.

**Mechanism:** Profile the limiting resource, choose a larger resource class, estimate migration or restart impact, and benchmark the representative workload.

**Trade-off:** Vertical scaling simplifies state and operations but has finite ceilings and may preserve a large failure domain.

**Trap:** Buying more CPU for lock contention wastes money.

**Recall test:** Match CPU, memory, disk, and lock bottlenecks to suitable interventions.

**Full topic:** [47. Vertical Scaling](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-047).

## 48. CDN

A content delivery network serves content from geographically distributed edge locations.

**Mechanism:** DNS or another routing mechanism selects an edge.

**Trade-off:** A CDN includes delivery infrastructure and routing; edge caching is one function.

**Trap:** Ignoring query strings or authorization context can leak private data.

**Recall test:** Classify public images, account pages, and signed downloads by cacheability.

**Full topic:** [48. CDN](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-048).

## 49. Edge Caching

Edge caching stores reusable responses near users.

**Mechanism:** Define cacheability, key dimensions, TTL, revalidation, and stale behavior.

**Trade-off:** Browser caches serve one client context, shared edge caches serve many users, and application caches store internal objects.

**Trap:** Caching errors for too long prolongs incidents.

**Recall test:** Design a key for a localized product page.

**Full topic:** [49. Edge Caching](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-049).

## 50. Cache Invalidation

Cache invalidation removes or supersedes copies after their source changes.

**Mechanism:** Choose TTL expiry, explicit delete, versioned keys, write-through, or event-driven invalidation.

**Trade-off:** TTL provides simple bounded refresh behavior under stated assumptions.

**Trap:** Broadcasting invalidations without delivery monitoring creates silent divergence.

**Recall test:** Reproduce the delayed-reader race with controlled barriers.

**Full topic:** [50. Cache Invalidation](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-050).

## 51. Feature Flags

A feature flag chooses behavior at runtime without rebuilding the application.

**Mechanism:** Define an owner, purpose, default, expiry, and targeting rule.

**Trade-off:** Deployment controls which code is present; flags control which behavior runs.

**Trap:** Randomly selecting per request creates inconsistent user experiences.

**Recall test:** Assign stable cohorts in the algorithms lab.

**Full topic:** [51. Feature Flags](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-051).

## 52. Blue-Green Deployment

Blue-green deployment maintains two application environments and switches traffic from the current one to a prepared replacement.

**Mechanism:** Build one immutable artifact, deploy green, apply backward-compatible schema expansion, warm dependencies, run checks, switch a controlled portion or all routing, and drain blue.

**Trade-off:** Blue-green can switch quickly and isolate application changes but may require near-double capacity.

**Trap:** Forgetting long-lived connections leaves old traffic active.

**Recall test:** Draw blue and green sharing a database.

**Full topic:** [52. Blue-Green Deployment](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-052).

## 53. Canary Releases

A canary release exposes a change to a limited population before broad rollout.

**Mechanism:** Define eligibility and stable assignment, deploy the candidate, compare it with a control over equivalent traffic, and monitor error, latency, saturation, and business outcomes.

**Trade-off:** Canary reduces blast radius but increases comparison and routing complexity.

**Trap:** Comparing different customer populations creates confounding.

**Recall test:** Define three guardrails and a minimum sample for checkout.

**Full topic:** [53. Canary Releases](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-053).

## 54. Rolling Deployments

A rolling deployment replaces application instances gradually.

**Mechanism:** Define desired replicas, maximum unavailable capacity, and allowed surge.

**Trade-off:** Rolling updates use less duplicate capacity than full blue-green but take longer and produce mixed versions.

**Trap:** Readiness passing before model loading completes sends traffic too early.

**Recall test:** Calculate peak Pods and connection budget for a surge.

**Full topic:** [54. Rolling Deployments](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-054).

## 55. Rollbacks

A rollback returns a system to a previously acceptable state after a harmful change.

**Mechanism:** Define rollback triggers and an owner before release.

**Trade-off:** Rollback can be fast when changes are reversible.

**Trap:** Automatically reverting on a noisy single metric can oscillate versions.

**Recall test:** Classify three changes as reversible, conditionally reversible, or irreversible.

**Full topic:** [55. Rollbacks](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-055).

## 56. Health Checks

A health check is a targeted observation used to decide whether a component can perform a particular role.

**Mechanism:** Define the consumer and action for each check: restart, route, alert, or synthetic validation.

**Trade-off:** Black-box checks observe outcomes from outside.

**Trap:** A database outage causing every liveness probe to fail restarts healthy applications and worsens recovery.

**Recall test:** Define separate live, ready, and synthetic checks.

**Full topic:** [56. Health Checks](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-056).

## 57. Liveness and Readiness Probes

Liveness asks whether restarting a container may help it recover.

**Mechanism:** Kubelet executes configured probes with periods, deadlines, and failure thresholds.

**Trade-off:** Process status, Pod phase, readiness, and application success are distinct.

**Trap:** Too-small timeouts under CPU throttling create false failures.

**Recall test:** Read the supplied probe values and compute the approximate startup allowance.

**Full topic:** [57. Liveness and Readiness Probes](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-057).

## 58. Monitoring

Monitoring continuously checks known indicators of service behavior.

**Mechanism:** Define user journeys, collect service and resource signals, label them with bounded dimensions, aggregate over explicit windows, visualize trends, and connect actionable conditions to runbooks.

**Trade-off:** Monitoring answers anticipated questions.

**Trap:** Collecting hundreds of dashboards without ownership creates noise.

**Recall test:** Build a four-signal dashboard specification for checkout.

**Full topic:** [58. Monitoring](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-058).

## 59. Logging

Logs are timestamped records of events and decisions.

**Mechanism:** Emit structured records with event name, severity, service version, trace ID, operation ID, and sanitized error category.

**Trade-off:** Logs offer detailed context but cost storage and query time.

**Trap:** Logging entire request bodies leaks credentials and increases cost.

**Recall test:** Emit and parse a structured event in the lab.

**Full topic:** [59. Logging](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-059).

## 60. Distributed Tracing

Distributed tracing follows one operation through several components.

**Mechanism:** Create a trace with spans for meaningful operations.

**Trade-off:** Metrics find population trends, logs explain events, and traces connect paths.

**Trap:** Missing propagation creates disconnected traces.

**Recall test:** Build a trace tree from the lab events and locate the critical path.

**Full topic:** [60. Distributed Tracing](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-060).

## 61. Metrics

Metrics summarize measurements over time.

**Mechanism:** Use counters for cumulative events, gauges for current values, and histograms for distributions.

**Trade-off:** Counters preserve event totals but need rate windows.

**Trap:** User IDs as labels create a time series per user and can exhaust storage.

**Recall test:** Compute success ratio and retry amplification from lab counters.

**Full topic:** [61. Metrics](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-061).

## 62. Alerts

An alert asks a person or automation to act on a condition.

**Mechanism:** Define the symptom, affected population, severity, threshold, time window, owner, and runbook.

**Trade-off:** Symptom alerts reveal user impact.

**Trap:** Paging on every CPU spike creates fatigue.

**Recall test:** Write a page and a ticket condition for checkout.

**Full topic:** [62. Alerts](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-062).

## 63. SLOs

A service level objective is a measurable target for user-facing service behavior over a defined window.

**Mechanism:** Identify a user journey, choose an SLI, define good and eligible events, set the target and window, and document exclusions narrowly.

**Trade-off:** Tighter targets can require more redundancy, slower changes, and higher cost.

**Trap:** Excluding all overloaded requests makes the SLO look good by hiding real harm.

**Recall test:** Write a complete checkout SLO with numerator, denominator, window, target, and owner.

**Full topic:** [63. SLOs](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-063).

## 64. SLIs

A service level indicator measures a property users care about.

**Mechanism:** Define eligible events, a good-event predicate, observation point, aggregation window, and data-quality checks.

**Trade-off:** A metric is any measurement; an SLI is selected to represent service quality.

**Trap:** Counting only completed requests excludes hung requests unless deadlines are accounted for.

**Recall test:** Define good and eligible checkout events.

**Full topic:** [64. SLIs](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-064).

## 65. Error Budgets

An error budget is the amount of unreliability allowed by an SLO.

**Mechanism:** Compute allowed bad fraction as 1-target.

**Trade-off:** Request-based budgets weight traffic volume; time-based budgets weight elapsed intervals.

**Trap:** Treating the budget as only a dashboard produces no operational change.

**Recall test:** Compute burn and remaining budget from sample counters.

**Full topic:** [65. Error Budgets](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-065).

## 66. Observability

Observability is the ability to infer useful internal state from a system's outputs.

**Mechanism:** Instrument boundaries and state transitions with shared operation IDs, stable service and release metadata, bounded metrics, contextual logs, and propagated traces.

**Trade-off:** Monitoring checks known conditions.

**Trap:** Telemetry without release IDs makes change correlation difficult.

**Recall test:** Diagnose the pool-wait scenario with three competing hypotheses.

**Full topic:** [66. Observability](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-066).

## 67. Secrets Management

Secrets management controls sensitive credentials throughout their lifecycle.

**Mechanism:** Prefer workload identity and short-lived credentials where supported.

**Trade-off:** Environment variables are convenient but can leak through diagnostics or process inspection.

**Trap:** Copying a secret into a Docker layer or log preserves it after later deletion.

**Recall test:** Run the redaction test.

**Full topic:** [67. Secrets Management](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-067).

## 68. IAM

Identity and access management determines who or what can do which actions on which resources.

**Mechanism:** Authenticate a human or workload, evaluate policy using principal, action, resource, and context, and deny by default when no grant applies.

**Trade-off:** RBAC groups permissions by role; ABAC evaluates attributes and can express finer context at greater policy complexity.

**Trap:** Broad wildcard permissions expand compromise impact.

**Recall test:** Build a principal-action-resource matrix for buyers, sellers, support, and workers.

**Full topic:** [68. IAM](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-068).

## 69. OAuth

OAuth enables delegated authorization: an application obtains limited access to a resource without receiving the user's password for that resource.

**Mechanism:** In authorization-code flow with PKCE, the client creates a verifier and sends its derived challenge with the authorization request.

**Trade-off:** Authentication asks who the user is; OAuth authorization asks what delegated access is granted.

**Trap:** Loose redirect matching enables token/code leakage.

**Recall test:** Draw every participant and message in code plus PKCE flow.

**Full topic:** [69. OAuth](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-069).

## 70. JWT Rotation

JWT rotation can refer to replacing signing keys or rotating refresh credentials; these are distinct mechanisms.

**Mechanism:** Publish a new verification key before issuing tokens signed by its key ID.

**Trade-off:** Short-lived access tokens bound exposure but do not provide instant revocation by themselves.

**Trap:** Trusting an arbitrary token-provided key URL enables key substitution or SSRF.

**Recall test:** Write a signing-key overlap timeline.

**Full topic:** [70. JWT Rotation](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-070).

## 71. TLS

TLS protects a connection against eavesdropping and tampering while authenticating the server, and optionally the client.

**Mechanism:** The client connects, negotiates supported protocol parameters, validates the certificate chain and hostname, performs a key exchange, and derives traffic keys.

**Trade-off:** TLS provides transport protection, not encryption of database files or end-to-end confidentiality across terminating proxies.

**Trap:** Disabling certificate verification to fix a deployment removes the identity guarantee.

**Recall test:** Use a standard client with verification enabled.

**Full topic:** [71. TLS](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-071).

## 72. Encryption at Rest

Encryption at rest protects stored data against certain forms of unauthorized storage access.

**Mechanism:** Use established storage encryption or authenticated application-level encryption where required.

**Trade-off:** Disk encryption is transparent and protects lost media.

**Trap:** Encrypting production storage but leaving plaintext exports or logs creates gaps.

**Recall test:** Draw data keys and wrapping keys separately.

**Full topic:** [72. Encryption at Rest](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-072).

## 73. Encryption in Transit

Encryption in transit protects data while it moves between endpoints.

**Mechanism:** Inventory communication paths, use authenticated transport protocols, validate peer identities, manage certificates or credentials, and prevent insecure fallback.

**Trade-off:** TLS protects transport endpoints.

**Trap:** Encrypting without validating peer identity can still permit interception.

**Recall test:** Mark every decrypting endpoint in the ShopStream architecture.

**Full topic:** [73. Encryption in Transit](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-073).

## 74. WAF

A web application firewall inspects HTTP traffic and applies protective rules.

**Mechanism:** Place the WAF at an authorized traffic boundary, normalize requests, evaluate managed and custom rules, and choose allow, block, challenge, or log actions.

**Trade-off:** A WAF addresses application-layer request patterns.

**Trap:** Treating a blocked-request count as proof of safety ignores bypasses and false positives.

**Recall test:** Design a scoped rule in log-only mode for an isolated test route.

**Full topic:** [74. WAF](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-074).

## 75. DDoS Protection

Distributed denial-of-service protection preserves useful service during excessive malicious traffic.

**Mechanism:** Use upstream network protection, traffic filtering, CDN caching, connection limits, application admission control, and protected origin access.

**Trade-off:** Autoscaling absorbs some legitimate growth but may amplify cost during abuse.

**Trap:** Exposing an origin IP lets attackers bypass the CDN.

**Recall test:** Map bandwidth, connection, and expensive-query attacks to appropriate control layers.

**Full topic:** [75. DDoS Protection](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-075).

## 76. CORS

Cross-origin resource sharing is a browser mechanism that controls which origins may read selected cross-origin responses.

**Mechanism:** The browser compares origins, sends a preflight for certain methods or headers, and checks response access-control headers.

**Trade-off:** Same-origin policy restricts browser reading.

**Trap:** Returning whatever Origin was supplied with credentials enabled trusts every site.

**Recall test:** Evaluate two allowed origins and one lookalike in the security lab.

**Full topic:** [76. CORS](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-076).

## 77. CSRF

Cross-site request forgery tricks a user's browser into performing an unwanted action using automatically attached credentials, commonly cookies.

**Mechanism:** Use non-GET methods for state changes, bind an unpredictable CSRF token to the user's session or use a correctly signed double-submit design, validate it on mutations, and check Origin or Referer under a defined policy.

**Trade-off:** CORS controls response reading, not all request sending.

**Trap:** Putting a CSRF token only in a cookie that browsers attach automatically provides no independent proof.

**Recall test:** Run a constant-time token comparison test with missing and wrong tokens.

**Full topic:** [77. CSRF](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-077).

## 78. SQL Injection

SQL injection occurs when untrusted input changes the structure of a database command.

**Mechanism:** Use driver parameter binding for values, allowlists for identifiers or sort directions that cannot be parameterized as values, and narrowly scoped database roles.

**Trade-off:** Escaping strings manually is fragile and context-dependent.

**Trap:** Parameter placeholders cannot safely substitute arbitrary table names or ORDER BY fragments.

**Recall test:** Run the safe-query demo using an apostrophe and a harmless SQL-looking string.

**Full topic:** [78. SQL Injection](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-078).

## 79. XSS

Cross-site scripting occurs when untrusted content executes as script in a user's browser under a trusted site's origin.

**Mechanism:** Use context-appropriate output encoding, safe DOM APIs such as textContent for text, and maintained sanitization for allowed rich HTML.

**Trade-off:** Input validation limits acceptable data; output encoding protects a specific rendering context.

**Trap:** Using innerHTML for plain text creates a dangerous sink.

**Recall test:** Render a harmless markup-like review as text and verify the DOM contains no new element.

**Full topic:** [79. XSS](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-079).

## 80. SSRF

Server-side request forgery occurs when an attacker influences a server to request an unintended destination.

**Mechanism:** Prefer a fixed allowlist of required destinations and protocols.

**Trade-off:** Input validation is one layer; egress policy limits what a compromised or bypassed fetcher can reach.

**Trap:** Blocking only localhost misses private, link-local, IPv6, alternate encodings, and redirect paths.

**Recall test:** Run the strict allowlist validator on allowed and lookalike hosts.

**Full topic:** [80. SSRF](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-080).

## 81. Database Migrations

A database migration changes schema or data in a controlled versioned process.

**Mechanism:** Use expand-and-contract: add compatible schema, deploy code that tolerates both forms, backfill in bounded checkpointed batches, switch reads and writes after verification, then remove old schema only after old code and rollback requirements expire.

**Trade-off:** Schema migration differs from a bulk data repair, though both may share tooling.

**Trap:** One giant backfill transaction creates locks, replication lag, and large rollback work.

**Recall test:** Walk through the supplied expansion SQL.

**Full topic:** [81. Database Migrations](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-081).

## 82. Schema Versioning

Schema versioning tracks the structure and meaning of data exchanged or stored over time.

**Mechanism:** Identify schema version and owner, define optional/default behavior, validate compatibility in CI, and evolve through additive changes where possible.

**Trade-off:** Database migrations change physical or logical storage.

**Trap:** Making an optional field required breaks older producers.

**Recall test:** Write v1 and v2 order-event examples with explicit currency units.

**Full topic:** [82. Schema Versioning](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-082).

## 83. Disaster Recovery

Disaster recovery restores useful service after a major failure such as a lost region, corrupted database, or compromised environment.

**Mechanism:** Identify critical functions and dependencies.

**Trade-off:** Cold recovery costs less but takes longer.

**Trap:** Backups without restore tests give false confidence.

**Recall test:** Build a dependency-ordered recovery checklist.

**Full topic:** [83. Disaster Recovery](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-083).

## 84. Backups

A backup is a recoverable historical copy of data.

**Mechanism:** Choose full and incremental backups plus transaction-log retention where point-in-time recovery is supported.

**Trade-off:** Snapshots are fast but depend on storage and consistency guarantees.

**Trap:** A successful backup job does not prove a usable restore.

**Recall test:** Back up and restore the SQLite order lab, then compare row counts and invariants.

**Full topic:** [84. Backups](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-084).

## 85. Failover

Failover transfers service responsibility to another instance or site after failure.

**Mechanism:** Detect failure with multiple signals, decide authority through a safe coordination mechanism, fence the old owner, check candidate data freshness, promote, update routing, reconnect clients, and validate business operations.

**Trade-off:** Automatic failover reduces response time but can amplify false detection.

**Trap:** Equating timeout with confirmed death creates unsafe promotion.

**Recall test:** Draw a partition where both database hosts remain alive.

**Full topic:** [85. Failover](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-085).

## 86. Multi-Region Deployment

Multi-region deployment places service components in geographically separated areas.

**Mechanism:** Choose active-passive, partitioned ownership, or active-active per data and operation.

**Trade-off:** Active-passive simplifies write authority but pays for standby and may increase normal latency for distant users.

**Trap:** Both regions depending on one secret manager, DNS account, or payment integration preserves a global failure point.

**Recall test:** Assign home regions for orders and local replicas for catalog.

**Full topic:** [86. Multi-Region Deployment](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-086).

## 87. Chaos Engineering

Chaos engineering tests reliability hypotheses by introducing controlled failures.

**Mechanism:** State a measurable steady-state hypothesis, choose a realistic failure, establish baselines and blast radius, prepare abort conditions and rollback, inject the fault, observe user impact, then remove the fault and verify recovery.

**Trade-off:** Unit tests verify local logic; load tests explore capacity; chaos experiments explore behavior under failure.

**Trap:** Running an experiment while telemetry is broken makes impact unknown.

**Recall test:** Write a staging-only experiment for a slow payment dependency.

**Full topic:** [87. Chaos Engineering](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-087).

## 88. Cost Optimization

Cost optimization reduces spending while preserving required behavior.

**Mechanism:** Attribute costs to workloads and tenants, establish unit economics, identify idle capacity and dominant drivers, then test right-sizing, caching, batching, storage lifecycle, and commitment choices.

**Trade-off:** Reserved or committed capacity trades flexibility for pricing benefits under provider-specific terms.

**Trap:** Turning off replicas without testing failure capacity sacrifices availability.

**Recall test:** Calculate unit cost from a supplied workload and resource total.

**Full topic:** [88. Cost Optimization](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-088).

## 89. Cold Starts

A cold start is initialization work before an instance can serve useful requests.

**Mechanism:** Break startup into image transfer, runtime initialization, dependency import, network setup, model loading, and warmup.

**Trade-off:** Lazy initialization can shorten startup but moves delay to the first relevant request.

**Trap:** Downloading unverified model artifacts during every request is slow and unsafe.

**Recall test:** Time import, model setup, and first request separately in the toy API.

**Full topic:** [89. Cold Starts](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-089).

## 90. Serverless Limits

Serverless platforms manage execution infrastructure but impose resource and service quotas.

**Mechanism:** Inventory platform limits and adjustable quotas, estimate concurrent demand, bound request sizes and duration, externalize durable state, and design retry/idempotency behavior.

**Trade-off:** Serverless can reduce infrastructure management and suit bursty workloads.

**Trap:** Storing the only copy of a job result in ephemeral local storage loses it on replacement.

**Recall test:** Calculate concurrency with Little's Law.

**Full topic:** [90. Serverless Limits](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-090).

## 91. Latency

Latency is the elapsed time for an operation from a defined start to a defined finish.

**Mechanism:** Define the measurement boundary and clock.

**Trade-off:** Latency is time per operation; throughput is completed operations per time.

**Trap:** Comparing client and server timers with different boundaries yields false conclusions.

**Recall test:** Add the worked phase budget and identify the largest reducible part.

**Full topic:** [91. Latency](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-091).

## 92. Throughput

Throughput is the rate of completed useful work.

**Mechanism:** Define the work unit and success condition, measure arrivals and completions over explicit intervals, and track concurrency, queue length, and latency.

**Trade-off:** Batching may improve throughput by amortizing overhead while worsening individual latency.

**Trap:** Reporting only peak one-second throughput exaggerates sustainable capacity.

**Recall test:** Compute L for the numerical example.

**Full topic:** [92. Throughput](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-092).

## 93. P99 Latency

P99 latency is a percentile threshold: roughly 99% of measured operations finish at or below it under the chosen estimation convention.

**Mechanism:** Define the population, time window, success/failure inclusion, and percentile convention.

**Trade-off:** Median describes the middle, P95 and P99 describe progressively smaller tails, and maximum captures the single worst sample but is noisy.

**Trap:** Ten samples cannot characterize a stable one-percent tail.

**Recall test:** Run the distribution demo and verify 59.6 ms mean and 2,000 ms P99.

**Full topic:** [93. P99 Latency](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-093).

## 94. Tail Latency

Tail latency describes unusually slow operations at the high end of a distribution.

**Mechanism:** Measure high percentiles and correlate slow traces with queueing, garbage collection, locks, disk, network loss, cold starts, and workload skew.

**Trade-off:** Average optimization can leave tails unchanged.

**Trap:** Hedging every request during overload amplifies the cause.

**Recall test:** Compute the fanout probability in the lab.

**Full topic:** [94. Tail Latency](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-094).

## 95. Network Partitions

A network partition prevents some components from communicating while others remain reachable.

**Mechanism:** Detect missing communication using timeouts while recognizing uncertainty.

**Trade-off:** A partition differs from a process crash, packet loss, or high latency, although observations can look similar.

**Trap:** Promoting every isolated replica creates split brain.

**Recall test:** Draw a partial connectivity matrix for three services.

**Full topic:** [95. Network Partitions](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-095).

## 96. Clock Skew

Clock skew is disagreement between clocks.

**Mechanism:** Use wall time for human timestamps and monotonic clocks for local elapsed time.

**Trade-off:** NTP improves synchronization but does not create a perfect global clock.

**Trap:** Last-write-wins based solely on wall time can discard a later causal update.

**Recall test:** Simulate two machines with a three-minute offset and validate token behavior.

**Full topic:** [96. Clock Skew](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-096).

## 97. DNS

DNS maps names to records such as IP addresses and service information.

**Mechanism:** The application consults local and resolver caches.

**Trade-off:** DNS resolves names; load balancers route connections or requests.

**Trap:** Very low TTLs increase lookup load without guaranteeing immediate cutover.

**Recall test:** Trace a cold and cached lookup on paper.

**Full topic:** [97. DNS](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-097).

## 98. TCP vs UDP

TCP provides a reliable ordered byte stream with congestion and flow control.

**Mechanism:** TCP establishes connection state, numbers bytes, acknowledges reception, retransmits losses, controls sender rate, and presents an ordered stream without application message boundaries.

**Trade-off:** TCP is appropriate for many reliable transfers.

**Trap:** Assuming one send equals one TCP receive breaks framing.

**Recall test:** Frame two messages over a byte stream and simulate partial reads.

**Full topic:** [98. TCP vs UDP](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-098).

## 99. HTTP/2 and HTTP/3

HTTP/2 and HTTP/3 preserve HTTP request-response semantics while changing how messages share a connection.

**Mechanism:** HTTP/2 multiplexes framed streams over TCP and compresses headers with HPACK.

**Trade-off:** HTTP/1.1 often uses multiple connections for concurrency.

**Trap:** Claiming HTTP/3 eliminates all head-of-line blocking is too broad.

**Recall test:** Draw a lost segment under HTTP/2 and a lost QUIC stream packet under HTTP/3.

**Full topic:** [99. HTTP/2 and HTTP/3](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-099).

## 100. gRPC

gRPC is an RPC framework that lets clients call defined remote service methods using generated interfaces and structured messages.

**Mechanism:** Define services and messages, commonly in Protocol Buffers, generate client/server code, establish a channel, call methods with deadlines and metadata, and handle status codes.

**Trade-off:** JSON/HTTP is easy to inspect and broadly compatible with public clients. gRPC offers typed binary contracts and streaming at the cost of tooling and browser integration considerations.

**Trap:** Omitting deadlines lets calls wait too long.

**Recall test:** Read the supplied proto contract and identify unary versus streaming methods.

**Full topic:** [100. gRPC](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-100).

## 101. Webhooks

A webhook is an HTTP callback notifying another system that an event occurred.

**Mechanism:** Sign a canonical raw payload with a shared secret or supported asymmetric scheme, include event ID and timestamp, verify before parsing business actions, enforce replay policy, durably enqueue or record the event, and acknowledge promptly.

**Trade-off:** Webhooks push updates; polling pulls them.

**Trap:** Parsing and reserializing JSON before signature verification changes bytes.

**Recall test:** Run the HMAC verification and tamper tests.

**Full topic:** [101. Webhooks](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-101).

## 102. API Versioning

API versioning manages contract evolution for clients that cannot all upgrade at once.

**Mechanism:** Define the public contract: paths, methods, fields, units, errors, authorization, pagination, and semantics.

**Trade-off:** URL versions are visible and easy to route but duplicate endpoint surfaces.

**Trap:** Adding a required request field breaks old clients.

**Recall test:** Classify changes as additive, conditionally compatible, or breaking.

**Full topic:** [102. API Versioning](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-102).

## 103. Semantic Versioning

Semantic Versioning communicates intended compatibility through MAJOR.MINOR.PATCH for a declared public API.

**Mechanism:** Declare the public API.

**Trade-off:** Calendar versioning communicates release time rather than compatibility intent.

**Trap:** Calling a breaking behavior change a patch does not make it compatible.

**Recall test:** Assign versions to three concrete library changes.

**Full topic:** [103. Semantic Versioning](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-103).

## 104. Infrastructure as Code

Infrastructure as code expresses infrastructure configuration in reviewable files.

**Mechanism:** Declare desired resources, separate environments and variables, validate syntax and policy, preview changes, review destructive actions, apply through controlled identity, and detect drift.

**Trade-off:** Declarative tools reconcile desired state; imperative scripts specify steps.

**Trap:** Copying environments without isolating state can modify the wrong resources.

**Recall test:** Review the local Terraform plan without cloud resources.

**Full topic:** [104. Infrastructure as Code](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-104).

## 105. Terraform

Terraform is an infrastructure-as-code tool that compares configuration, recorded state, and provider observations to plan resource changes.

**Mechanism:** Initialize providers and backend, format and validate configuration, refresh observations as appropriate, build a plan, review it, and apply the selected plan through authorized credentials.

**Trade-off:** Terraform manages infrastructure lifecycle, while configuration-management tools often manage software inside hosts and Helm packages Kubernetes resources.

**Trap:** State can contain secrets even when output is marked sensitive.

**Recall test:** Run fmt, init, validate, and plan when Terraform is installed.

**Full topic:** [105. Terraform](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-105).

## 106. Helm Charts

A Helm chart packages parameterized Kubernetes manifests.

**Mechanism:** Define Chart.yaml, values, templates, and dependencies.

**Trade-off:** Helm packages and manages releases; plain manifests and Kustomize offer different configuration approaches.

**Trap:** Unquoted or poorly typed values can render invalid objects.

**Recall test:** Render the included chart with one and three replicas.

**Full topic:** [106. Helm Charts](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-106).

## 107. Build Caching

Build caching reuses outputs when their relevant inputs have not changed.

**Mechanism:** Identify build steps and their input graph.

**Trade-off:** Caching improves speed but consumes storage and adds invalidation complexity.

**Trap:** Restoring privileged caches from untrusted pull requests can introduce poisoned artifacts.

**Recall test:** Change application code and dependency inputs separately and predict layer reuse.

**Full topic:** [107. Build Caching](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-107).

## 108. Dependency Hell

Dependency hell occurs when required packages, versions, native libraries, or runtime assumptions conflict.

**Mechanism:** Declare direct dependencies, resolve the full graph, lock exact selected versions and integrity metadata, isolate environments, and test supported runtime/platform combinations.

**Trade-off:** Loose ranges ease updates but can drift.

**Trap:** Installing into a shared global environment makes unrelated projects affect each other.

**Recall test:** Build the optional API dependencies in a clean virtual environment.

**Full topic:** [108. Dependency Hell](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-108).

## 109. Production Incidents

A production incident is a disruption requiring coordinated response to reduce user harm.

**Mechanism:** Declare severity based on impact, appoint an incident commander, assign technical and communication roles, establish one timeline, and stop unrelated risky changes.

**Trade-off:** Symptoms are observed harm, contributing factors increase likelihood or severity, causes explain mechanisms, and remediation changes the system.

**Trap:** Restarting everything destroys evidence and can create a cold-start surge.

**Recall test:** Run the checkout incident tabletop with a timed evidence log.

**Full topic:** [109. Production Incidents](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-109).

## 110. On-Call

On-call is a structured responsibility for responding to urgent service problems.

**Mechanism:** Define primary and secondary responders, handoff expectations, escalation paths, severity policy, and access checks.

**Trade-off:** On-call is operational coverage; incident command is coordination during a specific event.

**Trap:** Pages without runbooks or access waste the most important minutes.

**Recall test:** Write a shift handoff with risks, ongoing incidents, and ownership.

**Full topic:** [110. On-Call](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-110).

## 111. Postmortems

A postmortem is a structured learning review after an incident.

**Mechanism:** Record impact, timeline, detection, response, technical mechanism, contributing factors, and what went well.

**Trade-off:** An incident report records events; a postmortem explains and improves the system.

**Trap:** Blaming one person discourages evidence sharing.

**Recall test:** Complete the supplied postmortem template for the migration incident.

**Full topic:** [111. Postmortems](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-111).
