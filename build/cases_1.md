## Part XIV. End-to-End System Design Case Studies

### Case 1. URL shortener

**Requirements and contract.** Create a short link for an allowed HTTP/HTTPS destination, redirect visitors, optionally expire or disable a link, and report aggregate click counts. Assume public redirects and authenticated creation. A creation success must survive the agreed database failure model. Analytics may lag and must not delay redirects. Set separate objectives for creation and redirection; a popular link creates a highly skewed workload.

**Estimates.** Assume one million new links/day and 100 million redirects/day: about 11.6 writes/second and 1,157 reads/second on average. With an assumed tenfold redirect peak, design tests around 11,570 reads/second. At 500 bytes of logical metadata per link, one year is about 182.5 GB before indexes, replicas, and backups. A seven-character base62 space has 62^7, about 3.52 trillion, possibilities; random allocation still needs collision detection and retry. The birthday effect means a large space does not eliminate collisions at scale.

[[FIG:case-url-overview]]

The client-facing service has two paths: a durable authenticated creation path and a read-heavy redirect path. Analytics is asynchronous. A cache accelerates redirects but cannot become the only copy of the mapping.

**API contracts.** POST /v1/links accepts destination, optional expiry, and an idempotency key; it returns 201 with code, short_url, and expiry. GET /{code} returns a documented redirect status and Location, or a stable 404/410 policy for unavailable links. DELETE /v1/links/{code} requires ownership. Choose 302/307 or permanent redirects based on whether destinations can change and how client/CDN caching should behave. Do not inadvertently cache a redirect permanently if abuse removal must take effect quickly.

**Schema.** links(code primary key, owner_id, destination, created_at, expires_at, disabled_at, version). A unique operation table scopes creation keys to owner. click_events(event_id, code, observed_at, coarse_region) is separate from the mapping and can be aggregated with bounded retention. Avoid collecting unnecessary visitor identifiers. Index owner_id plus created_at for account management; the primary code lookup already has its key index.

[[FIG:case-url-detail]]

Read the detailed diagram as a cache-aside flow. On a miss the redirect service reads the mapping, checks disabled/expiry state, caches a versioned permitted result, and returns the redirect. The event publisher emits analytics without making analytics availability a dependency of redirection.

**Step-by-step flow.** Validate the creation request and destination policy, generate a code, insert under a uniqueness constraint, and commit the idempotent result. On a collision, generate another code within a bounded retry budget. For a redirect, normalize the code, check a bounded cache, read the database on miss, validate current policy, and respond. Queue analytics after selecting a durable or explicitly lossy analytics contract. Do not turn analytics failure into a false redirect failure.

[[FIG:case-url-sequence]]

**Failures and security.** A cache outage can multiply database demand, so cap origin reads and reserve capacity. A hot malicious destination requires disable propagation and an edge purge strategy. Avoid fetching arbitrary destinations merely to validate them; if preview fetching is required, isolate it against SSRF. Restrict schemes, creation abuse, and account access. A short code is not a secret unless the product explicitly designs an unguessable private-link mechanism with sufficient entropy and access checks.

**Scaling and trade-offs.** Start with one relational database, replicas for permitted reads, and a shared cache. Partition analytics separately. Shard mappings only when measured storage/write/operational limits justify it, using a routing rule that supports rebalancing. A global CDN can accelerate redirects but complicates fast deletion and regional policy. The key design choice is the freshness/removal guarantee, not the number of servers drawn.

**Validation and interview probe.** Test concurrent creation with one operation key, generated-code collisions, disabled-link cache races, expiry boundaries, and a hot-key burst. Restore the mapping database and verify links remain resolvable. A strong follow-up asks: 'How quickly must an abusive link stop redirecting everywhere?' A bounded stale window may be acceptable for ordinary edits but unacceptable for urgent removal, requiring a separate deny mechanism.

### Case 2. Rate-limited public API

**Requirements and contract.** Serve a tenant-scoped product API with authentication, per-tenant quotas, burst allowances, and predictable overload responses. Distinguish purchased quota from current service capacity. A tenant can remain within quota while the shared backend is overloaded; a healthy backend can reject a tenant that exhausted its allocation.

**Estimates.** Assume 10,000 active tenants, aggregate peak 20,000 requests/second, and a typical tenant allowance of ten requests/second with a burst of fifty. This does not imply every tenant can simultaneously use its maximum: aggregate capacity and commercial commitments must be reconciled. At 200 bytes of limiter state per active key, 100,000 active tenant-operation keys require about 20 MB before store overhead and replication.

