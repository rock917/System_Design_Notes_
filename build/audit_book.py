"""Audit saved coverage, links, image files and the exported Mermaid subset.

This checks graph references and source structure, not a Mermaid-engine render.
"""
from pathlib import Path
import ast
import html
from html.parser import HTMLParser
import json
import re
import sys
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlsplit
from PIL import Image,ImageFont
import render_book

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent if HERE.name=='build' else HERE.parent/'outputs/system-design-master-handbook'


def mermaid_lint(path):
    lines=path.read_text(encoding='utf-8').splitlines();defined=set();refs=[]
    if lines[0]=='flowchart TD':
        for line in lines[1:]:
            node=re.fullmatch(r'\s+(N\d+)(?:\["[^"\n]+"\]|\{"[^"\n]+"\})',line)
            edge=re.fullmatch(r'\s+(N\d+) (?:-->|-\.->)(?:\|[^|\n]+\|)? (N\d+)',line)
            if node:defined.add(node[1])
            elif edge:refs.extend([edge[1],edge[2]])
            else:raise ValueError(f'{path.name}: unsupported source line {line}')
    elif lines[0]=='sequenceDiagram':
        for line in lines[1:]:
            node=re.fullmatch(r'\s+participant (P\d+) as .+',line)
            edge=re.fullmatch(r'\s+(P\d+)(?:->>|-->>)(P\d+): .+',line)
            if node:defined.add(node[1])
            elif edge:refs.extend([edge[1],edge[2]])
            else:raise ValueError(f'{path.name}: unsupported source line {line}')
    elif lines[0]=='stateDiagram-v2':
        defined.add('[*]')
        for line in lines[1:]:
            node=re.fullmatch(r'\s+state "[^"\n]+" as (S\d+)',line)
            edge=re.fullmatch(r'\s+(S\d+|\[\*\]) --> (S\d+|\[\*\])(?:: .+)?',line)
            if node:defined.add(node[1])
            elif edge:refs.extend([edge[1],edge[2]])
            else:raise ValueError(f'{path.name}: unsupported source line {line}')
    else:raise ValueError(f'{path.name}: unknown diagram type')
    assert refs and set(refs)<=defined,(path.name,set(refs)-defined)
    return {'nodes':len(defined),'references':len(refs)}


class Links(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.links=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.append(attrs['id'])
        for attr in ('href','src'):
            if attr in attrs:self.links.append(attrs[attr])


def main():
    errors=[];warnings=[];counts={};main=(ROOT/'SYSTEM_DESIGN_MASTER_HANDBOOK.md').read_text(encoding='utf-8')
    coverage=json.loads((ROOT/'coverage.json').read_text());figures=json.loads((ROOT/'diagrams/manifest.json').read_text())
    assert [x['number'] for x in coverage]==list(range(1,112))
    topic_sections=re.split(r'<a id="topic-\d{3}"></a>',main)[1:]
    for row in coverage:
        section=next(s for s in topic_sections if re.match(r'\s*### '+str(row['number'])+r'\. ',s))
        # Last numbered topic is followed by the separate AI and case-study parts.
        section=section.split('\n## Part ',1)[0]
        headings=re.findall(r'^#### (\d+)\. ',section,re.M)
        assert headings==list(map(str,range(1,15))),(row['number'],headings)
        assert len(re.findall(r'^\*\*'+str(row['number'])+r'\.\d+ - ',section,re.M))==10
        for level in ('Beginner','Intermediate','Advanced'):assert '**'+level+' solution:**' in section
    assert not re.search(r'\bTODO\b|write this later|details omitted|\[\[FIG:',main,re.I)
    counts.update(topics=111,teaching_sections=111*14,topic_questions=1110,topic_exercises=333)
    png_count=svg_count=mmd_count=0;bounds=[]
    for figure in figures:
        png=ROOT/'diagrams'/figure['png']
        assert f'](diagrams/{figure["png"]})' in main,('figure absent from book',figure['id'])
        with Image.open(png) as image:
            image.verify();png_count+=1
        if figure['svg']:
            svg=ET.parse(ROOT/'diagrams'/figure['svg']).getroot();svg_count+=1
            width=float(svg.attrib['width']);height=float(svg.attrib['height'])
            for text in svg.findall('{http://www.w3.org/2000/svg}text'):
                size=int(text.attrib.get('font-size','24'));bold=text.attrib.get('font-weight')=='700'
                font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf',size)
                value=''.join(text.itertext());tw=max(font.getlength(s) for s in value.splitlines() or [''])
                x=float(text.attrib['x']);y=float(text.attrib['y']);left=x-tw/2 if text.attrib.get('text-anchor')=='middle' else x
                if left<0 or left+tw>width or y<0 or y>height:bounds.append({'figure':figure['id'],'text':value,'left':round(left,1),'right':round(left+tw,1),'y':y})
        if figure['mermaid']:mermaid_lint(ROOT/'diagrams'/figure['mermaid']);mmd_count+=1
    counts.update(pngs=png_count,svgs=svg_count,mermaid_sources=mmd_count)
    if bounds:errors.append({'svg_text_bounds':bounds})
    all_md=[p for p in ROOT.rglob('*.md') if 'build' not in p.relative_to(ROOT).parts]
    all_html=[p for p in ROOT.rglob('*.html') if 'build' not in p.relative_to(ROOT).parts]
    anchors={};links={}
    for path in all_md:
        text=path.read_text(encoding='utf-8');tokens=list(render_book.blocks(text))
        anchors[path.resolve()]={b[3] for b in tokens if b[0]=='heading'}
        no_code=re.sub(r'```.*?```','',text,flags=re.S)
        links[path]=re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',no_code)
    for path in all_html:
        parsed=Links();parsed.feed(path.read_text(encoding='utf-8'))
        if len(set(parsed.ids))!=len(parsed.ids):errors.append({'duplicate_html_ids':str(path)})
        anchors[path.resolve()]=set(parsed.ids);links[path]=parsed.links
    broken=[];checked=0
    for path,targets in links.items():
        for target in targets:
            if urlsplit(target).scheme or target.startswith('//'):continue
            relative,_,anchor=unquote(html.unescape(target)).partition('#')
            resolved=(path.parent/relative).resolve() if relative else path.resolve();checked+=1
            if not resolved.exists():broken.append([path.relative_to(ROOT).as_posix(),target,'missing file'])
            elif anchor and resolved in anchors and anchor not in anchors[resolved]:broken.append([path.relative_to(ROOT).as_posix(),target,'missing anchor'])
    if broken:errors.append({'broken_links':broken})
    for path in (ROOT/'examples').rglob('*.py'):ast.parse(path.read_text(encoding='utf-8'),filename=str(path))
    counts.update(local_links_checked=checked,markdown_files=len(all_md),html_files=len(all_html),python_files_parsed=len(list((ROOT/'examples').glob('*.py'))))
    report={'counts':counts,'errors':errors,'warnings':warnings,'mermaid_validation':'Strict exported-subset structure and all node/participant references checked; Mermaid engine unavailable.'}
    (HERE/'audit_results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2));return 1 if errors else 0


if __name__=='__main__':sys.exit(main())
