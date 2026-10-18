# Glossary

The 111 topic entries retain the original topic numbers. Additional terms below support the mechanisms and case studies.

## Rate Limiting (1)

Rate limiting decides how much work one caller may submit during a period. See [1. Rate Limiting](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-001).

## Caching (2)

A cache keeps a reusable copy near the reader. See [2. Caching](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-002).

## Load Balancing (3)

A load balancer distributes incoming work among eligible servers. See [3. Load Balancing](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-003).

## Reverse Proxies (4)

A reverse proxy accepts requests on behalf of an application server. See [4. Reverse Proxies](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-004).

## API Gateways (5)

An API gateway applies shared API policies at a service boundary. See [5. API Gateways](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-005).

## CI/CD (6)

Continuous integration repeatedly combines changes and checks them. See [6. CI/CD](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-006).

## Docker (7)

A container packages an application's user-space dependencies and runs an isolated process. See [7. Docker](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-007).

## Kubernetes (8)

Kubernetes continually tries to make running workloads match declared desired state. See [8. Kubernetes](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-008).

## Service Discovery (9)

Service discovery maps a logical service name to current reachable instances. See [9. Service Discovery](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-009).

## Circuit Breakers (10)

A circuit breaker stops repeatedly calling a dependency that is likely to fail. See [10. Circuit Breakers](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-010).

## Timeouts (11)

A timeout limits how long a caller waits. See [11. Timeouts](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-011).

## Retries (12)

A retry repeats an operation after a failure that might be temporary. See [12. Retries](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-012).

## Exponential Backoff (13)

Exponential backoff increases the delay between repeated attempts. See [13. Exponential Backoff](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-013).

## Idempotency (14)

An idempotent operation has the same intended effect when repeated as when performed once. See [14. Idempotency](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-014).

## Message Queues (15)

A message queue stores work until a consumer can process it. See [15. Message Queues](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-015).

## Pub/Sub (16)

Publish/subscribe sends an event to multiple independently interested subscribers. See [16. Pub/Sub](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-016).

## Event-Driven Architecture (17)

An event-driven system reacts to recorded facts instead of coordinating every action through direct calls. See [17. Event-Driven Architecture](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-017).

## Distributed Transactions (18)

A distributed transaction coordinates changes across multiple transactional participants. See [18. Distributed Transactions](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-018).

## Saga Pattern (19)

A Saga implements a business workflow as local transactions with compensating actions. See [19. Saga Pattern](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-019).

## Dead Letter Queues (20)

A dead letter queue isolates messages that cannot be processed under the normal retry policy. See [20. Dead Letter Queues](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-020).

## Cron Jobs (21)

Cron-style scheduling starts work according to time rules. See [21. Cron Jobs](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-021).

## WebSockets (22)

WebSockets provide a long-lived bidirectional message channel. See [22. WebSockets](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-022).

## Long Polling (23)

Long polling holds an HTTP request until an update arrives or a server timeout ends it. See [23. Long Polling](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-023).

## Server-Sent Events (24)

Server-sent events stream text events from a server to a browser over HTTP. See [24. Server-Sent Events](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-024).

## Database Indexing (25)

An index is a searchable structure that helps a database find rows without examining every row. See [25. Database Indexing](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-025).

## Query Optimization (26)

Query optimization reduces the work needed to produce a correct database result. See [26. Query Optimization](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-026).

## N+1 Queries (27)

N+1 occurs when one query fetches a list and another query runs for each list item. See [27. N+1 Queries](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-027).

## Connection Pooling (28)

A connection pool reuses a bounded set of database connections. See [28. Connection Pooling](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-028).

## Read Replicas (29)

A read replica serves a copy of database data to offload reads. See [29. Read Replicas](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-029).

## Sharding (30)

Sharding splits a dataset across independently hosted partitions. See [30. Sharding](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-030).

## Partitioning (31)

Partitioning divides a logical table or dataset into smaller pieces using a rule. See [31. Partitioning](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-031).

## Replication (32)

Replication maintains copies of data on multiple machines. See [32. Replication](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-032).

## Leader Election (33)

Leader election chooses a coordinator among replicas. See [33. Leader Election](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-033).

## CAP Theorem (34)

CAP explains a limit during a network partition: a distributed service cannot guarantee both linearizable behavior and a response for every request to a nonfailed node under the theorem's assumptions. See [34. CAP Theorem](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-034).

## Eventual Consistency (35)

Eventual consistency allows replicas to differ temporarily but requires convergence under appropriate delivery and update assumptions. See [35. Eventual Consistency](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-035).

## Optimistic Locking (36)

Optimistic locking lets concurrent readers proceed, then checks whether data changed before accepting a write. See [36. Optimistic Locking](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-036).

