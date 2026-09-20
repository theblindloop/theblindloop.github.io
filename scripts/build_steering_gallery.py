"""Render a category gallery of recorded, request-matched measured worlds."""
import html,json,re

def build_gallery(root,records):
    categories=list(dict.fromkeys(r['category'] for r in records))
    buttons=[];panels=[]
    for i,key in enumerate(categories):
        examples=[r for r in records if r['category']==key]
        label=key.replace('-',' · ').capitalize()
        buttons.append(f'<button data-support-category="{key}" aria-pressed="{str(i==0).lower()}" aria-controls="support-{key}">{label}<small>{len(examples)} worlds</small></button>')
        cards=[]
        for e in examples:
            w=json.loads((root/'data/worlds'/f'{e["world"]}.json').read_text())
            cards.append(f'<article class="support-card"><a href="questions.html#world={w["id"]}&amp;sample=1"><img src="{e["image"]}" loading="lazy" alt="{html.escape(w["title"])}"></a><div><h3>{html.escape(w["title"])}</h3><details><summary>Read the original question</summary><p>{html.escape(e["question"])}</p></details><details><summary>Recorded answer</summary><p>{html.escape(e["answer"])}</p></details><a href="questions.html#world={w["id"]}&amp;sample=1">Try all three instances ↗</a><p class="support-measurement">{e["stability"]*100:g}% category agreement across {e["measurementScenes"]} measured scenes.</p></div></article>')
        panels.append(f'<section id="support-{key}" class="support-panel" {"hidden" if i else ""}><h2>{label}</h2><p>{len(examples)} recorded worlds · {len(examples)*3} instances available in the question viewer</p><div class="support-cards">'+''.join(cards)+'</div></section>')
    head=(root/'index.html').read_text().split('</head>')[0]
    head=re.sub(r'<script[^>]*>.*?</script>','',head,flags=re.S)
    head=re.sub(r'<title>.*?</title>','<title>Questions by image-support category · BlindLoop</title>',head,flags=re.S)
    body=f'''<body class="support-gallery-page"><nav class="site-nav" aria-label="Main navigation"><a class="wordmark" href="index.html">BlindLoop</a><div class="nav-links"><a href="index.html#steering">Results overview</a><a href="steering.html">How steering works</a><a href="questions.html">All questions</a></div></nav><main class="container site-width support-gallery"><header><p class="eyebrow">Image-support gallery</p><h1>Questions by image-support category</h1><p>Browse {len(records)} recorded question worlds by their measured image-support category. Each world has three original instances to try.</p><p class="support-caveat">A category summarizes which regions affect the inverse program when masked. Each label combines measurements across several scenes; it is not a mask of the displayed image or a measure of human attention. The selected worlds have complete measurements, match the requested category, and receive that category in at least two thirds of the analyzed scenes.</p><a href="steering.html#masking">How the masking test works →</a></header><nav class="support-filters" aria-label="Measured categories">{''.join(buttons)}</nav><div id="support-panels">{''.join(panels)}</div></main><footer class="reading-footer"><a href="index.html">Project overview</a> · <a href="steering.html">Steering explanation</a></footer></body></html>'''
    (root/'steering-gallery.html').write_text(head+'<script src="static/js/support-gallery.js" defer></script></head>'+body)
    (root/'data/steering-gallery.json').write_text(json.dumps({'selection':'Up to 12 worlds per measured category; same source audit and request join as steering-examples.json; descending stability, then question length and record ID.','examples':records},indent=2)+'\n')

    from sync_navigation import sync
    sync(root)
