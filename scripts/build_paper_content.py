#!/usr/bin/env python3
"""Build static paper sections from manuscript tables and exact source excerpts.
Read-only inputs; imported research programs are parsed, never executed.
"""
import argparse
import ast
import hashlib
import html
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
MACROS = {'geminiflash':'Gemini', 'solhigh':'Sol (high)', 'solmax':'Sol (max)', 'luna':'Luna', 'opus':'Opus 5', 'deepseek':'DS-V4-Flash', 'gemmatwelve':'Gemma 4 12B', 'gemmathirtyone':'Gemma 4 31B', 'qwentwentyseven':'Qwen 3.8 27B'}
def clean(s):
    s = re.sub(r'\\cite\{[^}]+\}', '', s)
    s = re.sub(r'\\increase\{([^}]+)\}', r'+\1', s)
    s = re.sub(r'\\decrease\{([^}]+)\}', r'-\1', s)
    for key, val in sorted(MACROS.items(),key=lambda x:-len(x[0])): s=s.replace('\\'+key,val)
    s=s.replace('\\scriptstyle','').replace('\\pm','±').replace('\\times','×').replace('\\%','%')
    return re.sub(r'\s+',' ',s.translate(str.maketrans('','','${}'))).strip()
def rows(source,label):
    start=source.index('\\label{'+label+'}')
    body=source[start:source.index('\\bottomrule',start)]
    body=body[body.index('\\midrule')+len('\\midrule'):]
    body=re.sub(r'\\(?:midrule|cmidrule(?:\([^)]*\))?\{[^}]*\})','',body)
    body=re.sub(r'\\multirow[^\n]*', '', body)
    result=[]
    for row in body.split('\\\\'):
        if '&' not in row: continue
        cells=row.split('&')
        if '\\multirow' in cells[0] or not cells[0].strip():cells=cells[1:]
        cells=[clean(x.replace('\\midrule','')) for x in cells]
        if cells:result.append(cells)
    return result

def table(id,caption,headers,rs):
    assert all(len(r)==len(headers) for r in rs),(id,rs)
    head=''.join('<th scope="col">'+html.escape(x)+'</th>' for x in headers)
    def cell(i, value):
        delta = (id == 'external' and i > 0) or ('Change' in headers[i]) or ('change' in headers[i])
        style = ''
        if delta:
            try:
                value_number = float(value.split()[0])
                style = ' class="delta-positive"' if value_number > 0 else (' class="delta-negative"' if value_number < 0 else '')
            except ValueError: pass
        tag = 'th' if i == 0 else 'td'
        return '<' + tag + (' scope="row"' if i == 0 else '') + style + '>' + html.escape(value) + '</' + tag + '>'
    body=''.join('<tr>'+''.join(cell(i,x) for i,x in enumerate(r))+'</tr>' for r in rs)
    return f'<p class="table-scroll-hint">Scroll horizontally to view all columns →</p><div class="paper-table" tabindex="0" role="region" aria-label="{html.escape(caption)}"><table id="table-{id}"><caption>{caption}</caption><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'

