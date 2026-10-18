from pathlib import Path
import ast
import csv
import hashlib
import json
import re
import shutil
import textwrap
import visuals

ROOT=Path(__file__).resolve().parent.parent
PACKAGED=Path(__file__).resolve().parent.name=='build'
WORK=Path(__file__).resolve().parent
OUT=ROOT if PACKAGED else ROOT/'outputs/system-design-master-handbook'
OUT.mkdir(parents=True,exist_ok=True)

PARTS=[
('II','Backend Architecture and API Reliability',[1,3,4,5,10,11,12,13,14]),
('III','Databases and Data Management',[25,26,27,28,29,30,31,32,36,37,81,82]),
('IV','Distributed Systems and Messaging',[15,16,17,18,19,20,21,33,34,35,38,95,96]),
('V','Concurrency, Runtime, and Performance',[39,40,41,42,43,44,89,90,91,92,93,94]),
('VI','Scaling, Caching, and Delivery',[2,45,46,47,48,49,50]),
('VII','Containers, Kubernetes, and Delivery Engineering',[6,7,8,9,51,52,53,54,55,56,57,106,107,108]),
('VIII','Observability and Site Reliability Engineering',[58,59,60,61,62,63,64,65,66]),
('IX','Application Security and Identity',[67,68,69,70,71,72,73,74,75,76,77,78,79,80]),
('X','Networking, Communication, and API Evolution',[22,23,24,97,98,99,100,101,102,103]),
('XI','Infrastructure, Cloud, and Disaster Recovery',[83,84,85,86,87,88,104,105]),
('XII','Production Operations and Incident Management',[109,110,111])]


def read_topics():
    topics=[]
    for file in sorted(WORK.glob('topics_*.txt')):
        for block in file.read_text(encoding='utf-8').split('@@')[1:]:
            lines=block.strip().splitlines();num,name=lines[0].split('|',1)
            record={'id':int(num),'name':name}
            for line in lines[1:]:
                key,value=line.split(': ',1);record[key]=value
            for field in ['E','A','M','W','T','F','D','X','V','R','L']:
                assert field in record,(num,field)
            topics.append(record)
    topics.sort(key=lambda x:x['id'])
    assert [t['id'] for t in topics]==list(range(1,112))
    assert sorted(n for _,_,ids in PARTS for n in ids)==list(range(1,112))
    overrides={38:'Worker requests ownership|Acquire lease and fencing token|Lease valid for work?|Write with token validation|Stop or reacquire safely|Renew or compare-and-release|Finish protected work',
      40:'Operation waits for lock|Build wait-for dependencies|Cycle detected?|Abort selected victim|Continue bounded waiting|Release resources as progress resumes|Restore progress',
      65:'Measure bad-event fraction|Calculate remaining budget and burn|Policy threshold crossed?|Change release and reliability priorities|Continue measured delivery|Observe changes and verify reliability|Review policy with stakeholders',
      78:'Untrusted query input|Bind values and restrict DB role|Identifiers from allowlist?|Execute parameterized statement|Reject unsupported query shape|Read only authorized rows|Return scoped rows and safe errors',
      79:'Untrusted content displayed|Identify output context and policy|Safe encoding or sanitizer applied?|Render inert or approved content|Reject unsafe rendering path|Observe CSP violations|Test browser behavior'}
    for t in topics:
        if t['id'] in overrides:t['V']=overrides[t['id']]
    return topics


TOPICS=read_topics();BY_ID={t['id']:t for t in TOPICS}
PART_FOR={n:f'Part {roman}. {title}' for roman,title,ids in PARTS for n in ids}


def first(text):
    return re.split(r'(?<=[.!?])\s+(?=[A-Z0-9])',text,maxsplit=1)[0]


def sentences(text):
    return re.split(r'(?<=[.!?])\s+(?=[A-Z0-9])',text)


def link(number,external=False):
    return f'[{number}. {BY_ID[number]["name"]}]('+('SYSTEM_DESIGN_MASTER_HANDBOOK.md' if external else '')+f'#topic-{number:03d})'


SOURCES=[
('postgres-isolation','PostgreSQL transaction isolation','https://www.postgresql.org/docs/current/transaction-iso.html',[18,36,37,39]),
('postgres-explain','PostgreSQL EXPLAIN','https://www.postgresql.org/docs/current/using-explain.html',[25,26,27]),
('k8s-probes','Kubernetes probe semantics','https://kubernetes.io/docs/concepts/workloads/pods/probes/',[8,56,57]),
('docker-stages','Docker multi-stage builds','https://docs.docker.com/build/building/multi-stage/',[7,107]),
('terraform-state','Terraform state','https://developer.hashicorp.com/terraform/language/state',[104,105]),
('helm-charts','Helm chart structure','https://helm.sh/docs/topics/charts/',[106]),
('sre-slo','Google SRE service-level objectives','https://sre.google/sre-book/service-level-objectives/',[63,64,65]),
('otel-signals','OpenTelemetry signals','https://opentelemetry.io/docs/concepts/signals/',[58,59,60,61,66]),
('oauth-bcp','RFC 9700 OAuth security guidance','https://www.rfc-editor.org/rfc/rfc9700.html',[69,70]),
('csrf','OWASP CSRF prevention','https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html',[77]),
('ssrf','OWASP SSRF prevention','https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html',[80]),
('sqli','OWASP SQL injection prevention','https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html',[78]),
('cors','MDN CORS guide','https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS',[76]),
('http2','RFC 9113 HTTP/2','https://www.rfc-editor.org/rfc/rfc9113.html',[99]),
('http3','RFC 9114 HTTP/3','https://www.rfc-editor.org/rfc/rfc9114.html',[99]),
('quic','RFC 9000 QUIC transport','https://www.rfc-editor.org/rfc/rfc9000.html',[98,99]),
('grpc','gRPC core concepts','https://grpc.io/docs/what-is-grpc/core-concepts/',[100]),
('semver','Semantic Versioning 2.0.0 specification','https://semver.org/',[103]),
('sqlite','Python sqlite3 reference','https://docs.python.org/3/library/sqlite3.html',[14,84])]

