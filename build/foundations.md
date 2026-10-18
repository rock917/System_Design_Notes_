## Part I. Foundations of Production Systems

### How to use this book

This handbook assumes basic programming: variables, functions, collections, exceptions, and simple complexity analysis. You do not need prior cloud or distributed-systems experience. Learn enough SQL to write SELECT, INSERT, UPDATE, and JOIN statements; enough HTTP to distinguish a request, response, method, status, header, and body; and enough operating-system vocabulary to distinguish a process, thread, file, socket, and memory allocation. When a term is unfamiliar, use the glossary rather than skipping the surrounding argument.

The original 111 topic numbers are permanent identifiers. Learning parts group them by dependency rather than numerical order. Each topic contains fourteen teaching sections, a worked example, a visual, interview practice, and exercises with solution guidance. The interview answers intentionally revisit the mechanism from different angles: first explain it without reading the answer, then compare your reasoning. The standalone interview bank repeats those questions for revision; those repetitions are not additional unique questions.

Use a three-pass method. On the first pass, read the explanation, problem, analogy, and diagram. On the second, reproduce the worked example and run the applicable lab. On the third, close the book and answer the scenario and advanced questions. Keep an engineering notebook with four entries for every design decision: requirement, assumption, chosen mechanism, and evidence that would make you change your mind.

All capacity numbers in this book are hypothetical unless explicitly described as output from an included deterministic program. They illustrate arithmetic, not measured performance claims for a product or provider. The source notes identify official documentation consulted on 18 October 2026. Provider limits, security recommendations, tool flags, and supported versions should be checked again before a real deployment. The examples are educational; the audit states which were executed and which configurations still need their actual runtimes.

### 1. Begin with a user promise

System design starts with behavior, not a shopping list of components. A functional requirement says what users can do: browse products, maintain a cart, place an order, pay, and receive a receipt. A non-functional requirement qualifies that behavior: response time, availability, privacy, durability, freshness, cost, and operational constraints. An order accepted successfully must not silently vanish. A catalog description may be allowed to lag briefly. Those two promises justify different data paths.

Ask concrete scope questions in an interview even when no production stakeholder is present. Is payment authorization or payment settlement required? Must a chat message be durable before it appears delivered? Is a prediction response a small vector or a streamed generated answer? How many tenants exist, and can one tenant dominate traffic? What failures must the system tolerate? What is explicitly excluded? Write answers as assumptions when the interviewer leaves them open.

An invariant is a condition that must remain true across all valid state transitions. For ShopStream, stock cannot become negative, a logical checkout cannot create two charges, and one tenant cannot read another tenant's private order. An objective is a measured target such as 99% of accepted interactive predictions completing within a chosen time. Invariants and objectives differ: trading a little latency for lower cost may be acceptable, while trading away authorization correctness is not.

### 2. A request from browser to database and back

A customer enters the shop address. The browser obtains an address through DNS, potentially using cached results. It establishes a transport connection, negotiates TLS and verifies the service identity, then sends an HTTP request. A CDN may answer a permitted cached request. Otherwise an edge proxy or load balancer forwards it to an eligible application instance. The application authenticates the caller, authorizes the specific operation, validates input, and acquires bounded resources.

For a product read, the application may check an internal cache. On a miss it acquires a database connection, executes a query under the relevant isolation semantics, releases the connection, updates the cache if permitted, and returns a response. The proxy and browser apply their own response handling and caching rules. Each hop can queue, time out, reject, disconnect, or produce an ambiguous outcome. A request that never reached the application cannot appear in its application log, so outside-in evidence matters.

HTTP status codes communicate protocol-level outcomes, not a complete business history. A 202 can mean durable acceptance for later processing. A timeout can mean the client stopped waiting after the server committed. A 200 containing an incorrect price is still a correctness failure. Define stable operation identifiers and explicit states such as pending, confirmed, declined, and reconciliation-required where asynchronous work or ambiguity exists.

[[FIG:seq-http]]

Read this sequence top to bottom. The client talks to a resolver before the service connection. The proxy forwards a request to the application; the application alone owns the database operation shown. A response lost on the return path is a different failure from a request rejected before database access. Connection setup is shown separately because a reused connection amortizes that work.

### 3. Capacity estimation with units

