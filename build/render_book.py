"""Rebuild complete offline HTML and PDF from the saved handbook Markdown.

Dependencies: Pillow, reportlab, pypdf. No browser, network, or cloud service.
The small parser covers the explicit Markdown subset used by this handbook.
"""
from pathlib import Path
import html
import json
import os
import re
import sys
import textwrap
from collections import Counter
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
    Spacer, PageBreak, Image, Table, TableStyle, Preformatted, KeepTogether)
from reportlab.platypus.tableofcontents import TableOfContents
from pypdf import PdfReader

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent if HERE.name=='build' else HERE.parent/'outputs/system-design-master-handbook'
FONT_DIR=Path(os.environ.get('HANDBOOK_FONT_DIR','C:/Windows/Fonts'))
FONT_FILES={'Book':'arial.ttf','Book-Bold':'arialbd.ttf','Book-Italic':'ariali.ttf',
            'Book-BoldItalic':'arialbi.ttf','Code':'consola.ttf','Code-Bold':'consolab.ttf'}
NAVY='#153047'; TEAL='#167D8D'; GRAY='#536776'
WIDTH=A4[0]-96


def slug(text):
    return re.sub(r'[^a-z0-9]+','-',text.lower()).strip('-')


def blocks(source):
    lines=source.splitlines();i=0;serial=Counter();pending=None
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line.startswith('```'):
            language=line[3:];body=[];i+=1
            while i<len(lines) and not lines[i].strip().startswith('```'):
                body.append(lines[i]);i+=1
            if i==len(lines):raise ValueError('Unclosed code fence')
            yield ('code',language,'\n'.join(body));i+=1;continue
        anchor=re.fullmatch(r'<a id="([^"]+)"></a>',line)
        if anchor:pending=anchor.group(1);i+=1;continue
        heading=re.match(r'^(#{1,6}) (.+)$',line)
        if heading:
            level=len(heading.group(1));title=heading.group(2);key=slug(title)
            serial[key]+=1
            key=pending or key+(f'-{serial[key]}' if serial[key]>1 else '')
            pending=None
            yield ('heading',level,title,key);i+=1;continue
        image=re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)',line)
        if image:yield ('image',image.group(1),image.group(2));i+=1;continue
        if line.startswith('|') and line.endswith('|'):
            rows=[]
            while i<len(lines):
                item=lines[i].strip()
                if not item:
                    j=i+1
                    while j<len(lines) and not lines[j].strip():j+=1
                    if j<len(lines) and lines[j].strip().startswith('|'):i=j;continue
                    break
                if not item.startswith('|'):break
                cells=[v.strip() for v in re.split(r'(?<!\\)\|',item.strip('|'))]
                if not all(re.fullmatch(r':?-{3,}:?',v) for v in cells):rows.append(cells)
                i+=1
            yield ('table',rows);continue
        bullet=re.match(r'^(- |\d+\. )(.+)$',line)
        if bullet:yield ('list',bullet.group(1).strip(),bullet.group(2));i+=1;continue
        if line=='---':yield ('rule',);i+=1;continue
        paragraph=[line];i+=1
        while i<len(lines) and lines[i].strip():
            if re.match(r'^(#{1,6} |```|!\[|<a id=|\||- |\d+\. )',lines[i].strip()):break
            paragraph.append(lines[i].strip());i+=1
        yield ('paragraph',' '.join(paragraph))


