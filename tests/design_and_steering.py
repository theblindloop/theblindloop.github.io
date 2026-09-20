#!/usr/bin/env python3
import argparse,csv,hashlib,json
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
def main(base,paper):
    from PIL import Image
    pixels=json.loads((ROOT/'data/method-pixels.json').read_text())
    for item in pixels['instances']:
        path=ROOT/item['image']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256']
        img=Image.open(path).convert('RGB');x,y=item['rowOrigin']
        assert item['pixels']==[[list(img.getpixel((x+i,y+j))) for i in range(86)] for j in range(3)]
        for row in item['pixels']:
            dark=[sum(rgb)/3<105 for rgb in row]
            assert sum(v and (i==0 or not dark[i-1]) for i,v in enumerate(dark))==int(item['answer'])
    data=json.loads((ROOT/'data/steering-examples.json').read_text())
    if paper:
        source=paper/data['source'];assert hashlib.sha256(source.read_bytes()).hexdigest()==data['sourceSha256']
        rows={r['record_id']:r for r in csv.DictReader(source.open())}
        join_source=paper/data['requestJoinSource']
        assert hashlib.sha256(join_source.read_bytes()).hexdigest()==data['requestJoinSha256']
        joins={r['replay_record_id']:r for r in csv.DictReader(join_source.open())}
        for e in data['examples']:
            r=rows[e['recordId']]
            assert joins[e['recordId']]['qd_target_match']=='True'
            assert joins[e['recordId']]['qd_target_cell']==e['requestedCategory']
            assert (r['support_scale'],r['support_shape'])==(e['measuredScale'],e['measuredShape'])
            assert float(r['descriptor_stability_fraction'])==e['stability']
    assert len(data['examples'])==18
    assert len({e['category'] for e in data['examples']})==9
    for e in data['examples']:
        w=json.loads((ROOT/'data/worlds'/f'{e["world"]}.json').read_text());s=w['samples'][0]
        assert e['image']==s['image'] and e['question']==s['question'] and e['answer']==s['answer']
        assert hashlib.sha256((ROOT/e['image']).read_bytes()).hexdigest()==e['imageSha256']
    with sync_playwright() as p:
        b=p.chromium.launch();page=b.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce');errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(base+'/#method',wait_until='networkidle');page.evaluate('document.fonts.ready')
        for i in range(3):
            page.locator(f'[data-method-sample="{i}"]').click()
            assert page.locator('[data-method-count]').all_text_contents()==[str(6+i)]*3
            assert page.locator('#method-runs i').count()==6+i
            assert page.locator('#method-image').evaluate('(img)=>img.decode().then(()=>img.naturalWidth>0)')
        page.locator('[data-method-sample="0"]').click()
        page.locator('.verification-map').screenshot(path=str(ROOT/'artifacts/redesign-method-desktop.png'))
        page.locator('#training').screenshot(path=str(ROOT/'artifacts/redesign-training-desktop.png'))
        assert page.locator('#table-transfer td.delta-positive').count()==4
        page.goto(base+'/results.html#external',wait_until='networkidle')
        assert page.locator('#table-external td.delta-negative').count()>0
        page.locator('#external').screenshot(path=str(ROOT/'artifacts/redesign-external-desktop.png'))
        for width in [320,390,768,1024,1440]:
            page.set_viewport_size({'width':width,'height':844})
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),width
        page.set_viewport_size({'width':390,'height':844})
        page.goto(base+'/#method',wait_until='networkidle')
        page.locator('.verification-map').screenshot(path=str(ROOT/'artifacts/redesign-method-mobile.png'))
        page.goto(base+'/steering.html',wait_until='networkidle')
        expect(page.locator('.category-cell')).to_have_count(9)
        expect(page.locator('#probe-grid button')).to_have_count(64)
        for button in page.locator('.category-cell').all():
            button.click();expect(button).to_have_attribute('aria-pressed','true')
            assert page.locator('.category-panel:visible').count()==1
            assert page.locator('.category-panel:visible .steering-sample').count()==2
            for img in page.locator('.category-panel:visible img').all():assert img.evaluate('(img)=>img.decode().then(()=>img.naturalWidth>0)')
        page.get_by_role('button',name='Mask row 4, column 5',exact=True).click()
        expect(page.locator('#probe-mask')).to_be_visible()
        page.locator('#reset-mask').click();expect(page.locator('#probe-mask')).to_be_hidden()
        page.locator('.category-cell').first.click()
        for width in [320,390,768,1024,1440]:
            page.set_viewport_size({'width':width,'height':844});assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),('steering',width)
            page.evaluate('document.querySelectorAll("details").forEach(d=>d.open=true)');assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),('steering-details',width)
            page.evaluate('document.querySelectorAll("details").forEach(d=>d.open=false)')
        page.locator('#category-grid').screenshot(path=str(ROOT/'artifacts/steering-grid-desktop.png'))
        page.locator('#masking').screenshot(path=str(ROOT/'artifacts/steering-masking-desktop.png'))
        page.set_viewport_size({'width':390,'height':844})
        page.locator('#category-grid').screenshot(path=str(ROOT/'artifacts/steering-grid-mobile.png'))
        page.locator('#masking').screenshot(path=str(ROOT/'artifacts/steering-masking-mobile.png'))
        page.locator('.category-panel:visible .steering-sample a').first.click()
        expect(page.locator('#question-viewer')).to_be_visible()
        assert not errors,errors
        b.close()
    print('PASS: 18 source-bound examples across 9 categories; three method instances; delta colors; 64 mask positions; gallery links; 320–1440px overflow checks.')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:8767');p.add_argument('--paper',type=Path);a=p.parse_args();main(a.url.rstrip('/'),a.paper)