Assume one million daily active users, each making twenty API requests per day. Daily volume is 20 million requests. Dividing by 86,400 seconds gives about 231.5 requests/second on average. Assume a peak-to-average factor of eight: the planning peak is about 1,852 requests/second. This is a stated hypothesis to validate, not a universal traffic rule. A product launch can create a much sharper burst than ordinary daily seasonality.

If mean time in the system at that load is 0.2 seconds, Little's Law gives average concurrent work L=lambda*W=1,852*0.2, about 370 requests. This relationship concerns stable long-run averages and consistent boundaries. It does not mean 370 operating-system threads are necessarily needed: asynchronous I/O, internal fanout, and resource-specific hold time change how concurrency maps to implementation resources.

Assume each response averages 12 KB, ignoring request bytes, compression, and protocol overhead. At peak, response bandwidth is approximately 1,852*12 KB=22.2 MB/second, or 178 Mb/second using decimal units. Add realistic overhead and failure headroom rather than provisioning exactly that figure. Large downloads can dominate bandwidth even when their request count is small.

Assume 100,000 orders/day and 2 KB of logical order data. One year is about 73 GB of logical data. Three complete copies make 219 GB before indexes, logs, backups, deleted-row overhead, and growth. If the measured index/storage overhead factor is two, the online footprint becomes roughly 438 GB under that assumed factor. State whether an estimate is logical, physical, replicated, or retained-backup size; mixing them is a common design error.

[[FIG:ill-capacity]]

The illustration preserves units through the calculation. Move from users/day to requests/day, divide by seconds/day, multiply by a stated peak factor, then derive concurrency and bytes/second separately. Do not multiply concurrency by throughput again; they are already related through time in the system.

### 4. Bottlenecks, utilization, and headroom

A system is a chain and network of resource constraints. CPU execution, database locks, pool slots, disk IOPS, memory bandwidth, network throughput, and external quotas can each become the bottleneck. Low CPU with high latency often means waiting, not spare usable capacity. Measure queue wait and resource hold time to determine which constraint is active.

Suppose a worker takes 10 ms of CPU per request on a single fully available core. The ideal CPU-only ceiling is 100 requests/second. If each request also holds a database connection for 200 ms, a pool of ten connections has an ideal occupancy ceiling of 50 requests/second. The smaller relevant capacity dominates. Real scheduling, I/O, contention, and variance reduce these idealized ceilings.

At 1,000 jobs/second arriving and 1,100 completing, a backlog of 60,000 jobs drains at only 100 jobs/second, taking 600 seconds. Dividing by 1,100 would incorrectly ignore continuing arrivals. During recovery, capacity must handle live traffic plus catch-up. If queues contain expired work, process policy may discard or reconcile it instead of spending resources on results users no longer need.

The ideal M/M/1 queue assumes Poisson arrivals, exponential service times, one server, and a stable arrival rate below service rate. Its mean time in system is 1/(mu-lambda). At mu=100/second and lambda=50/second, the model gives 20 ms; at lambda=90 it gives 100 ms. Real workloads rarely fit every assumption, but the shape explains why latency deteriorates near saturation. Benchmark realistic distributions and keep failure headroom.

### 5. Availability, durability, and correlated failures

Availability describes whether required operations can be completed. Durability describes preservation of accepted data. A system can be available while returning stale results, or durable while temporarily unavailable. Reliability combines multiple aspects of correct useful behavior over time. Choose measurable definitions rather than treating these terms as interchangeable praise.

For independent serial dependencies with availability A1 and A2, a simplified model multiplies them. Two required 99.9% dependencies yield 0.999 squared, about 99.8001%. The independence and identical measurement-window assumptions matter. Shared power, networking, credentials, code, or operators can correlate failures and invalidate the estimate. Redundant replicas improve availability only if the surviving path has independent dependencies and enough capacity.

A 99.9% time-based objective over thirty days permits approximately 43.2 minutes of bad time. A request-based 99.9% objective instead permits 0.1% of eligible requests to be bad. A five-minute peak-hour outage and a five-minute overnight outage consume equal time budgets but can consume very different request budgets. Use the definition that represents the promised experience and report its limitations.