## Pessimistic Locking (37)

Pessimistic locking reserves access before changing shared data. See [37. Pessimistic Locking](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-037).

## Distributed Locks (38)

A distributed lock coordinates exclusive work across processes or machines. See [38. Distributed Locks](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-038).

## Race Conditions (39)

A race condition occurs when correctness depends on the timing of concurrent operations. See [39. Race Conditions](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-039).

## Deadlocks (40)

A deadlock is a cycle of operations waiting for resources held by one another. See [40. Deadlocks](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-040).

## Memory Leaks (41)

A memory leak is retained memory that the program no longer needs. See [41. Memory Leaks](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-041).

## Garbage Collection (42)

Garbage collection reclaims memory that a program can no longer reach. See [42. Garbage Collection](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-042).

## Thread Safety (43)

Thread-safe code preserves its contract when several threads call it concurrently. See [43. Thread Safety](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-043).

## Backpressure (44)

Backpressure makes a slow downstream stage constrain upstream production. See [44. Backpressure](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-044).

## Autoscaling (45)

Autoscaling changes capacity in response to demand or schedules. See [45. Autoscaling](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-045).

## Horizontal Scaling (46)

Horizontal scaling adds machines or process instances. See [46. Horizontal Scaling](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-046).

## Vertical Scaling (47)

Vertical scaling gives one machine more CPU, memory, storage performance, or accelerator capacity. See [47. Vertical Scaling](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-047).

## CDN (48)

A content delivery network serves content from geographically distributed edge locations. See [48. CDN](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-048).

## Edge Caching (49)

Edge caching stores reusable responses near users. See [49. Edge Caching](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-049).

## Cache Invalidation (50)

Cache invalidation removes or supersedes copies after their source changes. See [50. Cache Invalidation](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-050).

## Feature Flags (51)

A feature flag chooses behavior at runtime without rebuilding the application. See [51. Feature Flags](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-051).

## Blue-Green Deployment (52)

Blue-green deployment maintains two application environments and switches traffic from the current one to a prepared replacement. See [52. Blue-Green Deployment](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-052).

## Canary Releases (53)

A canary release exposes a change to a limited population before broad rollout. See [53. Canary Releases](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-053).

## Rolling Deployments (54)

A rolling deployment replaces application instances gradually. See [54. Rolling Deployments](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-054).

## Rollbacks (55)

A rollback returns a system to a previously acceptable state after a harmful change. See [55. Rollbacks](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-055).

## Health Checks (56)

A health check is a targeted observation used to decide whether a component can perform a particular role. See [56. Health Checks](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-056).

## Liveness and Readiness Probes (57)

Liveness asks whether restarting a container may help it recover. See [57. Liveness and Readiness Probes](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-057).

## Monitoring (58)

Monitoring continuously checks known indicators of service behavior. See [58. Monitoring](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-058).

## Logging (59)

Logs are timestamped records of events and decisions. See [59. Logging](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-059).

## Distributed Tracing (60)

Distributed tracing follows one operation through several components. See [60. Distributed Tracing](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-060).

## Metrics (61)

Metrics summarize measurements over time. See [61. Metrics](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-061).

## Alerts (62)

An alert asks a person or automation to act on a condition. See [62. Alerts](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-062).

## SLOs (63)

A service level objective is a measurable target for user-facing service behavior over a defined window. See [63. SLOs](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-063).

## SLIs (64)

A service level indicator measures a property users care about. See [64. SLIs](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-064).

## Error Budgets (65)

An error budget is the amount of unreliability allowed by an SLO. See [65. Error Budgets](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-065).

## Observability (66)

Observability is the ability to infer useful internal state from a system's outputs. See [66. Observability](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-066).

## Secrets Management (67)

Secrets management controls sensitive credentials throughout their lifecycle. See [67. Secrets Management](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-067).

## IAM (68)

Identity and access management determines who or what can do which actions on which resources. See [68. IAM](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-068).

## OAuth (69)

OAuth enables delegated authorization: an application obtains limited access to a resource without receiving the user's password for that resource. See [69. OAuth](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-069).

## JWT Rotation (70)

JWT rotation can refer to replacing signing keys or rotating refresh credentials; these are distinct mechanisms. See [70. JWT Rotation](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-070).

## TLS (71)

TLS protects a connection against eavesdropping and tampering while authenticating the server, and optionally the client. See [71. TLS](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-071).

## Encryption at Rest (72)

Encryption at rest protects stored data against certain forms of unauthorized storage access. See [72. Encryption at Rest](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-072).

## Encryption in Transit (73)

Encryption in transit protects data while it moves between endpoints. See [73. Encryption in Transit](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-073).

