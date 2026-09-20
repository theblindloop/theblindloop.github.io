"""Validate exact abstract, recorded teaser instances, and measured-category galleries."""
import hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_method_extras import abstract_content
if len(sys.argv)!=2: raise SystemExit('Usage: python3 tests/method_and_support.py /path/to/manuscript')
paper=Path(sys.argv[1])
abstract=abstract_content((paper/'iclr2027_conference.tex').read_text())
records=json.loads((ROOT/'data/method-examples.json').read_text())
for r in records:
 for kind in ['forward','inverse']:
  p=ROOT/r[kind]['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r[kind]['sha256']
 lines=(ROOT/r['forward']['path']).read_text().splitlines();e=r['forwardExcerpt'];assert '\n'.join(lines[e['startLine']-1:e['endLine']])==e['text']
 for measurement,sample in zip(r['displayMeasurements'],r['samples']):
  assert measurement['answer']==sample['answer']
  assert measurement['imageSha256']==sample['sha256']
  if 'panels' in measurement:
   winners=[p['panel'] for p in measurement['panels'] if p['counts']==[1,1] and p['touching']]
   assert winners==[int(sample['answer'].split('-')[-1])]
  elif 'checkpoints' in measurement:
   assert str(sum(p['upperY']+4 < p['markerY'] < p['lowerY']-4 for p in measurement['checkpoints']))==sample['answer']
  else:
   assert min(measurement['markers'],key=lambda m:m['distance'])['name']==sample['answer']
   assert measurement['rms']<5
 for s in r['samples']:assert hashlib.sha256((ROOT/s['image']).read_bytes()).hexdigest()==s['sha256']
gallery=json.loads((ROOT/'data/steering-gallery.json').read_text())['examples']
assert len({r['category'] for r in gallery})==9
assert len({r['world'] for r in gallery})==len(gallery)
for r in gallery:
 assert hashlib.sha256((ROOT/r['image']).read_bytes()).hexdigest()==r['imageSha256']
 assert r['stability']>=2/3
with sync_playwright() as p:
 b=p.chromium.launch();page=b.new_page(viewport={'width':1440,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8767',wait_until='networkidle')
 assert page.locator('#abstract p').inner_text()==abstract
 assert page.locator('#method .section-intro .eyebrow').evaluate('(e)=>getComputedStyle(e,"::before").content')=='counter(chapter, decimal-leading-zero)' # CSS numbering remains driven by section order
 assert page.locator('[data-teaser]').count()==4
 styles=[]
 for i in range(4):
  page.locator(f'[data-teaser="{i}"]').click();panel=page.locator(f'#teaser-panel-{i}')
  assert panel.locator('.render-title').inner_text().startswith('Rendered image\nThe renderer draws the scene')
  expect(panel.locator('.pixel-boundary')).to_be_visible()
  styles.append(panel.locator('.answer-panel').evaluate_all('(els)=>els.map(e=>{const s=getComputedStyle(e);const t=getComputedStyle(e.querySelector(".arm-title>span"));return [s.backgroundColor,s.borderTopColor,s.borderRadius,t.color,t.fontSize,t.fontWeight]})'))
 assert all(style==styles[0] for style in styles),styles
 for i,r in enumerate(records,1):
  page.locator(f'[data-teaser="{i}"]').click();panel=page.locator(f'#teaser-panel-{i}');expect(panel).to_be_visible()
  for j,s in enumerate(r['samples']):
   panel.locator(f'[data-teaser-sample="{j}"]').click();expect(panel.locator(f'[data-inverse-measurement="{j}"]')).to_be_visible();assert panel.locator('[data-alt-answer]').all_text_contents()==[s['answer']]*2
   assert panel.locator('[data-alt-comparison]').all_text_contents()==[s['answer']]*2
   img=panel.locator('[data-teaser-slide]:visible img');assert img.get_attribute('src')==s['image'];assert img.evaluate('(i)=>i.decode().then(()=>i.naturalWidth>0)')
  for width in [320,390,768,1440]:
   page.set_viewport_size({'width':width,'height':1000});panel.locator('details').first.evaluate('(e)=>e.open=true');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(i,width)
  page.set_viewport_size({'width':1440,'height':1000});panel.screenshot(path=str(ROOT/f'artifacts/teaser-{i}.png'))
 page.locator('[data-teaser="0"]').click();expect(page.locator('.method-laboratory')).to_be_visible()
 page.locator('[data-teaser="3"]').focus();page.keyboard.press('ArrowRight');expect(page.locator('[data-teaser="0"]')).to_be_focused()
 for width in [1440,390]:
  page.set_viewport_size({'width':width,'height':1000});page.locator('.support-atlas').screenshot(path=str(ROOT/f'artifacts/support-atlas-{width}.png'))
 page.locator('.atlas-example').last.click();page.wait_for_url('**/steering-gallery.html#distributed-multipart');expect(page.locator('#support-distributed-multipart')).to_be_visible()
 for button in page.locator('[data-support-category]').all():
  button.click();key=button.get_attribute('data-support-category');panel=page.locator('#support-'+key);expect(panel).to_be_visible();assert panel.locator('.support-card').count()==len([r for r in gallery if r['category']==key])
 for width in [320,390,768,1440]:
  page.set_viewport_size({'width':width,'height':1000});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 page.set_viewport_size({'width':1440,'height':1000});page.locator('.support-panel:visible').screenshot(path=str(ROOT/'artifacts/support-gallery-desktop.png'))
 assert not errors,errors;b.close()
print(f'PASS: verbatim abstract; three added source-bound worlds; nine recorded instances; four teaser tabs; {len(gallery)} gallery worlds; nine category filters; keyboard and mobile layouts.')
