# System Design Master Handbook

A complete study package covering the original 111 numbered topics, fifteen learning parts, eight design case studies, executable local labs, editable diagrams, revision material, and assessments.

## Open and navigate

Start with [the illustrated offline HTML edition](SYSTEM_DESIGN_MASTER_HANDBOOK.html), [the PDF](SYSTEM_DESIGN_MASTER_HANDBOOK.pdf), or [the full Markdown source](SYSTEM_DESIGN_MASTER_HANDBOOK.md). HTML images are local; keep this folder together. Markdown uses rendered PNGs so diagrams remain visible in viewers without Mermaid support. Editable Mermaid and SVG sources are in diagrams/. Use the PDF bookmarks/table of contents or the original topic numbers to navigate.

## Prerequisites

Basic programming, exceptions, simple data structures, SQL fundamentals, HTTP request/response vocabulary, and basic process/thread concepts. Part I supplies the production-system foundations. You do not need cloud credentials, a GPU, or Kubernetes to begin. Python 3.11+ runs the standard-library labs.

## Study rhythm

Plan roughly 8-12 focused hours per week for the first pass, then revisit advanced topics over subsequent months. A typical day: 25 minutes reading, 15 minutes drawing the mechanism from memory, 30 minutes on a lab or design question, and 10 minutes recording mistakes. Every week, reserve one session for an incident scenario and one for closed-book revision. Twelve weeks is a roadmap, not a guarantee of mastery; extend the schedule when an invariant or failure case remains unclear.

## Twelve-week roadmap

| Week | Focus | Reading | Practical outcome |
|---|---|---|---|

| 1 | Foundations and request paths | Part I; Topics 4, 11, 91, 92, 97, 98 | Draw one request; run arithmetic and framing labs. |

| 2 | Reliable APIs | Part II; Topics 1, 3, 5, 10, 12, 13, 14 | Build admission, retry, and idempotency tests. |

| 3 | Relational data | Part III through Topics 25-31, 36, 37 | Run local transaction labs; inspect PostgreSQL plans when available. |

| 4 | Messaging and distributed state | Part IV; Topics 32-35, 95, 96 | Build outbox/inbox and Saga failure experiments. |

| 5 | Concurrency and performance | Part V | Reproduce races, deadlocks, queue growth, and tail latency. |

| 6 | Caching and scale | Part VI; Topics 89, 90 | Design freshness, stampede control, and capacity budgets. |

| 7 | Containers and delivery | Part VII; Topics 81, 82 | Package the API; review mixed-version rollout and probe behavior. |

| 8 | Observability and reliability | Part VIII | Define SLIs/SLOs, budget policy, dashboards, traces, and alerts. |

| 9 | Identity and security | Part IX | Run defensive tests and draw trust boundaries. |

| 10 | Protocols, evolution, infrastructure | Parts X-XI | Design webhook replay, API evolution, IaC, and recovery. |

| 11 | Operations and ML serving | Parts XII-XIII | Run incident table-tops and deploy the local toy inference API. |

| 12 | Integrated system design | Parts XIV-XV | Complete eight case reviews and the final integrated assessment. |

## Chapters and topics

- Part I. Foundations of Production Systems

- Part II. Backend Architecture and API Reliability: [1. Rate Limiting](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-001), [3. Load Balancing](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-003), [4. Reverse Proxies](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-004), [5. API Gateways](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-005), [10. Circuit Breakers](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-010), [11. Timeouts](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-011), [12. Retries](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-012), [13. Exponential Backoff](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-013), [14. Idempotency](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-014).

- Part III. Databases and Data Management: [25. Database Indexing](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-025), [26. Query Optimization](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-026), [27. N+1 Queries](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-027), [28. Connection Pooling](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-028), [29. Read Replicas](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-029), [30. Sharding](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-030), [31. Partitioning](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-031), [32. Replication](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-032), [36. Optimistic Locking](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-036), [37. Pessimistic Locking](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-037), [81. Database Migrations](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-081), [82. Schema Versioning](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-082).

- Part IV. Distributed Systems and Messaging: [15. Message Queues](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-015), [16. Pub/Sub](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-016), [17. Event-Driven Architecture](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-017), [18. Distributed Transactions](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-018), [19. Saga Pattern](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-019), [20. Dead Letter Queues](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-020), [21. Cron Jobs](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-021), [33. Leader Election](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-033), [34. CAP Theorem](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-034), [35. Eventual Consistency](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-035), [38. Distributed Locks](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-038), [95. Network Partitions](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-095), [96. Clock Skew](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-096).

- Part V. Concurrency, Runtime, and Performance: [39. Race Conditions](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-039), [40. Deadlocks](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-040), [41. Memory Leaks](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-041), [42. Garbage Collection](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-042), [43. Thread Safety](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-043), [44. Backpressure](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-044), [89. Cold Starts](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-089), [90. Serverless Limits](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-090), [91. Latency](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-091), [92. Throughput](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-092), [93. P99 Latency](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-093), [94. Tail Latency](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-094).