## WAF (74)

A web application firewall inspects HTTP traffic and applies protective rules. See [74. WAF](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-074).

## DDoS Protection (75)

Distributed denial-of-service protection preserves useful service during excessive malicious traffic. See [75. DDoS Protection](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-075).

## CORS (76)

Cross-origin resource sharing is a browser mechanism that controls which origins may read selected cross-origin responses. See [76. CORS](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-076).

## CSRF (77)

Cross-site request forgery tricks a user's browser into performing an unwanted action using automatically attached credentials, commonly cookies. See [77. CSRF](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-077).

## SQL Injection (78)

SQL injection occurs when untrusted input changes the structure of a database command. See [78. SQL Injection](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-078).

## XSS (79)

Cross-site scripting occurs when untrusted content executes as script in a user's browser under a trusted site's origin. See [79. XSS](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-079).

## SSRF (80)

Server-side request forgery occurs when an attacker influences a server to request an unintended destination. See [80. SSRF](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-080).

## Database Migrations (81)

A database migration changes schema or data in a controlled versioned process. See [81. Database Migrations](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-081).

## Schema Versioning (82)

Schema versioning tracks the structure and meaning of data exchanged or stored over time. See [82. Schema Versioning](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-082).

## Disaster Recovery (83)

Disaster recovery restores useful service after a major failure such as a lost region, corrupted database, or compromised environment. See [83. Disaster Recovery](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-083).

## Backups (84)

A backup is a recoverable historical copy of data. See [84. Backups](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-084).

## Failover (85)

Failover transfers service responsibility to another instance or site after failure. See [85. Failover](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-085).

## Multi-Region Deployment (86)

Multi-region deployment places service components in geographically separated areas. See [86. Multi-Region Deployment](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-086).

## Chaos Engineering (87)

Chaos engineering tests reliability hypotheses by introducing controlled failures. See [87. Chaos Engineering](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-087).

## Cost Optimization (88)

Cost optimization reduces spending while preserving required behavior. See [88. Cost Optimization](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-088).

## Cold Starts (89)

A cold start is initialization work before an instance can serve useful requests. See [89. Cold Starts](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-089).

## Serverless Limits (90)

Serverless platforms manage execution infrastructure but impose resource and service quotas. See [90. Serverless Limits](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-090).

## Latency (91)

Latency is the elapsed time for an operation from a defined start to a defined finish. See [91. Latency](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-091).

## Throughput (92)

Throughput is the rate of completed useful work. See [92. Throughput](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-092).

## P99 Latency (93)

P99 latency is a percentile threshold: roughly 99% of measured operations finish at or below it under the chosen estimation convention. See [93. P99 Latency](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-093).

## Tail Latency (94)

Tail latency describes unusually slow operations at the high end of a distribution. See [94. Tail Latency](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-094).

## Network Partitions (95)

A network partition prevents some components from communicating while others remain reachable. See [95. Network Partitions](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-095).

## Clock Skew (96)

Clock skew is disagreement between clocks. See [96. Clock Skew](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-096).

## DNS (97)

DNS maps names to records such as IP addresses and service information. See [97. DNS](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-097).

## TCP vs UDP (98)

TCP provides a reliable ordered byte stream with congestion and flow control. See [98. TCP vs UDP](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-098).

## HTTP/2 and HTTP/3 (99)

HTTP/2 and HTTP/3 preserve HTTP request-response semantics while changing how messages share a connection. See [99. HTTP/2 and HTTP/3](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-099).

## gRPC (100)

gRPC is an RPC framework that lets clients call defined remote service methods using generated interfaces and structured messages. See [100. gRPC](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-100).

## Webhooks (101)

A webhook is an HTTP callback notifying another system that an event occurred. See [101. Webhooks](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-101).

## API Versioning (102)

API versioning manages contract evolution for clients that cannot all upgrade at once. See [102. API Versioning](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-102).

## Semantic Versioning (103)

Semantic Versioning communicates intended compatibility through MAJOR.MINOR.PATCH for a declared public API. See [103. Semantic Versioning](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-103).

## Infrastructure as Code (104)

Infrastructure as code expresses infrastructure configuration in reviewable files. See [104. Infrastructure as Code](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-104).

## Terraform (105)

Terraform is an infrastructure-as-code tool that compares configuration, recorded state, and provider observations to plan resource changes. See [105. Terraform](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-105).

## Helm Charts (106)

A Helm chart packages parameterized Kubernetes manifests. See [106. Helm Charts](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-106).

## Build Caching (107)

Build caching reuses outputs when their relevant inputs have not changed. See [107. Build Caching](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-107).

## Dependency Hell (108)