LAB_FUNCTION={1:('algorithms.py','TokenBucket'),2:('algorithms.py','TTLCache'),3:('algorithms.py','round_robin'),
10:('algorithms.py','CircuitBreaker'),11:('algorithms.py','retry_transient'),12:('algorithms.py','retry_transient'),13:('algorithms.py','jitter_delays'),
14:('orders.py','place_order'),15:('messaging.py','process_queue'),17:('orders.py','consume_notification'),19:('messaging.py','OrderSaga'),20:('messaging.py','process_queue'),21:('messaging.py','settle_once'),
24:('protocols.py','sse_event'),28:('concurrency.py','Pool'),30:('algorithms.py','shard_for'),33:('algorithms.py','quorum_available'),35:('algorithms.py','apply_newer'),
38:('concurrency.py','FencedLedger'),39:('concurrency.py','lost_update_schedule'),40:('concurrency.py','has_cycle'),41:('concurrency.py','retention_demo'),44:('concurrency.py','queue_model'),45:('concurrency.py','desired_workers'),
50:('algorithms.py','apply_newer'),51:('algorithms.py','enabled_for'),60:('performance.py','critical_path'),63:('performance.py','budget'),65:('performance.py','budget'),
68:('security.py','authorize'),76:('security.py','cors_origin'),77:('security.py','csrf_valid'),78:('security.py','safe_name_search'),80:('security.py','allowed_partner_url'),82:('protocols.py','read_order_v2'),
84:('orders.py','backup'),91:('performance.py','capacity'),92:('performance.py','capacity'),93:('performance.py','percentile'),94:('performance.py','fanout_slow_probability'),98:('protocols.py','take_messages'),101:('security.py','verify_webhook'),109:('incident_drill.py','recovery_complete')}

CONFIGS={4:'nginx.conf',6:'ci.yml',7:'Dockerfile',8:'k8s.yaml',9:'k8s.yaml',25:'database.sql',26:'database.sql',27:'database.sql',31:'database.sql',36:'database.sql',37:'database.sql',54:'k8s.yaml',57:'k8s.yaml',81:'database.sql',100:'service.proto',104:'main.tf',105:'main.tf',106:'helm/Chart.yaml',107:'Dockerfile'}


def snippet(file,symbol):
    text=(OUT/'examples'/file).read_text(encoding='utf-8');lines=text.splitlines()
    node=next(n for n in ast.parse(text).body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name==symbol)
    return '\n'.join(lines[node.lineno-1:node.end_lineno])


def interview(t):
    n,name=t['id'],t['name'];related=[int(x) for x in t['R'].split(',')]
    return [
    ('Conceptual','Beginner',f'A teammate wants to add {name.lower()} everywhere. What concrete need should justify it?',t['E']+' '+first(t['T'])),
    ('Conceptual','Intermediate',f'What must be represented or coordinated for {name.lower()} to work correctly?',t['M']),
    ('Conceptual','Beginner','Explain the analogy, then identify where it stops being a trustworthy model.',t['A']+' The implementation must still follow the explicit state and failure rules described in the mechanism; an analogy cannot establish a delivery, timing, or security guarantee.'),
    ('Conceptual','Intermediate',f'Which nearby alternative would you compare with {name.lower()}, and what changes the choice?',t['T']),
    ('Conceptual','Intermediate','How can an apparently functioning implementation still violate the intended contract?',t['F']),
    ('Scenario','Intermediate','Walk through the worked ShopStream example. What evidence establishes the outcome, and what remains an assumption?',t['W']+' Verify the stated state transition or measurement at the responsible boundary. The numerical values, when present, are assumptions or deterministic examples rather than vendor performance guarantees.'),
    ('Scenario','Advanced','You must validate this behavior before rollout. What experiment would expose a false correctness claim?',t['X']+' Record the starting state, injected condition, observed result, and invariant. A successful startup alone does not demonstrate the behavior under test.'),
    ('Scenario','Advanced',f'A change involving {name.lower()} produces a customer-visible regression. How would you investigate and choose a safe response?',t['F']+' '+t['D']),
    ('Advanced follow-up','Expert','Which hidden assumptions become important under failure, scale, or a changed workload?',t['D']),
    ('Advanced follow-up','Expert',f'How does this design interact with {BY_ID[related[0]]["name"].lower()} and {BY_ID[related[1]]["name"].lower()}?',
     first(t['M'])+' '+first(BY_ID[related[0]]['M'])+' '+first(BY_ID[related[1]]['M'])+' Specify which component owns each decision and trace a failure across the combined boundary. Do not infer one component\'s guarantee from another component\'s name.')]


FIGURES={}


def figure(key):
    f=FIGURES[key]
    source=f'[editable Mermaid](diagrams/{f["mermaid"]})' if f['mermaid'] else ('[editable SVG](diagrams/'+f['svg']+')' if f['svg'] else 'original generated illustration')
    return f'![Figure {f["number"]}. {f["title"]}](diagrams/{f["png"]})\n\n*Figure {f["number"]}. {f["title"]}.* {f["caption"]} Source: {source}.\n'


def expand_figures(text):
    return re.sub(r'\[\[FIG:([^\]]+)\]\]',lambda m:figure(m.group(1)),text)


EXTRA_VISUALS={
2:['arch-cache','seq-cache','state-cache'],3:['arch-proxy-lb'],5:['arch-gateway'],6:['arch-cicd','state-deploy'],7:['arch-docker'],8:['arch-kubernetes','seq-k8s'],
10:['state-breaker','ill-breaker'],11:['ill-budget'],13:['ill-backoff'],14:['state-payment'],15:['arch-queue','state-message','state-job'],16:['arch-pubsub'],17:['arch-sync-async','arch-microservices'],19:['arch-saga'],
25:['ill-index'],28:['ill-pool'],29:['arch-replication','seq-replica'],30:['arch-sharding'],32:['ill-replication'],44:['ill-queue','backpressure-analogy'],46:['ill-scaling'],48:['arch-cdn'],101:['seq-webhook'],18:['seq-saga'],
58:['arch-observability'],60:['seq-trace'],68:['arch-auth','seq-login'],69:['seq-oauth'],72:['ill-envelope'],74:['arch-secure-web'],81:['ill-migration'],
83:['arch-backup','ill-rpo'],86:['arch-regions'],93:['ill-latency'],94:['ill-fanout'],96:['ill-clock'],97:['arch-client'],104:['arch-iac'],109:['state-incident'],70:['state-token']}