- Part VI. Scaling, Caching, and Delivery: [2. Caching](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-002), [45. Autoscaling](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-045), [46. Horizontal Scaling](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-046), [47. Vertical Scaling](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-047), [48. CDN](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-048), [49. Edge Caching](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-049), [50. Cache Invalidation](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-050).

- Part VII. Containers, Kubernetes, and Delivery Engineering: [6. CI/CD](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-006), [7. Docker](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-007), [8. Kubernetes](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-008), [9. Service Discovery](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-009), [51. Feature Flags](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-051), [52. Blue-Green Deployment](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-052), [53. Canary Releases](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-053), [54. Rolling Deployments](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-054), [55. Rollbacks](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-055), [56. Health Checks](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-056), [57. Liveness and Readiness Probes](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-057), [106. Helm Charts](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-106), [107. Build Caching](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-107), [108. Dependency Hell](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-108).

- Part VIII. Observability and Site Reliability Engineering: [58. Monitoring](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-058), [59. Logging](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-059), [60. Distributed Tracing](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-060), [61. Metrics](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-061), [62. Alerts](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-062), [63. SLOs](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-063), [64. SLIs](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-064), [65. Error Budgets](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-065), [66. Observability](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-066).

- Part IX. Application Security and Identity: [67. Secrets Management](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-067), [68. IAM](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-068), [69. OAuth](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-069), [70. JWT Rotation](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-070), [71. TLS](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-071), [72. Encryption at Rest](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-072), [73. Encryption in Transit](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-073), [74. WAF](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-074), [75. DDoS Protection](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-075), [76. CORS](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-076), [77. CSRF](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-077), [78. SQL Injection](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-078), [79. XSS](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-079), [80. SSRF](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-080).

- Part X. Networking, Communication, and API Evolution: [22. WebSockets](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-022), [23. Long Polling](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-023), [24. Server-Sent Events](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-024), [97. DNS](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-097), [98. TCP vs UDP](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-098), [99. HTTP/2 and HTTP/3](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-099), [100. gRPC](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-100), [101. Webhooks](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-101), [102. API Versioning](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-102), [103. Semantic Versioning](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-103).

- Part XI. Infrastructure, Cloud, and Disaster Recovery: [83. Disaster Recovery](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-083), [84. Backups](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-084), [85. Failover](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-085), [86. Multi-Region Deployment](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-086), [87. Chaos Engineering](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-087), [88. Cost Optimization](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-088), [104. Infrastructure as Code](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-104), [105. Terraform](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-105).

- Part XII. Production Operations and Incident Management: [109. Production Incidents](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-109), [110. On-Call](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-110), [111. Postmortems](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-111).

- Part XIII. AI/ML Systems Engineering

- Part XIV. Eight End-to-End System Design Case Studies

- Part XV. Assessments, Practice, Sources, and Implementation Appendix

## Study files

- [Quick revision for all topics](QUICK_REVISION.md)
- [Interview questions with model answers](INTERVIEW_QUESTIONS.md)
- [Glossary](GLOSSARY.md)
- [Projects, labs, and incident scenarios](PROJECTS_AND_LABS.md)
- [Example setup and actual outputs](examples/README.md)
- [Visual index](VISUAL_INDEX.md)
- [Coverage CSV](coverage.csv) and [coverage JSON](coverage.json)
- [Verification report and limitations](VERIFICATION_REPORT.md)
- [Complete file inventory](FILE_INDEX.md)

## Progress checklist

Mark a topic after you can explain its mechanism, trace a failure, answer a scenario question, and complete or justify its practical exercise. A checked box is your learning progress, not the automated coverage audit.

- [ ] [1. Rate Limiting](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-001)

- [ ] [2. Caching](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-002)

- [ ] [3. Load Balancing](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-003)

- [ ] [4. Reverse Proxies](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-004)

- [ ] [5. API Gateways](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-005)

- [ ] [6. CI/CD](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-006)

- [ ] [7. Docker](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-007)

- [ ] [8. Kubernetes](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-008)

- [ ] [9. Service Discovery](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-009)

- [ ] [10. Circuit Breakers](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-010)

- [ ] [11. Timeouts](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-011)

- [ ] [12. Retries](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-012)

- [ ] [13. Exponential Backoff](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-013)

- [ ] [14. Idempotency](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-014)

- [ ] [15. Message Queues](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-015)

- [ ] [16. Pub/Sub](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-016)

- [ ] [17. Event-Driven Architecture](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-017)

- [ ] [18. Distributed Transactions](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-018)

- [ ] [19. Saga Pattern](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-019)

- [ ] [20. Dead Letter Queues](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-020)

- [ ] [21. Cron Jobs](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-021)

- [ ] [22. WebSockets](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-022)

- [ ] [23. Long Polling](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-023)

- [ ] [24. Server-Sent Events](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-024)

- [ ] [25. Database Indexing](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-025)