INLINE=re.compile(r'(`[^`]+`|\[[^\]]+\]\([^\s)]+\)|\*\*.+?\*\*|(?<!\*)\*[^*]+\*(?!\*))')
def inline(text,pdf=False):
    result=[];pos=0
    for match in INLINE.finditer(text):
        result.append(html.escape(text[pos:match.start()]));value=match.group()
        if value.startswith('`'):
            escaped=html.escape(value[1:-1]);result.append(f'<font name="Code">{escaped}</font>' if pdf else f'<code>{escaped}</code>')
        elif value.startswith('['):
            label,target=re.fullmatch(r'\[([^\]]+)\]\(([^)]+)\)',value).groups()
            if pdf and target.startswith('SYSTEM_DESIGN_MASTER_HANDBOOK.md#'):target='#'+target.split('#',1)[1]
            if not pdf and target.endswith('.md'):target=target[:-3]+'.html'
            if not pdf and '.md#' in target:target=target.replace('.md#','.html#')
            attr=html.escape(target,quote=True)
            result.append(f'<link href="{attr}" color="{TEAL}">{inline(label,True)}</link>' if pdf else f'<a href="{attr}">{inline(label)}</a>')
        elif value.startswith('**'):result.append('<b>'+inline(value[2:-2],pdf)+'</b>')
        else:result.append('<i>'+inline(value[1:-1],pdf)+'</i>')
        pos=match.end()
    result.append(html.escape(text[pos:]))
    return ''.join(result)


CSS='''
:root{color-scheme:light;--ink:#153047;--muted:#536776;--accent:#167D8D}
*{box-sizing:border-box}[hidden]{display:none!important}body{margin:0;background:#f2f6f8;color:var(--ink);font:17px/1.65 system-ui,Arial,sans-serif}
nav{position:fixed;inset:0 auto 0 0;width:285px;padding:26px 22px;background:#153047;color:white;overflow:auto}
nav a{color:#d9eff1;text-decoration:none;display:block;font-size:13px;line-height:1.5;margin:9px 0}
nav .sub{padding-left:12px;border-left:1px solid #496071}nav strong{font-size:21px;line-height:1.3;display:block}
nav input{margin:20px 0 5px;width:100%;padding:10px;border:0;border-radius:4px}nav small{color:#c0d2dc}
main{max-width:1120px;margin:0 auto 0 285px;padding:50px 6%;background:white;min-height:100vh}
h1{font-size:44px;line-height:1.12;letter-spacing:-1px}h2{font-size:31px;line-height:1.25;border-top:4px solid var(--accent);padding-top:25px;margin-top:80px}
h3{font-size:26px;line-height:1.3;margin-top:65px}h4{font-size:20px;margin-top:35px}h5{font-size:18px}
[id]{scroll-margin-top:20px}a{color:#076e83;text-underline-offset:3px}p{margin:14px 0}code{font:0.88em Consolas,monospace;background:#edf3f6;padding:2px 4px;border-radius:3px}
pre{background:#edf3f6;border-left:3px solid #167D8D;padding:18px;overflow:auto;font:13px/1.5 Consolas,monospace;tab-size:4}pre code{padding:0;background:none;font:inherit}
figure{margin:28px 0}figure img{display:block;width:100%;height:auto;border:1px solid #dce6eb}figcaption{font-size:13px;color:var(--muted);margin-top:8px}
table{border-collapse:collapse;width:100%;font-size:14px;margin:25px 0;table-layout:fixed}th,td{padding:10px;border:1px solid #cfdae0;text-align:left;vertical-align:top;overflow-wrap:anywhere}th{background:#eaf3f6}
.listitem{padding-left:25px;position:relative;margin:9px 0}.marker{position:absolute;left:0;color:var(--accent)}.edition{font-size:13px;color:var(--muted)}
@media(max-width:900px){nav{position:relative;width:auto;max-height:340px}main{margin:0;padding:30px 6%}h1{font-size:36px}}
@media print{nav{display:none}main{margin:0;padding:0;max-width:none}body{font-size:10pt;background:white}h2{break-before:page}h2,h3,h4{break-after:avoid}figure,tr,pre{break-inside:avoid}a{color:inherit}pre{white-space:pre-wrap}}
'''