def topic_text(t):
    n,name=t['id'],t['name'];related=[int(x) for x in t['R'].split(',')]
    e=sentences(t['E']);plain=e[0];problem=' '.join(e[1:])
    output=[f'<a id="topic-{n:03d}"></a>',f'### {n}. {name}',
            f'Prerequisites and related reading: '+', '.join(link(x) for x in related)+'.',
            '#### 1. Simple explanation',plain,
            '#### 2. The problem it solves',problem,
            '#### 3. Intuitive analogy',t['A'],
            '#### 4. Technical working mechanism']
    output+= [f'{i+1}. {s}' for i,s in enumerate(sentences(t['M']))]
    output+=['\n**Boundary and advanced reasoning.** '+t['D'],
             '#### 5. Architecture and diagrams',figure(f'topic-{n:03d}')]
    for key in EXTRA_VISUALS.get(n,[]):output.append(figure(key))
    output+=['#### 6. Step-by-step example']
    output +=[f'{i+1}. {s}' for i,s in enumerate(sentences(t['W']))]
    output+=['#### 7. Implementation']
    if n in LAB_FUNCTION:
        file,symbol=LAB_FUNCTION[n];code=snippet(file,symbol)
        output +=[f'The complete runnable module is [examples/{file}](examples/{file}); run `python {file}` from the examples directory. The following excerpt isolates `{symbol}`. Required imports, surrounding definitions, expected output, and limitations are in the complete module and [lab guide](examples/README.md).',
                   '```python\n'+code+'\n```',
                   f'Read the state changes in this excerpt alongside the mechanism above. The lab is a model of its stated boundary; it does not establish the behavior of a distributed deployment or an external provider. Check the assertions in [test_examples.py](examples/test_examples.py) and compare your output with [recorded outputs](examples/actual_outputs/).']
    elif n in CONFIGS:
        file=CONFIGS[n]
        output +=[f'Use the complete [configuration or SQL example](examples/{file}) and its setup/run instructions in [examples/README.md](examples/README.md). Read every field in the configuration against the mechanism above; file parsing and runtime behavior are different validation levels.',
                   'The configuration requires its named runtime. See the verification report before assuming it was executed here. Use a disposable local environment for database and orchestration exercises; the examples do not deploy cloud resources.']
    else:
        output +=['For this topic, the worked scenario and the exercise below are the direct practical implementation of the reasoning. A standalone toy implementation would hide important platform or protocol guarantees. Use the relevant official implementation or managed runtime for real deployment, and validate its actual contract.',
                  f'The associated [examples/{t["L"]}](examples/{t["L"]}) illustrates a related local boundary, not a full implementation of {name.lower()}. [The lab guide](examples/README.md) distinguishes executable simulations, configurations, and design exercises.']
    output+=['#### 8. Production use cases',problem+' '+first(t['W']),
             '#### 9. Advantages and disadvantages',t['T'],
             '#### 10. Common mistakes and debugging',t['F'],
             '#### 11. Comparison with related concepts',
             '| Decision | Engineering interpretation |\n|---|---|\n'+
             f'| What this topic contributes | {plain} |\n'+
             f'| Nearest alternatives and limits | {t["T"]} |\n'+
             f'| Combined design | Read {link(related[0])} and {link(related[1])}; identify which layer owns each invariant rather than assuming their guarantees are interchangeable. |',
             '#### 12. Interview preparation']
    for i,(kind,difficulty,q,answer) in enumerate(interview(t),1):
        output +=[f'**{n}.{i} - {kind}; {difficulty}. {q}**',f'**Model answer:** {answer}']
    output +=['**Common incorrect answer:** "Adding the component makes the guarantee automatic." This is wrong because the mechanism depends on specific state, boundaries, and failure assumptions. '+first(t['F']),
              '**A deeper interviewer probe:** Change the timing, workload, or failure condition described in the advanced answer. Ask which invariant still holds, what observation would disprove it, and whether the fallback changes the user contract. '+first(t['D']),
              '#### 13. Exercises and solution walkthroughs',
              f'**Beginner exercise:** Reproduce the worked example for {name.lower()} on paper. Record the initial state, each transition, and the result before reading the walkthrough.',
              '**Beginner solution:** '+t['W'],
              '**Intermediate exercise:** '+first(t['X'])+' Write the observable assertion and identify which component owns it.',
              '**Intermediate solution:** '+t['X']+' Use the provided lab where applicable; for platform behavior, record the runtime version and actual evidence instead of treating a diagram as a test.',
              '**Advanced exercise:** Extend the example to a failure or scale condition described below. State the guarantee you retain, the one you relax if necessary, and a safe recovery procedure.',
              '**Advanced solution:** '+t['D']+' '+first(t['F'])+' A complete solution identifies a detection signal, a bounded action, and a verification of the business outcome.',
              '#### 14. Key takeaways']
    points=[plain,first(t['M']),first(t['T']),first(t['F']),first(t['D'])]
    output +=['- '+p for p in points]
    output +=['\n**When to use it:** '+problem,
               '**Terminology:** See this topic\'s glossary entry and the linked related terms. **Continue with:** '+', '.join(link(x) for x in related)+'.']
    refs=[f'[{title}]({url})' for _,title,url,ids in SOURCES if n in ids]
    if refs:output +=['**Official verification references:** '+', '.join(refs)+'. These references verify the named protocol or platform details; the examples, diagrams, and numerical assumptions are original teaching material.']
    return '\n\n'.join(output)+'\n'


def read_practice():
    records=[]
    for block in (WORK/'practice.txt').read_text(encoding='utf-8').split('@@')[1:]:
        lines=block.strip().splitlines();header=lines[0].split('|')
        d={'id':header[0],'title':header[1],'difficulty':header[2] if len(header)>2 else 'Advanced'}
        for line in lines[1:]:k,v=line.split(': ',1);d[k]=v
        records.append(d)
    return records


