#!/usr/bin/env python3
"""Build nine category examples from recorded, complete support measurements."""
import argparse,csv,hashlib,html,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def build(paper):
    source=paper/'figures/results/image-support-steering/data/support_audit_replay.csv'
    rows=list(csv.DictReader(source.open()))
    joins={r['replay_record_id']:r for r in csv.DictReader((source.parent/'support_replay_join.csv').open())}
    worlds=[json.loads(p.read_text()) for p in (ROOT/'data/worlds').glob('*.json')]
    by_record={w['recordId']:w for w in worlds}
    cells=[];panels=[];manifest=[]
    scales=['focal','regional','distributed'];shapes=['compact','pathlike','multipart']
    for y,scale in enumerate(scales):
      for x,shape in enumerate(shapes):
        key=scale+'-'+shape;label=scale.title()+' · '+shape
        eligible=[r for r in rows if r['support_scale']==scale and r['support_shape']==shape and r['attestation_status']=='complete' and float(r['descriptor_stability_fraction'])>=2/3 and r['record_id'] in by_record and joins[r['record_id']]['qd_target_match']=='True']
        eligible.sort(key=lambda r:(-float(r['descriptor_stability_fraction']),len(by_record[r['record_id']]['samples'][0]['question']),r['record_id']))
        chosen=eligible[:2];assert len(chosen)==2,key
        # Category glyphs are diagrams, not measured support maps.
        size=[.36,.65,.9][y];shape_svg={'compact':'<rect x="20" y="20" width="60" height="60" rx="12"/>','pathlike':'<path d="M10 75L30 30 52 63 73 22 90 35" fill="none" stroke="currentColor" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>','multipart':'<circle cx="20" cy="25" r="12"/><circle cx="78" cy="25" r="12"/><circle cx="25" cy="78" r="12"/><circle cx="80" cy="75" r="12"/>'}[shape]
        icon=f'<svg viewBox="0 0 100 100" aria-hidden="true"><rect class="glyph-field" x="2" y="2" width="96" height="96" rx="9"/><g transform="translate({50*(1-size)} {50*(1-size)}) scale({size})" fill="currentColor">{shape_svg}</g></svg>'
        cells.append(f'<button type="button" class="category-cell scale-{scale}" data-category="{key}" aria-pressed="{str(x==0 and y==0).lower()}" aria-controls="category-{key}">{icon}<span>{label}</span></button>')
        cards=[]
        for r in chosen:
            w=by_record[r['record_id']];s=w['samples'][0]
            manifest.append({'category':key,'world':w['id'],'recordId':w['recordId'],'measuredScale':scale,'measuredShape':shape,'stability':float(r['descriptor_stability_fraction']),'measurementScenes':int(r['attestation_scene_count']),'requestedCategory':joins[r['record_id']]['qd_target_cell'],'image':s['image'],'imageSha256':s['sha256'],'question':s['question'],'answer':s['answer']})
            cards.append(f'<article class="steering-sample"><a href="questions.html#world={w["id"]}&amp;sample=1"><img src="{s["image"]}" alt="{html.escape(w["title"])}" loading="lazy"></a><div><span class="sample-category">Measured {label}</span><h3>{html.escape(w["title"])}</h3><p class="sample-question">{html.escape(s["question"])}</p><details><summary>Recorded answer</summary><p>{html.escape(s["answer"])}</p></details><a href="questions.html#world={w["id"]}&amp;sample=1">Try all three instances ↗</a><p class="small-note">The world matched its requested category. {float(r["descriptor_stability_fraction"])*100:g}% category agreement across {r["attestation_scene_count"]} measured scenes.</p></div></article>')
        panels.append(f'<section id="category-{key}" class="category-panel" {"hidden" if x or y else ""}><h2>{label}</h2><div class="steering-samples">'+''.join(cards)+'</div></section>')
    template=(ROOT/'content/steering-page.html').read_text().replace('{{cells}}',''.join(cells)).replace('{{panels}}',''.join(panels))
    index=(ROOT/'index.html').read_text();head=index[:index.index('<body')];head=head.replace('<title>BlindLoop — Executable Visual Questions</title>','<title>Image-support steering — BlindLoop</title>')
    import re
    head=re.sub(r'\s*<script[^>]+></script>','',head)
    head=head.replace('</head>','<link rel="stylesheet" href="static/css/steering.css"><script src="static/js/steering.js" defer></script></head>')
    nav=index[index.index('    <nav'):index.index('    <main')]
    nav=nav.replace('href="#"','href="index.html"');nav=re.sub(r'href="#([^\"]+)"',r'href="index.html#\1"',nav)
    footer=index[index.index('    <footer'):index.index('    <dialog')]
    (ROOT/'steering.html').write_text(head+'<body class="steering-page"><a class="skip-link" href="#main">Skip to content</a>'+nav+'<main id="main">'+template+'</main>'+footer+'</body></html>\n')
    (ROOT/'data/steering-examples.json').write_text(json.dumps({'source':str(source.relative_to(paper)),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'requestJoinSource':str((source.parent/'support_replay_join.csv').relative_to(paper)),'requestJoinSha256':hashlib.sha256((source.parent/'support_replay_join.csv').read_bytes()).hexdigest(),'examples':manifest},indent=2)+'\n')
    print('Built steering explainer: 9 measured categories, 18 worlds, original recorded images/questions.')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--paper',type=Path,required=True);build(p.parse_args().paper)
