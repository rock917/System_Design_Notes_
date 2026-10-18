"""Original SVG/PNG diagrams and matching editable Mermaid sources.
The graph renderer uses the same nodes/edges as the Mermaid exporter.
It does not claim to be the Mermaid rendering engine.
"""
from pathlib import Path
import html
import json
import math
import re
import textwrap
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = (ROOT if Path(__file__).resolve().parent.name == 'build' else ROOT / 'outputs/system-design-master-handbook') / 'diagrams'
OUT.mkdir(parents=True, exist_ok=True)
MANIFEST = []
FONT = 'C:/Windows/Fonts/arial.ttf'
BOLD = 'C:/Windows/Fonts/arialbd.ttf'
NAVY = '#153047'; TEAL = '#167D8D'; RED = '#A23D3D'; PALE = '#EAF3F6'; GRAY = '#536776'


class Canvas:
    def __init__(self, width=1200, height=850):
        self.w, self.h = width, height
        self.image = Image.new('RGB', (width, height), 'white')
        self.draw = ImageDraw.Draw(self.image)
        self.svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="white"/>']

    def text(self, x, y, value, size=24, color=NAVY, bold=False, anchor='mm'):
        font = ImageFont.truetype(BOLD if bold else FONT, size)
        self.draw.text((x, y), value, font=font, fill=color, anchor=anchor)
        align = 'middle' if anchor.startswith('m') else 'start'
        baseline = 'central' if anchor.endswith('m') else 'hanging'
        self.svg.append(f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" fill="{color}" font-weight="{700 if bold else 400}" text-anchor="{align}" dominant-baseline="{baseline}">{html.escape(value)}</text>')

    def lines(self, points, color=GRAY, width=3, dash=False, arrow=False):
        if dash:
            for a,b in zip(points, points[1:]):
                length = math.dist(a,b)
                for start in range(0, max(1,int(length)), 15):
                    t1,t2=start/max(1,length), min(start+8,length)/max(1,length)
                    self.draw.line([(a[0]+(b[0]-a[0])*t1,a[1]+(b[1]-a[1])*t1),
                                    (a[0]+(b[0]-a[0])*t2,a[1]+(b[1]-a[1])*t2)], fill=color,width=width)
        else:
            self.draw.line(points, fill=color, width=width)
        coords=' '.join(f'{x},{y}' for x,y in points)
        self.svg.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="{width}"'+(' stroke-dasharray="8 7"' if dash else '')+'/>')
        if arrow:
            end, previous = points[-1], points[-2]
            angle=math.atan2(end[1]-previous[1], end[0]-previous[0])
            wing=[end,(end[0]-14*math.cos(angle-.45),end[1]-14*math.sin(angle-.45)),
                  (end[0]-14*math.cos(angle+.45),end[1]-14*math.sin(angle+.45))]
            self.draw.polygon(wing,fill=color)
            self.svg.append(f'<polygon points="{" ".join(f"{x},{y}" for x,y in wing)}" fill="{color}"/>')

    def box(self,x,y,w,h,label,decision=False,kind='normal',size=23):
        fill = '#FFF3D8' if decision else ('#FBECEC' if kind=='failure' else PALE)
        stroke = RED if kind=='failure' else NAVY
        if decision:
            points=[(x,y-h/2),(x+w/2,y),(x,y+h/2),(x-w/2,y)]
            self.draw.polygon(points, fill=fill, outline=stroke, width=3)
            self.svg.append(f'<polygon points="{" ".join(f"{a},{b}" for a,b in points)}" fill="{fill}" stroke="{stroke}" stroke-width="3"/>')
        else:
            self.draw.rounded_rectangle((x-w/2,y-h/2,x+w/2,y+h/2),radius=12,fill=fill,outline=stroke,width=3)
            self.svg.append(f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="3"/>')
        wrap_width=max(12, int(w/(size*.54)) - (5 if decision else 2))
        lines=textwrap.wrap(label,width=wrap_width,break_long_words=False)
        for index,line in enumerate(lines):
            self.text(x,y+(index-(len(lines)-1)/2)*(size+5),line,size=size)

    def save(self,key):
        self.image.save(OUT/(key+'.png'))
        (OUT/(key+'.svg')).write_text(''.join(self.svg)+'</svg>',encoding='utf-8')


def add_manifest(key,title,kind,caption,topics=None,source=True):
    MANIFEST.append(dict(id=key,title=title,kind=kind,caption=caption,topics=topics or [],
                         png=key+'.png',svg=key+'.svg',mermaid=key+'.mmd' if source else None))


def flow(topic):
    number=topic['id']; labels=topic['V'].split('|'); key=f'topic-{number:03d}'
    title=f'{number}. {topic["name"]}: decision and recovery flow'
    c=Canvas(1200,950)
    c.text(600,40,title,size=29,bold=True)
    # A central success path and a distinct failure/alternative branch.
    coords=[(430,130),(430,255),(430,400),(430,550),(975,400),(430,705),(430,845)]
    widths=[610,610,610,610,320,610,610]
    heights=[76,82,170,90,150,90,90]
    for index,(x,y) in enumerate(coords):
        c.box(x,y,widths[index],heights[index],labels[index],decision=index==2,
              kind='failure' if index==4 else 'normal',size=22)
    def edge(a,b,label='',alt=False):
        x1,y1=coords[a];x2,y2=coords[b]
        if y1==y2:
            start=(x1+widths[a]/2,y1);end=(x2-widths[b]/2,y2)
            points=[start,end]
            lx,ly=(start[0]+end[0])/2,y1-24
        elif a==4:
            start=(x1,y1+heights[a]/2); end=(x2+widths[b]/2,y2)
            points=[start,(x1,y2),end];lx,ly=x1-60,y2-24
        elif abs(b-a)>1 and a!=2:
            start=(x1-widths[a]/2,y1);end=(x2-widths[b]/2,y2)
            points=[start,(65,y1),(65,y2),end];lx,ly=95,(y1+y2)/2
        else:
            start=(x1,y1+heights[a]/2);end=(x2,y2-heights[b]/2)
            points=[start,end];lx,ly=x1+45,(start[1]+end[1])/2
        c.lines(points,color=RED if alt else TEAL,dash=alt,arrow=True)
        if label:c.text(lx,ly,label,size=21,color=RED if alt else TEAL,bold=True)
    edges=[(0,1,''),(1,2,''),(2,3,'Yes'),(2,4,'No')]
    # Alternative-processing flows: cached answer vs a miss, existing state vs new work.
    alternative={2,14,15,21,23,34,42,48,49,97}
    # Both branches need durable finalization/recovery, not a silent error end.
    converge={10,18,19,22,25,29,32,35,40,45,50,51,55,56,59,60,61,62,63,64,65,66,68,74,75,82,86,91,92,93,94,95,96,98,99,100,102,103,107,108,109,111}
    if number in alternative:
        edges.extend([(3,6,''),(4,5,''),(5,6,'')])
    else:
        edges.extend([(3,5,''),(5,6,'')])
        if number in converge:edges.append((4,5,''))
    if number==15:
        edges=[(0,1,''),(1,2,''),(2,3,'Yes'),(2,4,'No'),(3,6,''),(4,5,'Exhausted'),(5,6,'')]
    if number==20:
        edges=[(0,1,''),(1,2,''),(2,3,'Yes'),(2,4,'No'),(4,5,''),(5,6,'')]
    for a,b,label in edges:edge(a,b,label,alt=(a==4 or b==4))
    # Nodes are re-painted to mask crossings under shapes and preserve sharp labels.
    for index,(x,y) in enumerate(coords):
        c.box(x,y,widths[index],heights[index],labels[index],decision=index==2,
              kind='failure' if index==4 else 'normal',size=22)
    c.text(600,923,'Solid arrows: normal progress. Dashed arrows: alternative or failure handling.',size=18,color=GRAY)
    c.save(key)
    source=['flowchart TD']
    for i,label in enumerate(labels):
        safe=label.replace('"',"'")
        source.append(f'  N{i}{{"{safe}"}}' if i==2 else f'  N{i}["{safe}"]')
    for a,b,label in edges:
        connector='-.->' if a==4 or b==4 else '-->'
        source.append(f'  N{a} {connector}'+(f'|{label}|' if label else '')+f' N{b}')
    (OUT/(key+'.mmd')).write_text('\n'.join(source)+'\n',encoding='utf-8')
    caption=f'Start at "{labels[0]}" and move to "{labels[1]}". At "{labels[2]}", the Yes branch goes to "{labels[3]}" and the No branch goes to "{labels[4]}". Follow the arrows to the terminal or recovery outcome; a dashed branch is not an implicit success.'
    add_manifest(key,title,'flowchart',caption,[number])


def architecture(key,title,labels,edges,caption,topics=None):
    c=Canvas(1200,720+len(edges)*36)
    c.text(600,42,title,29,bold=True)
    count=len(labels)
    columns=3 if count>6 else 2
    rows=math.ceil(count/columns)
    xs=[220,600,980] if columns==3 else [315,885]
    ys=[170+i*(420/max(1,rows-1)) for i in range(rows)]
    coords={i:(xs[i%columns],ys[i//columns]) for i in range(count)}
    w=310 if columns==3 else 400;h=110
    routes=[]
    def route(a,b):
        def ports(i):
            x,y=coords[i]
            return [((x-w/2,y),(x-w/2-18,y)),((x+w/2,y),(x+w/2+18,y)),
                    ((x,y-h/2),(x,y-h/2-18)),((x,y+h/2),(x,y+h/2+18))]
        def clear(points):
            for (x1,y1),(x2,y2) in zip(points,points[1:]):
                if x1!=x2 and y1!=y2:return False
                for x,y in coords.values():
                    left,right=x-w/2+1,x+w/2-1;top,bottom=y-h/2+1,y+h/2-1
                    if x1==x2 and left<x1<right and max(min(y1,y2),top)<min(max(y1,y2),bottom):return False
                    if y1==y2 and top<y1<bottom and max(min(x1,x2),left)<min(max(x1,x2),right):return False
            return True
        lanes_x=[30,1170]+[(xs[i]+xs[i+1])/2 for i in range(len(xs)-1)]
        lanes_y=[85,655]+[(ys[i]+ys[i+1])/2 for i in range(len(ys)-1)]
        candidates=[]
        for start,p in ports(a):
            for end,q in ports(b):
                middles=[[p,(q[0],p[1]),q],[p,(p[0],q[1]),q]]
                middles += [[p,(x,p[1]),(x,q[1]),q] for x in lanes_x]
                middles += [[p,(p[0],y),(q[0],y),q] for y in lanes_y]
                for mid in middles:
                    points=[start]+mid+[end]
                    points=[p for i,p in enumerate(points) if not i or p!=points[i-1]]
                    if not clear(points):continue
                    cost=sum(math.dist(p,q) for p,q in zip(points,points[1:]))+len(points)*8
                    for u,v in zip(points,points[1:]):
                        for old in routes:
                            for r,s in zip(old,old[1:]):
                                if u[0]==v[0]==r[0]==s[0] or u[1]==v[1]==r[1]==s[1]:cost+=50
                    candidates.append((cost,points))
        assert candidates,(key,a,b)
        return min(candidates,key=lambda item:item[0])[1]
    number_labels=[]
    for edge_number,(a,b,label,*style) in enumerate(edges,1):
        points=route(a,b);routes.append(points)
        start,end=max(zip(points,points[1:]),key=lambda pair:math.dist(*pair))
        dx,dy=end[0]-start[0],end[1]-start[1];length=math.hypot(dx,dy)
        options=[((start[0]+end[0])/2-dy/length*side,(start[1]+end[1])/2+dx/length*side) for side in (17,-17,0)]
        def label_cost(point):
            x,y=point
            return sum(100 for nx,ny in coords.values() if abs(x-nx)<w/2+14 and abs(y-ny)<h/2+14)+sum(100 for lx,ly,_ in number_labels if math.dist(point,(lx,ly))<29)
        lx,ly=min(options,key=label_cost)
        c.lines(points,dash=bool(style),arrow=True,color=GRAY if style else TEAL)
        number_labels.append((lx,ly,edge_number))
    for i,label in enumerate(labels):
        c.box(*coords[i],w,h,label,size=23)
    for lx,ly,edge_number in number_labels:
        c.draw.ellipse((lx-13,ly-14,lx+13,ly+14),fill='white')
        c.svg.append(f'<ellipse cx="{lx}" cy="{ly}" rx="13" ry="14" fill="white"/>')
        c.text(lx,ly,str(edge_number),size=24,color=TEAL,bold=True)
    c.text(600,680,'Numbered connections: source -> destination | message or responsibility',21,bold=True)
    for i,(a,b,label,*style) in enumerate(edges):
        text=f'{i+1}. {labels[a]} -> {labels[b]} | {label}'+(' (control / failure)' if style else '')
        c.text(70,720+i*36,text,size=21,anchor='lm',color=GRAY)
    c.save(key)
    lines=['flowchart TD']+[f'  N{i}["{label}"]' for i,label in enumerate(labels)]
    for a,b,label,*style in edges:
        lines.append(f'  N{a} '+('-.->' if style else '-->')+(f'|{label}|' if label else '')+f' N{b}')
    (OUT/(key+'.mmd')).write_text('\n'.join(lines)+'\n',encoding='utf-8')
    add_manifest(key,title,'architecture',caption,topics)


def sequence(key,title,participants,messages,caption,topics=None):
    width=1200;height=200+len(messages)*95
    c=Canvas(width,height)
    c.text(600,35,title,28,bold=True)
    xs=[110+i*(980/max(1,len(participants)-1)) for i in range(len(participants))]
    for i,name in enumerate(participants):
        c.lines([(xs[i],125),(xs[i],height-40)],dash=True,width=2)
        c.box(xs[i],92,190,60,name,size=21)
    lines=['sequenceDiagram']+[f'  participant P{i} as {name}' for i,name in enumerate(participants)]
    for i,(a,b,label,*failure) in enumerate(messages):
        y=185+i*95
        color=RED if failure else TEAL
        c.lines([(xs[a],y),(xs[b],y)],arrow=True,color=color,dash=bool(failure))
        # Two-line captions keep message labels readable within an A4 column.
        for j,line in enumerate(textwrap.wrap(label, width=max(22,int(abs(xs[b]-xs[a])/12)))):
            c.text((xs[a]+xs[b])/2,y-48+j*24,line,size=22,color=color)
        lines.append(f'  P{a}'+('-->>' if failure else '->>')+f'P{b}: {label}')
    c.save(key)
    (OUT/(key+'.mmd')).write_text('\n'.join(lines)+'\n',encoding='utf-8')
    add_manifest(key,title,'sequence',caption,topics)


ARCHITECTURES=[
('arch-client','Client-server and trust boundaries',['Browser','Edge proxy','Application','PostgreSQL'],[(0,1,'HTTPS'),(1,2,'trusted hop'),(2,3,'SQL')],'The browser reaches the proxy; the application performs authorized data access. Each hop has its own deadline and identity boundary.',[4,71]),
('arch-monolith','ShopStream: modular monolith',['Client','One API process','Catalog module','Orders module','PostgreSQL','Payment provider'],[(0,1,'request'),(1,2,'local call'),(1,3,'local call'),(2,4,'read'),(3,4,'transaction'),(3,5,'idempotent API')],'Modules share deployment and a local database transaction boundary. Payment is still a remote, independently failing dependency.',[18,46]),
('arch-microservices','ShopStream: explicit service boundaries',['Gateway','Catalog service','Orders service','Catalog store','Orders store','Payment adapter'],[(0,1,'browse'),(0,2,'checkout'),(1,3,'local data'),(2,4,'local data'),(2,5,'operation ID')],'Separate services own data and communicate through contracts. This adds independent scaling and independent failure states.',[17,19]),
('arch-proxy-lb','Reverse proxy and backend selection',['Client','Reverse proxy / LB','API replica A','API replica B','Session store','Database'],[(0,1,'HTTPS'),(1,2,'eligible route'),(1,3,'eligible route'),(2,4,'session'),(3,4,'session'),(2,5,'query'),(3,5,'query')],'The proxy selects a ready backend. Shared state and database capacity remain dependencies of both replicas.',[3,4]),
('arch-gateway','Gateway policy and object authorization',['Client','API gateway','Quota store','Order service','Identity keys','Orders database'],[(0,1,'credential'),(1,2,'atomic debit'),(1,4,'verify key','control'),(1,3,'principal'),(3,5,'owner-scoped SQL')],'Gateway authentication and quota precede service-level ownership checks. A gateway pass is not blanket authorization.',[5,68]),
('arch-cache','Local and shared cache placement',['Application','Local cache','Shared cache','Authoritative DB','Invalidation relay','Outbox'],[(0,1,'lookup'),(0,2,'lookup'),(0,3,'bounded miss'),(3,5,'same commit'),(5,4,'event'),(4,2,'invalidate','control')],'Local and shared caches reduce different costs. The source transaction and invalidation path determine freshness.',[2,50]),
('arch-queue','Durable queue and failure isolation',['Producer','Broker queue','Worker','Local effect store','Retry scheduler','DLQ'],[(0,1,'publish'),(1,2,'deliver'),(2,3,'commit effect'),(2,4,'transient failure','failure'),(4,1,'retry','control'),(2,5,'exhausted','failure')],'Acknowledge only after the promised durable effect. Retry and DLQ paths remain visible instead of being counted as completion.',[15,20]),
('arch-pubsub','Independent subscription progress',['Order publisher','Event topic','Notification subscription','Analytics subscription','Email worker','Projection worker'],[(0,1,'OrderPlaced'),(1,2,'copy'),(1,3,'copy'),(2,4,'deliver'),(3,5,'deliver')],'Each subscription has its own progress and failure handling. Consumers in one subscription can share work rather than each receiving every event.',[16]),
('arch-sync-async','Synchronous response and asynchronous completion',['Client','Order API','Order DB + outbox','Event relay','Job worker','Status API'],[(0,1,'command'),(1,2,'commit'),(2,3,'pending event'),(3,4,'job'),(4,2,'terminal state'),(0,5,'poll'),(5,2,'read status')],'Durable acceptance is an earlier milestone than business completion. A status API exposes the distinction.',[17,90]),
('arch-saga','Saga ownership and compensation',['Workflow store','Orchestrator','Inventory service','Payment adapter','Order service','Repair queue'],[(0,1,'resume state'),(1,2,'reserve / release'),(1,3,'pay / reconcile'),(1,4,'confirm / reject'),(1,5,'stuck compensation','failure')],'The orchestrator persists progress and handles unknown outcomes. Compensation is a retryable business action, not time reversal.',[18,19]),
('arch-replication','Primary and asynchronously applied replicas',['Writer','Primary database','Replication log','Replica A','Replica B','Reader'],[(0,1,'write'),(1,2,'append'),(2,3,'replay'),(2,4,'replay'),(5,3,'eligible read'),(5,1,'fresh read')],'Replica reads are selected by freshness requirements. Log transport and application can lag independently.',[29,32]),
('arch-sharding','Shard routing and hot ownership',['Request','Shard directory','Shard A','Shard B','Shard C','Rebalancer'],[(0,1,'key'),(1,2,'owner A'),(1,3,'owner B'),(1,4,'owner C'),(5,1,'epoch update','control')],'The directory maps a key to an owner. Rebalancing must fence old ownership before stale routers can write divergent data.',[30,31]),
('arch-docker','Container image and host boundary',['Image registry','Container runtime','Application container','Host kernel','Persistent volume','Host network'],[(0,1,'pull layers'),(1,2,'start process'),(2,3,'system calls'),(2,4,'mounted data'),(2,5,'packets')],'The container shares the host kernel. Durable storage and network configuration are outside its disposable writable layer.',[7]),
('arch-kubernetes','Kubernetes control and serving paths',['API server','Controllers','Scheduler','Kubelet / node','Ready Pods','Service endpoints'],[(0,1,'desired state','control'),(0,2,'unscheduled Pods','control'),(2,3,'placement','control'),(3,4,'start and probe','control'),(4,5,'readiness','control')],'Controllers reconcile desired state; kubelets run workloads. Service eligibility depends on readiness and endpoint updates.',[8,9,57]),
('arch-cicd','Immutable artifact promotion',['Source revision','Build and test','Artifact registry','Staging','Canary','Production'],[(0,1,'inputs'),(1,2,'digest'),(2,3,'same bytes'),(3,4,'verified promotion'),(4,5,'guardrails pass')],'One artifact digest moves through environments. Configuration and migration compatibility are reviewed alongside the binary.',[6,52,53,54]),
('arch-observability','Correlated telemetry pipeline',['Application','Metrics endpoint','Log shipper','Trace exporter','Collector','Query and alerts'],[(0,1,'counts'),(0,2,'events'),(0,3,'spans'),(1,4,'scrape'),(2,4,'batch'),(3,4,'batch'),(4,5,'bounded telemetry')],'Metrics, logs, and traces retain different information. Shared operation and release IDs make evidence joinable.',[58,59,60,66]),
('arch-auth','Identity and resource authorization',['Browser','Authorization server','Application session','API gateway','Resource service','Owned data'],[(0,1,'authorize'),(1,2,'code exchange'),(2,3,'credential'),(3,4,'verified principal'),(4,5,'ownership check')],'Login or delegated access establishes a principal. The final service still checks action and resource ownership.',[68,69,70]),
('arch-secure-web','Layered defensive application',['Browser','CDN / WAF','Gateway','Application','Restricted database','Secret manager'],[(0,1,'TLS'),(1,2,'filtered request'),(2,3,'authenticated call'),(3,4,'bound SQL'),(3,5,'workload identity','control')],'Filtering, authentication, authorization, safe query construction, and secret handling address different threats.',[67,74,78,79,80]),
('arch-cdn','CDN edge and protected origin',['User region A','User region B','Edge A','Edge B','Origin shield','Object origin'],[(0,2,'asset'),(1,3,'asset'),(2,4,'miss'),(3,4,'miss'),(4,5,'origin fetch')],'Nearby edges serve permitted copies. A miss converges on origin capacity, so cold-cache behavior needs its own test.',[48,49]),
('arch-regions','Multi-region authority and recovery',['Global routing','Region A API','Region B API','Writer A','Replica B','Fencing authority'],[(0,1,'normal route'),(0,2,'regional route'),(1,3,'write'),(3,4,'replicate'),(2,4,'eligible read'),(5,3,'authority','control'),(5,4,'promotion gate','control')],'A replica is not an independent writer until a safe authority transition occurs. Route availability and data consistency are separate decisions.',[83,85,86]),
('arch-backup','Backup, key access, and isolated restore',['Database','Backup process','Protected archive','Key manager','Isolated restore','Integrity validation'],[(0,1,'consistent capture'),(1,2,'encrypted copy'),(3,4,'authorized keys','control'),(2,4,'restore'),(4,5,'business invariants')],'Recovery needs both data and keys. Validation in isolation is evidence that the archived copy is actually usable.',[72,83,84]),
('arch-iac','Infrastructure plan and controlled apply',['Versioned configuration','Plan runner','Protected state','Reviewed plan','Provider API','Live resources'],[(0,1,'desired state'),(2,1,'identity mapping'),(1,3,'proposed diff'),(3,4,'approved apply','control'),(4,5,'create/update'),(5,2,'observed mapping','control')],'Configuration, state, proposed changes, and live resources are distinct. Access to state and apply credentials is restricted.',[104,105]),
('arch-feature-store','Offline and online feature consistency',['Raw events','Versioned transform','Offline feature dataset','Online feature store','Training pipeline','Inference service'],[(0,1,'input'),(1,2,'historical features'),(1,3,'materialize'),(2,4,'point-in-time join'),(3,5,'fresh lookup')],'Training and inference share a transformation contract but have different time and access requirements. Monitor materialization lag.',[2,35,50,82]),
('arch-ai-quality','Serving reliability and model quality',['Model artifact','Serving deployment','User outcomes','Reliability telemetry','Evaluation dataset','Quality review'],[(0,1,'verified version'),(1,2,'prediction'),(1,3,'latency/errors'),(0,5,'candidate'),(4,5,'versioned evaluation'),(2,5,'approved feedback','control')],'Operational success and useful predictions are evaluated independently, then combined in a release decision.',[53,63,66]),
('arch-production','ShopStream production reference architecture',['Client / CDN','Gateway + API replicas','Cache','Orders DB + outbox','Broker + workers','Payment provider','Telemetry','Backup / recovery','Identity / secrets'],[(0,1,'HTTPS'),(1,2,'catalog lookup'),(1,3,'transaction'),(3,4,'events'),(4,5,'operation ID'),(1,6,'signals','control'),(3,7,'protected copy'),(8,1,'identity','control')],'Requests, durable state, asynchronous work, telemetry, and recovery are separate paths. Shared dependencies remain explicit.',[1,2,3,14,17,67,83])
]


CASE_DATA={
'url':('URL shortener',['Client','Redirect / create API','Mapping cache','Links database','Analytics queue','Analytics worker'],[(0,1,'request'),(1,2,'lookup'),(1,3,'create or miss'),(1,4,'click event'),(4,5,'aggregate')],['Client','API','Cache','Database'],[(0,1,'GET short code'),(1,2,'Lookup permitted mapping'),(2,1,'Miss',1),(1,3,'Read mapping and policy'),(3,1,'Versioned destination'),(1,2,'Cache with bounded TTL'),(1,0,'Redirect with Location')]),
'api':('Rate-limited API',['Tenant client','Policy gateway','Atomic quota store','Application workers','Database pool','Usage ledger'],[(0,1,'credential'),(1,2,'cost debit'),(1,3,'admitted request'),(3,4,'bounded query'),(3,5,'actual usage')],['Client','Gateway','Limiter','Service'],[(0,1,'Authenticated request'),(1,2,'Atomic tenant-cost debit'),(2,1,'Allow or reject'),(1,3,'Admit within capacity'),(3,1,'Result or bounded failure'),(1,0,'200 or explicit 429 / 503')]),
'orders':('Orders and payments',['Buyer','Order API','Orders + inventory DB','Outbox relay','Saga worker','Payment provider'],[(0,1,'checkout key'),(1,2,'local commit'),(2,3,'pending event'),(3,4,'work'),(4,5,'provider operation ID'),(4,2,'guarded transition')],['Buyer','Orders','Database','Payment'],[(0,1,'Checkout with key K'),(1,2,'Commit order reservation and intent'),(2,1,'Durable pending order'),(1,3,'Pay with stable operation ID'),(3,1,'Response lost: outcome unknown',1),(1,3,'Query original operation'),(3,1,'Confirmed result'),(1,2,'Confirm order and outbox'),(1,0,'Stable order state')]),
'chat':('Real-time chat',['Client sockets','Connection servers','Membership service','Message history','Delivery broker','Recipient sockets'],[(0,1,'message ID'),(1,2,'authorize'),(1,3,'persist sequence'),(1,4,'fanout'),(4,5,'deliver')],['Sender','Chat service','History','Recipient'],[(0,1,'Message with client ID'),(1,2,'Persist with conversation sequence'),(2,1,'Durable acknowledgment'),(1,0,'Accepted message ID'),(1,3,'Live delivery'),(3,1,'Connection lost',1),(3,1,'Reconnect after cursor'),(1,2,'Read missing history'),(1,3,'Replay newer messages')]),
'notify':('Notification service',['Caller','Intent API','Intent DB + outbox','Priority queues','Provider adapter','Delivery callback'],[(0,1,'notification key'),(1,2,'durable intent'),(2,3,'channel work'),(3,4,'rate-limited send'),(4,5,'provider status'),(5,2,'deduplicated update')],['Caller','Service','Worker','Provider'],[(0,1,'Create notification intent'),(1,0,'202 durable acceptance'),(1,2,'Deliver queued intent'),(2,3,'Send with stable key'),(3,2,'Temporary failure',1),(2,3,'Retry under deadline'),(3,1,'Signed delivery callback'),(1,0,'Status query result')]),
'video':('Video delivery',['Uploader','Upload metadata API','Object storage','Transcode workers','Published manifest','CDN viewers'],[(0,1,'session request'),(0,2,'scoped upload'),(1,3,'job'),(3,2,'renditions'),(3,4,'verified publication'),(4,5,'playback'),(2,5,'cached segments')],['Uploader','Metadata','Worker','Storage'],[(0,1,'Complete uploaded object'),(1,3,'Verify source checksum'),(1,2,'Schedule rendition job'),(2,3,'Write immutable renditions'),(3,2,'Stored checksums'),(2,1,'All required outputs valid'),(1,3,'Publish versioned manifest'),(1,0,'Ready for authorized playback')]),
'ai':('AI inference platform',['Client','Auth + cost admission','Versioned cache','Bounded queue / batcher','Model workers','Artifact registry','Usage ledger','Quality evaluation'],[(0,1,'input'),(1,2,'permitted lookup'),(1,3,'admit'),(3,4,'compatible batch'),(5,4,'verified model','control'),(4,6,'actual usage'),(4,7,'approved evaluation','control')],['Client','Gateway','Batcher','Model'],[(0,1,'Versioned bounded input'),(1,2,'Admit under deadline'),(2,3,'Compatible bounded batch'),(3,2,'Model output and timing'),(2,1,'Per-request result'),(1,0,'Response with model version'),(0,1,'Optional cancellation',1)]),
'jobs':('Distributed job system',['Submitter','Job API','Job DB + outbox','Broker','Worker pool','Result store','DLQ / reconciler'],[(0,1,'operation key'),(1,2,'durable intent'),(2,3,'publish reference'),(3,4,'leased work'),(4,5,'fenced result'),(4,2,'terminal state'),(4,6,'exhausted failure','failure')],['Client','Job API','Worker','Store'],[(0,1,'Submit idempotent job'),(1,3,'Commit job and outbox'),(1,0,'202 job ID'),(1,2,'Dispatch leased attempt'),(2,3,'Write result with fencing token'),(3,2,'Durable completion'),(2,1,'Acknowledge completion'),(0,1,'Poll authorized result')])
}


def make_architectures_and_sequences():
    for args in ARCHITECTURES:architecture(*args)
    sequence('seq-http','HTTP request from name lookup to response',['Client','Resolver','Proxy','Application','Database'],
             [(0,1,'Resolve service name'),(1,0,'Address with cache policy'),(0,2,'Connect and negotiate TLS'),(0,2,'HTTP request'),(2,3,'Forward with deadline'),(3,4,'Authorized query'),(4,3,'Rows'),(3,2,'Response'),(2,0,'HTTP result')],
             'Read top to bottom. Each arrow names a request or reply. Connection setup may be reused; a lost response does not prove a write failed.',[4,71,97])
    sequence('seq-cache','Cache miss and bounded origin read',['Client','API','Cache','Database'],[(0,1,'Read product'),(1,2,'GET scoped key'),(2,1,'Miss',1),(1,3,'Query authoritative product'),(3,1,'Value and version'),(1,2,'SET with TTL'),(1,0,'Product response')], 'A miss reaches the origin; a hit would return earlier. Concurrent refresh and update races require the policies in Topic 50.',[2,50])
    sequence('seq-login','Login and session creation',['Browser','Login service','Identity store','Session store'],[(0,1,'Submit credentials over TLS'),(1,2,'Verify using password-hash library'),(2,1,'Identity result'),(1,3,'Create new random session ID'),(1,0,'Secure HttpOnly cookie'),(0,1,'Cookie plus CSRF-bound mutation'),(1,3,'Load session and check expiry'),(1,0,'Authorized result or denial')],'Rotate session identifiers after authentication; cookies do not replace CSRF or object-level authorization.',[68,77])
    sequence('seq-oauth','Authorization code with PKCE',['Browser','Client','Auth server','Resource API'],[(1,0,'Start bound authorization request'),(0,2,'Authorize with code challenge'),(2,0,'Redirect with short-lived code'),(0,1,'Deliver code and bound state'),(1,2,'Exchange code plus verifier'),(2,1,'Audience-specific tokens'),(1,3,'Access token'),(3,1,'Authorized resource')],'The code is exchanged by the client. Validate redirect binding, issuer, and audience with maintained libraries.',[69,70])
    sequence('seq-replica','Read after write with replica lag',['Client','API','Primary','Replica'],[(0,1,'Create order'),(1,2,'Commit write'),(2,1,'Commit position'),(2,3,'Replication delayed',1),(0,1,'Read own new order'),(1,2,'Freshness requires primary'),(2,1,'Current order'),(1,0,'Read-your-write result')],'A session token or explicit primary route prevents a stale replica from falsely hiding a newly accepted order.',[29,35])
    sequence('seq-k8s','Deployment and health gates',['Controller','Kubelet','Pod','Service'],[(0,1,'Desired new Pod'),(1,2,'Start container'),(1,2,'Startup probe'),(2,1,'Initialization complete'),(1,2,'Readiness probe'),(2,1,'Ready'),(1,3,'Endpoint eligibility update'),(3,2,'Route new traffic')],'Startup gates other probes. Readiness controls routing eligibility; liveness has a separate restart purpose.',[8,54,57])
    sequence('seq-trace','Trace context across synchronous and async work',['Gateway','Orders','Database','Worker'],[(0,1,'Request with trace context'),(1,2,'Child database span'),(2,1,'Commit order and outbox'),(1,0,'Response span completes'),(1,3,'Event with trace link'),(3,2,'New processing span and effect'),(3,1,'Business completion event')],'Async work may outlive the initial request. A trace link and operation ID preserve causality without pretending it is one synchronous stack.',[17,60])
    sequence('seq-saga','Saga failure and compensating action',['Coordinator','Inventory','Payment','Workflow store'],[(0,3,'Persist workflow start'),(0,1,'Reserve with operation ID'),(1,0,'Reservation confirmed'),(0,2,'Attempt payment'),(2,0,'Known decline',1),(0,3,'Persist compensation intent'),(0,1,'Release reservation idempotently'),(1,0,'Release confirmed'),(0,3,'Persist rejected terminal state')],'Only a known payment decline takes this path. An unknown payment outcome first requires reconciliation; failed compensation remains durably pending.',[18,19])
    sequence('seq-webhook','Webhook delivery, retry, and durable acceptance',['Sender','Receiver','Inbox DB','Worker'],[(0,1,'Signed raw event with ID'),(1,2,'Verify then commit inbox event'),(2,1,'Durable acceptance'),(1,0,'Response lost',1),(0,1,'Retry same signed event ID'),(1,2,'Check duplicate ID'),(2,1,'Existing accepted event'),(1,0,'Successful acknowledgment'),(2,3,'Process accepted work idempotently')],'A response can be lost after durable acceptance. Repeated delivery uses the same event identity and does not repeat the local effect.',[14,101])
    for key,(title,labels,edges,participants,messages) in CASE_DATA.items():
        architecture(f'case-{key}-detail',title+': components and data',labels,edges,
                     f'Detailed architecture for the {title.lower()} case. Follow labeled edges and read the adjacent failure analysis; the diagram is a logical design, not a claim of deployed infrastructure.')
        # Overview abstracts user intent, service boundary, and durable outcome.
        architecture(f'case-{key}-overview',title+': high-level responsibilities',
                     [labels[0],title+' service boundary','Durable authoritative state','External delivery or processing'],
                     [(0,1,'intent / result'),(1,2,'state contract'),(1,3,'explicit dependency')],
                     'This overview establishes the user, service responsibility, durable state, and external work. The detailed component diagram refines the same boundary.')
        sequence(f'case-{key}-sequence',title+': operation timeline',participants,messages,
                 'Read downward in time. Solid arrows show normal messages; dashed arrows mark a failure or alternative event. Durable acceptance and final business completion may occur at different points.')


def state_diagram(key,title,states,transitions,caption,topics):
    # State labels in a circular arrangement preserve back-edges without pretending time is linear.
    c=Canvas(1200,790+len(transitions)*37);c.text(600,40,title,29,bold=True)
    coords=[]
    for i in range(len(states)):
        angle=2*math.pi*i/len(states)-math.pi/2
        coords.append((600+380*math.cos(angle),430+240*math.sin(angle)))
    for number,(a,b,label) in enumerate(transitions,1):
        x1,y1=coords[a];x2,y2=coords[b]
        dx,dy=x2-x1,y2-y1;length=math.hypot(dx,dy)
        fraction=min(122.5/abs(dx) if dx else 1e9,45/abs(dy) if dy else 1e9)
        start=(x1+dx*fraction,y1+dy*fraction);end=(x2-dx*fraction,y2-dy*fraction)
        offset=55 if any(aa==b and bb==a for aa,bb,_ in transitions) else 0
        mid=((x1+x2)/2-dy/length*offset,(y1+y2)/2+dx/length*offset)
        c.lines([start,mid,end],arrow=True)
        c.text(mid[0]-dy/length*20,mid[1]+dx/length*20,str(number),24,color=TEAL,bold=True)
    for i,state in enumerate(states):c.box(*coords[i],245,90,state,size=23)
    c.text(600,110,'Start',21,bold=True)
    c.lines([(600,126),(600,145)],arrow=True)
    c.text(600,740,'Transition triggers and actions',24,bold=True)
    for i,(a,b,label) in enumerate(transitions):
        c.text(100,790+i*37,f'{i+1}. {states[a]} -> {states[b]}: {label}',size=23,anchor='lm')
    c.save(key)
    lines=['stateDiagram-v2']+[f'  state "{state}" as S{i}' for i,state in enumerate(states)]
    lines+=['  [*] --> S0']+[f'  S{a} --> S{b}: {label}' for a,b,label in transitions]
    (OUT/(key+'.mmd')).write_text('\n'.join(lines)+'\n',encoding='utf-8')
    add_manifest(key,title,'state',caption,topics)


def make_states():
    state_diagram('state-breaker','Circuit breaker state transitions',['Closed','Open','Half-open'],[(0,1,'failure threshold'),(1,2,'cooldown'),(2,0,'probe succeeds'),(2,1,'probe fails')],'Closed records eligible outcomes. Open rejects calls. Half-open limits recovery probes; success closes and failure reopens.',[10])
    state_diagram('state-deploy','Deployment lifecycle',['Built','Verified','Canary','Promoted','Reverted'],[(0,1,'checks pass'),(1,2,'release begins'),(2,3,'guardrails pass'),(2,4,'regression'),(3,4,'late regression')],'Rollback requires compatible data and configuration; an artifact change cannot undo irreversible effects.',[6,53,55])
    state_diagram('state-job','Durable job lifecycle',['Queued','Running','Completed','Retry waiting','Dead letter'],[(0,1,'lease claimed'),(1,2,'result committed'),(1,3,'transient failure'),(3,0,'retry due'),(1,4,'budget exhausted')],'The result commits before acknowledgment. Retry waiting is durable in a real implementation; dead letter requires ownership.',[15,20])
    state_diagram('state-payment','Payment outcome and reconciliation',['Pending','Confirmed','Declined','Unknown','Refund pending'],[(0,1,'provider confirms'),(0,2,'provider declines'),(0,3,'response lost'),(3,1,'reconcile success'),(3,2,'reconcile failure'),(1,4,'approved compensation')],'Unknown is not declined. A refund is a new financial action, not erasure of the original payment.',[14,19])
    state_diagram('state-message','Message processing lifecycle',['Available','In flight','Acknowledged','Redelivered','Quarantined'],[(0,1,'consumer receives'),(1,2,'durable effect then ack'),(1,3,'lease or ack lost'),(3,1,'new attempt'),(1,4,'poison policy')],'Redelivery can occur after the effect succeeded. Deduplicate at the effect boundary.',[15,20])
    state_diagram('state-incident','Incident lifecycle',['Detected','Declared','Mitigating','Recovered','Reviewed'],[(0,1,'impact assessed'),(1,2,'roles and action'),(2,3,'user and data checks'),(3,4,'learning review'),(3,2,'recovery regresses')],'Recovery includes business integrity and queue freshness. Review produces owned verifiable actions.',[109,110,111])
    state_diagram('state-token','Credential lifecycle',['Issued','Valid','Expired','Revoked','Renewed'],[(0,1,'validated claims'),(1,2,'expiry reached'),(1,3,'revocation'),(2,4,'valid renewal grant'),(4,1,'new token issued')],'Renewal requires its own valid grant. Expired or revoked access tokens must not authorize resource actions.',[69,70])
    state_diagram('state-cache','Cache entry lifecycle',['Absent','Fresh','Expired','Refreshing','Evicted'],[(0,3,'miss and refresh owner'),(3,1,'origin result stored'),(1,2,'TTL elapsed'),(2,3,'refresh admitted'),(1,4,'capacity eviction'),(4,0,'entry unavailable')],'Expiration and eviction are different causes of absence. Refresh ownership limits a stampede.',[2,50])


def illustration(key,title,kind,caption,topics):
    c=Canvas(1200,750); c.text(600,45,title,30,bold=True)
    if kind=='latency':
        c.lines([(130,610),(1100,610)],arrow=True);c.lines([(130,610),(130,150)],arrow=True)
        c.box(350,480,230,260,'980 requests at 20 ms',size=25)
        c.box(850,560,230,100,'20 requests at 2000 ms',size=24)
        c.text(600,120,'Mean = 59.6 ms; nearest-rank P99 = 2000 ms',25,bold=True)
        c.text(600,670,'Schematic population bars; heights are not a linear frequency scale.',20,color=GRAY)
    elif kind=='queue':
        c.box(220,250,300,110,'Arrival: 120 jobs/s');c.box(980,250,300,110,'Service: 100 jobs/s')
        c.lines([(380,250),(810,250)],arrow=True)
        for i in range(10):c.box(170+i*94,470,75,85,str(i+1),size=22)
        c.text(600,590,'Backlog grows by 20 jobs/s while these rates persist.',25,bold=True)
        c.text(600,640,'A 1000-job empty buffer buys about 50 seconds in the continuous model.',21)
    elif kind=='scaling':
        c.box(310,360,350,360,'Vertical: one larger host',size=28)
        for x,y in [(800,270),(1030,270),(800,480),(1030,480)]:c.box(x,y,180,140,'Replica',size=25)
        c.text(900,610,'Horizontal: more hosts',27,bold=True)
        c.text(600,690,'Both still depend on shared storage and coordination limits.',23,color=GRAY)
    elif kind=='replication':
        for x in [240,600,960]:c.box(x,260,280,150,'Copy: A B C',size=27)
        for x,label in zip([240,600,960],['Shard: A','Shard: B','Shard: C']):c.box(x,540,280,150,label,size=27)
        c.text(600,130,'Replication keeps copies of the same data.',25,bold=True)
        c.text(600,420,'Sharding assigns different data to different owners.',25,bold=True)
    elif kind=='index':
        c.box(600,180,260,90,'Root separator: 50',size=25)
        c.box(300,380,360,110,'Leaf range: 1 ... 49',size=25)
        c.box(900,380,360,110,'Leaf range: 50 ... 99',size=25)
        c.lines([(550,225),(300,325)],arrow=True);c.lines([(650,225),(900,325)],arrow=True)
        c.box(900,600,360,95,'Find key 72 in this range',size=25)
        c.lines([(900,435),(900,552)],arrow=True)
        c.text(330,600,'Conceptual B-tree lookup;\nnot physical page sizes.',22)
    elif kind=='budget':
        phases=[('DNS',20),('Connect/TLS',60),('Queue',100),('App',40),('Database',50),('Transfer',30)]
        x=120
        for label,value in phases:
            w=value*3
            c.box(x+w/2,340,w-4,200,f'{label}: {value} ms',size=22)
            x+=w
        c.text(600,540,'Sequential example total: 300 ms',28,bold=True)
        c.text(600,610,'A reused connection may remove setup phases, not all downstream work.',22)
    elif kind=='capacity':
        labels=['1M users/day x 20 requests','20M requests/day / 86400','231.5 average requests/s','x8 assumed peak = 1852/s','x0.2 seconds = 370 in flight']
        for i,label in enumerate(labels):
            c.box(600,150+i*115,850,75,label,size=26)
            if i<4:c.lines([(600,188+i*115),(600,225+i*115)],arrow=True)
    elif kind=='clock':
        c.text(180,200,'Host A',27,bold=True);c.text(180,430,'Host B',27,bold=True)
        c.lines([(300,200),(1100,200)],arrow=True);c.lines([(300,430),(1100,430)],arrow=True)
        c.box(470,200,260,90,'12:00:02 send',size=24);c.box(900,430,270,90,'11:59:59 receive',size=24)
        c.lines([(560,250),(810,380)],arrow=True)
        c.text(600,610,'Causality says send precedes receive despite wall-clock labels.',25,bold=True)
    elif kind=='backoff':
        for i,cap in enumerate([100,200,400,800]):
            y=190+i*120;c.text(200,y,f'Retry {i+1}',24,bold=True)
            c.lines([(350,y),(350+cap*.75,y)],width=18,color=TEAL)
            c.text(990,y,f'0 ... {cap} ms',24)
        c.text(600,690,'Full jitter samples within each capped window; it does not guarantee the maximum wait.',20)
    elif kind=='breaker':
        events=[('t=0','3 failures'),('t=1','Fail fast'),('t=5','One probe'),('t=5+','Close or reopen')]
        c.lines([(110,360),(1100,360)],arrow=True)
        for i,(time,label) in enumerate(events):
            x=190+i*270;c.text(x,250,time,27,bold=True);c.box(x,470,230,125,label,size=24)
            c.lines([(x,300),(x,400)],width=3)
        c.text(600,650,'Illustrative threshold: 3 failures; cooldown: 5 seconds.',23)
    elif kind=='rpo':
        c.lines([(100,370),(1100,370)],arrow=True)
        for x,label in [(190,'Last recoverable data'),(620,'Disaster'),(1010,'Service restored')]:
            c.lines([(x,330),(x,410)]);c.box(x,240,270,110,label,size=23)
        c.text(390,500,'RPO: tolerated data gap',25,bold=True)
        c.text(840,580,'RTO: target recovery time',25,bold=True)
    elif kind=='batching':
        for i in range(5):c.box(160+i*220,220,170,90,f'Request {i+1}',size=24)
        c.box(600,420,950,110,'Bounded wait + compatible batch + memory limit',size=28)
        c.box(600,610,500,90,'One model execution batch',size=26)
        c.lines([(600,265),(600,365)],arrow=True);c.lines([(600,475),(600,565)],arrow=True)
    elif kind=='pool':
        for i in range(3):c.box(260+i*340,300,240,140,f'Connection {i+1}',size=24)
        c.box(600,550,820,100,'Additional callers wait only within a bounded deadline',size=26)
        c.text(600,140,'Pool size limits simultaneous ownership, not total requests.',25,bold=True)
    elif kind=='envelope':
        c.box(300,230,420,130,'Data encrypted by data key',size=27)
        c.box(900,230,420,130,'Data key wrapped by key-encryption key',size=25)
        c.box(600,530,850,140,'Store ciphertext + wrapped key; control key access separately',size=28)
        c.lines([(300,295),(300,440),(500,460)],arrow=True);c.lines([(900,295),(900,440),(700,460)],arrow=True)
    elif kind=='fanout':
        c.box(600,180,400,95,'Page waits for all required branches',size=25)
        for i in range(5):
            x=160+i*220;c.box(x,420,175,120,'Required call',size=23)
            c.lines([(600,227),(x,360)],arrow=True)
        c.text(600,620,'100 independent 1%-slow branches: at least one slow = 63.4%.',25,bold=True)
    elif kind=='migration':
        labels=['Expand schema','Dual-compatible code','Bounded backfill','Switch reads','Contract after safe window']
        for i,label in enumerate(labels):
            c.box(600,145+i*115,850,76,label,size=26)
            if i<4:c.lines([(600,183+i*115),(600,222+i*115)],arrow=True)
    c.save(key);add_manifest(key,title,'illustration',caption,topics,source=False)


def make_illustrations():
    specs=[
    ('ill-latency','How a good mean hides slow requests','latency','980 fast and 20 slow requests yield a 59.6 ms mean but a 2000 ms P99. The bars are a schematic, not a scaled histogram.',[91,93]),
    ('ill-queue','Why a queue grows under sustained overload','queue','Arrival minus service gives the backlog growth rate. The continuous-time estimate differs slightly from the discrete tick convention in the runnable model.',[15,44]),
    ('ill-scaling','Vertical and horizontal capacity','scaling','A larger host and more hosts solve different constraints. Shared bottlenecks and failure domains still matter.',[46,47]),
    ('ill-replication','Copies versus divided ownership','replication','Top: each replica has A, B, and C. Bottom: shards own different subsets. Real systems can combine sharding with replication.',[30,31,32]),
    ('ill-index','B-tree search narrows the candidate range','index','The root directs key 72 toward the relevant sorted range. This is a conceptual tree; real page fanout and visibility rules are more complex.',[25]),
    ('ill-budget','One request, several latency budgets','budget','Add only sequential phases. Parallel work uses the critical path rather than the sum of every span.',[11,91]),
    ('ill-capacity','From daily users to concurrent work','capacity','Every step preserves its units and states its assumption. Peak factor and mean response time must later be measured.',[45,92]),
    ('ill-clock','Clock labels can contradict causal order','clock','The receiving host clock is behind. Use causal links for ordering and monotonic local clocks for elapsed time.',[60,96]),
    ('ill-backoff','Exponential retry windows with full jitter','backoff','Each retry samples a different window; the cap and total deadline still bound the policy.',[12,13]),
    ('ill-breaker','Circuit breaker failure and recovery timeline','breaker','Failures open the breaker, a cooldown rejects work, and a limited probe tests recovery. This timeline supplements the state diagram.',[10]),
    ('ill-rpo','Recovery point and recovery time are different','rpo','RPO concerns how recent recoverable data must be; RTO concerns how long restoring service may take.',[83,84]),
    ('ill-batching','Batching trades waiting for shared execution','batching','Bound both queue delay and memory. Compatible shapes and useful throughput determine whether batching helps.',[44,88,92]),
    ('ill-pool','Connection ownership and bounded waiting','pool','Each token represents one reusable connection. Exceptions must return ownership; adding application replicas multiplies potential demand.',[28]),
    ('ill-envelope','Envelope encryption separates data and key protection','envelope','The data key encrypts content; a separately controlled wrapping key protects the data key. Restore needs both authorized paths.',[67,72]),
    ('ill-fanout','Fanout amplifies the probability of a slow branch','fanout','The calculation assumes independent branch events and all branches required. Correlation and partial-result contracts change the result.',[94]),
    ('ill-migration','Expand-and-contract migration sequence','migration','The old contract remains during mixed-version operation. Removing it is a separate, later change after backfill and rollback requirements are satisfied.',[81,82])]
    for args in specs:illustration(*args)
    add_manifest('backpressure-analogy','Backpressure as a bounded restaurant ticket rack','illustration',
                 'Left: arriving orders accumulate faster than one chef can finish them. Right: the same chef has a bounded rack and upstream admission pauses. The illustration is qualitative; the queue model supplies the arithmetic.',[44],source=False)
    MANIFEST[-1]['svg']=None


def build(topics):
    for topic in topics:flow(topic)
    make_architectures_and_sequences();make_states();make_illustrations()
    (OUT/'manifest.json').write_text(json.dumps(MANIFEST,indent=2),encoding='utf-8')
    return MANIFEST