def practice_markdown(records):
    lines=['# Projects and Labs','Use the thirty coding/configuration labs first, then the fifteen architecture exercises and ten incident table-tops. Solutions follow each task so you can compare a written attempt. Run only against local or explicitly authorized systems.']
    for prefix,title in [('LAB','Practical coding and configuration labs'),('DESIGN','Architecture-design exercises'),('INCIDENT','Production incident scenarios')]:
        lines+=['## '+title]
        for d in records:
            if not d['id'].startswith(prefix):continue
            lines +=[f'### {d["id"]}. {d["title"]} ({d["difficulty"]})','**Task:** '+d['Task'],'**Solution walkthrough:** '+d['Solution']]
            if 'Artifact' in d:lines +=[f'**Associated file:** [examples/{d["Artifact"]}](examples/{d["Artifact"]}). See [setup and expected output](examples/README.md).']
    lines+=['## Final integrated assessment',
    'Design ShopStream for an assumed 2,000 peak API requests/second, 100 checkout requests/second, and 200 inference requests/second. A region can fail, a payment response can disappear, an old app version can remain during rollout, and one tenant can submit a large batch. Choose explicit freshness, availability, RPO, RTO, latency, and cost objectives. State what is excluded and identify assumptions needing measurement.',
    '**Required submission:** Produce requirements, estimates with units, three architecture views, API contracts, schemas and invariants, cache policy, admission/retry/deadline policy, order Saga, inference scheduling, migration and rollout plan, security boundaries, telemetry, recovery plan, and one incident runbook. Include a test that falsifies each critical correctness claim.',
    '**Model solution outline:** Begin with a modular transactional order core. Use an idempotent provider operation and reconciliation for ambiguous payment outcomes. Cache only permitted catalog/prediction representations with versioned scoped keys. Bound API and inference work independently, reserving interactive capacity. Use a durable outbox and idempotent consumers for notifications and jobs. Keep schema changes additive through mixed-version operation. Put identity and object authorization at explicit boundaries, rotate secrets, and protect every required transport hop. Measure pool wait, queue age, P99, user success, model quality, and cost separately. Select a regional ownership model with fencing and enough failover capacity, then demonstrate restoration and reconciliation against the chosen RPO/RTO.',
    '**Scoring rubric (100 points):** Requirements and assumptions 10; capacity arithmetic 10; data invariants and transaction boundaries 15; failure handling and recovery 15; security and privacy 10; performance and backpressure 10; deployment compatibility 10; observability and operations 10; trade-offs and test evidence 10. A design that claims exactly-once arbitrary external effects, uses a cache as the sole payment authority, or omits cross-tenant authorization must be corrected before it can pass, regardless of the diagram quality.',
    '**Expert follow-up:** Remove one of your assumptions: clocks are less accurate, one region has stale data, the provider shortens idempotency retention, or the new model doubles output length. Revisit the affected contract, arithmetic, and mitigation. A strong answer changes the design or states the weaker guarantee; it does not repeat the original component list.']
    return '\n\n'.join(lines)+'\n'


