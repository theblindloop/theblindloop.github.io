"""Build the exact abstract and source-linked method examples without executing code."""
import ast,hashlib,html,json,re
from build_inverse_measurements import build_measurements

def abstract_content(source):
    text=re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',source,re.S).group(1)
    text=text.replace(r'\method{}','BlindLoop').replace('--','–')
    text=re.sub(r'\\url\{([^}]+)\}',r'\1',text)
    assert '\\' not in text, 'New abstract TeX needs explicit rendering'
    return re.sub(r'\s+',' ',text).strip()

def build_extras(root):
    configs=[
      ('profile-linked-ring-panel','Interlocked rings','Which panel contains interlocked rings?','Read each panel’s linked flag and select the unique linked pair.','Locate the five frames, separate the two ink colors, and count connected pieces of each color.','An interlocked pair has one connected curve of each color. A stacked pair splits the rear ring into two pieces. The program also checks that the color masks touch.'),
      ('profile-band-checkpoint-count','Checkpoints in a band','How many checkpoints are inside the band?','Compare each trace value with the lower and upper band values; count strict inclusions.','Measure the two blue boundary heights and the black marker center at each checkpoint.','At each of the six specified checkpoint positions, compare the measured marker height with the blue boundaries, using a four-pixel interior margin.'),
      ('profile-conditioned-fragmented-circle-center-cdefdbd958','Circle center','Which dot is at the circle’s center?','Compare the marker coordinates with the specified circle center; select the closest.','Segment the dark arc pixels and fit a circle by least squares.','Find each colored marker’s centroid and select the one nearest the fitted center. Reject weak fits and an insufficient gap between candidates.')]
    tabs=['<button id="teaser-tab-0" role="tab" aria-selected="true" aria-controls="teaser-panel-0" data-teaser="0"><img src="static/questions/profile-guitar-string-count/sample-1.png" alt=""><span>Guitar strings<small>Count dark runs</small></span></button>'];panels=[];records=[]
    for i,(id,label,title,forward,inverse,detail) in enumerate(configs,1):
        w=json.loads((root/'data/worlds'/f'{id}.json').read_text());samples=w['samples'];g=w['programs']['generator'];inv=w['programs']['inverse']
        source=(root/g['path']).read_text();node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='analytic_gold');excerpt='\n'.join(source.splitlines()[node.lineno-1:node.end_lineno])
        tabs.append(f'<button id="teaser-tab-{i}" role="tab" aria-selected="false" tabindex="-1" aria-controls="teaser-panel-{i}" data-teaser="{i}"><img src="{samples[0]['image']}" alt=""><span>{label}<small>{['Connected components','Compare boundaries','Fit a circle'][i-1]}</small></span></button>')
        input_fields=[['panels[].linked'],['trace_values','lower_values','upper_values'],['center','markers']][i-1]
        renderer_detail=[
            'Ring positions, colors, and front/back choices become five framed panels. Gaps show which ring passes behind at each crossing.',
            'Lower and upper values become the blue band. Trace values become a black line with six checkpoint markers.',
            'The circle geometry becomes separated dark arcs. Candidate coordinates become four colored dots.'
        ][i-1]
        input_markup='<div class="scene-field-list" aria-label="Scene fields used by the forward program">'+''.join('<code>'+html.escape(field)+'</code>' for field in input_fields)+'</div>'
        measurements,measurement_records=build_measurements(root,w)
        slides=[]
        for j,s in enumerate(samples):
            zoom=''
            if id=='profile-linked-ring-panel':
                panel_index=int(s['answer'].split('-')[-1])-1
                x=10+panel_index*210
                zoom=f'<div class="ring-detail"><svg viewBox="{x} 10 200 200" role="img" aria-label="Enlarged original pixels of recorded answer {s["answer"]}"><image href="{s["image"]}" width="1060" height="220" /></svg><span>{s["answer"]} · enlarged original pixels<br>The crop shows the panel identified by the recorded answer.</span></div>'
            slides.append(f'<figure data-teaser-slide="{j}" {"hidden" if j else ""}><a href="questions.html#world={id}&amp;sample={j+1}"><img src="{s["image"]}" loading="lazy" alt="{html.escape(title)} — recorded instance {j+1}"></a><figcaption>Original image · <a href="questions.html#world={id}&amp;sample={j+1}">Open full-size question ↗</a></figcaption>{zoom}</figure>')
        buttons=''.join(f'<button data-teaser-sample="{j}" aria-pressed="{str(j==0).lower()}" aria-label="Instance {j+1}"><img src="{samples[j]['image']}" alt=""><span>{j+1:02}</span></button>' for j in range(len(samples)))
        panels.append(f'''<section class="method-alt" id="teaser-panel-{i}" role="tabpanel" aria-labelledby="teaser-tab-{i}" hidden data-answers='{html.escape(json.dumps([s['answer'] for s in samples]),quote=True)}'><header class="alt-heading"><h3>{title}</h3><div class="alt-instances" role="group" aria-label="Recorded instances">{buttons}</div></header><div class="alt-diagram"><div class="alt-forward answer-panel answer-panel-forward"><header class="arm-title forward-title"><span>Forward program</span><h4>Scene → answer</h4></header><p class="arm-input-label">READ THE SCENE SPECIFICATION</p>{input_markup}<p>{forward}</p><details><summary>Original forward code</summary><pre tabindex="0"><code>{html.escape(excerpt)}</code></pre></details><a href="{g['path']}">Full forward source ↗</a><div class="alt-answer"><span>Forward answer</span><strong data-alt-answer>{html.escape(samples[0]['answer'])}</strong></div></div><div class="alt-image renderer-panel"><header class="render-title"><span>Rendered image</span><h4>The renderer draws the scene</h4><p class="renderer-description">{renderer_detail}</p></header><div class="lab-connection"><span>scene</span><span aria-hidden="true">→</span><strong>renderer</strong><span aria-hidden="true">→</span><span>pixels</span></div>{''.join(slides)}<div class="pixel-boundary"><span class="boundary-lock" aria-hidden="true">↳</span><p><strong>The inverse program receives only the image.</strong><br>The inverse does not receive the scene specification.</p></div></div><div class="alt-inverse answer-panel answer-panel-inverse"><header class="arm-title inverse-title"><span>Inverse program</span><h4>Image → answer</h4></header><p class="arm-input-label">READ ONLY THE IMAGE PIXELS</p><p class="inverse-intro">{inverse}</p>{measurements}<a href="{inv['path']}">Full inverse source ↗</a><div class="alt-answer"><span>Inverse answer</span><strong data-alt-answer>{html.escape(samples[0]['answer'])}</strong></div></div></div><div class="lab-comparison"><div><h4><span class="verifier-label">VERIFIER</span>Compare the answers</h4><p><span class="agreement-equation"><span>Forward <strong data-alt-comparison>{html.escape(samples[0]['answer'])}</strong></span><span aria-label="equals">=</span><span>Inverse <strong data-alt-comparison>{html.escape(samples[0]['answer'])}</strong></span></span><span class="agreement-explanation">The verifier repeats this check on fresh scenes. Both answers must be valid and agree on every scene included in the test.</span></p><a href="programs.html#verification">Image-replacement test →</a></div></div><details class="alt-question"><summary>Original question</summary><p>{html.escape(samples[0]['question'])}</p></details><p class="alt-note">The images and answers are from recorded instances. The diagrams illustrate measurements made from those images using the thresholds and operations in the source code. They are explanatory figures, not additional verification results.</p></section>''')
        records.append({'world':id,'samples':samples,'forward':g,'inverse':inv,'displayMeasurements':measurement_records,'forwardExcerpt':{'startLine':node.lineno,'endLine':node.end_lineno,'text':excerpt}})
    (root/'data/method-examples.json').write_text(json.dumps(records,indent=2)+'\n')
    return '<p class="teaser-picker-label">Choose a question world</p><div class="teaser-tabs" role="tablist" aria-label="Method question examples">'+''.join(tabs)+'</div>',''.join(panels)