Dependency hell occurs when required packages, versions, native libraries, or runtime assumptions conflict. See [108. Dependency Hell](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-108).

## Production Incidents (109)

A production incident is a disruption requiring coordinated response to reduce user harm. See [109. Production Incidents](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-109).

## On-Call (110)

On-call is a structured responsibility for responding to urgent service problems. See [110. On-Call](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-110).

## Postmortems (111)

A postmortem is a structured learning review after an incident. See [111. Postmortems](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-111).

## ACID

Atomicity, consistency, isolation, and durability: distinct transaction properties with implementation-specific failure and concurrency boundaries.

## Acknowledgment

A protocol message confirming a defined milestone. A broker acknowledgment, socket acknowledgment, and business completion acknowledgment mean different things.

## Admission control

A decision to accept, defer, or reject work before expensive resource consumption.

## Artifact digest

A cryptographic identifier for exact artifact bytes, unlike a mutable tag or compatibility version.

## Atomicity

All changes within a stated transaction boundary commit together or are rolled back.

## Backfill

A controlled process that populates new or corrected data for historical records.

## Blast radius

The set of users, data, and components a failure or change can affect.

## Cardinality

The number of distinct values or combinations; high metric-label cardinality can create excessive time-series storage.

## Causality

A relationship where one event can influence another, distinct from apparent ordering by unsynchronized clocks.

## Cold start

Initialization before useful service, including runtime, artifact, dependency, and model setup.

## Compensation

A new business action intended to repair an earlier committed effect; it may not restore the exact original world.

## Consensus

Agreement on a value or ordered log under stated fault and timing assumptions, often using intersecting quorums.

## Control plane

Components that configure or coordinate the system; the data plane handles ordinary workload traffic.

## Deadline

An absolute end to a remaining work budget, propagated across attempts rather than reset at every hop.

## Durability

Preservation of accepted committed data under the storage and replication failures covered by the configuration.

## ETag

An HTTP representation validator that can support conditional reads or write preconditions.

## Fencing token

An increasing ownership epoch enforced by the protected resource to reject stale owners.

## Goodput

Useful successful work per unit time, excluding rejected, duplicated, or otherwise unhelpful work.

## Head-of-line blocking

A delay where one missing or unfinished item prevents progress of later items at a particular layer.

## Histogram

A distribution represented by bucket counts; compatible bucket populations can be aggregated before estimating quantiles.

## Idempotency key

A caller-supplied identifier for one logical operation, scoped and persisted under an explicit replay contract.

## Invariant

A condition that must hold across all valid state transitions, such as nonnegative inventory or tenant isolation.

## JWKS

JSON Web Key Set, a structured set of verification keys obtained from a trusted issuer configuration.

## Lease

Time-bounded permission whose expiry does not physically stop a paused previous owner.

## Linearizability

A consistency model in which operations behave as though each takes effect at one instant between invocation and response, respecting real-time order.

## Little's Law

For a stable system and consistent boundaries, average number in system equals average arrival/completion rate times average time in system.

## MVCC

Multiversion concurrency control: keeping versions so readers can observe an appropriate snapshot while writes proceed under defined rules.

## NAT

Network address translation; many clients can share one public address, which affects IP-based rate-limit fairness.

## OIDC

OpenID Connect, an identity layer built on OAuth flows; an ID token and an API access token have different purposes and audiences.

## Outbox / inbox

Local transaction patterns for committed event publication intent and consumer deduplication coupled to local effects.

## PKCE

Proof Key for Code Exchange, binding an authorization-code exchange to a verifier whose challenge was sent earlier.

## Projection

A derived read model built from authoritative state or events; it can lag and may need rebuilding.

## Quorum

A required subset of participants. Safety depends on protocol rules and intersection assumptions, not only arithmetic.

## RPO

Recovery point objective: the tolerated gap between the failure time and the newest recoverable data.

## RTO

Recovery time objective: the target duration to restore the defined useful service after disruption.

## Serialization anomaly

A concurrent transaction outcome that cannot be explained by any serial execution of the transactions.

## SLA

Service level agreement, typically a contractual commitment with defined consequences, distinct from an internal SLO.

## Split brain

Conflicting active authorities accepting operations after coordination fails.

## Tail sampling

Choosing traces after observing enough of their outcome, which requires buffering and may preserve unusual failures.

## TTL

Time to live: an expiry duration whose meaning depends on the cache, DNS record, lease, or other object involved.

## WAL

Write-ahead log, a durable change record used by databases for recovery and often replication.

## Write skew

Concurrent transactions update different rows after reading a shared condition, jointly violating an invariant.

## Zero trust

An architectural approach that requires explicit identity and authorization rather than treating network location alone as sufficient trust.