def examples_readme():
    lines=['# Runnable examples and environment guide',
    'The executable labs use Python 3.11+ and only its standard library. They were executed here with the bundled Python 3.12.14 runtime. No package installation, account, GPU, or cloud credential is needed. The inference score is deterministic teaching arithmetic, not a trained model. SQLite examples demonstrate local transactions; PostgreSQL behavior is taught separately in database.sql.',
    '## Quick start','Open a terminal in this examples directory. On Windows, `py -3` can replace `python` if that is how Python is installed.',
    '```text\npython -m unittest -v\npython algorithms.py\npython orders.py\npython messaging.py\npython concurrency.py\npython performance.py\npython security.py\npython protocols.py\npython incident_drill.py\n```',
    'The default suite executes algorithm, transaction, security, protocol, and in-process HTTP-handler tests. Real loopback socket tests are opt-in: set RUN_SOCKET_TESTS=1 and rerun. In this authoring sandbox, outgoing loopback connections were denied; those four tests were skipped, while the same HTTP handlers were tested in memory. If your managed temporary directory has restrictive cleanup permissions, set TMP and TEMP to a writable local scratch directory before running.',
    '## What each module teaches']
    descriptions={
    'algorithms':'Fake-time token refill, bounded TTL cache, circuit-breaker transitions, jitter, retry budget, round-robin routing, hash partitioning, stable feature cohorts, versioned projection updates, and quorum arithmetic. These are single-process models, not distributed implementations.',
    'orders':'Concurrent idempotency keys, payload conflict, guarded stock decrement, atomic outbox creation, local inbox deduplication, and SQLite backup/restore. Temporary demo data is removed after execution. No real payment or email is sent.',
    'messaging':'Duplicate delivery, poison-message attempts, DLQ, Saga confirmation/decline/unknown outcomes, compensation retry, and logical scheduled-period deduplication. State is in memory and is not restart-durable.',
    'concurrency':'Guaranteed pool-token release, stale-owner fencing, queue conservation, autoscaling arithmetic, a forced lost-update schedule, wait-for cycle detection, and traced memory retention. Pool tokens are not actual database connections.',
    'performance':'Nearest-rank percentiles, error budgets, independent fanout probability, Little\'s Law, and a simplified DAG critical path. Outputs are arithmetic, not measured vendor benchmarks.',
    'security':'Parameterized SQL, HTML text-context escaping, exact origin and partner allowlists, CSRF comparison, cross-tenant authorization, raw-body HMAC verification, and allowlisted structured logging. URL validation does not fetch anything and is not a complete arbitrary-destination SSRF defense.',
    'protocols':'Length-prefixed framing under partial reads, SSE formatting, retained-cursor replay, and an explicitly justified historical schema adapter. It does not implement TCP, QUIC, OAuth, or gRPC.',
    'incident_drill':'A timed offline response exercise showing why unknown payment outcomes remain part of recovery after HTTP metrics improve.'}
    for name,description in descriptions.items():
        recorded=(OUT/'examples/actual_outputs'/f'{name}.txt').read_text(encoding='utf-8').strip()
        lines +=[f'### {name}.py',description,f'Run `python {name}.py`. Important lines are documented in the module; the behavior tests name the intended invariants. Actual captured output:', '```text\n'+recorded+'\n```']
    lines +=['## Local inference API',
    'The server validates bounded finite feature arrays, authenticates a single demo key, limits requests, bounds in-flight model work, caches by model version and normalized input, and exposes /live, /ready, and /metrics. It uses ThreadingHTTPServer for teaching, which is not a hardened production server and does not itself bound all incoming connection threads. A production service needs a maintained server/runtime, transport security, tenant identity, global quotas if required, durable usage, robust shutdown/draining, privacy review, and realistic load tests.',
    'PowerShell:',
    "```powershell\n$env:DEMO_API_KEY = 'local-demo-key-change-me'\npython inference_api.py\n```",
    'In another local terminal:',
    "```powershell\n$headers = @{ 'X-API-Key' = 'local-demo-key-change-me' }\nInvoke-RestMethod -Uri 'http://127.0.0.1:8000/v1/predict' -Method Post -Headers $headers -ContentType 'application/json' -Body '{\"features\":[0,0]}'\nInvoke-RestMethod -Uri 'http://127.0.0.1:8000/ready'\n```",
    'Bash:',
    "```bash\nexport DEMO_API_KEY=local-demo-key-change-me\npython inference_api.py\n# In another terminal:\ncurl -H 'X-API-Key: local-demo-key-change-me' -H 'Content-Type: application/json' --data '{\"features\":[0,0]}' http://127.0.0.1:8000/v1/predict\n```",
    'Expected response: score 0.5, model_version toy-linear-v1, cached false on the first permitted request and true on a repeat within TTL. Incorrect credentials return 401, invalid inputs 400, quota exhaustion 429, and occupied inference slots 503. The cache and limiter are per process. Health/metrics endpoints are local demonstration endpoints; restrict exposure in a real deployment.',
    '## PostgreSQL lab',
    'Install a supported PostgreSQL runtime and psql, create a disposable empty database, and set DATABASE_URL to its connection URI without committing credentials. Run `psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f database.sql` in Bash, or `psql $env:DATABASE_URL -v ON_ERROR_STOP=1 -f database.sql` in PowerShell. Expect 100,000 orders, two different plan observations, one successful version-guarded update followed by zero affected rows, and partition-pruning evidence. Exact plan choice and timings vary. The script creates handbook_lab and does not delete existing schemas. It was not executed here because no PostgreSQL server was available.',
    '## Container and local Kubernetes',
    'With a running Docker engine, run `docker build -t shopstream-inference:local .`, then `docker run --rm -p 127.0.0.1:8000:8000 -e DEMO_API_KEY=local-demo-key-change-me shopstream-inference:local`. The key is a disposable local example, not a production credential. Docker was installed here but its Linux engine was not running, so no image build is claimed.',
    'For a local Kubernetes cluster, first confirm `kubectl config current-context` names that intended local cluster and load the built image using the cluster\'s supported mechanism. Create the local secret with `kubectl create secret generic shopstream-demo-key --from-literal=api-key=local-demo-key-change-me`, then `kubectl apply -f k8s.yaml`. Inspect `kubectl rollout status deployment/shopstream-inference`, `kubectl get pods`, `kubectl get endpointslices`, and `kubectl describe hpa shopstream-inference`. Use `kubectl port-forward service/shopstream-inference 8000:80` for a local call. Do not point these teaching commands at an unrelated production cluster.',
    'HPA requires the metrics API. The local image tag must exist in the cluster runtime. The manifest references a Secret rather than embedding one, uses non-root and read-only-root settings, and has different startup/readiness/liveness roles. It does not supply a public Ingress, TLS certificate, cloud load balancer, full network policy, or durable application database. Those choices require the real deployment environment. Server-side admission and live probe behavior were not tested here.',
    '## Terraform, Helm, proxy, and CI examples',
    '`terraform fmt -check`, `terraform init`, `terraform validate`, and `terraform plan` inspect the built-in terraform_data example. Optional `terraform apply` creates local Terraform state and no cloud resource; review the plan first. Terraform was unavailable here. Keep state and plan files private and out of source control when they contain sensitive values.',
    '`helm lint helm` and `helm template shopstream helm` render the local chart. Inspect labels, secret references, ports, resource settings, and probes. A local installation uses `helm upgrade --install shopstream helm` only after the image and Secret are ready in the intended context. Helm was unavailable here; rendered chart output and cluster execution remain verification tasks.',
    '`nginx -t -c <absolute-path-to-nginx.conf>` validates the supplied isolated local proxy configuration when Nginx is installed. It listens only on 127.0.0.1:8080 and forwards to the local API. It deliberately provides no fake certificate or pretend production TLS configuration. For real TLS, use valid issued certificates, verified hostnames, current maintained server guidance, and an explicit upstream transport policy.',
    'Copy ci.yml into .github/workflows/labs.yml in a repository whose examples directory matches its working-directory. It runs tests and builds a local image but does not publish or deploy. Review and pin third-party action commits for a real privileged release pipeline. service.proto is a contract example: install a compatible protobuf/gRPC toolchain and language plugin before generating stubs; no server implementation or compiler execution is claimed here.',
    '## Test boundary and next experiments',
    'See [../VERIFICATION_REPORT.md](../VERIFICATION_REPORT.md) for exact results. Passing deterministic tests does not prove cloud quotas, broker delivery, database replication, TLS configuration, distributed coordination, or production capacity. Extend the labs using the thirty tasks in [../PROJECTS_AND_LABS.md](../PROJECTS_AND_LABS.md), and record each added experiment with runtime, input, fault, expected invariant, and actual outcome.']
    return '\n\n'.join(lines)+'\n'