def steering_overview(root):
    examples=json.loads((root/'data/steering-examples.json').read_text())['examples']
    result='<div class="support-atlas"><div class="atlas-corner">Extent ↓<br>Shape →</div>'+''.join(f'<div class="atlas-column">{name}<small>{desc}</small></div>' for name,desc in [('Compact','Concentrated region'),('Pathlike','Elongated pattern'),('Multipart','Separated regions')])
    for scale,desc in [('focal','Small extent'),('regional','Intermediate extent'),('distributed','Broad extent')]:
        result+=f'<div class="atlas-row">{scale.title()}<small>{desc}</small></div>'
        for shape in ['compact','pathlike','multipart']:
            key=scale+'-'+shape;e=next(e for e in examples if e['category']==key)
            result+=f'<a class="atlas-example" href="steering-gallery.html#{key}" aria-label="Browse {scale} {shape} questions"><img src="{e["image"]}" loading="lazy" alt="Recorded {scale} {shape} example"><span>{scale.title()} · {shape}<b aria-hidden="true">↗</b></span></a>'
    return result+'</div><p class="small-note">Original question images from worlds with the measured category. Labels summarize measurements across scenes; these thumbnails are not support masks. Select a cell to browse its gallery.</p><a class="study-detail-link" href="steering-gallery.html">Browse all nine categories →</a>'
