# Verification report

Study edition: 18 October 2026. This report distinguishes checked artifacts from platform behavior that still requires its actual runtime.

## Coverage

The saved handbook covers all 111 original numbered topics in fifteen parts, with eight end-to-end case studies: URL shortener, rate-limited API, order and payment system, chat, notifications, video delivery, AI inference, and distributed job processing. Every numbered topic has fourteen teaching sections, a worked scenario, related-topic links, ten question-and-answer entries, and beginner/intermediate/advanced exercises with solution walkthroughs.

The assessment material contains 1,110 topic question-and-answer entries (555 conceptual, 333 scenario-based, 222 advanced follow-ups), 333 topic exercises, thirty practical labs, fifteen architecture exercises, ten incident scenarios, and a final integrated assessment. The separate interview bank reorganizes the same questions; it is not an additional set. The book repeats core ideas in revision and assessment contexts, so total word count is not a count of distinct technical claims.

Machine-readable traceability is in [coverage.csv](coverage.csv) and [coverage.json](coverage.json). All original IDs 1-111 occur exactly once in the coverage list. Automated checks require all fourteen teaching headings and ten answers per topic, all three exercise solution levels, and no unfinished figure markers or placeholder phrases. This is an author review plus automated checks, not an independent expert peer review.

## Figures

There are 194 distinct visual assets: 111 flowcharts, 41 architecture diagrams, seventeen sequence diagrams, eight state diagrams, and seventeen technical illustrations. All are embedded as local images in the main Markdown, HTML, and PDF. There are 193 editable SVGs and 177 matching Mermaid sources; the remaining illustration is an original generated raster image.

PNG files were decoded and verified. SVG files were parsed as XML, and every text label was checked against its canvas bounds. All 177 Mermaid files passed a strict structural checker for the exported flowchart, sequence, and state subset, including node/participant declarations and edge references. A Mermaid engine was not installed, so an actual Mermaid-engine rendering is **not verified**. The included PNG/SVG renderer uses the same graph definitions and provides the finished reading assets without requiring Mermaid.

To independently render a source with a locally installed Mermaid CLI, run `mmdc -i diagrams/topic-010.mmd -o breaker-mermaid.svg`. Repeat for the other sources, or use the bulk instructions in the build guide. The source and bundled renderer remain available for corrections.

## Executed examples

Python 3.12.14 on Windows ran 44 tests: **40 passed, four skipped, zero failures, zero errors**. The source targets Python 3.11+, but only 3.12.14 was executed here. Eight command-line demonstrations exited with status zero, and their actual output is saved in [examples/actual_outputs/](examples/actual_outputs/). The ninth module is the HTTP inference application.

Executed checks include token budgets, refill boundaries, TTL and eviction, circuit-breaker transitions, retry deadlines, jitter bounds, routing, versioned projections, deterministic quorum arithmetic, concurrent SQLite idempotency, payload mismatch, tenant key scope, atomic stock updates, rollback, outbox/inbox deduplication, backup restoration, Saga ambiguity/compensation, DLQ behavior, fencing, bounded pools and queues, deadlock-cycle detection, percentile arithmetic, safe parameter binding, ownership checks, CORS matching, CSRF comparison, webhook tampering/expiry, URL allowlisting, partial stream framing, schema adaptation, incident recovery, and the inference API's parsing, authentication, validation, prediction/cache, health, and metrics handlers. Authentication tests include non-ASCII invalid input.

The four skipped tests use real loopback HTTP connections, which this execution environment blocks. Equivalent handler cases execute through in-memory request streams using the actual HTTP parser and handler classes. This verifies handler behavior but does not test network transport, connection lifecycle, or server capacity. To run the additional socket checks in an unrestricted local environment, set `RUN_SOCKET_TESTS=1` before running the test command in [examples/README.md](examples/README.md).

## Configuration boundaries

The PostgreSQL SQL, Dockerfile, Kubernetes manifests, Helm templates, Nginx configuration, Terraform example, CI workflow, and protobuf contract were reviewed for consistency with their examples. They were **not executed in their production runtimes**. Python files were parsed successfully. `kubectl kustomize` successfully parsed and serialized the Kubernetes ConfigMap, Service, Deployment, and HorizontalPodAutoscaler locally. This does not validate API admission, cluster policy, or running behavior. No Helm/protobuf/Terraform parser validation or CI workflow execution is claimed.

Docker CLI was present, but its Linux daemon was unavailable. A Kubernetes client was present; no cluster apply or rollout was performed. PostgreSQL, Helm, Terraform, Nginx, and a protobuf compiler were unavailable. No cloud resources were provisioned, no real payment/email provider was contacted, and no load, replication, TLS, OAuth provider, GPU, or multi-region experiment was executed.

The inference service uses Python's teaching HTTP server and a deterministic toy score, with process-local limits and a static demo identity. It is not a production inference server or a trained predictive model. Distributed guarantees described in the textbook are design reasoning; a local simulation does not establish them for an actual deployment.

## Reproduction and evidence

Open [the examples guide](examples/README.md) for dependencies, commands, expected outputs, and environment setup. Build sources and machine-readable test, rendering, and structural-audit records are retained in build/. [The file index](FILE_INDEX.md) maps the deliverables and their purposes. SHA-256 inventory records are supplied with the final package for integrity checks, not as a claim of provenance or independent certification.

## Final document quality checks

The complete PDF has **734 pages**, including the full implementation appendix and captured demonstration output. All 111 topic headings were found at their recorded PDF destinations. All 194 figures occur as embedded PDF images, matching the manifest. All 734 pages were checked for text outside the page boundaries: none was found across 1,621,723 extracted characters, and there were no empty pages.

Forty-one selected pages were rendered with Poppler and visually inspected: cover, contents, all fifteen part openings, selected topic explanations, architecture/state/sequence/illustration pages, case-study material, code and configuration pages, and the final page. Contact-sheet review was supplemented with full-page review of representative diagrams and source listings. This is a sampled visual inspection, not a claim that all 734 pages were individually examined by a human. The automated geometry check covered every page.

The final Markdown/HTML audit checks local file paths and anchors, topic structure, PNG decoding, SVG XML and text bounds, Python parsing, and exported Mermaid graph references. The exact current link count and zero-error result are retained in build/audit_results.json. HTML has a local chapter filter, local figures, and no required external assets. HTML source, links, anchors, and image files were checked; **browser runtime and visual verification remain unconfirmed** because a managed browser executable was unavailable and installed Edge failed to launch in the sandbox. The PDF supplies the visually checked reading edition.

Final defensive-code review also added checks for absent tenant identity, non-ASCII invalid credentials/signatures, non-string CSRF input, and boolean webhook timestamps. The final suite still reports forty passes and four skipped socket tests. Reports describe these local checks only; independent expert review, full Mermaid-engine rendering, browser interaction, and actual service/runtime integration remain follow-up verification tasks.