def glossary():
    lines=['# Glossary','The 111 topic entries retain the original topic numbers. Additional terms below support the mechanisms and case studies.']
    for t in TOPICS:lines +=[f'## {t["name"]} ({t["id"]})',first(t['E'])+' See '+link(t['id'],True)+'.']
    terms={
    'ACID':'Atomicity, consistency, isolation, and durability: distinct transaction properties with implementation-specific failure and concurrency boundaries.',
    'Acknowledgment':'A protocol message confirming a defined milestone. A broker acknowledgment, socket acknowledgment, and business completion acknowledgment mean different things.',
    'Admission control':'A decision to accept, defer, or reject work before expensive resource consumption.',
    'Artifact digest':'A cryptographic identifier for exact artifact bytes, unlike a mutable tag or compatibility version.',
    'Atomicity':'All changes within a stated transaction boundary commit together or are rolled back.',
    'Backfill':'A controlled process that populates new or corrected data for historical records.',
    'Blast radius':'The set of users, data, and components a failure or change can affect.',
    'Cardinality':'The number of distinct values or combinations; high metric-label cardinality can create excessive time-series storage.',
    'Causality':'A relationship where one event can influence another, distinct from apparent ordering by unsynchronized clocks.',
    'Cold start':'Initialization before useful service, including runtime, artifact, dependency, and model setup.',
    'Compensation':'A new business action intended to repair an earlier committed effect; it may not restore the exact original world.',
    'Consensus':'Agreement on a value or ordered log under stated fault and timing assumptions, often using intersecting quorums.',
    'Control plane':'Components that configure or coordinate the system; the data plane handles ordinary workload traffic.',
    'Deadline':'An absolute end to a remaining work budget, propagated across attempts rather than reset at every hop.',
    'Durability':'Preservation of accepted committed data under the storage and replication failures covered by the configuration.',
    'ETag':'An HTTP representation validator that can support conditional reads or write preconditions.',
    'Fencing token':'An increasing ownership epoch enforced by the protected resource to reject stale owners.',
    'Goodput':'Useful successful work per unit time, excluding rejected, duplicated, or otherwise unhelpful work.',
    'Head-of-line blocking':'A delay where one missing or unfinished item prevents progress of later items at a particular layer.',
    'Histogram':'A distribution represented by bucket counts; compatible bucket populations can be aggregated before estimating quantiles.',
    'Idempotency key':'A caller-supplied identifier for one logical operation, scoped and persisted under an explicit replay contract.',
    'Invariant':'A condition that must hold across all valid state transitions, such as nonnegative inventory or tenant isolation.',
    'JWKS':'JSON Web Key Set, a structured set of verification keys obtained from a trusted issuer configuration.',
    'Lease':'Time-bounded permission whose expiry does not physically stop a paused previous owner.',
    'Linearizability':'A consistency model in which operations behave as though each takes effect at one instant between invocation and response, respecting real-time order.',
    'Little\'s Law':'For a stable system and consistent boundaries, average number in system equals average arrival/completion rate times average time in system.',
    'MVCC':'Multiversion concurrency control: keeping versions so readers can observe an appropriate snapshot while writes proceed under defined rules.',
    'NAT':'Network address translation; many clients can share one public address, which affects IP-based rate-limit fairness.',
    'OIDC':'OpenID Connect, an identity layer built on OAuth flows; an ID token and an API access token have different purposes and audiences.',
    'Outbox / inbox':'Local transaction patterns for committed event publication intent and consumer deduplication coupled to local effects.',
    'PKCE':'Proof Key for Code Exchange, binding an authorization-code exchange to a verifier whose challenge was sent earlier.',
    'Projection':'A derived read model built from authoritative state or events; it can lag and may need rebuilding.',
    'Quorum':'A required subset of participants. Safety depends on protocol rules and intersection assumptions, not only arithmetic.',
    'RPO':'Recovery point objective: the tolerated gap between the failure time and the newest recoverable data.',
    'RTO':'Recovery time objective: the target duration to restore the defined useful service after disruption.',
    'Serialization anomaly':'A concurrent transaction outcome that cannot be explained by any serial execution of the transactions.',
    'SLA':'Service level agreement, typically a contractual commitment with defined consequences, distinct from an internal SLO.',
    'Split brain':'Conflicting active authorities accepting operations after coordination fails.',
    'Tail sampling':'Choosing traces after observing enough of their outcome, which requires buffering and may preserve unusual failures.',
    'TTL':'Time to live: an expiry duration whose meaning depends on the cache, DNS record, lease, or other object involved.',
    'WAL':'Write-ahead log, a durable change record used by databases for recovery and often replication.',
    'Write skew':'Concurrent transactions update different rows after reading a shared condition, jointly violating an invariant.',
    'Zero trust':'An architectural approach that requires explicit identity and authorization rather than treating network location alone as sufficient trust.'}
    for term,definition in sorted(terms.items(),key=lambda kv:kv[0].lower()):lines +=[f'## {term}',definition]
    return '\n\n'.join(lines)+'\n'