Backups answer how far back data can be restored; failover answers how service responsibility changes. RPO measures tolerated loss of recent data. RTO measures targeted recovery time. A secondary region with stale data and missing credentials may satisfy neither objective. Recovery must be demonstrated with a drill and integrity checks.

### 6. Data modeling before database selection

ShopStream's initial relational model includes users, products, carts, cart_items, orders, order_items, payments, inventory, and outbox events. Store money as an integer minor-unit amount plus explicit currency under a defined currency contract. Snapshot the purchased product name and price in the order line so historical invoices do not change when the catalog changes. Use foreign keys and constraints where they represent local invariants.

An order and payment are related but not identical entities. One order may have several payment attempts and one logical successful payment intent. An external provider operation needs its own stable ID and state. An order status must not be inferred solely from whether the latest HTTP call returned 200. Preserve pending and unknown states and reconcile them.

Choose storage based on access patterns and guarantees. A relational database is a strong default for transactional orders and constraints. An object store suits large immutable model artifacts and media. A search index is a derived view for text retrieval. A cache stores disposable copies. A broker transports or retains messages under its own contract. Adding each specialized system introduces synchronization, access control, backup, and incident responsibilities.

### 7. ACID and isolation in concrete terms

Atomicity means a transaction's local changes commit together or are rolled back. Consistency in ACID refers to preserving defined database/application rules, not automatically synchronizing every replica. Isolation controls which concurrent effects a transaction may observe. Durability means committed changes survive the failures covered by the database's configured storage and replication guarantees.

Consider two account rows. A transfer must debit one and credit the other together, while checking sufficient funds. A transaction prevents half a local transfer, but the chosen isolation and locking still matter under concurrent withdrawals. A CHECK constraint can enforce a nonnegative balance on a row. Cross-row invariants may require a stronger transaction design.

In PostgreSQL's usual Read Committed mode, each statement sees a committed snapshot at statement start, with important rules for concurrent updates. Repeatable Read gives a stable transaction snapshot but can permit serialization anomalies. Serializable aims for outcomes equivalent to a serial execution and can abort transactions that must be retried. PostgreSQL treats requested Read Uncommitted as Read Committed. These are PostgreSQL-specific details; isolation names do not imply identical implementation behavior across databases. See the official [transaction isolation documentation](https://www.postgresql.org/docs/current/transaction-iso.html) for those specific semantics.

Write skew illustrates why atomic row updates are not enough. Two doctors are on call. Each transaction observes that the other is on call, then independently sets its own row off call. Both writes can succeed under snapshot isolation even though the final state violates the rule that at least one doctor remains. Serialize the relevant decision, lock a shared guard under a correct design, or use a suitable constraint/model. Do not merely add separate version columns and assume the cross-row invariant is protected.

