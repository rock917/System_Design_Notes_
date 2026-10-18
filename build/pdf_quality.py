from pathlib import Path
import json
import subprocess
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
import pdfplumber
from pypdf import PdfReader
from PIL import Image,ImageDraw,ImageFont

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent if HERE.name=='build' else HERE.parent/'outputs/system-design-master-handbook'
PDF=ROOT/'SYSTEM_DESIGN_MASTER_HANDBOOK.pdf'
QA=HERE/'pdf-qa';QA.mkdir(exist_ok=True)
POPPLER=Path(os.environ.get('HANDBOOK_PDFTOPPM') or shutil.which('pdftoppm') or 'C:/Users/bobby/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe')
render=json.loads((HERE/'render_results.json').read_text())
coverage=json.loads((ROOT/'coverage.json').read_text())
reader=PdfReader(PDF)
headings=render['headings'];missing=[]
for topic in coverage:
    p=headings[topic['anchor']]-1
    text=' '.join(reader.pages[p].extract_text().split())
    if topic['section_heading'] not in text:missing.append(topic['number'])
assert not missing,missing
assert len(render['figure_placements'])==194
assert set(x['file'] for x in render['figure_placements'])=={'diagrams/'+f['png'] for f in json.loads((ROOT/'diagrams/manifest.json').read_text())}
chosen={1,2,8,11,len(reader.pages)}
chosen.update(v for k,v in headings.items() if k.startswith('part-'))
chosen.update(headings['topic-'+str(n).zfill(3)] for n in (1,10,25,34,38,69,81,98,111))
chosen.update(x['page'] for x in render['figure_placements'] if Path(x['file']).stem in {'arch-production','state-breaker','seq-oauth','ill-index','case-orders-detail','backpressure-analogy','seq-saga','arch-inference'})
chosen.update(v for k,v in headings.items() if k in {'complete-runnable-implementation-appendix','environment-commands-and-actual-example-outputs'})
chosen.update(headings[k] for k in ['source-file-examples-algorithms-py','source-file-examples-security-py','source-file-examples-database-sql','source-file-examples-k8s-yaml'])
chosen=sorted(chosen)
def draw(page):
    dest=QA/f'page-{page:04d}'
    subprocess.run([str(POPPLER),'-f',str(page),'-l',str(page),'-scale-to','1400','-png','-singlefile',str(PDF),str(dest)],check=True,capture_output=True)
    return dest.with_suffix('.png')
with ThreadPoolExecutor(max_workers=4) as pool:images=list(pool.map(draw,chosen))
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
for sheet_start in range(0,len(images),12):
    subset=images[sheet_start:sheet_start+12];sheet=Image.new('RGB',(1000,4*380),'#dce6eb');canvas=ImageDraw.Draw(sheet)
    for i,path in enumerate(subset):
        image=Image.open(path);image.thumbnail((240,340));x=(i%4)*250+(250-image.width)//2;y=(i//4)*380+25
        sheet.paste(image,(x,y));canvas.text(((i%4)*250+9,(i//4)*380+3),path.stem,font=font,fill='#153047')
    sheet=sheet.crop((0,0,1000,((len(subset)+3)//4)*380));sheet.save(QA/f'contact-{sheet_start//12+1}.png')
print(f'Rendered {len(images)} selected pages; checking all PDF page geometry.',flush=True)
outliers=[];empty=[];image_count=0;char_count=0
with pdfplumber.open(PDF) as book:
    for number,page in enumerate(book.pages,1):
        chars=page.chars;char_count+=len(chars);image_count+=len(page.images)
        if not chars:empty.append(number)
        bad=[c for c in chars if c['x0']<-1 or c['x1']>page.width+1 or c['top']<-1 or c['bottom']>page.height+1]
        if bad:outliers.append({'page':number,'count':len(bad),'sample':''.join(c['text'] for c in bad[:70])})
        page.close()
        if number%150==0:print(f'Checked page {number}/{len(reader.pages)}',flush=True)
assert not outliers,outliers
assert not empty,empty
assert image_count==194,image_count
report={'pages':len(reader.pages),'topic_headings_found':111,'figures_placed':194,'pdf_image_objects':image_count,
        'pages_geometry_checked':len(reader.pages),'characters_checked':char_count,'out_of_page_text':outliers,'empty_pages':empty,
        'rendered_sample_pages':chosen,'rendered_sample_count':len(chosen),'visual_review':'Pending human/assistant inspection of rendered pages; geometry is automated.'}
(HERE/'pdf_audit_results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='rendered_sample_pages'},indent=2),flush=True)