def roadmap():
    phases=[
    ('Foundations and request paths','Part I; Topics 4, 11, 91, 92, 97, 98','Draw one request; run arithmetic and framing labs.'),
    ('Reliable APIs','Part II; Topics 1, 3, 5, 10, 12, 13, 14','Build admission, retry, and idempotency tests.'),
    ('Relational data','Part III through Topics 25-31, 36, 37','Run local transaction labs; inspect PostgreSQL plans when available.'),
    ('Messaging and distributed state','Part IV; Topics 32-35, 95, 96','Build outbox/inbox and Saga failure experiments.'),
    ('Concurrency and performance','Part V','Reproduce races, deadlocks, queue growth, and tail latency.'),
    ('Caching and scale','Part VI; Topics 89, 90','Design freshness, stampede control, and capacity budgets.'),
    ('Containers and delivery','Part VII; Topics 81, 82','Package the API; review mixed-version rollout and probe behavior.'),
    ('Observability and reliability','Part VIII','Define SLIs/SLOs, budget policy, dashboards, traces, and alerts.'),
    ('Identity and security','Part IX','Run defensive tests and draw trust boundaries.'),
    ('Protocols, evolution, infrastructure','Parts X-XI','Design webhook replay, API evolution, IaC, and recovery.'),
    ('Operations and ML serving','Parts XII-XIII','Run incident table-tops and deploy the local toy inference API.'),
    ('Integrated system design','Parts XIV-XV','Complete eight case reviews and the final integrated assessment.')]
    lines=['# System Design Master Handbook','A complete study package covering the original 111 numbered topics, fifteen learning parts, eight design case studies, executable local labs, editable diagrams, revision material, and assessments.',
    '## Open and navigate','Start with [the illustrated offline HTML edition](SYSTEM_DESIGN_MASTER_HANDBOOK.html), [the PDF](SYSTEM_DESIGN_MASTER_HANDBOOK.pdf), or [the full Markdown source](SYSTEM_DESIGN_MASTER_HANDBOOK.md). HTML images are local; keep this folder together. Markdown uses rendered PNGs so diagrams remain visible in viewers without Mermaid support. Editable Mermaid and SVG sources are in diagrams/. Use the PDF bookmarks/table of contents or the original topic numbers to navigate.',
    '## Prerequisites','Basic programming, exceptions, simple data structures, SQL fundamentals, HTTP request/response vocabulary, and basic process/thread concepts. Part I supplies the production-system foundations. You do not need cloud credentials, a GPU, or Kubernetes to begin. Python 3.11+ runs the standard-library labs.',
    '## Study rhythm','Plan roughly 8-12 focused hours per week for the first pass, then revisit advanced topics over subsequent months. A typical day: 25 minutes reading, 15 minutes drawing the mechanism from memory, 30 minutes on a lab or design question, and 10 minutes recording mistakes. Every week, reserve one session for an incident scenario and one for closed-book revision. Twelve weeks is a roadmap, not a guarantee of mastery; extend the schedule when an invariant or failure case remains unclear.',
    '## Twelve-week roadmap','| Week | Focus | Reading | Practical outcome |\n|---|---|---|---|']
    lines +=[f'| {i} | {title} | {reading} | {project} |' for i,(title,reading,project) in enumerate(phases,1)]
    lines+=['## Chapters and topics','- Part I. Foundations of Production Systems']
    for roman,title,ids in PARTS:
        lines +=[f'- Part {roman}. {title}: '+', '.join(link(n,True) for n in ids)+'.']
    lines +=['- Part XIII. AI/ML Systems Engineering','- Part XIV. Eight End-to-End System Design Case Studies','- Part XV. Assessments, Practice, Sources, and Implementation Appendix',
    '## Study files','- [Quick revision for all topics](QUICK_REVISION.md)\n- [Interview questions with model answers](INTERVIEW_QUESTIONS.md)\n- [Glossary](GLOSSARY.md)\n- [Projects, labs, and incident scenarios](PROJECTS_AND_LABS.md)\n- [Example setup and actual outputs](examples/README.md)\n- [Visual index](VISUAL_INDEX.md)\n- [Coverage CSV](coverage.csv) and [coverage JSON](coverage.json)\n- [Verification report and limitations](VERIFICATION_REPORT.md)\n- [Complete file inventory](FILE_INDEX.md)',
    '## Progress checklist','Mark a topic after you can explain its mechanism, trace a failure, answer a scenario question, and complete or justify its practical exercise. A checked box is your learning progress, not the automated coverage audit.']
    lines +=[f'- [ ] {link(t["id"],True)}' for t in TOPICS]
    lines +=['## Rebuild and verify','The authoring sources and scripts are retained in build/. Run `python build/run_examples.py` to repeat local tests and demo capture. `python build/build_handbook.py` rebuilds Markdown and visuals when Pillow is installed; `python build/render_book.py` rebuilds HTML/PDF with Pillow, ReportLab, and pypdf. Font paths default to Windows Arial/Consolas and can be adjusted at the top of the renderer. Rebuilding diagrams uses the bundled graph renderer, not a Mermaid engine. See the verification report for the source-validation boundary and optional Mermaid CLI commands.']
    return '\n\n'.join(lines)+'\n'