def make_html(tokens,path):
    nav=[];body=[]
    for block in tokens:
        kind=block[0]
        if kind=='heading':
            _,level,title,key=block
            if level in (2,3):nav.append(f'<a class="{"sub" if level==3 else "part"}" href="#{key}">{html.escape(title)}</a>')
            body.append(f'<h{level} id="{key}">{inline(title)}</h{level}>')
        elif kind=='paragraph':body.append('<p>'+inline(block[1])+'</p>')
        elif kind=='list':body.append('<div class="listitem"><span class="marker">'+('•' if block[1]=='-' else html.escape(block[1]))+'</span>'+inline(block[2])+'</div>')
        elif kind=='code':body.append(f'<pre data-language="{html.escape(block[1])}"><code>{html.escape(block[2])}</code></pre>')
        elif kind=='image':body.append(f'<figure><img src="{html.escape(block[2])}" alt="{html.escape(block[1])}" loading="lazy"><figcaption>{html.escape(block[1])}</figcaption></figure>')
        elif kind=='table':
            body.append('<table>')
            for index,row in enumerate(block[1]):
                tag='th' if index==0 else 'td';body.append('<tr>'+''.join(f'<{tag}>{inline(cell)}</{tag}>' for cell in row)+'</tr>')
            body.append('</table>')
        else:body.append('<hr>')
    title=next(b[2] for b in tokens if b[0]=='heading')
    page='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title><style>'+CSS+'</style></head><body>'
    page+='<nav><strong>System Design<br>Master Handbook</strong><p><a href="README.html">Study guide</a><a href="SYSTEM_DESIGN_MASTER_HANDBOOK.pdf">Complete PDF</a></p><input id="filter" type="search" placeholder="Filter chapter navigation" aria-label="Filter chapter navigation"><small>Use Ctrl+F to search the text.</small><div id="toc">'+''.join(nav)+'</div></nav><main><p class="edition">ILLUSTRATED STUDY EDITION · OCTOBER 2026</p>'+''.join(body)+'</main>'
    page+='<script>document.getElementById("filter").addEventListener("input",function(){const q=this.value.toLowerCase();document.querySelectorAll("#toc a").forEach(a=>a.hidden=!a.textContent.toLowerCase().includes(q));});</script></body></html>'
    path.write_text(page,encoding='utf-8')


def fonts():
    for name,file in FONT_FILES.items():pdfmetrics.registerFont(TTFont(name,str(FONT_DIR/file)))
    pdfmetrics.registerFontFamily('Book',normal='Book',bold='Book-Bold',italic='Book-Italic',boldItalic='Book-BoldItalic')
    pdfmetrics.registerFontFamily('Code',normal='Code',bold='Code-Bold',italic='Code',boldItalic='Code-Bold')