[[FIG:case-api-overview]]

The gateway authenticates and classifies requests before admission. The limiter's state store coordinates quota; application concurrency limits separately protect downstream work. Metrics record logical requests and rejected requests independently.

**API contracts.** GET /v1/products supports bounded pagination and stable filtering. POST mutations require an operation key where replay can duplicate effects. A quota rejection returns 429 and a useful Retry-After policy; a shared-capacity rejection may use 503 according to the contract. Error responses contain a stable code and request ID without exposing credential details. Document whether denied requests consume quota and how weighted operations are charged.

**Schema and state.** tenants(id, plan_id, status), api_credentials(id, tenant_id, verifier_reference, revoked_at), plans(id, refill_rate, burst, daily_budget), and usage_ledger(tenant_id, operation_id, units, timestamp). Ephemeral limiter records contain key, tokens, last_refill, and policy_version. Monetary billing or purchased credit balances belong in a durable ledger, not solely in an evictable token bucket.

[[FIG:case-api-detail]]

**Step-by-step flow.** Verify the credential, derive tenant from trusted identity, normalize the route to a bounded operation name, assign estimated cost, atomically refill/debit tokens, acquire a concurrency slot, execute with a remaining deadline, release resources, and record actual usage. For expensive inference, reserve an estimate and reconcile actual tokens or compute under an explicit overrun policy.

[[FIG:case-api-sequence]]

**Failures and security.** If the limiter store fails, public browsing might use a small local emergency allowance while paid generation fails closed or uses preallocated leases. The decision must be explicit per operation. Do not key solely by forwarded IP or accept a caller-provided tenant ID. Limit request size before expensive parsing. Prevent one tenant from consuming the entire pool even if it spreads traffic across API keys.

**Scaling and trade-offs.** One strict global bucket requires coordination. Regional leases reduce per-request coordination but can reserve unused quota and introduce bounded overshoot if accounting is not strict. A hierarchical design can combine global purchased budget, regional allowances, tenant fairness, and local concurrency. Explain each bound and failure policy. More limiter replicas do not automatically preserve a single global quota.

**Validation and interview probe.** Test exact refill boundaries, weighted cost, concurrent debits, tenant isolation, expiry, policy changes, and store outage. Load-test accepted goodput and rejection latency together. Ask how a new policy reaches cached gateways and whether a revoked credential can continue using old regional allowance. A complete answer includes policy versioning and an emergency revocation path.

### Case 3. E-commerce orders and payments

**Requirements and contract.** Create an order, reserve inventory, request payment, and expose a durable state the user can query. Prevent duplicate logical charges and overselling under the defined stock model. Support cancellation and refund as explicit business operations. Do not claim that an HTTP timeout means the order failed.

**Estimates.** Assume 100,000 orders/day, about 1.16/second average, and a sale peak of 100/second. Each order has four lines averaging 250 bytes plus 1 KB of header and workflow metadata: roughly 2 KB/order before indexes and audit history. A payment provider taking 500 ms on average produces about fifty concurrent calls at 100/second under stable conditions, before retries and headroom. Confirm provider quotas rather than assuming local capacity is sufficient.

[[FIG:case-orders-overview]]

The initial design keeps order and inventory state in one database, with a payment integration and durable outbox. Split service ownership only when organizational or scaling requirements justify losing that simple local transaction boundary.

**API contracts.** POST /v1/orders accepts cart snapshot/version, shipping choice, and Idempotency-Key. It returns a stable order ID and state, possibly 202 pending. GET /v1/orders/{id} returns current state and permitted next actions. POST /v1/orders/{id}/cancel is an authorized idempotent command whose outcome depends on whether shipping has crossed its irreversible boundary. Payment callbacks are authenticated and deduplicated.

**Schema.** orders(id, tenant_id, customer_id, status, total_minor, currency, version); order_items(order_id, sku, quantity, unit_price_minor, product_name_snapshot); inventory(sku, available, reserved, version); payments(id, order_id, provider_operation_id unique, state, amount_minor); operations(tenant_id, key, request_hash, result); outbox(event_id, aggregate_id, schema_version, payload); inbox(consumer_id, event_id). Add database checks and uniqueness for local invariants rather than relying only on code.

[[FIG:case-orders-detail]]