def main():
    global FIGURES
    if not (OUT/'diagrams/manifest.json').exists() or '--visuals' in __import__('sys').argv:
        figures=visuals.build(TOPICS)
    else:figures=json.loads((OUT/'diagrams/manifest.json').read_text())
    for i,f in enumerate(figures,1):f['number']=i
    FIGURES={f['id']:f for f in figures}
    (OUT/'diagrams/manifest.json').write_text(json.dumps(figures,indent=2),encoding='utf-8')
    (OUT/'examples/README.md').write_text(examples_readme(),encoding='utf-8')
    records=read_practice();practice=practice_markdown(records)
    (OUT/'PROJECTS_AND_LABS.md').write_text(practice,encoding='utf-8')
    (OUT/'GLOSSARY.md').write_text(glossary(),encoding='utf-8')
    (OUT/'README.md').write_text(roadmap(),encoding='utf-8')
    intro=['# System Design Master Handbook','Backend Engineering, Distributed Systems, DevOps, Security, Production Operations, and AI/ML Serving',
           'Study edition | 18 October 2026 | Original topic identifiers 1-111',
           '## Contents','Part I supplies prerequisites and engineering foundations. Parts II-XII teach all 111 original topics. Part XIII connects them to AI/ML serving. Part XIV applies them in eight complete designs. Part XV contains practical assessment, official references, and the full implementation appendix.']
    for roman,title,ids in PARTS:
        intro.append(f'**Part {roman}. {title}**\n\n'+', '.join(link(n) for n in ids)+'.')
    main_text='\n\n'.join(intro)+'\n\n'+expand_figures((WORK/'foundations.md').read_text(encoding='utf-8'))
    coverage=[];interviews=['# Interview Questions and Model Answers',
       'There are 1,110 unique topic questions: 555 conceptual, 333 scenario-based, and 222 advanced follow-ups. They are the same question set embedded in the main handbook, reorganized here for independent revision. Difficulty tags identify Beginner, Intermediate, Advanced, and Expert. An additional ten incident scenarios and a final integrated assessment appear in PROJECTS_AND_LABS.md.']
    revision=['# Quick Revision','Use after studying the full topic. These notes intentionally omit the depth, diagrams, and exercises in the textbook.']
    for roman,title,ids in PARTS:
        main_text+=f'\n\n## Part {roman}. {title}\n\n'
        for number in ids:
            t=BY_ID[number];section=topic_text(t);main_text+=section
            wc=len(re.findall(r'\b[\w-]+\b',section));author_wc=sum(len(t[k].split()) for k in ['E','A','M','W','T','F','D','X'])
            assert author_wc>=250,(number,author_wc)
            coverage.append({'number':number,'topic':t['name'],'chapter':PART_FOR[number],
                'section_heading':f'{number}. {t["name"]}','anchor':f'topic-{number:03d}',
                'explanation_exists':True,'practical_example':'Worked scenario and three exercises; '+('runnable excerpt' if number in LAB_FUNCTION else 'configuration' if number in CONFIGS else 'conceptual/platform experiment justified'),
                'interview_questions':10,'teaching_sections':14,'diagram':f'diagrams/topic-{number:03d}.png',
                'reviewed':'Author mechanism/failure review; automated structure and link audit; independent expert review not performed',
                'authored_core_words':author_wc,'section_words_including_practice':wc})
    # Independent bank grouped by difficulty, with stable topic-question IDs.
    for difficulty in ['Beginner','Intermediate','Advanced','Expert']:
        interviews +=['## '+difficulty]
        for t in TOPICS:
            for i,(kind,level,q,answer) in enumerate(interview(t),1):
                if level==difficulty:
                    interviews +=[f'### {t["id"]}.{i} - {t["name"]} - {kind}',q,'**Model answer:** '+answer,
                       '**Avoid this mistake:** '+first(t['F']), '**Deeper probe:** '+first(t['D'])+' Explain what evidence would verify that boundary.']
    for t in TOPICS:
        revision +=[f'## {t["id"]}. {t["name"]}',first(t['E']),
            '**Mechanism:** '+first(t['M']), '**Trade-off:** '+first(t['T']), '**Trap:** '+first(t['F']),
            '**Recall test:** '+first(t['X']), '**Full topic:** '+link(t['id'],True)+'.']
    (OUT/'INTERVIEW_QUESTIONS.md').write_text('\n\n'.join(interviews)+'\n',encoding='utf-8')
    (OUT/'QUICK_REVISION.md').write_text('\n\n'.join(revision)+'\n',encoding='utf-8')
    main_text+='\n\n'+expand_figures((WORK/'ai.md').read_text(encoding='utf-8'))
    main_text+='\n\n'+expand_figures((WORK/'cases_1.md').read_text(encoding='utf-8'))
    main_text+='\n\n'+expand_figures((WORK/'cases_2.md').read_text(encoding='utf-8'))
    main_text+='\n\n## Part XV. Assessment, Reference, and Implementation Appendix\n\n'
    # Embed the entire practice guide with lower-level headings.
    practice_body=practice.split('\n',1)[1]
    practice_body=re.sub(r'^### ', '##### ', practice_body,flags=re.M)
    practice_body=re.sub(r'^## ', '### ', practice_body,flags=re.M)
    main_text+=practice_body
    main_text+='\n\n### Official references and verification scope\n\n'
    main_text+='The following primary or official documentation was consulted on 18 October 2026 for version-sensitive details. This textbook uses original explanations, examples, and diagrams; it does not reproduce official figures or promise provider-specific performance. Verify current runtime behavior before deployment.\n\n'
    for _,title,url,ids in SOURCES:main_text+=f'- [{title}]({url}) - related topics '+', '.join(map(str,ids))+'.\n'
    main_text+='\n\n### Complete runnable implementation appendix\n\n'
    main_text+='The following files are the full source used by the labs, not pseudocode. The setup guide and captured outputs follow them. Configurations require the named runtimes and have the explicit verification limits stated in the guide.\n\n'
    files=['algorithms.py','orders.py','messaging.py','concurrency.py','performance.py','security.py','protocols.py','inference_api.py','incident_drill.py','test_examples.py','database.sql','Dockerfile','k8s.yaml','nginx.conf','main.tf','ci.yml','service.proto','requirements-api.txt','helm/Chart.yaml','helm/values.yaml','helm/templates/deployment.yaml','helm/templates/service.yaml']
    for file in files:
        language='python' if file.endswith('.py') else 'sql' if file.endswith('.sql') else 'yaml' if file.endswith('.yaml') or file.endswith('.yml') else 'text'
        main_text+=f'\n\n#### Source file: examples/{file}\n\n```{language}\n'+(OUT/'examples'/file).read_text(encoding='utf-8')+'\n```\n'
    setup=examples_readme().replace('# Runnable examples and environment guide','### Environment, commands, and actual example outputs')
    setup=re.sub(r'^## ', '#### ',setup,flags=re.M)
    setup=setup.replace('](../VERIFICATION_REPORT.md)', '](VERIFICATION_REPORT.md)').replace('](../PROJECTS_AND_LABS.md)', '](PROJECTS_AND_LABS.md)')
    main_text+='\n\n'+setup
    # Unifying ASCII punctuation keeps PDF fonts and source tools predictable.
    main_text=main_text.replace('\u2014',' - ').replace('\u2013','-').replace('\u2011','-')
    (OUT/'SYSTEM_DESIGN_MASTER_HANDBOOK.md').write_text(main_text,encoding='utf-8')
    coverage.sort(key=lambda r:r['number'])
    (OUT/'coverage.json').write_text(json.dumps(coverage,indent=2),encoding='utf-8')
    with (OUT/'coverage.csv').open('w',newline='',encoding='utf-8') as file:
        writer=csv.DictWriter(file,fieldnames=list(coverage[0]));writer.writeheader();writer.writerows(coverage)
    index=['# Visual Index','All images are local and embedded in the main handbook. PNGs are the portable reading assets. SVG and Mermaid files are editable originals or matching graph sources. The PNG/SVG renderer and Mermaid exporter share graph definitions; a full Mermaid parser was not available during authoring.','| Figure | Title | Category | Topics | Source |','|---|---|---|---|---|']
    for f in figures:
        source=f'[Mermaid](diagrams/{f["mermaid"]})' if f['mermaid'] else f'[SVG](diagrams/{f["svg"]})' if f['svg'] else 'Generated original'
        index.append(f'| {f["number"]} | [{f["title"]}](diagrams/{f["png"]}) | {f["kind"]} | '+', '.join(map(str,f['topics']))+f' | {source} |')
    (OUT/'VISUAL_INDEX.md').write_text('\n\n'.join(index[:3])+'\n\n'+'\n'.join(index[3:])+'\n',encoding='utf-8')
    stats={'topics':len(TOPICS),'parts':15,'case_studies':8,'unique_interview_questions':1110,'conceptual_questions':555,'scenario_questions':333,'advanced_followups':222,
           'topic_exercises':333,'practical_labs':30,'architecture_exercises':15,'incident_scenarios':10,
           'figures':len(figures),'figure_categories':{k:sum(f['kind']==k for f in figures) for k in ['flowchart','architecture','sequence','state','illustration']},
           'main_words':len(re.findall(r'\b[\w-]+\b',main_text)),
           'authored_topic_core_words':sum(c['authored_core_words'] for c in coverage),
           'minimum_authored_topic_words':min(c['authored_core_words'] for c in coverage),
           'maximum_authored_topic_words':max(c['authored_core_words'] for c in coverage),
           'python_demo_modules':9,'configuration_and_contract_files':13}
    (WORK/'book_stats.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
    print(json.dumps(stats,indent=2))


if __name__=='__main__':main()