- [ ] [26. Query Optimization](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-026)

- [ ] [27. N+1 Queries](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-027)

- [ ] [28. Connection Pooling](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-028)

- [ ] [29. Read Replicas](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-029)

- [ ] [30. Sharding](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-030)

- [ ] [31. Partitioning](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-031)

- [ ] [32. Replication](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-032)

- [ ] [33. Leader Election](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-033)

- [ ] [34. CAP Theorem](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-034)

- [ ] [35. Eventual Consistency](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-035)

- [ ] [36. Optimistic Locking](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-036)

- [ ] [37. Pessimistic Locking](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-037)

- [ ] [38. Distributed Locks](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-038)

- [ ] [39. Race Conditions](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-039)

- [ ] [40. Deadlocks](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-040)

- [ ] [41. Memory Leaks](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-041)

- [ ] [42. Garbage Collection](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-042)

- [ ] [43. Thread Safety](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-043)

- [ ] [44. Backpressure](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-044)

- [ ] [45. Autoscaling](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-045)

- [ ] [46. Horizontal Scaling](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-046)

- [ ] [47. Vertical Scaling](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-047)

- [ ] [48. CDN](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-048)

- [ ] [49. Edge Caching](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-049)

- [ ] [50. Cache Invalidation](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-050)

- [ ] [51. Feature Flags](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-051)

- [ ] [52. Blue-Green Deployment](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-052)

- [ ] [53. Canary Releases](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-053)

- [ ] [54. Rolling Deployments](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-054)

- [ ] [55. Rollbacks](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-055)

- [ ] [56. Health Checks](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-056)

- [ ] [57. Liveness and Readiness Probes](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-057)

- [ ] [58. Monitoring](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-058)

- [ ] [59. Logging](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-059)

- [ ] [60. Distributed Tracing](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-060)

- [ ] [61. Metrics](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-061)

- [ ] [62. Alerts](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-062)

- [ ] [63. SLOs](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-063)

- [ ] [64. SLIs](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-064)

- [ ] [65. Error Budgets](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-065)

- [ ] [66. Observability](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-066)

- [ ] [67. Secrets Management](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-067)

- [ ] [68. IAM](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-068)

- [ ] [69. OAuth](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-069)

- [ ] [70. JWT Rotation](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-070)

- [ ] [71. TLS](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-071)

- [ ] [72. Encryption at Rest](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-072)

- [ ] [73. Encryption in Transit](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-073)

- [ ] [74. WAF](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-074)

- [ ] [75. DDoS Protection](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-075)

- [ ] [76. CORS](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-076)

- [ ] [77. CSRF](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-077)

- [ ] [78. SQL Injection](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-078)

- [ ] [79. XSS](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-079)

- [ ] [80. SSRF](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-080)

- [ ] [81. Database Migrations](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-081)

- [ ] [82. Schema Versioning](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-082)

- [ ] [83. Disaster Recovery](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-083)

- [ ] [84. Backups](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-084)

- [ ] [85. Failover](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-085)

- [ ] [86. Multi-Region Deployment](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-086)

- [ ] [87. Chaos Engineering](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-087)

- [ ] [88. Cost Optimization](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-088)

- [ ] [89. Cold Starts](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-089)

- [ ] [90. Serverless Limits](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-090)

- [ ] [91. Latency](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-091)

- [ ] [92. Throughput](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-092)

- [ ] [93. P99 Latency](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-093)

- [ ] [94. Tail Latency](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-094)

- [ ] [95. Network Partitions](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-095)

- [ ] [96. Clock Skew](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-096)

- [ ] [97. DNS](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-097)

- [ ] [98. TCP vs UDP](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-098)

- [ ] [99. HTTP/2 and HTTP/3](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-099)

- [ ] [100. gRPC](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-100)

- [ ] [101. Webhooks](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-101)

- [ ] [102. API Versioning](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-102)

- [ ] [103. Semantic Versioning](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-103)

- [ ] [104. Infrastructure as Code](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-104)

- [ ] [105. Terraform](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-105)

- [ ] [106. Helm Charts](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-106)

- [ ] [107. Build Caching](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-107)

- [ ] [108. Dependency Hell](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-108)

- [ ] [109. Production Incidents](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-109)

- [ ] [110. On-Call](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-110)

- [ ] [111. Postmortems](SYSTEM_DESIGN_MASTER_HANDBOOK.md#topic-111)

## Rebuild and verify

The authoring sources and scripts are retained in build/. Run `python build/run_examples.py` to repeat local tests and demo capture. `python build/build_handbook.py` rebuilds Markdown and visuals when Pillow is installed; `python build/render_book.py` rebuilds HTML/PDF with Pillow, ReportLab, and pypdf. Font paths default to Windows Arial/Consolas and can be adjusted at the top of the renderer. Rebuilding diagrams uses the bundled graph renderer, not a Mermaid engine. See the verification report for the source-validation boundary and optional Mermaid CLI commands.