class Book(BaseDocTemplate):
    def __init__(self,path):
        super().__init__(str(path),pagesize=A4,leftMargin=48,rightMargin=48,topMargin=57,bottomMargin=47,
            title='System Design Master Handbook',author='Study edition prepared for Bobby',pageCompression=1)
        frame=Frame(48,47,WIDTH,A4[1]-104,id='normal',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
        self.addPageTemplates(PageTemplate(id='book',frames=frame,onPage=self.decorate))
        self.current_part='SYSTEM DESIGN MASTER HANDBOOK';self.heading_pages={};self.image_pages=[]
    def beforeDocument(self):
        self.current_part='SYSTEM DESIGN MASTER HANDBOOK';self.heading_pages={};self.image_pages=[]
    def decorate(self,canvas,doc):
        if doc.page==1:return
        canvas.saveState();canvas.setStrokeColor(colors.HexColor('#d9e4e9'));canvas.setLineWidth(.5)
        canvas.line(48,35,A4[0]-48,35);canvas.setFillColor(colors.HexColor(GRAY));canvas.setFont('Book',8)
        canvas.drawString(48,23,'SYSTEM DESIGN MASTER HANDBOOK  |  STUDY EDITION')
        canvas.drawRightString(A4[0]-48,23,str(doc.page));canvas.restoreState()
    def afterFlowable(self,flow):
        if hasattr(flow,'heading_key'):
            key=flow.heading_key;title=flow.heading_text;level=flow.heading_level
            self.canv.bookmarkPage(key);self.heading_pages[key]=self.page
            if level in (2,3):
                outline_level=level-2
                self.canv.addOutlineEntry(title,key,outline_level,closed=level==2)
                self.notify('TOCEntry',(outline_level,html.escape(title),self.page,key))
        if hasattr(flow,'figure_path'):self.image_pages.append({'file':flow.figure_path,'page':self.page})


def make_pdf(tokens,path):
    fonts()
    base=dict(fontName='Book',fontSize=10.2,leading=14.4,textColor=colors.HexColor(NAVY),spaceAfter=7,allowWidows=0,allowOrphans=0)
    styles={'body':ParagraphStyle('body',**base)}
    for level,size,leading,before,after in [(1,30,36,0,20),(2,22,28,12,18),(3,18,23,12,14),(4,13,18,12,8),(5,11.5,16,10,6),(6,10.5,15,8,5)]:
        styles[level]=ParagraphStyle(f'h{level}',parent=styles['body'],fontName='Book-Bold',fontSize=size,leading=leading,spaceBefore=before,spaceAfter=after,keepWithNext=True)
    styles['caption']=ParagraphStyle('caption',parent=styles['body'],fontSize=9,leading=12,textColor=colors.HexColor(GRAY))
    styles['cell']=ParagraphStyle('cell',parent=styles['body'],fontSize=9,leading=12,spaceAfter=2)
    styles['bullet']=ParagraphStyle('bullet',parent=styles['body'],leftIndent=14,firstLineIndent=0,bulletIndent=1)
    styles['code']=ParagraphStyle('code',fontName='Code',fontSize=7.6,leading=10.2,textColor=colors.HexColor(NAVY),backColor=colors.HexColor('#edf3f6'),borderPadding=7,spaceBefore=4,spaceAfter=8)
    doc=Book(path);story=[]
    story += [Spacer(1,112),Paragraph('SYSTEM DESIGN',ParagraphStyle('cover-small',fontName='Book-Bold',fontSize=14,leading=20,textColor=colors.HexColor(TEAL),spaceAfter=15)),
              Paragraph('Master<br/>Handbook',ParagraphStyle('cover',fontName='Book-Bold',fontSize=48,leading=53,textColor=colors.HexColor(NAVY),spaceAfter=30)),
              Paragraph('Backend engineering · Distributed systems<br/>Databases · Networking · Security<br/>DevOps · Production operations · AI/ML serving',ParagraphStyle('subtitle',parent=styles['body'],fontSize=15,leading=23)),
              Spacer(1,38),Paragraph('111 topics / 15 parts / 8 system designs',styles[3]),
              Paragraph('194 original figures · Runnable demonstrations<br/>Interview answers, exercises, and incident walkthroughs',styles['body']),
              Spacer(1,50),Paragraph('STUDY EDITION · 18 OCTOBER 2026',styles['caption']),PageBreak(),Paragraph('Navigation',styles[2]),
              Paragraph('The entries below and the PDF bookmarks link to every part and chapter. Original topic numbers stay stable across the Markdown, HTML, examples, and coverage audit. The PDF contains the complete handbook, including implementation source and recorded outputs.',styles['body'])]
    toc=TableOfContents();toc.levelStyles=[ParagraphStyle('toc0',fontName='Book-Bold',fontSize=10,leading=15,spaceBefore=9,leftIndent=0,rightIndent=25),ParagraphStyle('toc1',fontName='Book',fontSize=9,leading=13,spaceBefore=2,leftIndent=12,rightIndent=25)]
    story +=[toc,PageBreak()]
    for index,block in enumerate(tokens):
        kind=block[0]
        if kind=='heading':
            _,level,title,key=block
            if level==1:continue
            if level==2 and title.startswith('Part '):
                story.append(PageBreak())
                if re.match(r'Part (?:II|III|IV|V|VI|VII|VIII|IX|X|XI|XII)\.',title):
                    story.append(Spacer(1,105))
            elif level==3 and key.startswith('topic-'):story.append(PageBreak())
            paragraph=Paragraph(f'<a name="{key}"/>'+inline(title,True),styles[level])
            paragraph.heading_key=key;paragraph.heading_text=title;paragraph.heading_level=level
            story.append(paragraph)
            if level==2 and re.match(r'Part (?:II|III|IV|V|VI|VII|VIII|IX|X|XI|XII)\.',title):
                topics=[row for row in json.loads((ROOT/'coverage.json').read_text()) if row['chapter']==title]
                story.append(Paragraph('CHAPTERS IN THIS PART',styles['caption']))
                for row in topics:
                    story.append(Paragraph(f'<link href="#{row["anchor"]}" color="{TEAL}">{html.escape(row["section_heading"])}</link>',styles['body']))
        elif kind=='paragraph':
            style=styles['caption'] if block[1].startswith('*Figure ') else styles['body']
            story.append(Paragraph(inline(block[1],True),style))
        elif kind=='list':story.append(Paragraph(inline(block[2],True),styles['bullet'],bulletText='•' if block[1]=='-' else block[1]))
        elif kind=='code':
            # Display wraps preserve source indentation; executable originals remain intact.
            lines=[]
            for line in block[2].expandtabs(4).splitlines():
                if len(line)<=100:lines.append(line)
                else:
                    indent=len(line)-len(line.lstrip());lines.extend(textwrap.wrap(line,width=100,subsequent_indent=' '*min(indent+4,20),replace_whitespace=False,drop_whitespace=False,break_long_words=True,break_on_hyphens=False))
            for start in range(0,len(lines),42):story.append(Preformatted('\n'.join(lines[start:start+42]),styles['code']))
        elif kind=='image':
            imgpath=ROOT/block[2]
            with PILImage.open(imgpath) as img:w,h=img.size
            scale=min(WIDTH/w,605/h);figure=Image(str(imgpath),width=w*scale,height=h*scale)
            figure.hAlign='CENTER';figure.figure_path=block[2]
            story.extend([Spacer(1,7),figure,Spacer(1,7)])
        elif kind=='table':
            rows=block[1];columns=max(map(len,rows));data=[]
            for row in rows:
                assert len(row)==columns,('inconsistent table columns',row)
                data.append([Paragraph(inline(cell,True),styles['cell']) for cell in row])
            widths=[WIDTH/columns]*columns
            if columns==2:widths=[WIDTH*.28,WIDTH*.72]
            table=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eaf3f6')),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#cfdae0')),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
            story.extend([table,Spacer(1,10)])
        else:story.append(Spacer(1,8))
    doc.multiBuild(story,maxPasses=5)
    reader=PdfReader(str(path))
    result={'pages':len(reader.pages),'source_blocks':len(tokens),'headings':doc.heading_pages,'figure_placements':doc.image_pages,'pdf_bytes':path.stat().st_size}
    (HERE/'render_results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('headings','figure_placements')},indent=2),flush=True)


def main():
    mainfile=ROOT/'SYSTEM_DESIGN_MASTER_HANDBOOK.md'
    tokens=list(blocks(mainfile.read_text(encoding='utf-8')))
    for file in ROOT.glob('*.md'):
        make_html(tokens if file==mainfile else list(blocks(file.read_text(encoding='utf-8'))),file.with_suffix('.html'))
    # The examples guide needs paths relative to its own directory.
    make_html(list(blocks((ROOT/'examples/README.md').read_text(encoding='utf-8'))),ROOT/'examples/README.html')
    p=ROOT/'examples/README.html';value=p.read_text(encoding='utf-8').replace('href="README.html"','href="../README.html"').replace('href="SYSTEM_DESIGN_MASTER_HANDBOOK.pdf"','href="../SYSTEM_DESIGN_MASTER_HANDBOOK.pdf"');p.write_text(value,encoding='utf-8')
    print('Offline HTML editions written.',flush=True)
    if '--html-only' not in sys.argv:make_pdf(tokens,ROOT/'SYSTEM_DESIGN_MASTER_HANDBOOK.pdf')


if __name__=='__main__':main()