**Step-by-step flow.** Authenticate and check cart ownership. Recalculate authoritative price and availability. In one local transaction, claim the operation key, create pending order, reserve stock, and write an outbox event. A workflow worker calls the provider with a stable payment operation ID. On confirmation, transition the order and emit fulfillment work. On decline, release the reservation. On timeout, retain an unknown/pending state and reconcile before choosing compensation. A callback can race with polling; guard transitions by current state/version.

[[FIG:case-orders-sequence]]

**Failures and security.** A worker can crash after the provider commits and before local persistence. Provider idempotency plus querying the same operation resolves it; local SQL atomicity alone cannot. Compensation can fail and must be retried durably. Verify webhook signatures over raw bytes, scope every order query to its owner or an authorized support role, and keep payment credentials out of logs. Minimize sensitive payment-data handling through an appropriate provider integration.

**Scaling and trade-offs.** Keep transactions short and avoid provider calls while holding database locks. Scale catalog separately from checkout and isolate bulk analytics. Sharding by customer or tenant keeps many order operations local but complicates global inventory for shared products. A Saga exposes intermediate states and lacks global serial isolation; reservations and guarded transitions protect the specific business invariants.

**Validation and interview probe.** Run the concurrent idempotency and rollback labs. Test last-unit contention, delayed callbacks, duplicate callbacks, expired reservations, compensation failure, and provider response loss. Reconcile ledger totals after a restore. The deeper question is 'What happens if payment is confirmed after inventory expires?' A correct answer defines a business repair policy, not merely another retry.

### Case 4. Real-time chat

**Requirements and contract.** Support authenticated direct and group chat, durable message history, delivery progress, reconnect, and approximate presence. Separate accepted, delivered-to-device, and read-by-user states. Presence can be eventually consistent; durable messages need stronger storage semantics. Ordering is per conversation rather than one global order across every chat.

**Estimates.** Assume 100,000 concurrent connections, each consuming an assumed 20 KB of application/network state: about 2 GB before runtime overhead, TLS buffers, and message backlog. At 10,000 messages/second and 1 KB/message, raw ingress is 10 MB/second. Fanout depends on recipient count; a 1,000-member room costs far more delivery work than a direct message. Measure connection and message capacity separately.

[[FIG:case-chat-overview]]

Connection servers own live sockets. A routing layer maps users to current connection locations. Durable history is independent of those sockets, allowing a replacement server to resume a conversation after a deployment or crash.

**API contracts.** POST /v1/conversations creates membership under authorization. A WebSocket message includes conversation_id, client_message_id, and body. The acknowledgment returns server_message_id and conversation_sequence only after the promised durable acceptance point. GET /v1/conversations/{id}/messages?after=sequence retrieves missed history with bounded pagination. Read receipts use their own monotonic cursor.

**Schema.** conversations(id, type), members(conversation_id, user_id, role, joined_at, left_at), messages(conversation_id, sequence, message_id, sender_id, client_message_id, body, created_at), and delivery_cursors(conversation_id, user_id, delivered_sequence, read_sequence). Enforce uniqueness on sender plus client_message_id within the chosen scope. Store presence separately with TTL because it is transient, not an authoritative membership record.

[[FIG:case-chat-detail]]

**Step-by-step flow.** Authenticate the socket and authorize conversation membership for each operation. Assign or obtain a conversation sequence, persist the message, acknowledge its stable ID, publish delivery work, and fan out to current socket owners. Recipients advance cursors after processing. On reconnect, the client resends unacknowledged client IDs and requests history after its cursor. A duplicate send returns the existing message; a lost live push is recovered from history.

[[FIG:case-chat-sequence]]

**Failures and security.** A socket server crash loses live connections but not accepted history. Bound send buffers for slow clients and disconnect with a resumable cursor when needed. Verify browser Origin and avoid long-lived credentials in URLs. Recheck membership after removal, define token expiry on established connections, and scan attachments through an isolated pipeline. End-to-end encryption is a separate product decision with search, moderation, and recovery consequences.

**Scaling and trade-offs.** Partition messages and sequencing by conversation, with special handling for very large rooms. Use shared delivery infrastructure to reach users connected to different hosts. Avoid a global sequence bottleneck. Sticky routing may reduce directory lookups but cannot replace durable state and reconnect logic. Approximate presence should not be used as proof a message was read.

**Validation and interview probe.** Disconnect after persistence but before acknowledgment, replay client IDs, remove a member during a live session, and simulate a slow recipient. Measure reconnect storms during rolling updates. Ask how a hot room is split while preserving per-room ordering; the answer must explicitly choose sequencing ownership and fanout strategy.