Read an EXPLAIN tree from child operations toward their parents. Estimated cost is not wall-clock milliseconds. Actual rows, loops, buffers, spills, and waits help explain work. EXPLAIN ANALYZE executes the statement, so use an isolated dataset for mutating queries. The official [EXPLAIN guide](https://www.postgresql.org/docs/current/using-explain.html) verifies these plan-reading distinctions; the included SQL lab supplies original data and queries for practice.

### 8. Synchronous and asynchronous boundaries

A synchronous call ties the caller's completion to a response from a dependency. It is easy to understand for a small read, but serial dependencies add latency and shared failure exposure. An asynchronous boundary lets the caller acknowledge durable acceptance and return while a worker completes the task later. It requires status retrieval, delivery semantics, retention, and user expectations about delay.

At-most-once delivery can lose messages because it avoids retries. At-least-once delivery can repeat messages because acknowledgment loss cannot always be distinguished from unfinished work. Exactly-once claims require a precise boundary. A broker transaction can atomically commit records and offsets within a supported system; it does not automatically atomically send email, update an unrelated database, and charge a card.

The outbox pattern closes one important gap: business state and an event-to-publish are committed in the same database transaction. A relay may publish more than once. The inbox pattern can make a consumer's deduplication record and local database effect atomic. External effects still need provider idempotency or reconciliation. The handbook's SQLite lab demonstrates this local boundary without pretending to implement a distributed broker.

### 9. Evolving ShopStream deliberately

Begin with a modular monolith and PostgreSQL. Modules separate catalog, accounts, carts, orders, and payments in code; they need not be independent services. One deployment and one transactional boundary reduce operating complexity while the product is small. Record the evidence that would justify a later change: repeated expensive reads, queue delay, an independently scaling workload, different ownership, or isolation needs.

[[FIG:arch-monolith]]

The client enters one application boundary. Modules share a database but have explicit responsibilities. The payment provider is already a distributed dependency even though the application is a monolith. A timeout at that boundary requires an operation ID and reconciliation from the first release.

| Stage | Motivation and change | New cost or failure mode | Evidence and test |
|---|---|---|---|
| 1. Indexes | Slow customer-order lookup; add query-shaped index | Write amplification and index storage | Compare plans and realistic write load |
| 2. Pooling | Connection setup and session growth | Pool wait and leaked ownership | Exception-release and saturation tests |
| 3. Cache | Repeated catalog reads | Stale copies and miss storms | Freshness race and origin-load test |
| 4. Rate limits | One caller consumes capacity | False rejection and limiter dependency | Tenant isolation and outage policy test |
| 5. Proxy/LB | Multiple API replicas and TLS boundary | Routing, drain, and proxy failure | Kill one replica under bounded load |
| 6. Queue | Receipts delay checkout | Duplicate delivery and aging backlog | Crash before acknowledgment |
| 7. Idempotency | Replayed checkout creates duplicates | Key retention and payload conflicts | Concurrent same-key requests |
| 8. Transactions | Stock and order must agree locally | Locks and isolation anomalies | Last-item and rollback tests |
| 9. Events | Several consumers need order facts | Schema drift and lost publication | Outbox replay and consumer-version matrix |
| 10. Saga | Separate business owners/datastores | Partial states and failed compensation | Unknown payment and compensation retry |
| 11. Scale out | Independent request capacity exhausted | Shared database and session limits | Aggregate capacity and failover test |
| 12. Containers | Reproducible packaging | Image, signal, and resource-limit issues | Non-root startup and termination test |
| 13. Orchestration | Managing replicas becomes burdensome | Control-plane and networking complexity | Readiness and node-loss drill |
| 14. CI/CD | Manual release errors | Build trust and promotion mistakes | Promote same digest and stop failed gates |
| 15. Telemetry | Cross-component diagnosis is slow | Data cost and sampling gaps | Correlated trace/log/metric exercise |
| 16. Security | Broader exposure and tenants | Policy drift and secret lifecycle | Cross-tenant negative tests and rotation |
| 17. Regions | Regional recovery/locality requirement | Conflicts and cross-region dependency | Fenced failover and residency review |
| 18. Recovery | Deletion/corruption survival | Backup/key/replay dependencies | Timed isolated restore with invariants |
| 19. Cost | Resource spend grows | Savings can remove headroom | Cost per useful result under SLO |
| 20. Operations | Incidents require coordinated response | Toil, fatigue, and unsafe changes | Tabletop, handoff, postmortem actions |

[[FIG:arch-production]]

This mature reference design adds components only where the preceding table gives a reason. It is a design vocabulary, not a requirement to deploy everything. Synchronous user paths, asynchronous events, and control/telemetry paths use different edge labels. Payments remain behind a deliberate idempotent integration boundary, and restoration remains necessary even with replicas.

### 10. Reading diagrams and testing claims

Every visual has a stable figure ID and local image. Editable Mermaid sources accompany graph diagrams, and SVG sources accompany technical illustrations. Labels and shapes carry meaning in grayscale: diamonds are decisions, labeled dashed edges represent failure or control paths, and arrows indicate the direction of the stated message or operation. Architecture arrows are not automatically trust grants. Sequence diagrams run downward in time, while state diagrams show allowed transitions rather than physical placement.

A useful test states the claim, introduces a discriminating input or fault, and checks an observable invariant. 'The service started' is weak evidence for idempotency. Two simultaneous same-key checkouts producing one durable order is stronger evidence for the local implementation. It still does not prove a real payment provider has matching semantics. Keep the boundary of each test visible.

When measuring performance, distinguish synthetic arithmetic, local microbenchmarks, load tests, and production observations. The included numbers are reproducible models and educational outputs. Build an open-loop load generator only against systems you own or are authorized to test, set a stop threshold, record errors and timeouts, and preserve the workload distribution. Optimization should follow evidence and end with remeasurement.