def build(paper, reuse_tables=False):
    sources={name:(paper/name).read_text() for name in ['iclr2027_conference.tex','appendix.tex']}
    configs=[('coverage','appendix.tex','tab:discovery-evaluator-detail'),('generation','appendix.tex','tab:discovery-generation'),('evaluation','iclr2027_conference.tex','tab:discovery-generator-evaluation-preview'),('feedback','appendix.tex','tab:model-feedback-summary'),('transfer','appendix.tex','tab:sft-generated-transfer'),('external','appendix.tex','tab:sft-multisplit'),('external-full','appendix.tex','tab:sft-external-full'),('heldout','appendix.tex','tab:sft-indistribution'),('direct','appendix.tex','tab:sft-direct'),('excluded','appendix.tex','tab:downstream-profile-holdout')]
    # Copy edits can reuse the published table snapshot without changing its provenance.
    datasets=json.loads((ROOT/'data/paper-tables.json').read_text()) if reuse_tables else {key:{'source':name,'label':label,'rows':rows(sources[name],label)} for key,name,label in configs}
    rs=lambda key:datasets[key]['rows']
    tables={}
    tables['coverage']=table('coverage','Scored responses and accuracy in the first two collections',['Evaluator','Profile: scored / total','Profile: accuracy','Steered: scored / total','Steered: accuracy'],rs('coverage'))
    for suffix,cols in [('profile',range(1,5)),('steered',range(5,9))]:
        tables['generation-'+suffix]=table('generation-'+suffix,'Generation outcomes: '+('profile-conditioned' if suffix=='profile' else 'image-support-steered')+' discovery',['Coding agent','Episodes','Accepted worlds','Passed replay','Accepted / hour'],[[r[0]]+[r[i] for i in cols] for r in rs('generation')])
    headers=['Coding agent','Worlds','Sol (high)','Opus 5','Gemini','Gemma 4 12B','Gemma 4 31B','Qwen 3.8 27B']
    for suffix,subset in [('profile',rs('evaluation')[:6]),('steered',rs('evaluation')[6:])]:tables['evaluation-'+suffix]=table('evaluation-'+suffix,'Evaluator accuracy (%): '+suffix+' collection',headers,subset)
    tables['feedback-generation']=table('feedback-generation','Model-feedback discovery: generation outcomes',['Coding agent','Passed checks','Complete panel','Passed replay','Panel-hard','Panel-hard (%)'],[r[:6] for r in rs('feedback')])
    tables['feedback-evaluation']=table('feedback-evaluation','Model-feedback discovery: accuracy (%) on complete-panel worlds',[headers[0]]+headers[2:],[[r[0]]+r[6:] for r in rs('feedback')])
    for key,caption in [('transfer','Transfer to 252 model-feedback worlds · 1,260 instances'),('heldout','Held-out profile-conditioned worlds · 45 worlds, 1,691 instances'),('direct','Direct training on model-feedback worlds · 50 held-out worlds, 250 instances')]:
        tables[key]=table(key,caption,['Model','Base (%)','SFT (%)','Change (pp)'],rs(key))
    tables['external']=table('external','External benchmarks: changes across four training splits',['Benchmark','Gemma 4 12B','Gemma 4 31B','Qwen 3.8 27B','Mean change'],rs('external'))
    tables['excluded']=table('excluded','Exclude one profile from training · Gemma 4 12B',['Excluded profile','Instances','Base (%)','SFT (%)','Change (pp)'],rs('excluded'))
    for i,model in enumerate(['Gemma 4 12B','Gemma 4 31B','Qwen 3.8 27B']):
        tables['external-full-'+str(i)]=table('external-full-'+str(i),'Single-checkpoint external scores · '+model,['Benchmark','Instances','Base','SFT','Change'],[r[:2]+r[2+3*i:5+3*i] for r in rs('external-full')])
    tables['human']=table('human','Classified human-review outcomes',['Discovery experiment','Instances','Neither reviewer','One reviewer','Both reviewers'],[['Profile-conditioned','400','370','25','5'],['Image-support-steered','200','183','13','4'],['Model-feedback','200','180','16','4'],['Total','800','733','54','13']])
    definitions=[('profile-guitar-string-count','Counting','Read the number of strings specified in the scene.','Locate the bright bridge in the image, identify narrow dark runs across it, and count them. Three adjacent rows must agree.',[("generator",'analytic_gold')],[("inverse",'decision_from_image',46,58)]),('steered-marked-articulation-search','Connectivity','Remove each marked cell from its specified island and count the remaining connected pieces.','Recover the colored cells and gold markers from pixels. Remove each recovered marked cell and find which island splits.',[("generator",'_scores'),("generator",'analytic_gold')],[("inverse",'decision_from_image')]),('feedback-breach-relevel-depth','A change to the scene','Remove the specified red column and recompute the water depth over the queried column.','Read the column heights, red column, and arrow from the image. Remove the recovered column and recompute the water level.',[("generator",'analytic_gold')],[("inverse",'decision_from_image'),("inverse",'_standing')])]
    programs=[];manifest=[]
    for n,(id,topic,fwd,inv,fs,ins) in enumerate(definitions):
        w=json.loads((ROOT/'data/worlds'/f'{id}.json').read_text())
        def excerpt(parts):
            out=[]
            for part in parts:
                kind,fn,*span=part; p=ROOT/w['programs'][kind]['path'];text=p.read_text();node=next(x for x in ast.parse(text).body if isinstance(x,ast.FunctionDef) and x.name==fn)
                a,b=span if span else (node.lineno,node.end_lineno)
                code='\n'.join(text.splitlines()[a-1:b]);out.append(code)
                manifest.append({'world':id,'path':w['programs'][kind]['path'],'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'startLine':a,'endLine':b,'text':code})
            return html.escape('\n\n'.join(out))
        images=''.join(f'<figure><a href="#world={id}&amp;sample={i+1}"><img loading="lazy" src="{s["image"]}" alt="{html.escape(w["title"])}: recorded instance {i+1}"></a><figcaption>Instance {i+1} · recorded answer <strong>{html.escape(s["answer"])}</strong></figcaption></figure>' for i,s in enumerate(w['samples']))
        programs.append(f'''<article class="program-example" id="program-example-{n}" {'hidden' if n else ''}><h3>{html.escape(w['title'])}</h3><div class="instance-strip">{images}</div><blockquote><span class="small-label">Original question</span><p>{html.escape(w['samples'][0]['question'])}</p></blockquote><div class="program-columns"><div class="forward-code"><h4>Forward program · scene → answer</h4><p>{fwd}</p><pre tabindex="0"><code>{excerpt(fs)}</code></pre><a href="{w['programs']['generator']['path']}">Read full renderer and forward source ↗</a></div><div class="inverse-code"><h4>Inverse program · image → answer</h4><p>{inv}</p><pre tabindex="0"><code>{excerpt(ins)}</code></pre><a href="{w['programs']['inverse']['path']}">Read full inverse source ↗</a></div></div></article>''')
    for name in ['stovetop_original','stovetop_same_answer','stovetop_answer_changed']:
        src=paper/'figures/results/inverse-arm'/f'{name}.png'; dest=ROOT/'static/images/method'/f'{name}.png';dest.write_bytes(src.read_bytes())
        manifest.append({'paperImage':str(src.relative_to(paper)),'path':str(dest.relative_to(ROOT)),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
    profile_overall=rs('evaluation')[5]
    steered_overall=rs('evaluation')[11]
    summary_rows=[[label, 'Frontier' if i<3 else 'Open-weight', profile_overall[i+2], steered_overall[i+2]] for i,label in enumerate(headers[2:])]
    tables['evaluation-summary']=table('evaluation-summary','Model accuracy (%) over scored responses',['Model','Model group','Profile-conditioned','Image-support-steered'],summary_rows)
    from build_method_extras import build_extras, abstract_content, steering_overview
    teaser_tabs,teaser_panels=build_extras(ROOT)
    tables['teaser-tabs']=teaser_tabs
    tables['teaser-panels']=teaser_panels
    tables['steering-atlas']=steering_overview(ROOT)
    template=(ROOT/'content/paper-sections.html').read_text()
    for key,markup in tables.items():template=template.replace('{{'+key+'}}',markup)
    template=template.replace('{{programs}}','\n'.join(programs))
    preview_world=json.loads((ROOT/'data/worlds/profile-guitar-string-count.json').read_text())
    preview=''.join(f'<figure><a href="#world={preview_world["id"]}&amp;sample={i+1}"><img loading="lazy" src="{sample["image"]}" alt="Recorded guitar instance {i+1}"></a><figcaption>Recorded answer: {html.escape(sample["answer"])}</figcaption></figure>' for i,sample in enumerate(preview_world['samples']))
    template=template.replace('{{program-preview}}','<div class="instance-strip">'+preview+'</div>')
    assert '{{' not in template
    index=ROOT/'index.html';text=index.read_text()
    abstract=abstract_content(sources['iclr2027_conference.tex'])
    abstract_html='<section class="section abstract-section" id="abstract"><div class="container reading-width"><h2 class="title is-3 has-text-centered">Abstract</h2><p class="paper-abstract">'+html.escape(abstract)+'</p></div></section>'
    text=re.sub(r'<section[^>]*id="abstract".*?</section>',abstract_html,text,flags=re.S)
    (ROOT/'data/paper-abstract.json').write_text(json.dumps({'source':'iclr2027_conference.tex','sourceSha256':hashlib.sha256(sources['iclr2027_conference.tex'].encode()).hexdigest(),'text':abstract},indent=2)+'\n')
    start=text.index('<!-- PAPER:START -->');end=text.index('<!-- PAPER:END -->')
    index.write_text(text[:start]+'<!-- PAPER:START -->\n'+template+'\n'+text[end:])
    (ROOT/'data/paper-tables.json').write_text(json.dumps(datasets,indent=2)+'\n')
    (ROOT/'data/paper-content-provenance.json').write_text(json.dumps({'sourceHashes':(json.loads((ROOT/'data/paper-content-provenance.json').read_text())['sourceHashes'] if reuse_tables else {k:hashlib.sha256(v.encode()).hexdigest() for k,v in sources.items()}),'excerptsAndImages':manifest},indent=2)+'\n')
    from build_story_pages import build_story_pages
    detailed=(ROOT/'content/detailed-sections.html').read_text()
    for key,markup in tables.items(): detailed=detailed.replace('{{'+key+'}}',markup)
    detailed=detailed.replace('{{programs}}','\n'.join(programs))
    assert '{{' not in detailed
    build_story_pages(ROOT,detailed)
    print('Built paper sections, tables, three source demonstrations, and renderer-swap illustration.')
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--paper',type=Path,required=True);parser.add_argument('--reuse-tables',action='store_true',help='Keep published table data and source hashes during a copy-only rebuild');args=parser.parse_args();build(args.paper,args.reuse_tables)
